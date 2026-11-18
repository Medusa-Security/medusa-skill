# Anansi

**Anansi — Human-Voice Code Commentary** is a Claude-compatible skill for adding, refreshing, reviewing, or trimming source-code comments across programming languages. It favors specific explanations of *why* code behaves as it does, keeps executable code untouched, and allows occasional code-related humor when the context is appropriate.

## Package contents

```text
anansi/
├── SKILL.md
├── LICENSE
├── README.md
├── references/
│   ├── comment-syntax.md
│   ├── humor-playbook.md
│   └── examples.md
├── scripts/
│   └── comment_audit.py
├── examples/
│   ├── before/
│   └── after/
└── tests/
    └── test_comment_audit.py
```

The before/after folders contain matching filenames. The examples illustrate comment-only changes; they are not universal style rules.

## Use

Add this skill directory to the skills location supported by your Claude environment. The skill triggers for requests to add, humanize, refresh, review, or remove code comments. Its default mode is ANNOTATE with a dry humor dial. It never edits executable code, and it preserves existing comments unless REFRESH or DIET is requested.

## Comment-only audit

The standard-library audit script compares original and updated source after removing recognized comments. For supported language adapters:

```bash
python3 scripts/comment_audit.py ORIGINAL UPDATED
python3 scripts/comment_audit.py ORIGINAL_DIR UPDATED_DIR
python3 -m unittest discover -s tests -v
```

The audit is conservative and language-limited; it is not a universal parser, formatter, or semantic checker. An unsupported language exits with status `2`; in that case, manually inspect the diff and report that automated verification was unavailable. `--allow-rewrite` permits comment text to change but still rejects code changes. See `references/comment-syntax.md` for syntax caveats and the script's supported language list.

## License and attribution

MIT License. Copyright (c) 2026 ak495867. See [`LICENSE`](LICENSE).
