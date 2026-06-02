from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import app.admin_server as admin


class FakeUpload:
    def __init__(self, field_name: str, filename: str, content: bytes) -> None:
        self.name = field_name
        self.filename = filename
        self._content = content
        self.file = SimpleNamespace()
        self.file.seek = lambda *args, **kwargs: None
        self.file.read = lambda *args, **kwargs: self._content


class FakeForm:
    def __init__(self, items: list[FakeUpload], fields: dict[str, str]) -> None:
        self.list = items
        self.fields = fields

    def getfirst(self, key: str, default: str = "") -> str:
        return self.fields.get(key, default)


class RunCourseSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_root = Path(self.tmp.name)
        patcher = mock.patch.object(admin, "RUNS_ROOT", self.run_root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_source_analyst_intake_creates_course_setup_and_brief(self) -> None:
        fields = {
            "agent": "source-analyst",
            "goal": "Комментарий к цели для курса",
            "target_audience": "Комментарий к аудитории для курса",
            "course_type": "Практический вводный курс",
            "target_audience_type": "Новички с базовым опытом ChatGPT",
            "learner_starting_level": "Умеет пользоваться ChatGPT, но не знает Git и сервер",
            "course_goal": "Научиться превращать исходные материалы в структуру курса",
            "expected_practical_result": "Разбор исходников и карта курса",
            "preferred_course_size": "6-8 уроков",
            "explanation_style": "Коротко и по делу",
            "scope_strictness": "MVP плюс минимальные пояснения архитектуры",
        }
        form = FakeForm([FakeUpload("files[]", "source.md", b"# source\n")], fields)

        result = admin.create_run_request_from_form(form)
        run_id = str(result["run_id"])
        run_dir = self.run_root / run_id

        setup_path = run_dir / admin.COURSE_SETUP_FILENAME
        brief_path = run_dir / admin.RUN_OUTPUT_DIR / admin.COURSE_BRIEF_FILENAME
        self.assertTrue(setup_path.exists())
        self.assertTrue(brief_path.exists())

        setup_payload = json.loads(setup_path.read_text(encoding="utf-8"))
        self.assertEqual(setup_payload["course_setup_source"], "ui_dropdowns")
        self.assertEqual(setup_payload["course_brief_status"], "available")
        self.assertEqual(setup_payload["course_brief_path"], "output/course_brief.md")
        self.assertEqual(setup_payload["course_setup"]["course_type"], "Практический вводный курс")
        self.assertEqual(setup_payload["course_setup"]["target_audience_type"], "Новички с базовым опытом ChatGPT")
        self.assertEqual(setup_payload["course_setup"]["goal_note"], "Комментарий к цели для курса")
        self.assertEqual(setup_payload["course_setup"]["audience_note"], "Комментарий к аудитории для курса")

        brief_md = brief_path.read_text(encoding="utf-8")
        self.assertIn("Этот файл создан интерфейсом из настроек курса. Это задание на курс, а не результат работы агента.", brief_md)
        self.assertIn("Практический вводный курс — Научиться превращать исходные материалы в структуру курса", brief_md)
        self.assertIn("Новички с базовым опытом ChatGPT", brief_md)
        self.assertIn("MVP плюс минимальные пояснения архитектуры", brief_md)
        self.assertIn("Комментарий к цели для курса", brief_md)
        self.assertIn("Комментарий к аудитории для курса", brief_md)
        self.assertIn("input/source_pack/source.md", brief_md)

        status_payload = admin.load_run_status(run_dir)
        self.assertEqual(status_payload["course_brief_status"], "available")
        self.assertEqual(status_payload["course_brief_path"], "output/course_brief.md")
        self.assertEqual(status_payload["course_setup_source"], "ui_dropdowns")
        self.assertEqual(status_payload["output_files"], ["course_brief.md"])

        request_md = (run_dir / admin.RUN_REQUEST_FILENAME).read_text(encoding="utf-8")
        self.assertIn("## Course setup", request_md)
        self.assertIn("Задание на курс", request_md)
        self.assertIn("Course brief status", request_md)
        self.assertIn("available", request_md)

        detail = admin.run_detail_payload(run_id)
        self.assertIn("course_brief.md", detail["output_files"])
        self.assertEqual(detail["status_json"]["course_brief_status"], "available")


if __name__ == "__main__":
    unittest.main()
