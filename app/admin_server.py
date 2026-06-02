#!/usr/bin/env python3
from __future__ import annotations

import cgi
import base64
import io
import hmac
import json
import mimetypes
import os
import re
import shutil
import subprocess
import hashlib
import secrets
import zipfile
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
STATIC_ROOT = REPO_ROOT / "static"
TEMPLATE_PATH = REPO_ROOT / "templates" / "admin.html"
RUNS_ROOT = REPO_ROOT / "runs"
HOST_DEFAULT = "127.0.0.1"
PORT_DEFAULT = 8091
AUTH_FILE_DEFAULT = REPO_ROOT / ".runtime" / "admin_basic_auth.json"
MAX_CONTENT_BYTES = 200 * 1024
AUTH_REALM = "Course Factory Admin"
AUTH_USERNAME = "admin"
AUTH_ITERATIONS = 210_000
RUN_ID_RE = re.compile(r"^\d{8}_\d{6}_[a-z][a-z0-9-]*$")
RUN_SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
RUN_ALLOWED_READ_EXTS = {".md", ".json", ".txt", ".log"}
RUN_REQUEST_FILENAME = "RUN_REQUEST.md"
RUN_STATUS_FILENAME = "status.json"
RUN_PENDING_STATUS = "pending_codex_execution"
RUN_INPUT_DIR = Path("input") / "source_pack"
RUN_UPSTREAM_INPUT_DIR = Path("input") / "upstream_artifacts"
RUN_OUTPUT_DIR = Path("output")
RUN_LOG_DIR = Path("logs")
RUN_ZIP_EXTS = {".zip"}
RUN_SUPPORTED_UPSTREAM_HANDOFFS = {("source-analyst", "course-architect"): "source_digest.md"}

AGENT_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.md$")
AGENT_ORDER = [
    "source-analyst",
    "course-architect",
    "lesson-designer",
    "lesson-writer",
    "assessment-designer",
    "quality-reviewer",
    "grounding-reviewer",
    "publisher",
]
ROLE_TITLES = {
    "source-analyst": "Source Analyst",
    "course-architect": "Course Architect",
    "lesson-designer": "Lesson Designer",
    "lesson-writer": "Lesson Writer",
    "assessment-designer": "Assessment Designer",
    "quality-reviewer": "Quality Reviewer",
    "grounding-reviewer": "Grounding Reviewer",
    "publisher": "Publisher",
}

AGENT_DESCRIPTIONS = {
    "source-analyst": "Разбирает исходные материалы",
    "course-architect": "Строит карту курса",
    "lesson-designer": "Проектирует каркас урока",
    "lesson-writer": "Пишет текст урока",
    "assessment-designer": "Создаёт проверки знаний",
    "quality-reviewer": "Проверяет качество курса",
    "grounding-reviewer": "Ищет неподтверждённые факты",
    "publisher": "Готовит курс к выдаче",
}

AUTH_STATE: dict[str, object] | None = None
AUTH_FILE_PATH: Path = AUTH_FILE_DEFAULT
SERVER_HOST = HOST_DEFAULT
SERVER_PORT = PORT_DEFAULT


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


def api_ok(payload: dict[str, object]) -> dict[str, object]:
    return {"ok": True, **payload}


def api_error_payload(code: str, message: str) -> dict[str, object]:
    return {"ok": False, "code": code, "error": message}


def run_git(args: list[str], *, timeout: int = 10, extra_env: dict[str, str] | None = None) -> tuple[int, str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return -1, ""
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.strip()


def git_text(args: list[str], *, timeout: int = 10, extra_env: dict[str, str] | None = None) -> str:
    code, output = run_git(args, timeout=timeout, extra_env=extra_env)
    if code != 0:
        return ""
    return output


def git_status_payload() -> dict[str, object]:
    branch = git_text(["branch", "--show-current"])
    head = git_text(["rev-parse", "HEAD"])
    status_short = git_text(["status", "--short"])
    remote_main = git_text(
        ["ls-remote", "origin", "refs/heads/main"],
        timeout=5,
        extra_env={"GIT_SSH_COMMAND": os.environ.get("GIT_SSH_COMMAND", "")} if os.environ.get("GIT_SSH_COMMAND") else None,
    )
    return {
        "branch": branch or None,
        "head": head or None,
        "status_short": status_short.splitlines() if status_short else [],
        "remote_main": remote_main or None,
    }


def slug_title(agent: str) -> str:
    return ROLE_TITLES.get(agent, agent.replace("-", " ").title())


def agent_description(agent: str) -> str:
    return AGENT_DESCRIPTIONS.get(agent, "")


def run_page_warning() -> str:
    return "MVP: кнопка создаёт заявку на запуск. Codex выполняет её отдельным controlled run."


def placeholder_files(role_title: str) -> dict[str, str]:
    return {
        "AGENT.md": (
            f"# {role_title}\n\n"
            "Temporary placeholder for the local admin MVP.\n\n"
            "See `docs/course_factory/AGENT_ROLES.md` and `docs/course_factory/ARTIFACT_CONTRACTS.md`.\n"
        ),
        "INPUT_CONTRACT.md": (
            "# Input contract\n\n"
            f"- Markdown source for the {role_title} role.\n"
            "- Respect source policy and STOP conditions.\n"
        ),
        "OUTPUT_CONTRACT.md": (
            "# Output contract\n\n"
            "- Produce the artifact named by the role contract.\n"
            "- Keep output file-based and git-trackable.\n"
        ),
        "TESTS.md": (
            "# Tests\n\n"
            "- Small controlled source pack.\n"
            "- Stop on missing sources, risky sources, or unclear acceptance.\n"
        ),
    }


def runtime_auth_path() -> Path:
    value = os.environ.get("COURSE_FACTORY_ADMIN_AUTH_FILE")
    if value:
        return Path(value).expanduser()
    return AUTH_FILE_DEFAULT


def runtime_host() -> str:
    return os.environ.get("COURSE_FACTORY_ADMIN_HOST", HOST_DEFAULT)


def runtime_port() -> int:
    raw = os.environ.get("COURSE_FACTORY_ADMIN_PORT")
    return int(raw) if raw else PORT_DEFAULT


def make_password_hash(password: str, salt: bytes, iterations: int = AUTH_ITERATIONS) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def ensure_auth_state(auth_path: Path) -> tuple[dict[str, object], str | None]:
    auth_path.parent.mkdir(parents=True, exist_ok=True)
    auth_path.parent.chmod(0o700)
    if auth_path.exists():
        raw = json.loads(auth_path.read_text(encoding="utf-8"))
        return raw, None

    password = secrets.token_urlsafe(24)
    salt = secrets.token_bytes(16)
    payload = {
        "username": AUTH_USERNAME,
        "iterations": AUTH_ITERATIONS,
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "hash_b64": base64.b64encode(make_password_hash(password, salt)).decode("ascii"),
    }
    auth_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    auth_path.chmod(0o600)
    return payload, password


def load_auth_state(auth_path: Path) -> dict[str, object]:
    raw = json.loads(auth_path.read_text(encoding="utf-8"))
    if raw.get("username") != AUTH_USERNAME:
        raise ValueError("invalid auth file username")
    if "salt_b64" not in raw or "hash_b64" not in raw:
        raise ValueError("invalid auth file contents")
    return raw


def verify_basic_auth(header_value: str | None, auth_state: dict[str, object]) -> bool:
    if not header_value or not header_value.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header_value[6:].strip()).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        return False
    if username != AUTH_USERNAME:
        return False
    try:
        salt = base64.b64decode(str(auth_state["salt_b64"]))
        expected = base64.b64decode(str(auth_state["hash_b64"]))
        iterations = int(auth_state.get("iterations", AUTH_ITERATIONS))
    except Exception:
        return False
    actual = make_password_hash(password, salt, iterations)
    return hmac.compare_digest(actual, expected)


def ensure_agent_scaffold() -> None:
    SKILLS_ROOT.mkdir(parents=True, exist_ok=True)
    for agent in AGENT_ORDER:
        agent_dir = SKILLS_ROOT / agent
        agent_dir.mkdir(parents=True, exist_ok=True)
        role_title = slug_title(agent)
        for filename, content in placeholder_files(role_title).items():
            path = agent_dir / filename
            if not path.exists():
                path.write_text(content, encoding="utf-8")


def is_safe_agent(agent: str) -> bool:
    return bool(agent) and bool(AGENT_NAME_RE.fullmatch(agent)) and (SKILLS_ROOT / agent).exists()


def resolve_agent_dir(agent: str) -> Path:
    if not is_safe_agent(agent):
        raise ValueError("invalid agent")
    agent_dir = SKILLS_ROOT / agent
    if agent_dir.is_symlink():
        raise ValueError("symlinked agent directory is not allowed")
    resolved = agent_dir.resolve(strict=True)
    root_resolved = SKILLS_ROOT.resolve(strict=True)
    if resolved != root_resolved / agent:
        raise ValueError("agent directory escapes allowed root")
    return resolved


def validate_filename(filename: str) -> None:
    if not filename:
        raise ValueError("filename is required")
    if "\x00" in filename:
        raise ValueError("filename contains NUL")
    if "/" in filename or "\\" in filename:
        raise ValueError("filename must not contain path separators")
    if ".." in filename:
        raise ValueError("filename must not contain ..")
    if filename.startswith("."):
        raise ValueError("hidden files are not editable")
    if not FILENAME_RE.fullmatch(filename):
        raise ValueError("filename must be a .md file with safe characters")
    if filename == ".gitkeep":
        raise ValueError(".gitkeep is not editable")


def resolve_markdown_path(agent: str, filename: str) -> Path:
    validate_filename(filename)
    agent_dir = resolve_agent_dir(agent)
    path = agent_dir / filename
    if path.is_symlink():
        raise ValueError("symlinked files are not allowed")
    if path.exists():
        resolved = path.resolve(strict=True)
        if agent_dir not in resolved.parents and resolved != agent_dir / filename:
            raise ValueError("file escapes allowed root")
    return path


def read_markdown(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path.name)
    if path.is_symlink():
        raise ValueError("symlinked files are not allowed")
    resolved = path.resolve(strict=True)
    if resolved.suffix.lower() != ".md":
        raise ValueError("only markdown files are allowed")
    return resolved.read_text(encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise ValueError("content exceeds 200 KB")
    path.write_text(content, encoding="utf-8", newline="\n")


def collect_agent_files(agent: str) -> list[dict[str, object]]:
    agent_dir = resolve_agent_dir(agent)
    files: list[dict[str, object]] = []
    for path in sorted(agent_dir.glob("*.md"), key=lambda p: p.name.lower()):
        if path.name.startswith(".") or path.name == ".gitkeep":
            continue
        st = path.stat()
        files.append(
            {
                "name": path.name,
                "relative_path": str(path.relative_to(REPO_ROOT)),
                "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "size": st.st_size,
            }
        )
    return files


def collect_page_state(page: str) -> dict[str, object]:
    ensure_agent_scaffold()
    agents = []
    seen = set()
    for agent in AGENT_ORDER:
        agent_dir = SKILLS_ROOT / agent
        if not agent_dir.exists() or not agent_dir.is_dir():
            continue
        seen.add(agent)
        agents.append(
            {
                "name": agent,
                "title": slug_title(agent),
                "description": agent_description(agent),
                "relative_path": str(agent_dir.relative_to(REPO_ROOT)),
                "files": collect_agent_files(agent),
            }
        )
    for agent_dir in sorted(SKILLS_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not agent_dir.is_dir() or agent_dir.name.startswith(".") or agent_dir.name in seen:
            continue
        agents.append(
            {
                "name": agent_dir.name,
                "title": slug_title(agent_dir.name),
                "description": agent_description(agent_dir.name),
                "relative_path": str(agent_dir.relative_to(REPO_ROOT)),
                "files": collect_agent_files(agent_dir.name),
            }
        )
    warning = (
        "MVP: кнопка создаёт заявку на запуск. Codex выполняет её отдельным controlled run."
        if page == "runs"
        else "Админка открыта наружу только для MVP. Не используйте личные пароли и не передавайте доступ."
    )
    return {
        "page": page,
        "warning": warning,
        "repo_root": str(REPO_ROOT),
        "skills_root": str(SKILLS_ROOT),
        "git": git_status_payload(),
        "agents": agents,
    }


def load_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def render_page(page: str) -> bytes:
    state = collect_page_state(page)
    template = load_template()
    safe_state_json = json.dumps(state, ensure_ascii=False).replace("<", "\\u003c")
    html_text = (
        template.replace("__STATE_JSON__", safe_state_json)
        .replace("__PAGE__", page)
        .replace("__PAGE_WARNING__", str(state["warning"]))
    )
    return html_text.encode("utf-8")


def json_body(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length > MAX_CONTENT_BYTES * 2:
        raise ValueError("request body too large")
    content_type = handler.headers.get_content_type()
    if content_type.startswith("multipart/form-data"):
        field_storage = parse_multipart_form(handler, length)
        data: dict[str, object] = {}
        for item in field_storage.list or []:
            if getattr(item, "filename", None):
                item.file.seek(0)
                data[item.name] = {
                    "filename": item.filename,
                    "content": item.file.read(),
                }
            else:
                data[item.name] = item.value
        return data
    raw = handler.rfile.read(length) if length else b""
    if content_type == "application/json":
        return json.loads(raw.decode("utf-8") if raw else "{}")
    if content_type == "application/x-www-form-urlencoded":
        parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
        return {key: values[-1] if values else "" for key, values in parsed.items()}
    raise ValueError(f"unsupported content type: {content_type}")


def parse_multipart_form(handler: BaseHTTPRequestHandler, length: int | None = None) -> cgi.FieldStorage:
    if length is None:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    if length > MAX_CONTENT_BYTES * 10:
        raise ValueError("request body too large")
    environ = {
        "REQUEST_METHOD": "POST",
        "CONTENT_TYPE": handler.headers.get("Content-Type", ""),
        "CONTENT_LENGTH": str(length),
    }
    return cgi.FieldStorage(
        fp=handler.rfile,
        headers=handler.headers,
        environ=environ,
        keep_blank_values=True,
    )


def safe_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if value is None:
        return ""
    return str(value)


def is_safe_run_id(run_id: str) -> bool:
    return bool(run_id) and bool(RUN_ID_RE.fullmatch(run_id))


def is_safe_run_filename(filename: str, *, allowed_exts: set[str] | None = None) -> bool:
    if not filename or "\x00" in filename:
        return False
    if filename.startswith("."):
        return False
    if "/" in filename or "\\" in filename or ".." in filename:
        return False
    if not RUN_SAFE_BASENAME_RE.fullmatch(filename):
        return False
    if allowed_exts is not None and Path(filename).suffix.lower() not in allowed_exts:
        return False
    return True


def normalize_run_relative_path(path_text: str, *, allow_nested: bool) -> str:
    raw = safe_text(path_text).strip().replace("\\", "/")
    if not raw:
        raise ApiError("INVALID_SOURCE_FILENAME", "Имя файла не может быть пустым.")
    if raw.startswith("/") or raw.startswith("~"):
        raise ApiError("INVALID_SOURCE_FILENAME", f"Недопустимый путь: {raw}")
    parts = raw.split("/")
    if not allow_nested and len(parts) != 1:
        raise ApiError("INVALID_SOURCE_FILENAME", f"Недопустимое имя файла: {raw}")
    if any(not part or part in {".", ".."} for part in parts):
        raise ApiError("INVALID_SOURCE_FILENAME", f"Недопустимый путь: {raw}")
    if any(part.startswith(".") for part in parts):
        raise ApiError("INVALID_SOURCE_FILENAME", f"Скрытые файлы запрещены: {raw}")
    for part in parts:
        if not RUN_SAFE_BASENAME_RE.fullmatch(part):
            raise ApiError("INVALID_SOURCE_FILENAME", f"Недопустимое имя файла: {raw}")
    return "/".join(parts)


def is_ignored_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/").strip("/")
    if not normalized:
        return True
    parts = normalized.split("/")
    return parts[0] == "__MACOSX" or any(part.startswith(".") and part not in {".", ".."} for part in parts)


def zip_member_path_is_safe(name: str) -> bool:
    normalized = name.replace("\\", "/").strip()
    if not normalized:
        return False
    if normalized.startswith("/") or normalized.startswith("~"):
        return False
    parts = normalized.split("/")
    if any(not part or part in {".", ".."} for part in parts):
        return False
    return all(RUN_SAFE_BASENAME_RE.fullmatch(part) for part in parts)


def resolve_run_dir(run_id: str, *, must_exist: bool = False) -> Path:
    if not is_safe_run_id(run_id):
        raise ApiError("INVALID_RUN_ID", "Некорректный идентификатор запуска.")
    run_dir = RUNS_ROOT / run_id
    if run_dir.is_symlink():
        raise ApiError("RUN_PATH_FORBIDDEN", "Символьные ссылки для запуска запрещены.")
    if must_exist and not run_dir.exists():
        raise ApiError("RUN_NOT_FOUND", "Запуск не найден.", status=404)
    return run_dir


def ensure_run_structure(run_dir: Path) -> None:
    (run_dir / RUN_INPUT_DIR).mkdir(parents=True, exist_ok=True)
    (run_dir / RUN_UPSTREAM_INPUT_DIR).mkdir(parents=True, exist_ok=True)
    (run_dir / RUN_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    (run_dir / RUN_LOG_DIR).mkdir(parents=True, exist_ok=True)
    (run_dir / RUN_OUTPUT_DIR / ".gitkeep").touch(exist_ok=True)
    (run_dir / RUN_LOG_DIR / ".gitkeep").touch(exist_ok=True)


def utc_now() -> datetime:
    return datetime.utcnow()


def utc_stamp() -> str:
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def create_unique_run_id(agent_slug: str) -> str:
    current = utc_now()
    for _ in range(120):
        run_id = f"{current.strftime('%Y%m%d_%H%M%S')}_{agent_slug}"
        if not (RUNS_ROOT / run_id).exists():
            return run_id
        current = current.replace(microsecond=0) + timedelta(seconds=1)
    raise RuntimeError("unable to create unique run_id")


def list_marked_files(directory: Path, *, allowed_exts: set[str] | None = None) -> list[str]:
    if not directory.exists() or not directory.is_dir():
        return []
    items: list[str] = []
    for path in sorted(directory.rglob("*"), key=lambda p: str(p.relative_to(directory)).lower()):
        if not path.is_file():
            continue
        relative = path.relative_to(directory)
        if any(part.startswith(".") for part in relative.parts) or relative.name == ".gitkeep":
            continue
        if allowed_exts and path.suffix.lower() not in allowed_exts:
            continue
        items.append(str(relative).replace("\\", "/"))
    return items


def read_optional_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    if path.is_symlink():
        raise ValueError("symlinked files are not allowed")
    return path.read_text(encoding="utf-8")


def normalize_run_input_file_path(filename: str) -> str:
    normalized = normalize_run_relative_path(filename, allow_nested=True)
    if normalized.startswith("source_pack/") or normalized.startswith("upstream_artifacts/"):
        return normalized
    return str(Path("source_pack") / normalized)


def run_status_path(run_dir: Path) -> Path:
    return run_dir / RUN_STATUS_FILENAME


def run_request_path(run_dir: Path) -> Path:
    return run_dir / RUN_REQUEST_FILENAME


def load_run_status(run_dir: Path) -> dict[str, object]:
    status_path = run_status_path(run_dir)
    if not status_path.exists():
        raise ApiError("RUN_STATUS_NOT_FOUND", "Файл status.json не найден.", status=404)
    return json.loads(status_path.read_text(encoding="utf-8"))


def collect_run_summary(run_dir: Path) -> dict[str, object]:
    status = load_run_status(run_dir)
    output_files = list_marked_files(run_dir / RUN_OUTPUT_DIR, allowed_exts=RUN_ALLOWED_READ_EXTS)
    return {
        "run_id": status.get("run_id", run_dir.name),
        "agent": status.get("agent", ""),
        "status": status.get("status", ""),
        "created_at_utc": status.get("created_at_utc", ""),
        "goal": status.get("goal", ""),
        "target_audience": status.get("target_audience", ""),
        "source_files": status.get("source_files", []),
        "output_files": output_files,
    }


def list_runs_payload() -> list[dict[str, object]]:
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, object]] = []
    for run_dir in RUNS_ROOT.iterdir():
        if not run_dir.is_dir() or run_dir.name.startswith(".") or not is_safe_run_id(run_dir.name):
            continue
        try:
            runs.append(collect_run_summary(run_dir))
        except Exception:
            continue
    runs.sort(key=lambda item: str(item.get("created_at_utc", "")), reverse=True)
    return runs


def find_agent_slug(agent: str) -> str:
    if not is_safe_agent(agent):
        raise ApiError("INVALID_AGENT", "Некорректный агент.")
    return agent


def run_request_markdown(run_id: str, agent: str, goal: str, target_audience: str, source_files: list[str]) -> str:
    lines = [
        "# Run request",
        "",
        "## Run ID",
        "",
        run_id,
        "",
        "## Agent",
        "",
        agent,
        "",
        "## Status",
        "",
        RUN_PENDING_STATUS,
        "",
        "## Goal",
        "",
        goal,
        "",
        "## Target audience",
        "",
        target_audience,
        "",
        "## Source files",
        "",
    ]
    if source_files:
        lines.extend([f"- input/source_pack/{name}" for name in source_files])
    else:
        lines.append("- (no source files)")
    lines.extend(
        [
            "",
            "## Execution rule",
            "",
            "This run request was created by the admin UI.",
            "",
            "The UI does not execute Codex or model calls.",
            "",
            "A separate controlled Codex run must read this request, execute only the selected agent, and write results to:",
            "",
            "`output/`",
            "",
        ]
    )
    if agent == "source-analyst":
        lines.extend(
            [
                "## Expected output for source-analyst",
                "",
                "If agent is `source-analyst`, expected output is:",
                "",
                "`output/source_digest.md`",
                "",
            ]
        )
    return "\n".join(lines)


def write_run_request_files(run_dir: Path, run_id: str, agent: str, goal: str, target_audience: str, source_files: list[str]) -> dict[str, object]:
    ensure_run_structure(run_dir)
    status_payload = {
        "run_id": run_id,
        "agent": agent,
        "status": RUN_PENDING_STATUS,
        "created_at_utc": utc_stamp(),
        "goal": goal,
        "target_audience": target_audience,
        "source_files": [f"input/source_pack/{name}" for name in source_files],
        "output_files": [],
    }
    (run_dir / RUN_INPUT_DIR).mkdir(parents=True, exist_ok=True)
    (run_dir / RUN_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    (run_dir / RUN_LOG_DIR).mkdir(parents=True, exist_ok=True)
    (run_dir / RUN_OUTPUT_DIR / ".gitkeep").touch(exist_ok=True)
    (run_dir / RUN_LOG_DIR / ".gitkeep").touch(exist_ok=True)
    run_request_path(run_dir).write_text(
        run_request_markdown(run_id, agent, goal, target_audience, source_files),
        encoding="utf-8",
    )
    run_status_path(run_dir).write_text(json.dumps(status_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return status_payload


def write_run_request_files_for_upstream_handoff(
    run_dir: Path,
    *,
    run_id: str,
    upstream_run_id: str,
    upstream_agent: str,
    target_agent: str,
    upstream_artifact_source_path: str,
    local_copied_artifact_path: str,
    upstream_request_md: str,
    course_brief_status: str,
    source_files: list[str],
) -> dict[str, object]:
    expected_execution_behavior = (
        "Course Architect may STOP with STOP_COURSE_BRIEF_MISSING unless a course brief artifact is provided by workflow/project setup."
        if course_brief_status == "missing"
        else "Course Architect can proceed if the upstream course brief artifact is available in the workflow chain."
    )
    ensure_run_structure(run_dir)
    status_payload = {
        "run_id": run_id,
        "agent": target_agent,
        "status": RUN_PENDING_STATUS,
        "created_at_utc": utc_stamp(),
        "goal": "Execute the next agent using upstream artifacts.",
        "target_audience": "from upstream handoff",
        "source_files": source_files,
        "output_files": [],
        "input_mode": "upstream_artifact_handoff",
        "upstream_run_id": upstream_run_id,
        "upstream_agent": upstream_agent,
        "upstream_artifact_source_path": upstream_artifact_source_path,
        "local_copied_artifact_path": local_copied_artifact_path,
        "course_brief_status": course_brief_status,
        "expected_execution_behavior": expected_execution_behavior,
    }
    request_lines = [
        "# Run request",
        "",
        "## Run ID",
        "",
        run_id,
        "",
        "## Agent",
        "",
        target_agent,
        "",
        "## Status",
        "",
        RUN_PENDING_STATUS,
        "",
        "## Input mode",
        "",
        "upstream_artifact_handoff",
        "",
        "## Upstream run ID",
        "",
        upstream_run_id,
        "",
        "## Upstream agent",
        "",
        upstream_agent,
        "",
        "## Target agent",
        "",
        target_agent,
        "",
        "## Upstream artifact source path",
        "",
        upstream_artifact_source_path,
        "",
        "## Local copied artifact path",
        "",
        local_copied_artifact_path,
        "",
        "## Inherited context",
        "",
        upstream_request_md.strip() or "(upstream RUN_REQUEST.md not available)",
        "",
        "## Course brief status",
        "",
        course_brief_status,
        "",
        "## Expected execution behavior",
        "",
        expected_execution_behavior,
        "",
        "## Execution rule",
        "",
        "This run request was created by the upstream artifact handoff workflow.",
        "",
        "The UI does not execute Codex or model calls.",
        "",
        "A separate controlled Codex run must read this request, execute only the selected agent, and write results to:",
        "",
        "`output/`",
        "",
    ]
    run_request_path(run_dir).write_text("\n".join(request_lines), encoding="utf-8")
    run_status_path(run_dir).write_text(json.dumps(status_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return status_payload


def store_run_source_file(run_dir: Path, filename: str, content: str, *, allow_nested: bool = False) -> str:
    normalized_filename = normalize_run_relative_path(filename, allow_nested=allow_nested)
    if Path(normalized_filename).suffix.lower() != ".md":
        raise ApiError("INVALID_SOURCE_FILENAME", "Некорректное имя исходного markdown-файла.")
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise ApiError("CONTENT_TOO_LARGE", "Файл превышает 200 KB.")
    target = run_dir / RUN_INPUT_DIR / Path(normalized_filename)
    if target.exists():
        raise ApiError("DUPLICATE_SOURCE_FILENAME", f"Файл уже существует: {normalized_filename}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        raise ValueError("symlinked source file is not allowed")
    target.write_text(content, encoding="utf-8", newline="\n")
    return str(Path("input") / "source_pack" / normalized_filename)


def extract_zip_source_files(run_dir: Path, archive_name: str, archive_bytes: bytes) -> list[str]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as exc:
        raise ApiError("INVALID_SOURCE_ARCHIVE", f"Некорректный zip-архив: {archive_name}") from exc

    extracted: list[str] = []
    seen: set[str] = set()
    try:
        for info in archive.infolist():
            raw_name = info.filename or ""
            if not raw_name or info.is_dir():
                continue
            normalized_name = raw_name.replace("\\", "/").strip()
            if is_ignored_zip_member(normalized_name):
                continue
            if not zip_member_path_is_safe(normalized_name):
                raise ApiError("INVALID_ZIP_SOURCE_PATH", f"Недопустимый путь в архиве: {raw_name}")
            relative_name = normalize_run_relative_path(normalized_name, allow_nested=True)
            if Path(relative_name).suffix.lower() != ".md":
                continue
            if relative_name in seen:
                raise ApiError("DUPLICATE_SOURCE_FILENAME", f"Файл уже существует: {relative_name}")
            if info.file_size > MAX_CONTENT_BYTES:
                raise ApiError("CONTENT_TOO_LARGE", f"Файл превышает 200 KB: {relative_name}")
            with archive.open(info) as source:
                raw_content = source.read(MAX_CONTENT_BYTES + 1)
            if len(raw_content) > MAX_CONTENT_BYTES:
                raise ApiError("CONTENT_TOO_LARGE", f"Файл превышает 200 KB: {relative_name}")
            try:
                content = raw_content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ApiError("INVALID_SOURCE_ENCODING", f"Файл не UTF-8: {relative_name}") from exc
            extracted_path = store_run_source_file(run_dir, relative_name, content, allow_nested=True)
            seen.add(relative_name)
            extracted.append(relative_name)
    except ApiError:
        raise
    except Exception as exc:
        raise ApiError("INVALID_SOURCE_ARCHIVE", f"Не удалось прочитать zip-архив: {archive_name}") from exc
    finally:
        archive.close()

    if not extracted:
        raise ApiError("ZIP_ARCHIVE_HAS_NO_MARKDOWN", f"ZIP-архив не содержит markdown-файлов: {archive_name}")
    return extracted


def supported_upstream_handoff(upstream_agent: str, target_agent: str) -> bool:
    return (upstream_agent, target_agent) in RUN_SUPPORTED_UPSTREAM_HANDOFFS


def resolve_completed_run_source_digest(upstream_run_id: str) -> tuple[Path, dict[str, object]]:
    upstream_run_dir = resolve_run_dir(upstream_run_id, must_exist=True)
    status = load_run_status(upstream_run_dir)
    if status.get("status") != "completed_success":
        raise ApiError("UPSTREAM_RUN_NOT_COMPLETED", "Upstream run must be completed_success.")
    if status.get("agent") != "source-analyst":
        raise ApiError("UPSTREAM_AGENT_UNSUPPORTED", "Upstream run must be Source Analyst for this handoff.")
    source_digest = upstream_run_dir / RUN_OUTPUT_DIR / "source_digest.md"
    if not source_digest.exists() or not source_digest.is_file():
        raise ApiError("UPSTREAM_SOURCE_DIGEST_MISSING", "Upstream source_digest.md is missing.")
    return source_digest, status


def find_course_brief_artifact() -> tuple[str, str]:
    candidates = [
        RUNS_ROOT / "course_brief.md",
        REPO_ROOT / "course_brief.md",
        REPO_ROOT / "docs" / "project" / "course_brief.md",
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return str(path.relative_to(REPO_ROOT)), path.read_text(encoding="utf-8")
    return "", ""


def create_upstream_handoff_run(upstream_run_id: str, target_agent: str) -> dict[str, object]:
    if target_agent != "course-architect":
        raise ApiError("UNSUPPORTED_TARGET_AGENT", "This upstream handoff slice only supports Course Architect.")

    source_digest_path, upstream_status = resolve_completed_run_source_digest(upstream_run_id)
    if not supported_upstream_handoff(str(upstream_status.get("agent", "")), target_agent):
        raise ApiError("UNSUPPORTED_UPSTREAM_HANDOFF", "Unsupported upstream handoff pair.")

    target_run_id = create_unique_run_id(target_agent)
    target_run_dir = RUNS_ROOT / target_run_id
    try:
        ensure_run_structure(target_run_dir)
        copied_root = target_run_dir / RUN_UPSTREAM_INPUT_DIR / upstream_run_id
        copied_root.mkdir(parents=True, exist_ok=True)
        copied_source_digest = copied_root / source_digest_path.name
        shutil.copy2(source_digest_path, copied_source_digest)
        local_copied_artifact_path = str(
            Path("input") / "upstream_artifacts" / upstream_run_id / source_digest_path.name
        )
        upstream_artifact_source_path = str(Path("output") / source_digest_path.name)

        upstream_request_path = RUNS_ROOT / upstream_run_id / RUN_REQUEST_FILENAME
        upstream_request_md = read_optional_text(upstream_request_path)
        _, course_brief_md = find_course_brief_artifact()
        course_brief_status = "present" if course_brief_md else "missing"

        source_files = [local_copied_artifact_path]
        status_payload = write_run_request_files_for_upstream_handoff(
            target_run_dir,
            run_id=target_run_id,
            upstream_run_id=upstream_run_id,
            upstream_agent=str(upstream_status.get("agent", "")),
            target_agent=target_agent,
            upstream_artifact_source_path=upstream_artifact_source_path,
            local_copied_artifact_path=local_copied_artifact_path,
            upstream_request_md=upstream_request_md,
            course_brief_status=course_brief_status,
            source_files=source_files,
        )
        status_payload["course_brief_status"] = course_brief_status
        status_payload["input_mode"] = "upstream_artifact_handoff"
        status_payload["upstream_run_id"] = upstream_run_id
        status_payload["upstream_agent"] = upstream_status.get("agent", "")
        status_payload["upstream_artifact_source_path"] = upstream_artifact_source_path
        status_payload["local_copied_artifact_path"] = local_copied_artifact_path
        return {
            "ok": True,
            "run_id": target_run_id,
            "status": RUN_PENDING_STATUS,
            "upstream_run_id": upstream_run_id,
            "upstream_agent": upstream_status.get("agent", ""),
            "target_agent": target_agent,
            "input_mode": "upstream_artifact_handoff",
            "course_brief_status": course_brief_status,
            "upstream_artifact_source_path": upstream_artifact_source_path,
            "local_copied_artifact_path": local_copied_artifact_path,
            "source_files": source_files,
        }
    except Exception:
        shutil.rmtree(target_run_dir, ignore_errors=True)
        raise


def read_run_file(run_id: str, kind: str, filename: str) -> tuple[Path, str]:
    run_dir = resolve_run_dir(run_id, must_exist=True)
    kind_map = {
        "input": run_dir / "input",
        "output": run_dir / RUN_OUTPUT_DIR,
        "request": run_dir,
        "log": run_dir / RUN_LOG_DIR,
    }
    if kind not in kind_map:
        raise ApiError("INVALID_KIND", "Недопустимый kind.")
    relative_name = normalize_run_input_file_path(filename) if kind == "input" else normalize_run_relative_path(filename, allow_nested=True)
    if Path(relative_name).suffix.lower() not in RUN_ALLOWED_READ_EXTS:
        raise ApiError("INVALID_FILENAME", "Некорректное имя файла.")
    root = kind_map[kind]
    target = root / Path(relative_name)
    if target.is_symlink():
        raise ApiError("FILE_PATH_FORBIDDEN", "Символьные ссылки для файлов запрещены.")
    if not target.exists() or not target.is_file():
        raise ApiError("FILE_NOT_FOUND", "Файл не найден.", status=404)
    resolved = target.resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    if root_resolved not in resolved.parents and resolved != root_resolved / relative_name:
        raise ApiError("FILE_PATH_FORBIDDEN", "Файл выходит за пределы разрешённой папки.")
    return resolved, relative_name


def create_run_request_from_form(form: cgi.FieldStorage) -> dict[str, object]:
    agent = safe_text(form.getfirst("agent", "")).strip()
    goal = safe_text(form.getfirst("goal", "")).strip()
    target_audience = safe_text(form.getfirst("target_audience", "")).strip()
    if not agent or not is_safe_agent(agent):
        raise ApiError("INVALID_AGENT", "Выберите корректного агента.")
    if not goal:
        raise ApiError("GOAL_REQUIRED", "Укажите цель запуска.")
    if not target_audience:
        raise ApiError("TARGET_AUDIENCE_REQUIRED", "Укажите целевую аудиторию.")

    upload_items = [
        item
        for item in (form.list or [])
        if getattr(item, "filename", None) and item.name in {"files", "files[]"}
    ]
    if not upload_items:
        raise ApiError("SOURCE_FILES_REQUIRED", "Добавьте хотя бы один markdown-файл.")

    source_files: list[str] = []
    run_id = create_unique_run_id(agent)
    run_dir = RUNS_ROOT / run_id
    try:
        ensure_run_structure(run_dir)

        for item in upload_items:
            filename = safe_text(item.filename).strip()
            item.file.seek(0)
            raw = item.file.read()
            if isinstance(raw, str):
                raw_bytes = raw.encode("utf-8")
            else:
                raw_bytes = raw
            suffix = Path(filename).suffix.lower()
            if suffix == ".md":
                normalized_name = normalize_run_relative_path(filename, allow_nested=False)
                try:
                    content = raw_bytes.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise ApiError("INVALID_SOURCE_ENCODING", f"Файл не UTF-8: {normalized_name}") from exc
                store_run_source_file(run_dir, normalized_name, content)
                source_files.append(normalized_name)
                continue
            if suffix == ".zip":
                extracted = extract_zip_source_files(run_dir, filename, raw_bytes)
                source_files.extend(extracted)
                continue
            raise ApiError("INVALID_SOURCE_FILENAME", f"Некорректное имя файла: {filename}")

        status_payload = write_run_request_files(run_dir, run_id, agent, goal, target_audience, source_files)
        return {
            "ok": True,
            **status_payload,
        }
    except Exception:
        shutil.rmtree(run_dir, ignore_errors=True)
        raise


def run_detail_payload(run_id: str) -> dict[str, object]:
    run_dir = resolve_run_dir(run_id, must_exist=True)
    status = load_run_status(run_dir)
    request_md = run_request_path(run_dir).read_text(encoding="utf-8") if run_request_path(run_dir).exists() else ""
    input_files = list_marked_files(run_dir / RUN_INPUT_DIR, allowed_exts=RUN_ALLOWED_READ_EXTS)
    upstream_input_files = [
        str(Path("upstream_artifacts") / name)
        for name in list_marked_files(run_dir / RUN_UPSTREAM_INPUT_DIR, allowed_exts=RUN_ALLOWED_READ_EXTS)
    ]
    output_files = list_marked_files(run_dir / RUN_OUTPUT_DIR, allowed_exts=RUN_ALLOWED_READ_EXTS)
    log_files = list_marked_files(run_dir / RUN_LOG_DIR, allowed_exts=RUN_ALLOWED_READ_EXTS)
    return {
        "ok": True,
        "run_id": run_id,
        "status_json": status,
        "run_request_md": request_md,
        "input_files": input_files,
        "upstream_input_files": upstream_input_files,
        "output_files": output_files,
        "log_files": log_files,
    }


def api_file(query: dict[str, list[str]]) -> tuple[int, dict[str, object]]:
    agent = query.get("agent", [""])[0]
    filename = query.get("filename", [""])[0]
    path = resolve_markdown_path(agent, filename)
    content = read_markdown(path)
    return 200, api_ok({
        "agent": agent,
        "filename": filename,
        "relative_path": str(path.relative_to(REPO_ROOT)),
        "content": content,
    })


def api_git_status() -> tuple[int, dict[str, object]]:
    return 200, git_status_payload()


def api_runs_list() -> tuple[int, dict[str, object]]:
    return 200, api_ok({"runs": list_runs_payload()})


def api_runs_create(handler: BaseHTTPRequestHandler) -> tuple[int, dict[str, object]]:
    form = parse_multipart_form(handler)
    payload = create_run_request_from_form(form)
    return 201, api_ok(payload)


def api_runs_next(handler: BaseHTTPRequestHandler) -> tuple[int, dict[str, object]]:
    payload = json_body(handler)
    upstream_run_id = safe_text(payload.get("upstream_run_id")).strip()
    target_agent = safe_text(payload.get("target_agent")).strip()
    if not upstream_run_id:
        raise ApiError("UPSTREAM_RUN_ID_REQUIRED", "Укажите upstream_run_id.")
    if not target_agent:
        raise ApiError("TARGET_AGENT_REQUIRED", "Укажите target_agent.")
    result = create_upstream_handoff_run(upstream_run_id, target_agent)
    return 201, api_ok(result)


def api_runs_detail(query: dict[str, list[str]]) -> tuple[int, dict[str, object]]:
    run_id = query.get("run_id", [""])[0]
    payload = run_detail_payload(run_id)
    return 200, api_ok(payload)


def api_runs_file(query: dict[str, list[str]]) -> tuple[int, dict[str, object]]:
    run_id = query.get("run_id", [""])[0]
    kind = query.get("kind", [""])[0]
    filename = query.get("filename", [""])[0]
    path, _ = read_run_file(run_id, kind, filename)
    return 200, api_ok({
        "run_id": run_id,
        "kind": kind,
        "filename": filename,
        "relative_path": str(path.relative_to(REPO_ROOT)),
        "content": path.read_text(encoding="utf-8"),
    })


def store_markdown(agent: str, filename: str, content: str) -> dict[str, object]:
    path = resolve_markdown_path(agent, filename)
    write_markdown(path, content)
    return {
        "ok": True,
        "agent": agent,
        "filename": filename,
        "relative_path": str(path.relative_to(REPO_ROOT)),
        "size": path.stat().st_size,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }


def api_save_or_upload(payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    agent = safe_text(payload.get("agent"))
    filename = safe_text(payload.get("filename"))
    content = payload.get("content")
    if isinstance(content, dict) and "content" in content:
        content = content["content"]
        if isinstance(content, bytes):
            content = content.decode("utf-8")
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    if content is None:
        raise ValueError("content is required")
    result = store_markdown(agent, filename, safe_text(content))
    return 200, result


class AdminHandler(BaseHTTPRequestHandler):
    server_version = "CourseFactoryAdmin/0.1"

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        print(f"[admin] {self.address_string()} - {format % args}")

    def send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_api_error(self, status: int, code: str, message: str) -> None:
        self.send_json(status, api_error_payload(code, message))

    def reject_unauthorized(self) -> None:
        body = "Доступ запрещён: нужен логин и пароль.".encode("utf-8")
        self.send_response(401)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("WWW-Authenticate", f'Basic realm="{AUTH_REALM}", charset="UTF-8"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def is_authorized(self) -> bool:
        assert AUTH_STATE is not None
        return verify_basic_auth(self.headers.get("Authorization"), AUTH_STATE)

    def do_GET(self) -> None:
        if not self.is_authorized():
            self.reject_unauthorized()
            return
        parsed = urlparse(self.path)
        is_api_route = parsed.path.startswith("/api/")
        try:
            if parsed.path == "/":
                self.send_html(200, render_page("home"))
                return
            if parsed.path == "/runs":
                self.send_html(200, render_page("runs"))
                return
            if parsed.path == "/api/file":
                status, payload = api_file(parse_qs(parsed.query, keep_blank_values=True))
                self.send_json(status, payload)
                return
            if parsed.path == "/api/git-status":
                status, payload = api_git_status()
                self.send_json(status, payload)
                return
            if parsed.path == "/api/runs":
                status, payload = api_runs_list()
                self.send_json(status, payload)
                return
            if parsed.path == "/api/runs/detail":
                status, payload = api_runs_detail(parse_qs(parsed.query, keep_blank_values=True))
                self.send_json(status, payload)
                return
            if parsed.path == "/api/runs/file":
                status, payload = api_runs_file(parse_qs(parsed.query, keep_blank_values=True))
                self.send_json(status, payload)
                return
            if parsed.path.startswith("/static/"):
                self.serve_static(parsed.path[len("/static/"):])
                return
            if is_api_route:
                self.send_api_error(404, "NOT_FOUND", "Маршрут API не найден.")
            else:
                self.send_json(404, {"ok": False, "error": "not found"})
        except ApiError as exc:
            if is_api_route:
                self.send_api_error(exc.status, exc.code, str(exc))
            else:
                self.send_json(exc.status, {"ok": False, "error": str(exc), "code": exc.code})
        except FileNotFoundError as exc:
            if is_api_route:
                self.send_api_error(404, "NOT_FOUND", f"Файл не найден: {exc}")
            else:
                self.send_json(404, {"ok": False, "error": f"file not found: {exc}"})
        except ValueError as exc:
            if is_api_route:
                self.send_api_error(400, "BAD_REQUEST", str(exc))
            else:
                self.send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # pragma: no cover - defensive error path
            if is_api_route:
                self.send_api_error(500, "INTERNAL_ERROR", f"Внутренняя ошибка: {exc}")
            else:
                self.send_json(500, {"ok": False, "error": f"internal error: {exc}"})

    def do_POST(self) -> None:
        if not self.is_authorized():
            self.reject_unauthorized()
            return
        parsed = urlparse(self.path)
        is_api_route = parsed.path.startswith("/api/")
        try:
            if parsed.path in {"/api/save", "/api/upload"}:
                payload = json_body(self)
                status, response = api_save_or_upload(payload)
                self.send_json(status, response)
                return
            if parsed.path == "/api/runs/create":
                status, response = api_runs_create(self)
                self.send_json(status, response)
                return
            if parsed.path == "/api/runs/next":
                status, response = api_runs_next(self)
                self.send_json(status, response)
                return
            if is_api_route:
                self.send_api_error(404, "NOT_FOUND", "Маршрут API не найден.")
            else:
                self.send_json(404, {"ok": False, "error": "not found"})
        except ApiError as exc:
            if is_api_route:
                self.send_api_error(exc.status, exc.code, str(exc))
            else:
                self.send_json(exc.status, {"ok": False, "error": str(exc), "code": exc.code})
        except FileNotFoundError as exc:
            if is_api_route:
                self.send_api_error(404, "NOT_FOUND", f"Файл не найден: {exc}")
            else:
                self.send_json(404, {"ok": False, "error": f"file not found: {exc}"})
        except ValueError as exc:
            if is_api_route:
                self.send_api_error(400, "BAD_REQUEST", str(exc))
            else:
                self.send_json(400, {"ok": False, "error": str(exc)})
        except json.JSONDecodeError as exc:
            if is_api_route:
                self.send_api_error(400, "INVALID_JSON", f"Неверный JSON: {exc}")
            else:
                self.send_json(400, {"ok": False, "error": f"invalid JSON: {exc}"})
        except Exception as exc:  # pragma: no cover - defensive error path
            if is_api_route:
                self.send_api_error(500, "INTERNAL_ERROR", f"Внутренняя ошибка: {exc}")
            else:
                self.send_json(500, {"ok": False, "error": f"internal error: {exc}"})

    def serve_static(self, relative_name: str) -> None:
        if ".." in relative_name or relative_name.startswith("/"):
            self.send_json(400, {"ok": False, "error": "invalid static path"})
            return
        path = STATIC_ROOT / relative_name
        if not path.exists() or not path.is_file():
            self.send_json(404, {"ok": False, "error": "static file not found"})
            return
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_text(200, body, f"{content_type}; charset=utf-8" if content_type.startswith("text/") else content_type)


def main() -> None:
    global AUTH_STATE, AUTH_FILE_PATH, SERVER_HOST, SERVER_PORT
    ensure_agent_scaffold()
    AUTH_FILE_PATH = runtime_auth_path()
    SERVER_HOST = runtime_host()
    SERVER_PORT = runtime_port()
    AUTH_STATE, generated_password = ensure_auth_state(AUTH_FILE_PATH)
    if generated_password:
        print("Admin password generated for this run.")
        print(f"Username: {AUTH_USERNAME}")
        print(f"Password: {generated_password}")
    server = ThreadingHTTPServer((SERVER_HOST, SERVER_PORT), AdminHandler)
    server.daemon_threads = True
    print(f"Course Factory Agent Admin: http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
