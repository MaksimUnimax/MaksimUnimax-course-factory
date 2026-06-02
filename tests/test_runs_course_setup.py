from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import app.admin_server as admin


REPO_ROOT = Path(__file__).resolve().parents[1]
UNIVERSAL_COURSE_SETUP = {
    "course_type": "Пошаговый учебный проект",
    "target_audience_type": "Смешанная аудитория",
    "learner_starting_level": "Нужна систематизация знаний",
    "primary_learning_result": "Практический навык",
    "final_output_type": "Учебный проект",
    "preferred_course_size": "5–7 уроков",
    "course_depth": "Практический уровень + типовые ошибки",
    "explanation_style": "Сначала простыми словами, потом термины",
    "practice_format": "Один общий проект по шагам",
    "assessment_format": "Практические задания",
    "feedback_mode": "Показывать типовую ошибку и исправление",
    "source_strictness": "Факты из исходников + явно помеченные учебные выводы",
    "domain_sensitivity": "Обычная учебная тема",
    "course_mode": "Превратить материалы в практический курс",
}


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
        fields = {"agent": "source-analyst", **UNIVERSAL_COURSE_SETUP}
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
        self.assertEqual(setup_payload["subject_source"], "uploaded_source_documents")
        self.assertEqual(setup_payload["methodology_source"], "accepted_course_factory_methodology_references")
        self.assertEqual(setup_payload["course_brief_status"], "available")
        self.assertEqual(setup_payload["course_brief_path"], "output/course_brief.md")
        self.assertEqual(setup_payload["course_setup_path"], "course_setup.json")
        self.assertEqual(set(setup_payload["course_setup"].keys()), set(UNIVERSAL_COURSE_SETUP.keys()))
        self.assertEqual(setup_payload["course_setup"], UNIVERSAL_COURSE_SETUP)
        self.assertNotIn("goal_note", setup_payload["course_setup"])
        self.assertNotIn("audience_note", setup_payload["course_setup"])
        self.assertNotIn("course_title", setup_payload["course_setup"])
        self.assertNotIn("source", setup_payload["course_setup"])

        brief_md = brief_path.read_text(encoding="utf-8")
        self.assertIn("# Задание на курс", brief_md)
        self.assertIn("Этот файл создан интерфейсом из выбранных настроек.", brief_md)
        self.assertIn("Это задание на курс, а не результат работы агента.", brief_md)
        self.assertIn("Тема и факты курса берутся из загруженных исходных документов.", brief_md)
        self.assertIn("Методика построения курса берётся из принятых методических референсов Course Factory.", brief_md)
        for value in UNIVERSAL_COURSE_SETUP.values():
            self.assertIn(value, brief_md)
        self.assertIn("## Основа по источникам", brief_md)
        self.assertIn("Загруженные исходные документы в `input/source_pack/`.", brief_md)
        self.assertIn("## Методическая основа", brief_md)
        self.assertIn("Принятые методические референсы Course Factory", brief_md)
        self.assertIn("docs/course_factory/METHOD_SOURCES.md", brief_md)
        self.assertIn("docs/course_factory/METHODOLOGY_REFERENCE_GOVERNANCE.md", brief_md)
        for forbidden in [
            "ChatGPT",
            "Codex",
            "GitHub-backed",
            "read-only preview",
            "Codex report",
            "Комментарий к цели",
            "Комментарий к аудитории",
        ]:
            self.assertNotIn(forbidden, brief_md)

        status_payload = admin.load_run_status(run_dir)
        self.assertEqual(status_payload["course_brief_status"], "available")
        self.assertEqual(status_payload["course_brief_path"], "output/course_brief.md")
        self.assertEqual(status_payload["course_setup_source"], "ui_dropdowns")
        self.assertEqual(status_payload["subject_source"], "uploaded_source_documents")
        self.assertEqual(status_payload["methodology_source"], "accepted_course_factory_methodology_references")
        self.assertEqual(status_payload["output_files"], ["course_brief.md"])
        self.assertEqual(status_payload["course_setup"], UNIVERSAL_COURSE_SETUP)

        request_md = (run_dir / admin.RUN_REQUEST_FILENAME).read_text(encoding="utf-8")
        self.assertIn("## Course setup", request_md)
        self.assertIn("Course brief status", request_md)
        self.assertIn("available", request_md)
        self.assertIn("## Subject source", request_md)
        self.assertIn("uploaded_source_documents", request_md)
        self.assertIn("## Methodology source", request_md)
        self.assertIn("accepted_course_factory_methodology_references", request_md)

        detail = admin.run_detail_payload(run_id)
        self.assertIn("course_brief.md", detail["output_files"])
        self.assertEqual(detail["status_json"]["course_brief_status"], "available")

    def test_runs_form_is_dropdown_only_and_topic_agnostic(self) -> None:
        template_text = (REPO_ROOT / "templates" / "admin.html").read_text(encoding="utf-8")
        js_text = (REPO_ROOT / "static" / "admin.js").read_text(encoding="utf-8")

        for field_id in [
            "run-course-type",
            "run-target-audience-type",
            "run-learner-starting-level",
            "run-primary-learning-result",
            "run-final-output-type",
            "run-preferred-course-size",
            "run-course-depth",
            "run-explanation-style",
            "run-practice-format",
            "run-assessment-format",
            "run-feedback-mode",
            "run-source-strictness",
            "run-domain-sensitivity",
            "run-course-mode",
        ]:
            self.assertIn(field_id, template_text)

        for forbidden in [
            'id="run-goal"',
            'id="run-target-audience"',
            "Комментарий к цели",
            "Комментарий к аудитории",
            "Практический вводный курс",
            "Мини-курс",
            "Пошаговый туториал",
            "Внутренний обучающий курс",
            "GitHub-backed",
            "Read-only preview",
            "Codex report",
        ]:
            self.assertNotIn(forbidden, template_text)

        self.assertIn("course_factory_runs_form_draft_v2", js_text)
        self.assertIn("courseSetupFieldKeys", js_text)
        self.assertNotIn('getElementById("run-goal")', js_text)
        self.assertNotIn('getElementById("run-target-audience")', js_text)
        self.assertNotIn("Комментарий к цели", js_text)
        self.assertNotIn("Комментарий к аудитории", js_text)


if __name__ == "__main__":
    unittest.main()
