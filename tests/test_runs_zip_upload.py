from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
import warnings
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
    def __init__(self, items: list[FakeUpload]) -> None:
        self.list = items
        self.course_setup = {
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

    def getfirst(self, key: str, default: str = "") -> str:
        values = {
            "agent": "source-analyst",
        }
        values.update(self.course_setup)
        return values.get(key, default)


def make_zip(entries: list[tuple[str, bytes | str]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries:
            if isinstance(content, str):
                content = content.encode("utf-8")
            archive.writestr(name, content)
    return buffer.getvalue()


class RunZipUploadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_root = Path(self.tmp.name)
        patcher = mock.patch.object(admin, "RUNS_ROOT", self.run_root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def create_run(self, uploads: list[FakeUpload]) -> dict[str, object]:
        return admin.create_run_request_from_form(FakeForm(uploads))

    def test_md_only_upload_still_works(self) -> None:
        result = self.create_run([FakeUpload("files[]", "brief.md", b"# brief\n")])

        run_id = str(result["run_id"])
        run_dir = self.run_root / run_id
        self.assertTrue((run_dir / "input" / "source_pack" / "brief.md").exists())
        self.assertEqual(result["source_files"], ["input/source_pack/brief.md"])

        detail = admin.run_detail_payload(run_id)
        self.assertEqual(detail["input_files"], ["brief.md"])
        self.assertIn("input/source_pack/brief.md", detail["run_request_md"])

    def test_zip_with_markdown_files_extracts_nested_paths(self) -> None:
        archive = make_zip(
            [
                ("docs/intro.md", "# intro\n"),
                ("docs/notes.txt", "ignore me"),
                ("nested/lesson.md", "# lesson\n"),
                ("__MACOSX/._junk", "ignored"),
            ]
        )

        result = self.create_run([FakeUpload("files[]", "bundle.zip", archive)])
        run_id = str(result["run_id"])
        run_dir = self.run_root / run_id

        self.assertTrue((run_dir / "input" / "source_pack" / "docs" / "intro.md").exists())
        self.assertTrue((run_dir / "input" / "source_pack" / "nested" / "lesson.md").exists())
        self.assertEqual(
            result["source_files"],
            [
                "input/source_pack/docs/intro.md",
                "input/source_pack/nested/lesson.md",
            ],
        )

        detail = admin.run_detail_payload(run_id)
        self.assertEqual(detail["input_files"], ["docs/intro.md", "nested/lesson.md"])

        path, relative_name = admin.read_run_file(run_id, "input", "nested/lesson.md")
        self.assertEqual(relative_name, "source_pack/nested/lesson.md")
        self.assertEqual(path.read_text(encoding="utf-8"), "# lesson\n")

    def test_mixed_md_and_zip_upload(self) -> None:
        archive = make_zip([("pack/topic.md", "# topic\n")])

        result = self.create_run(
            [
                FakeUpload("files[]", "overview.md", b"# overview\n"),
                FakeUpload("files[]", "pack.zip", archive),
            ]
        )

        self.assertEqual(
            result["source_files"],
            [
                "input/source_pack/overview.md",
                "input/source_pack/pack/topic.md",
            ],
        )

    def test_zip_path_traversal_is_rejected(self) -> None:
        archive = make_zip([("../evil.md", "bad"), ("safe.md", "ok")])

        with self.assertRaises(admin.ApiError) as ctx:
            self.create_run([FakeUpload("files[]", "bundle.zip", archive)])

        self.assertEqual(ctx.exception.code, "INVALID_ZIP_SOURCE_PATH")
        self.assertEqual(list(self.run_root.iterdir()), [])

    def test_zip_with_no_markdown_files_is_rejected(self) -> None:
        archive = make_zip([("notes.txt", "ignore"), ("__MACOSX/._junk", "ignored")])

        with self.assertRaises(admin.ApiError) as ctx:
            self.create_run([FakeUpload("files[]", "bundle.zip", archive)])

        self.assertEqual(ctx.exception.code, "ZIP_ARCHIVE_HAS_NO_MARKDOWN")
        self.assertEqual(list(self.run_root.iterdir()), [])

    def test_non_md_files_inside_zip_are_ignored(self) -> None:
        archive = make_zip([("notes.txt", "ignore"), ("docs/guide.md", "# guide\n")])

        result = self.create_run([FakeUpload("files[]", "bundle.zip", archive)])
        self.assertEqual(result["source_files"], ["input/source_pack/docs/guide.md"])

    def test_duplicate_zip_entries_are_rejected(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            archive = make_zip([("dup.md", "first"), ("dup.md", "second")])

        with self.assertRaises(admin.ApiError) as ctx:
            self.create_run([FakeUpload("files[]", "bundle.zip", archive)])

        self.assertEqual(ctx.exception.code, "DUPLICATE_SOURCE_FILENAME")
        self.assertEqual(list(self.run_root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
