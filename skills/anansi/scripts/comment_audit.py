#!/usr/bin/env python3
"""Audit whether source edits change executable tokens after comments are removed.

This is a conservative lexical checker, not a parser or formatter. Python is
lexed with ``tokenize``. Other supported languages use a small scanner that
recognizes only the comment and quoted-string forms listed below. Ambiguous
constructs (for example shell heredocs and interpolated strings in languages
where their expressions cannot safely be isolated) are rejected rather than
silently treated as comments or strings.

Supported extensions: .py; .c/.h; .cc/.cpp/.cxx/.hpp; .java; .js/.jsx/.mjs/.cjs;
.ts/.tsx; .go; .rs; .cs; .swift; .kt/.kts; .rb; .sh/.bash/.zsh; .sql; .yaml/.yml;
.toml; .html/.htm/.xml/.xhtml; .css; .lua. This list is intentionally explicit;
unsupported formats must not be presumed safe. YAML block scalars and other
syntax not confidently covered are rejected.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
import tokenize
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


class AuditError(Exception):
    """A user-correctable path, language, or lexical-safety problem."""


class UnsupportedLanguage(AuditError):
    """The file type or syntax is outside the scanner's safe subset."""


EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp",
    ".hpp": "cpp", ".hh": "cpp",
    ".java": "java",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".go": "go", ".rs": "rust", ".cs": "csharp", ".swift": "swift",
    ".kt": "kotlin", ".kts": "kotlin", ".rb": "ruby",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".sql": "sql", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".html": "html", ".htm": "html", ".xhtml": "xml", ".xml": "xml",
    ".css": "css", ".lua": "lua",
}
LANG_ALIASES = {
    "py": "python", "js": "javascript", "ts": "typescript", "sh": "shell",
    "c++": "cpp", "c#": "csharp", "yml": "yaml", "htm": "html",
}
SUPPORTED = set(EXTENSIONS.values())

# A (type, exact text) token stream. Whitespace is not executable except line
# endings in shell and Ruby, which delimit commands/statements in common cases.
Token = Tuple[str, str]
Comment = Tuple[int, str]  # token offset plus exact comment text


def _lang_from_path(path: Path, override: Optional[str]) -> str:
    ext = path.suffix.lower()
    inferred = EXTENSIONS.get(ext)
    if inferred:
        return inferred
    if override:
        lang = LANG_ALIASES.get(override.lower(), override.lower())
        if lang not in SUPPORTED:
            raise UnsupportedLanguage("unsupported --lang value: {!r}".format(override))
        return lang
    raise UnsupportedLanguage("unsupported language for {} (use --lang for an unknown extension)".format(path))


def _python_tokens(text: str, path: Path) -> Tuple[List[Token], List[Comment]]:
    tokens: List[Token] = []
    comments: List[Comment] = []
    try:
        stream = tokenize.generate_tokens(io.StringIO(text).readline)
        for item in stream:
            if item.type == tokenize.COMMENT:
                comments.append((len(tokens), item.string))
            elif item.type in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NL):
                continue
            else:
                # Preserve NEWLINE, INDENT and DEDENT: they can affect Python
                # statement boundaries and block structure.
                tokens.append((tokenize.tok_name.get(item.type, str(item.type)), item.string))
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        raise AuditError("cannot safely tokenize {}: {}".format(path, exc))
    return tokens, comments


_CLIKE = {"c", "cpp", "java", "javascript", "typescript", "go", "rust", "csharp", "swift", "kotlin", "css", "sql"}
_HASHLINE = {"ruby", "shell", "yaml", "toml"}
_LINE_ENDING_LANGS = {"ruby", "shell", "yaml"}
_OPERATORS = sorted({
    "===", "!==", ">>>=", "**=", "<<=", ">>=", "...", "=>", "==", "!=", "<=", ">=", "++", "--",
    "&&", "||", "??", "?.", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<", ">>", ">>>",
    "**", "->", "::", ":=", "...", "..=", "..", "??=", "?.", "\u003c\u003c", "\u003e\u003e",
}, key=len, reverse=True)


class Scanner:
    def __init__(self, text: str, lang: str, path: Path):
        self.text = text
        self.lang = lang
        self.path = path
        self.n = len(text)
        self.i = 0
        self.tokens: List[Token] = []
        self.comments: List[Comment] = []

    def fail(self, message: str) -> None:
        raise UnsupportedLanguage("{}: {}".format(self.path, message))

    def add_token(self, kind: str, value: str) -> None:
        self.tokens.append((kind, value))

    def add_comment(self, value: str) -> None:
        self.comments.append((len(self.tokens), value))

    def add_newline(self) -> None:
        # Blank/comment-only lines are semantically inert in shell unless they
        # split a continuation, which the comment scanner rejects below.
        if self.lang == "shell" and self.tokens and self.tokens[-1] == ("newline", "\n"):
            return
        self.add_token("newline", "\n")

    def _starts(self, value: str) -> bool:
        return self.text.startswith(value, self.i)

    def _quoted(self, quote: str, prefix: str = "") -> str:
        start = self.i
        self.i += len(prefix) + 1
        triple = quote in ("'", '"') and self.text.startswith(quote * 2, self.i)
        if triple:
            self.i += 2
        delim = quote * (3 if triple else 1)
        while self.i < self.n:
            if self.text.startswith(delim, self.i):
                self.i += len(delim)
                return self.text[start:self.i]
            ch = self.text[self.i]
            if ch == "\\":
                self.i += 1
                if self.i < self.n:
                    self.i += 1
                continue
            if not triple and ch in "\r\n" and self.lang not in ("javascript", "typescript", "go", "rust", "swift", "kotlin"):
                self.fail("newline in quoted literal; refusing uncertain lexical interpretation")
            self.i += 1
        self.fail("unterminated quoted literal")
        return ""

    def _block_comment(self, open_delim: str, close_delim: str, nested: bool = False) -> str:
        start = self.i
        self.i += len(open_delim)
        depth = 1
        while self.i < self.n:
            if nested and self.text.startswith(open_delim, self.i):
                depth += 1
                self.i += len(open_delim)
            elif self.text.startswith(close_delim, self.i):
                depth -= 1
                self.i += len(close_delim)
                if depth == 0:
                    return self.text[start:self.i]
            else:
                self.i += 1
        self.fail("unterminated block comment")
        return ""

    def _rust_raw(self) -> Optional[str]:
        if self.lang != "rust" or self.text[self.i] != "r":
            return None
        m = re.match(r'r(#+)?"', self.text[self.i:])
        if not m:
            return None
        start = self.i
        hashes = m.group(1) or ""
        close = '"' + hashes
        self.i += len(m.group(0))
        end = self.text.find(close, self.i)
        if end < 0:
            self.fail("unterminated Rust raw string")
        self.i = end + len(close)
        return self.text[start:self.i]

    def _cpp_raw(self) -> Optional[str]:
        if self.lang != "cpp" or not self.text.startswith('R"', self.i):
            return None
        m = re.match(r'R"([^ ()\\\t\r\n]{0,16})\(', self.text[self.i:])
        if not m:
            return None
        start = self.i
        close = ")" + m.group(1) + '"'
        self.i += len(m.group(0))
        end = self.text.find(close, self.i)
        if end < 0:
            self.fail("unterminated C++ raw string")
        self.i = end + len(close)
        return self.text[start:self.i]

    def _lua_long(self, is_comment: bool = False) -> Optional[str]:
        prefix = "--" if is_comment else ""
        pos = self.i + len(prefix)
        m = re.match(r'\[(=*)\[', self.text[pos:])
        if not m:
            return None
        opening = m.group(0)
        closing = "]" + m.group(1) + "]"
        start = self.i
        self.i = pos + len(opening)
        end = self.text.find(closing, self.i)
        if end < 0:
            self.fail("unterminated Lua long string/comment")
        self.i = end + len(closing)
        return self.text[start:self.i]

    def _template(self) -> None:
        # JS/TS template text is opaque, while each ${...} expression is lexed
        # normally so code or comments within an expression are not hidden.
        self.i += 1  # opening backtick
        self.add_token("template-open", "`")
        chunk_start = self.i
        while self.i < self.n:
            if self.text[self.i] == "\\":
                self.i = min(self.n, self.i + 2)
                continue
            if self.text[self.i] == "`":
                if self.i > chunk_start:
                    self.add_token("template-text", self.text[chunk_start:self.i])
                self.i += 1
                self.add_token("template-close", "`")
                return
            if self.text.startswith("${", self.i):
                if self.i > chunk_start:
                    self.add_token("template-text", self.text[chunk_start:self.i])
                self.i += 2
                self.add_token("template-expr-open", "${")
                self._scan(template_expr=True)
                chunk_start = self.i
                continue
            self.i += 1
        self.fail("unterminated JavaScript template literal")

    def _regex_can_start(self) -> bool:
        if not self.tokens:
            return True
        kind, value = self.tokens[-1]
        if kind == "word" and value in {
            "return", "throw", "case", "delete", "void", "typeof", "instanceof",
            "in", "of", "yield", "await", "new", "else", "do",
        }:
            return True
        return value in {
            "(", "[", "{", ",", ";", ":", "=", "!", "?", "+", "-", "*",
            "%", "&", "|", "^", "~", "=>", "&&", "||", "??", "==", "===",
            "!=", "!==", "<", ">", "<=", ">=", "+=", "-=", "*=", "/=", "%=",
        }

    def _js_regex(self) -> str:
        start = self.i
        self.i += 1
        in_class = False
        while self.i < self.n:
            ch = self.text[self.i]
            if ch in "\r\n":
                self.fail("unterminated JavaScript regular-expression literal")
            if ch == "\\":
                self.i = min(self.n, self.i + 2)
                continue
            if ch == "[":
                in_class = True
            elif ch == "]":
                in_class = False
            elif ch == "/" and not in_class:
                self.i += 1
                while self.i < self.n and (self.text[self.i].isalpha() or self.text[self.i].isdigit()):
                    self.i += 1
                return self.text[start:self.i]
            self.i += 1
        self.fail("unterminated JavaScript regular-expression literal")
        return ""

    def _scan(self, template_expr: bool = False) -> None:
        brace_depth = 0
        while self.i < self.n:
            ch = self.text[self.i]
            if template_expr and ch == "}":
                if brace_depth == 0:
                    self.i += 1
                    self.add_token("template-expr-close", "}")
                    return
                brace_depth -= 1
                self.add_token("punct", ch)
                self.i += 1
                continue

            # Ruby's multiline =begin/=end comments are recognized only at
            # the start of a physical line after optional indentation.
            if self.lang == "ruby" and ch == "=" and (self.i == 0 or self.text[self.i - 1] == "\n"):
                line_start = self.i
                while line_start > 0 and self.text[line_start - 1] not in "\r\n":
                    line_start -= 1
                if not self.text[line_start:self.i].strip() and self.text.startswith("=begin", self.i):
                    end = re.search(r"(?m)^=end(?:\s|$).*?(?:\n|$)", self.text[self.i:])
                    if not end:
                        self.fail("unterminated Ruby =begin comment")
                    raw = self.text[self.i:self.i + end.end()]
                    self.i += end.end()
                    self.add_comment(raw)
                    continue

            if ch in " \t\f\v\r\n":
                if ch in "\r\n" and self.lang in _LINE_ENDING_LANGS:
                    if ch == "\r" and self.i + 1 < self.n and self.text[self.i + 1] == "\n":
                        self.i += 2
                        self.add_newline()
                    else:
                        self.i += 1
                        self.add_newline()
                else:
                    self.i += 1
                continue

            if self.lang == "css" and self.text[self.i:self.i + 4].lower() == "url(":
                start = self.i
                self.i += 4
                quote = None
                while self.i < self.n:
                    current = self.text[self.i]
                    if current == "\\":
                        self.i = min(self.n, self.i + 2)
                        continue
                    if quote:
                        if current == quote:
                            quote = None
                    elif current in "'\"":
                        quote = current
                    elif current == ")":
                        self.i += 1
                        self.add_token("url", self.text[start:self.i])
                        break
                    self.i += 1
                else:
                    self.fail("unterminated CSS url() token")
                continue

            if self.lang == "yaml" and ch == "|" or self.lang == "yaml" and ch == ">":
                # YAML block scalars make comment-looking text literal. Rather
                # than guess indentation/chomping semantics, reject them.
                tail = self.text[self.i:]
                if re.match(r"[|>][+-]?(?:[1-9])?(?:\s|$)", tail):
                    self.fail("YAML block scalars are outside the safe subset")

            # Language-specific line comments.
            if self.lang in _CLIKE and self._starts("//"):
                if self.lang in ("javascript", "typescript") and self.i > 0 and self.text[self.i - 1] == "\\":
                    self.fail("ambiguous escaped slash in JavaScript; regex literal could not be identified safely")
                start = self.i
                self.i += 2
                while self.i < self.n and self.text[self.i] not in "\r\n":
                    self.i += 1
                self.add_comment(self.text[start:self.i])
                continue
            if self.lang in _CLIKE and self._starts("/*"):
                nested = self.lang in ("rust", "swift", "kotlin")
                self.add_comment(self._block_comment("/*", "*/", nested=nested))
                continue
            if self.lang in ("html", "xml") and self._starts("<!--"):
                self.add_comment(self._block_comment("<!--", "-->"))
                continue
            if self.lang == "lua" and self._starts("--"):
                block = self._lua_long(is_comment=True)
                if block is not None:
                    self.add_comment(block)
                else:
                    start = self.i
                    self.i += 2
                    while self.i < self.n and self.text[self.i] not in "\r\n":
                        self.i += 1
                    self.add_comment(self.text[start:self.i])
                continue
            if self.lang in ("sql", "ruby", "shell", "yaml", "toml"):
                is_comment = self._starts("--") if self.lang == "sql" else ch == "#"
                if self.lang == "yaml" and is_comment:
                    is_comment = self.i == 0 or self.text[self.i - 1].isspace()
                if self.lang == "shell" and is_comment:
                    is_comment = self.i == 0 or self.text[self.i - 1].isspace() or self.text[self.i - 1] in ";|&()"
                if self.lang == "shell" and self.i == 0 and self._starts("#!"):
                    start = self.i
                    while self.i < self.n and self.text[self.i] not in "\r\n":
                        self.i += 1
                    self.add_token("directive", self.text[start:self.i])
                    continue
                if is_comment:
                    if self.lang == "shell" and re.search(r"\\\r?\n[ \t]*$", self.text[:self.i]):
                        self.fail("comments on a continued shell line are outside the safe subset")
                    start = self.i
                    while self.i < self.n and self.text[self.i] not in "\r\n":
                        self.i += 1
                    self.add_comment(self.text[start:self.i])
                    continue
                if self.lang in ("sql", "toml") and self._starts("/*"):
                    self.add_comment(self._block_comment("/*", "*/"))
                    continue

            if self.lang == "shell" and self._starts("<<"):
                self.fail("shell heredocs/here-strings are outside the safe subset")
            if self.lang == "ruby" and self._starts("<<") and re.match(r"<<\s*['\"`]?[_A-Za-z]", self.text[self.i:]):
                self.fail("Ruby heredocs are outside the safe subset")

            if self.lang == "rust":
                raw = self._rust_raw()
                if raw is not None:
                    self.add_token("string", raw)
                    continue
            if self.lang == "cpp":
                raw = self._cpp_raw()
                if raw is not None:
                    self.add_token("string", raw)
                    continue
            if self.lang == "lua" and ch == "[":
                raw = self._lua_long()
                if raw is not None:
                    self.add_token("string", raw)
                    continue

            if self.lang in ("javascript", "typescript") and ch == "`":
                self._template()
                continue
            if self.lang in ("javascript", "typescript") and ch == "/" and self._regex_can_start():
                self.add_token("regex", self._js_regex())
                continue

            # Refuse string forms with interpolation expressions unless handled
            # structurally (JS/TS templates above). Treating their contents as
            # opaque could hide executable changes.
            if self.lang == "csharp" and (self._starts('$"') or self._starts('@"') or self._starts('$@"') or self._starts('@$"')):
                if "$" in self.text[self.i:self.i + 3]:
                    self.fail("C# interpolated strings are outside the safe subset")
                # Verbatim strings are harmless when not interpolated, but need
                # doubled-quote handling, so conservatively reject them too.
                self.fail("C# verbatim strings are outside the safe subset")
            if self.lang == "swift" and ch in "'\"":
                end = self.text.find(ch, self.i + 1)
                if ch == '"' and end >= 0 and "\\(" in self.text[self.i:end]:
                    self.fail("Swift interpolated strings are outside the safe subset")
            if self.lang == "kotlin" and ch == '"':
                end = self.text.find('"', self.i + 1)
                if end >= 0 and re.search(r"\$(?:[A-Za-z_{])", self.text[self.i:end]):
                    self.fail("Kotlin interpolated strings are outside the safe subset")
            if self.lang == "ruby" and ch == '"':
                end = self.text.find('"', self.i + 1)
                if end >= 0 and "#{" in self.text[self.i:end]:
                    self.fail("Ruby interpolated strings are outside the safe subset")

            # Backtick strings are raw strings in Go and quoted identifiers in
            # SQL. Other languages use them only for JS templates, handled above.
            if ch in "'\"" or (ch == "`" and self.lang in ("go", "sql")):
                raw = self._quoted(ch)
                self.add_token("string", raw)
                continue

            # Reject recognizable YAML block scalar indicator (including forms
            # with chomping/indent flags) before tokenizing it as punctuation.
            if self.lang == "yaml" and ch in "|>" and (self.i == 0 or self.text[self.i - 1].isspace()):
                if re.match(r"[|>][+-]?[1-9]?(?:\s|$)", self.text[self.i:]):
                    self.fail("YAML block scalars are outside the safe subset")

            if ch.isalpha() or ch == "_" or ord(ch) >= 128:
                start = self.i
                self.i += 1
                while self.i < self.n and (self.text[self.i].isalnum() or self.text[self.i] == "_" or ord(self.text[self.i]) >= 128):
                    self.i += 1
                self.add_token("word", self.text[start:self.i])
                continue
            if ch.isdigit():
                start = self.i
                self.i += 1
                while self.i < self.n and (self.text[self.i].isalnum() or self.text[self.i] in "_."):
                    self.i += 1
                self.add_token("number", self.text[start:self.i])
                continue
            matched = next((op for op in _OPERATORS if self.text.startswith(op, self.i)), None)
            if matched:
                self.add_token("operator", matched)
                self.i += len(matched)
            else:
                self.add_token("punct", ch)
                if template_expr and ch == "{":
                    brace_depth += 1
                self.i += 1
        if template_expr:
            self.fail("unterminated JavaScript template expression")

    def scan(self) -> Tuple[List[Token], List[Comment]]:
        self._scan()
        return self.tokens, self.comments


def lex(text: str, lang: str, path: Path) -> Tuple[List[Token], List[Comment]]:
    if lang == "python":
        return _python_tokens(text, path)
    if lang == "yaml":
        # Indentation and line breaks are meaningful in YAML. Block scalars
        # are intentionally rejected because their content can contain lines
        # that look like comments but are actually scalar text.
        if re.search(r"(?m)^[ \t]*(?:-[ \t]+)?(?:[^#\n]+:[ \t]*)?[|>][+-]?[1-9]?[ \t]*(?:#.*)?$", text):
            raise UnsupportedLanguage("{}: YAML block scalars are outside the safe subset".format(path))
        tokens: List[Token] = []
        comments: List[Comment] = []
        for line in text.splitlines():
            indent_len = len(line) - len(line.lstrip(" \t"))
            body = line[indent_len:]
            if "''" in body:
                raise UnsupportedLanguage("{}: escaped single quotes in YAML are outside the safe subset".format(path))
            scanner = Scanner(body, lang, path)
            line_tokens, line_comments = scanner.scan()
            base = len(tokens)
            if line_tokens:
                tokens.append(("indent", line[:indent_len]))
                comments.extend((base + 1 + offset, value) for offset, value in line_comments)
                tokens.extend(line_tokens)
                tokens.append(("newline", "\n"))
            else:
                comments.extend((base, value) for _, value in line_comments)
        
        return tokens, comments
    return Scanner(text, lang, path).scan()


def _read_lex(path: Path, lang_override: Optional[str]) -> Tuple[List[Token], List[Comment]]:
    lang = _lang_from_path(path, lang_override)
    try:
        if lang == "python":
            with tokenize.open(str(path)) as source_file:
                text = source_file.read()
        else:
            text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AuditError("cannot read {}: {}".format(path, exc))
    return lex(text, lang, path)


def _files(root: Path) -> Dict[str, Path]:
    if root.is_symlink():
        raise AuditError("symlink inputs are not followed: {}".format(root))
    if not root.exists():
        raise AuditError("path does not exist: {}".format(root))
    if root.is_file():
        return {root.name: root}
    if not root.is_dir():
        raise AuditError("not a regular file or directory: {}".format(root))
    found: Dict[str, Path] = {}
    for current, dirs, names in os.walk(str(root), followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(current) / d).is_symlink())
        for name in sorted(names):
            p = Path(current) / name
            if p.is_symlink():
                continue
            if p.is_file():
                found[p.relative_to(root).as_posix()] = p
    return found


def _language_pair(left: Path, right: Path, override: Optional[str]) -> str:
    l_lang = _lang_from_path(left, override)
    r_lang = _lang_from_path(right, override)
    if l_lang != r_lang:
        raise AuditError("language mismatch for {} and {} ({} vs {})".format(left, right, l_lang, r_lang))
    return l_lang


def audit(original: Path, annotated: Path, allow_rewrite: bool = False, lang: Optional[str] = None) -> int:
    """Audit two files/directories; return 0 for match and 1 for code changes."""
    left_is_dir = original.is_dir() if original.exists() else False
    right_is_dir = annotated.is_dir() if annotated.exists() else False
    if left_is_dir != right_is_dir:
        raise AuditError("both paths must be files or both must be directories")
    left_files, right_files = _files(original), _files(annotated)
    left_names, right_names = set(left_files), set(right_files)
    if left_names != right_names:
        missing_right = sorted(left_names - right_names)
        missing_left = sorted(right_names - left_names)
        parts = []
        if missing_right:
            parts.append("missing from target: " + ", ".join(missing_right))
        if missing_left:
            parts.append("missing from original: " + ", ".join(missing_left))
        raise AuditError("directory file sets differ (" + "; ".join(parts) + ")")

    code_diff = False
    for rel in sorted(left_names):
        before, after = left_files[rel], right_files[rel]
        language = _language_pair(before, after, lang)
        old_tokens, old_comments = _read_lex(before, language)
        new_tokens, new_comments = _read_lex(after, language)
        if old_tokens != new_tokens:
            print("Code differs: {}".format(rel), file=sys.stderr)
            code_diff = True
        elif old_comments != new_comments and not allow_rewrite:
            print("Warning: comments added, removed, moved, or changed: {} (use --allow-rewrite to allow)".format(rel), file=sys.stderr)
    return 1 if code_diff else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check whether annotated source differs only in comments; language support is an explicit conservative subset."
    )
    parser.add_argument("original", help="original source file or directory")
    parser.add_argument("annotated", help="annotated source file or directory")
    parser.add_argument("--lang", help="language override for files with unknown extensions (e.g. python, javascript)")
    parser.add_argument("--allow-rewrite", action="store_true", help="do not warn when comments differ")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return audit(Path(args.original), Path(args.annotated), args.allow_rewrite, args.lang)
    except AuditError as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
