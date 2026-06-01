#!/usr/bin/env python3
from __future__ import annotations

import cgi
import html
import json
import mimetypes
import os
import re
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
STATIC_ROOT = REPO_ROOT / "static"
TEMPLATE_PATH = REPO_ROOT / "templates" / "admin.html"
HOST = "127.0.0.1"
PORT = 8091
MAX_CONTENT_BYTES = 200 * 1024

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


def collect_home_state() -> dict[str, object]:
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
                "relative_path": str(agent_dir.relative_to(REPO_ROOT)),
                "files": collect_agent_files(agent_dir.name),
            }
        )
    return {
        "warning": "MVP локальный. Не открывать наружу без авторизации.",
        "repo_root": str(REPO_ROOT),
        "skills_root": str(SKILLS_ROOT),
        "git": git_status_payload(),
        "agents": agents,
    }


def load_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def render_home() -> bytes:
    state = collect_home_state()
    template = load_template()
    safe_state_json = json.dumps(state, ensure_ascii=False).replace("<", "\\u003c")
    html_text = template.replace("__STATE_JSON__", safe_state_json)
    return html_text.encode("utf-8")


def json_body(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length > MAX_CONTENT_BYTES * 2:
        raise ValueError("request body too large")
    raw = handler.rfile.read(length) if length else b""
    content_type = handler.headers.get_content_type()
    if content_type == "application/json":
        return json.loads(raw.decode("utf-8") if raw else "{}")
    if content_type == "application/x-www-form-urlencoded":
        parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
        return {key: values[-1] if values else "" for key, values in parsed.items()}
    if content_type.startswith("multipart/form-data"):
        environ = {
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": handler.headers.get("Content-Type", ""),
            "CONTENT_LENGTH": str(length),
        }
        raw_stream = os.fdopen(os.dup(handler.rfile.fileno()), "rb")
        try:
            field_storage = cgi.FieldStorage(
                fp=raw_stream,
                headers=handler.headers,
                environ=environ,
                keep_blank_values=True,
            )
        finally:
            raw_stream.close()
        data: dict[str, object] = {}
        for key in field_storage.keys() or []:
            item = field_storage[key]
            if isinstance(item, list):
                item = item[-1]
            if getattr(item, "filename", None):
                item.file.seek(0)
                data[key] = {
                    "filename": item.filename,
                    "content": item.file.read(),
                }
            else:
                data[key] = item.value
        return data
    raise ValueError(f"unsupported content type: {content_type}")


def safe_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if value is None:
        return ""
    return str(value)


def api_file(query: dict[str, list[str]]) -> tuple[int, dict[str, object]]:
    agent = query.get("agent", [""])[0]
    filename = query.get("filename", [""])[0]
    path = resolve_markdown_path(agent, filename)
    content = read_markdown(path)
    return 200, {
        "agent": agent,
        "filename": filename,
        "relative_path": str(path.relative_to(REPO_ROOT)),
        "content": content,
    }


def api_git_status() -> tuple[int, dict[str, object]]:
    return 200, git_status_payload()


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

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self.send_html(200, render_home())
                return
            if parsed.path == "/api/file":
                status, payload = api_file(parse_qs(parsed.query, keep_blank_values=True))
                self.send_json(status, payload)
                return
            if parsed.path == "/api/git-status":
                status, payload = api_git_status()
                self.send_json(status, payload)
                return
            if parsed.path.startswith("/static/"):
                self.serve_static(parsed.path[len("/static/"):])
                return
            self.send_json(404, {"ok": False, "error": "not found"})
        except FileNotFoundError as exc:
            self.send_json(404, {"ok": False, "error": f"file not found: {exc}"})
        except ValueError as exc:
            self.send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # pragma: no cover - defensive error path
            self.send_json(500, {"ok": False, "error": f"internal error: {exc}"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = json_body(self)
            if parsed.path in {"/api/save", "/api/upload"}:
                status, response = api_save_or_upload(payload)
                self.send_json(status, response)
                return
            self.send_json(404, {"ok": False, "error": "not found"})
        except FileNotFoundError as exc:
            self.send_json(404, {"ok": False, "error": f"file not found: {exc}"})
        except ValueError as exc:
            self.send_json(400, {"ok": False, "error": str(exc)})
        except json.JSONDecodeError as exc:
            self.send_json(400, {"ok": False, "error": f"invalid JSON: {exc}"})
        except Exception as exc:  # pragma: no cover - defensive error path
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
    ensure_agent_scaffold()
    server = ThreadingHTTPServer((HOST, PORT), AdminHandler)
    server.daemon_threads = True
    print(f"Course Factory Agent Admin: http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
