"""Tests for the comment-only source audit utility."""

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "comment_audit.py"
SPEC = importlib.util.spec_from_file_location("comment_audit", SCRIPT)
comment_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comment_audit)


class CommentAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.original = self.root / "original"
        self.annotated = self.root / "annotated"
        self.original.mkdir()
        self.annotated.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_pair(self, name, original, annotated):
        before = self.original / name
        after = self.annotated / name
        before.parent.mkdir(parents=True, exist_ok=True)
        after.parent.mkdir(parents=True, exist_ok=True)
        before.write_text(original, encoding="utf-8")
        after.write_text(annotated, encoding="utf-8")
        return before, after

    def audit_pair(self, name, original, annotated, allow_rewrite=False, lang=None):
        before, after = self.write_pair(name, original, annotated)
        return comment_audit.audit(before, after, allow_rewrite, lang)

    def test_python_cart_comment_only_edit(self):
        # Representative cart exercise: comments may be added without changing
        # Python indentation, string tokens, or executable statements.
        before = '''class Cart:\n    def __init__(self):\n        self.items = []\n\n    def add(self, item):\n        self.items.append(item)\n\n    def total(self):\n        return sum(item["price"] for item in self.items)\n'''
        after = '''# Small shopping cart implementation.\nclass Cart:\n    def __init__(self):\n        # Initialize the collection of items.\n        self.items = []\n\n    def add(self, item):\n        self.items.append(item)  # Keep insertion order.\n\n    def total(self):\n        return sum(item["price"] for item in self.items)\n'''
        self.assertEqual(self.audit_pair("cart.py", before, after), 0)

    def test_javascript_debounce_comment_only_edit_and_template_expression(self):
        before = '''function debounce(fn, delay) {\n  let timer;\n  return (...args) => {\n    clearTimeout(timer);\n    timer = setTimeout(() => fn(...args), delay);\n  };\n}\nconst label = `wait ${delay}`;\n'''
        annotated = '''// Delay a call until input settles.\nfunction debounce(fn, delay) {\n  let timer;\n  return (...args) => {\n    clearTimeout(timer);\n    timer = setTimeout(() => fn(...args), delay); // reset the timer\n  };\n}\nconst label = `wait ${delay}`;\n'''
        self.assertEqual(self.audit_pair("debounce.js", before, annotated), 0)
        changed_expression = annotated.replace("${delay}", "${delay + 1}")
        self.assertEqual(self.audit_pair("debounce.js", before, changed_expression), 1)

    def test_executable_change_fails(self):
        self.assertEqual(self.audit_pair("main.py", "value = 1\n", "value = 2\n"), 1)

    def test_comment_markers_inside_python_strings_are_not_comments(self):
        before = 'message = "literal # not comment"\nother = "https://example.test/a/*b*/"\n'
        changed_string = 'message = "literal # changed"\nother = "https://example.test/a/*b*/"\n'
        self.assertEqual(self.audit_pair("strings.py", before, changed_string), 1)

    def test_comment_markers_inside_javascript_strings_and_templates(self):
        before = 'const a = "// not a comment";\nconst b = `/* ${x} */`;\n'
        with_comments = '// actual comment\n' + before
        self.assertEqual(self.audit_pair("strings.js", before, with_comments), 0)
        changed_template_code = with_comments.replace("${x}", "${y}")
        self.assertEqual(self.audit_pair("strings.js", before, changed_template_code), 1)
        changed_template_text = with_comments.replace("/* ${x} */", "// ${x} */")
        self.assertEqual(self.audit_pair("strings.js", before, changed_template_text), 1)

    def test_comment_markers_inside_javascript_regex_and_css_url(self):
        js_before = "const re = /https?:\\/\\/host/;\nrun(re);\n"
        js_after = "// added note\nconst re = /https?:\\/\\/host/;\nrun(re);\n"
        self.assertEqual(self.audit_pair("regex.js", js_before, js_after), 0)
        js_changed = js_after.replace("run(re)", "run(other)")
        self.assertEqual(self.audit_pair("regex.js", js_before, js_changed), 1)

        css_before = "a { background: url(https://example.test/a.png); }\n"
        css_after = "/* note */\na { background: url(https://example.test/a.png); }\n"
        self.assertEqual(self.audit_pair("style.css", css_before, css_after), 0)
        css_changed = css_after.replace("a.png", "b.png")
        self.assertEqual(self.audit_pair("style.css", css_before, css_changed), 1)

    def test_added_and_removed_comments_warn_but_pass(self):
        before = "x = 1\n"
        with_comment = "# explanation\nx = 1\n"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(self.audit_pair("warn.py", before, with_comment), 0)
        self.assertIn("Warning:", stderr.getvalue())

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(self.audit_pair("warn.py", with_comment, before), 0)
        self.assertIn("Warning:", stderr.getvalue())

    def test_allow_rewrite_suppresses_comment_warning(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(self.audit_pair("rewrite.py", "# old\nx = 1\n", "# new\nx = 1\n", allow_rewrite=True), 0)
        self.assertEqual(stderr.getvalue(), "")

    def test_directory_relative_match_and_nested_files(self):
        (self.original / "nested").mkdir()
        (self.annotated / "nested").mkdir()
        (self.original / "a.py").write_text("x = 1\n", encoding="utf-8")
        (self.annotated / "a.py").write_text("# added\nx = 1\n", encoding="utf-8")
        (self.original / "nested" / "b.js").write_text("let x = 2;\n", encoding="utf-8")
        (self.annotated / "nested" / "b.js").write_text("let x = 2; // note\n", encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(comment_audit.audit(self.original, self.annotated), 0)
        self.assertEqual(stderr.getvalue().count("Warning:"), 2)

    def test_directory_missing_file_is_usage_error(self):
        (self.original / "a.py").write_text("x = 1\n", encoding="utf-8")
        with self.assertRaises(comment_audit.AuditError):
            comment_audit.audit(self.original, self.annotated)
        self.assertEqual(comment_audit.main([str(self.original), str(self.annotated)]), 2)

    def test_unknown_extension_and_lang_override(self):
        before, after = self.write_pair("sample.src", "const x = 1;\n", "// note\nconst x = 1;\n")
        with self.assertRaises(comment_audit.UnsupportedLanguage):
            comment_audit.audit(before, after)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(comment_audit.audit(before, after, lang="javascript"), 0)
        self.assertIn("Warning:", stderr.getvalue())
        self.assertEqual(comment_audit.main([str(before), str(after), "--lang", "not-a-language"]), 2)

    def test_unsupported_language_and_syntax_are_exit_two(self):
        before, after = self.write_pair("data.bin", "x", "x")
        self.assertEqual(comment_audit.main([str(before), str(after)]), 2)
        sh_before, sh_after = self.write_pair("script.sh", "cat <<EOF\ntext\nEOF\n", "cat <<EOF\ntext\nEOF\n")
        self.assertEqual(comment_audit.main([str(sh_before), str(sh_after)]), 2)

    def test_shell_comment_lines_preserve_shebang_and_fail_closed_on_continuations(self):
        before = "#!/usr/bin/env bash\nset -eu\n\nvalue=1\nprintf '%s\\n' \"$value\"\n"
        after = "#!/usr/bin/env bash\nset -eu\n# Keep the command grouped with the setup above.\n\nvalue=1\nprintf '%s\\n' \"$value\"\n"
        self.assertEqual(self.audit_pair("script.sh", before, after), 0)

        changed_shebang = after.replace("#!/usr/bin/env bash", "#!/usr/bin/env sh")
        self.assertEqual(self.audit_pair("script.sh", before, changed_shebang), 1)

        continuation_before = "printf '%s' \\\nvalue\n"
        continuation_after = "printf '%s' \\\n# this comment interrupts the command\nvalue\n"
        old, new = self.write_pair("continued.sh", continuation_before, continuation_after)
        with self.assertRaises(comment_audit.UnsupportedLanguage):
            comment_audit.audit(old, new)

    def test_yaml_indentation_is_executable_structure(self):
        before = "root:\n  child: one\n"
        after = "root:\n    child: one\n"
        self.assertEqual(self.audit_pair("config.yaml", before, after), 1)

    def test_yaml_block_scalar_fails_closed(self):
        before, after = self.write_pair("config.yaml", "message: |\n  # literal data\n", "message: |\n  # literal data\n")
        self.assertEqual(comment_audit.main([str(before), str(after)]), 2)

    def test_path_and_file_set_errors_are_exit_two(self):
        self.assertEqual(comment_audit.main([str(self.root / "missing.py"), str(self.annotated / "missing.py")]), 2)
        (self.original / "only.py").write_text("x = 1\n", encoding="utf-8")
        with self.assertRaises(comment_audit.AuditError):
            comment_audit.audit(self.original, self.annotated)


if __name__ == "__main__":
    unittest.main()
