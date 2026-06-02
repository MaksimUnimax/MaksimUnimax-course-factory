from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import app.admin_server as admin


class FakeJsonHeaders:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def get(self, key: str, default: str | None = None) -> str | None:
        if key.lower() == "content-length":
            return str(len(self.body))
        if key.lower() == "content-type":
            return "application/json"
        return default

    def get_content_type(self) -> str:
        return "application/json"


class FakeJsonHandler:
    def __init__(self, payload: dict[str, object]) -> None:
        self.body = json.dumps(payload).encode("utf-8")
        self.headers = FakeJsonHeaders(self.body)
        self.rfile = io.BytesIO(self.body)


def write_completed_source_analyst_run(run_root: Path, run_id: str, *, with_source_digest: bool = True, status: str = "completed_success") -> Path:
    run_dir = run_root / run_id
    admin.ensure_run_structure(run_dir)
    (run_dir / admin.RUN_OUTPUT_DIR / ".gitkeep").touch(exist_ok=True)
    (run_dir / admin.RUN_LOG_DIR / ".gitkeep").touch(exist_ok=True)
    (run_dir / admin.run_request_path(run_dir).name).write_text(
        admin.run_request_markdown(
            run_id,
            "source-analyst",
            "Build a source digest",
            "internal writer",
            ["source.md"],
        ),
        encoding="utf-8",
    )
    status_payload = {
        "run_id": run_id,
        "agent": "source-analyst",
        "status": status,
        "created_at_utc": "2026-06-01T10:22:42Z",
        "goal": "Build a source digest",
        "target_audience": "internal writer",
        "source_files": ["input/source_pack/source.md"],
        "output_files": ["source_digest.md"] if with_source_digest else [],
    }
    (run_dir / admin.RUN_STATUS_FILENAME).write_text(json.dumps(status_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if with_source_digest:
        (run_dir / admin.RUN_OUTPUT_DIR / "source_digest.md").write_text("# digest\n", encoding="utf-8")
    return run_dir


class RunUpstreamHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_root = Path(self.tmp.name)
        patcher = mock.patch.object(admin, "RUNS_ROOT", self.run_root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_api_runs_next_creates_course_architect_run_from_completed_source_analyst(self) -> None:
        upstream_run_id = "20260601_102242_source-analyst"
        upstream_run_dir = write_completed_source_analyst_run(self.run_root, upstream_run_id)
        upstream_status_before = (upstream_run_dir / admin.RUN_STATUS_FILENAME).read_text(encoding="utf-8")
        upstream_digest_before = (upstream_run_dir / admin.RUN_OUTPUT_DIR / "source_digest.md").read_text(encoding="utf-8")

        handler = FakeJsonHandler({
            "upstream_run_id": upstream_run_id,
            "target_agent": "course-architect",
        })
        status, payload = admin.api_runs_next(handler)

        self.assertEqual(status, 201)
        self.assertTrue(payload["ok"])
        new_run_id = str(payload["run_id"])
        new_run_dir = self.run_root / new_run_id

        status_payload = admin.load_run_status(new_run_dir)
        self.assertEqual(status_payload["status"], "pending_codex_execution")
        self.assertEqual(status_payload["input_mode"], "upstream_artifact_handoff")
        self.assertEqual(status_payload["upstream_run_id"], upstream_run_id)
        self.assertEqual(status_payload["upstream_agent"], "source-analyst")
        self.assertEqual(status_payload["course_brief_status"], "missing")
        self.assertEqual(
            status_payload["source_files"],
            [f"input/upstream_artifacts/{upstream_run_id}/source_digest.md"],
        )

        request_md = (new_run_dir / admin.RUN_REQUEST_FILENAME).read_text(encoding="utf-8")
        self.assertIn("upstream_artifact_handoff", request_md)
        self.assertIn(upstream_run_id, request_md)
        self.assertIn("Course brief status", request_md)
        self.assertIn("STOP_COURSE_BRIEF_MISSING", request_md)

        copied_digest = new_run_dir / admin.RUN_UPSTREAM_INPUT_DIR / upstream_run_id / "source_digest.md"
        self.assertTrue(copied_digest.exists())
        self.assertEqual(copied_digest.read_text(encoding="utf-8"), "# digest\n")

        detail = admin.run_detail_payload(new_run_id)
        self.assertEqual(detail["status_json"]["input_mode"], "upstream_artifact_handoff")
        self.assertEqual(detail["status_json"]["upstream_run_id"], upstream_run_id)
        self.assertEqual(detail["upstream_input_files"], [f"upstream_artifacts/{upstream_run_id}/source_digest.md"])

        path, relative_name = admin.read_run_file(
            new_run_id,
            "input",
            f"upstream_artifacts/{upstream_run_id}/source_digest.md",
        )
        self.assertEqual(relative_name, f"upstream_artifacts/{upstream_run_id}/source_digest.md")
        self.assertEqual(path.read_text(encoding="utf-8"), "# digest\n")

        self.assertEqual((upstream_run_dir / admin.RUN_STATUS_FILENAME).read_text(encoding="utf-8"), upstream_status_before)
        self.assertEqual((upstream_run_dir / admin.RUN_OUTPUT_DIR / "source_digest.md").read_text(encoding="utf-8"), upstream_digest_before)

    def test_rejects_missing_upstream_run(self) -> None:
        handler = FakeJsonHandler({
            "upstream_run_id": "20260601_000000_source-analyst",
            "target_agent": "course-architect",
        })

        with self.assertRaises(admin.ApiError) as ctx:
            admin.api_runs_next(handler)

        self.assertEqual(ctx.exception.code, "RUN_NOT_FOUND")

    def test_rejects_non_completed_upstream_run(self) -> None:
        upstream_run_id = "20260601_102242_source-analyst"
        write_completed_source_analyst_run(self.run_root, upstream_run_id, status="pending_codex_execution")

        handler = FakeJsonHandler({
            "upstream_run_id": upstream_run_id,
            "target_agent": "course-architect",
        })

        with self.assertRaises(admin.ApiError) as ctx:
            admin.api_runs_next(handler)

        self.assertEqual(ctx.exception.code, "UPSTREAM_RUN_NOT_COMPLETED")

    def test_rejects_source_analyst_without_source_digest(self) -> None:
        upstream_run_id = "20260601_102242_source-analyst"
        write_completed_source_analyst_run(self.run_root, upstream_run_id, with_source_digest=False)

        handler = FakeJsonHandler({
            "upstream_run_id": upstream_run_id,
            "target_agent": "course-architect",
        })

        with self.assertRaises(admin.ApiError) as ctx:
            admin.api_runs_next(handler)

        self.assertEqual(ctx.exception.code, "UPSTREAM_SOURCE_DIGEST_MISSING")

    def test_rejects_unsupported_target_agent(self) -> None:
        upstream_run_id = "20260601_102242_source-analyst"
        write_completed_source_analyst_run(self.run_root, upstream_run_id)

        handler = FakeJsonHandler({
            "upstream_run_id": upstream_run_id,
            "target_agent": "lesson-designer",
        })

        with self.assertRaises(admin.ApiError) as ctx:
            admin.api_runs_next(handler)

        self.assertEqual(ctx.exception.code, "UNSUPPORTED_TARGET_AGENT")

    def test_does_not_require_new_upload_for_handoff(self) -> None:
        upstream_run_id = "20260601_102242_source-analyst"
        write_completed_source_analyst_run(self.run_root, upstream_run_id)

        result = admin.create_upstream_handoff_run(upstream_run_id, "course-architect")
        self.assertEqual(result["input_mode"], "upstream_artifact_handoff")
        self.assertNotIn("files", result)


if __name__ == "__main__":
    unittest.main()
