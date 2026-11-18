# Comment syntax: practical quick reference

This is a **quick reference, not a complete grammar**. The exact parser, language version, file mode, preprocessor, linter, and embedding context matter. Before inserting a comment, confirm that the target accepts it at that location and that it will not alter parsing, formatting, signing, caching, or execution. Never assume that a comment-looking token is inert: some tools deliberately interpret comments as directives, and some languages execute text embedded in comments.

## First principles

- A comment is syntax the relevant parser ignores (or specially processes); it is not a general-purpose annotation that can be pasted into any text file.
- Distinguish **data** from comments. A `#`, `//`, `--`, or `/*` inside a string, regex, URL, template, or data value is ordinarily data. Conversely, adding a comment marker to a data format can make the file invalid.
- Never add comments to strict JSON. JSON has **no comment syntax**. JSONC and JSON5 are different, non-standard dialects with their own parser support; a file ending in `.json` is not automatically one of them.
- `#` lines in shell scripts, Python, YAML, etc. are not all the same thing. A shebang, type/lint suppression, scheduler directive, or build instruction may be consumed by a tool.
- Do not “comment out” unknown code as a substitute for understanding it. Nested block comments, preprocessing, multiline strings, and embedded languages can make that unsafe.

## C-like line and block comments

`// ...` usually runs to end of line; `/* ... */` is a non-nesting block. Most accept both, but consult version and embedded-language rules. Do not place `/*` inside another block comment and expect nesting. In C and C++ comments are removed/replaced during translation before string-literal concatenation; backslash-newline splicing can also change what looks like a line comment. `//` support is version-sensitive in older C dialects.

| Language / format | Common extensions | Syntax and caveats |
|---|---|---|
| C | `.c`, `.h` | `//`, `/* ... */`; block comments do not nest. `#` starts a preprocessor directive, not a comment. Backslash-newline splicing can extend a `//` comment. |
| C++ | `.cc`, `.cpp`, `.cxx`, `.hpp`, `.h` | `//`, `/* ... */`; non-nesting blocks. `#include`, `#if`, etc. are directives, not comments. `///` and `/** ... */` are often consumed by documentation generators. |
| Objective-C | `.m`, `.h` | C comment forms. `#import`/`#include` are preprocessing directives. Embedded Objective-C++ `.mm` also follows C++ rules. |
| Java | `.java` | `//`, `/* ... */`, `/** ... */`; doc comments may feed Javadoc. Unicode escapes are processed early enough that escaped characters can affect apparent comment boundaries. |
| C# | `.cs` | `//`, `/* ... */`, XML-doc `///` and `/** ... */`; documentation comments are tool input. `#if`, `#nullable`, `#pragma` are compiler directives, not comments. |
| JavaScript | `.js`, `.mjs`, `.cjs` | `//`, `/* ... */`; blocks do not nest. `<!--` / `-->` legacy script-embedding behavior exists in some contexts—avoid it. `//# sourceMappingURL=...` and lint/bundler annotations can be tool directives. |
| TypeScript | `.ts`, `.tsx`, `.mts`, `.cts` | JavaScript comment forms; `/// <reference ... />` is a triple-slash directive, not merely prose. Type/lint/build tools also read selected comment annotations. |
| JSX | `.jsx`, `.tsx` | JavaScript comments apply in JS expressions; inside JSX markup use `{/* ... */}`. Bare `//` or `/* */` in JSX child position is generally invalid or rendered as text depending on placement. |
| Go | `.go` | `//`, `/* ... */`; `//go:build`, `//go:generate`, and other recognized `//go:` lines are compiler/tool directives. Doc comments attach to declarations. |
| Rust | `.rs` | `//`, `/* ... */` (block comments nest); `///` and `//!` are documentation comments. `#[...]` is an attribute, not a comment; rustdoc and doctests can compile/run examples in docs. |
| Kotlin | `.kt`, `.kts` | `//`, `/* ... */` (nested), `/** ... */`; KDoc is processed by documentation tools. Script/build files may have additional tool conventions. |
| Scala | `.scala`, `.sc` | `//`, `/* ... */` (nested), `/** ... */`; Scaladoc annotations/tags are consumed by doc tooling. |
| Dart | `.dart` | `//`, `/* ... */` (nested), `///` doc comments; analyzer directives such as `// ignore:` affect diagnostics. |
| Swift | `.swift` | `//`, `/* ... */` (nested), `///` and `/** ... */`; documentation markup is tool input. `#if` and `#warning` are directives, not comments. |
| PHP | `.php`, `.phtml` | `//`, `#`, `/* ... */`, `/** ... */`; PHP open/close tags and HTML outside PHP change which parser owns the text. `__halt_compiler()` changes how later content is treated. |
| Groovy | `.groovy`, `.gradle` | `//`, `/* ... */`, `/** ... */`; Gradle/Groovy files are executable build scripts, and comments can coexist with strings/interpolated expressions. |
| ActionScript | `.as`, `.mxml` | `//`, `/* ... */`; MXML embeds XML and ActionScript, so use the syntax for the current region. |
| Apex | `.cls`, `.trigger` | `//`, `/* ... */`, `/** ... */`; documentation comments and platform tooling may interpret annotations. |
| Solidity | `.sol` | `//`, `/* ... */`, NatSpec `///`/`/** ... */`; NatSpec affects generated ABI documentation and tool output. |

## Hash, bang, and line-comment family

A leading `#` often starts a comment, but it can instead introduce a shebang, directive, preprocessor instruction, interpolation, or data. Comment behavior may depend on the first bytes of the file or on a parser's dialect.

| Language / format | Common extensions | Syntax and caveats |
|---|---|---|
| Python | `.py`, `.pyw` | `#` to line end; no block-comment syntax. Triple-quoted strings are strings, not comments, and can become docstrings or runtime values. `# type: ignore`, `# noqa`, `# fmt: off`, and coding-cookie lines affect tools/interpreter behavior. |
| Ruby | `.rb`, `.rake` | `#` line comments; `=begin` / `=end` block comments must appear at the start of a line (with whitespace allowed) and are uncommon. `__END__` changes the treatment of the remainder. |
| Perl | `.pl`, `.pm`, `.t` | `#` to line end; POD blocks (`=pod` … `=cut`) are documentation directives/text, not ordinary inline comments. A shebang selects the interpreter. |
| Bash | `.sh`, extensionless scripts | An unquoted `#` that begins a shell word starts a comment through line end; `foo#bar` is part of a word. `#!` is a launch convention. Here-documents and quoted strings can contain `#` as data. `# shellcheck`, `# shellcheck disable=...`, and scheduler comments may be actionable. |
| POSIX shell | `.sh` | An unquoted `#` at the beginning of a word starts a comment through line end; `foo#bar` is part of a word. A shebang is a launch convention. Here-doc data and quoted text are data. Bash-only syntax is not portable POSIX shell syntax. |
| Zsh | `.zsh` | `#` to line end in normal use; interactive `INTERACTIVE_COMMENTS` settings affect parsing. Shebang and tool annotations remain significant. |
| PowerShell | `.ps1`, `.psm1`, `.psd1` | `#` line comments; `<# ... #>` block comments. Here-strings have distinct delimiters; comment markers inside strings are data. `#requires` is an engine directive. |
| R | `.R`, `.r`, `.Rmd` | `#` line comments; R Markdown also embeds Markdown and possibly executable code chunks. Chunk options/directives affect execution. |
| Julia | `.jl` | `#` line comments; `#= ... =#` block comments nest. `#= comment =#` is not interchangeable with shell `#` in all contexts (e.g. strings/macros). |
| Elixir | `.ex`, `.exs` | `#` line comments; `@doc` and `@moduledoc` are executable attributes/doc metadata, not comments. |
| Erlang | `.erl`, `.hrl` | `%` to line end; `%` may occur in format strings/quoted atoms as data. |
| Haskell | `.hs`, `.lhs` | `--` line comments (lexical edge cases depend on following characters); `{- ... -}` block comments nest. `{-# ... #-}` is a pragma. Bird-style literate files use `>` for code lines. |
| OCaml | `.ml`, `.mli` | `(* ... *)` block comments nest; documentation comments commonly use `(** ... *)`. |
| F# | `.fs`, `.fsi`, `.fsx` | `//`, `(* ... *)` (nested), `///` XML documentation; directives such as `#r` / `#load` are not comments. |
| Lisp family (Common Lisp) | `.lisp`, `.lsp`, `.cl` | `;` to line end; `#| ... |#` block comments nest; `#;` comments out one following form. Reader syntax means comment placement can interact with parsing. |
| Scheme | `.scm`, `.ss` | `;` line comment; `#| ... |#` block comments in many dialects, often nested; `#;` datum comment is supported in many Scheme readers. Verify the chosen dialect. |
| Racket | `.rkt` | `;` line comments; `#| ... |#` nested blocks; `#;` comments out the next datum. `#lang` is a language directive, not a comment. |
| Clojure | `.clj`, `.cljs`, `.cljc`, `.edn` | `;` line comments; `#_` discards the next form (reader directive, not prose). EDN is a data format and supports reader-discard syntax, but not arbitrary comment conventions from JSON. |
| Fortran | `.f`, `.for`, `.f90`, `.f95`, `.f03`, `.f08` | Fixed-form source commonly uses `C`, `c`, or `*` in column 1; free-form uses `!` to line end. Source form/column matters; `!` may appear inside strings. |
| MATLAB / Octave | `.m` | `%` line comments; `%{ ... %}` block comments in supported placements; `%%` section markers are recognized by editors. MATLAB also uses `%` in format strings as data. |
| COBOL | `.cob`, `.cbl` | Fixed-format comment indicator often `*` or `/` in the indicator column; free-format commonly uses `*>`. Compiler/source-format mode determines meaning. |
| Assembly (common assemblers) | `.asm`, `.s`, `.S` | Varies by assembler: `;`, `#`, `@`, or `//` are common. `.S` may be preprocessed while `.s` may not. Directives such as `.include` are not comments. Check the specific assembler and architecture. |
| Makefile | `Makefile`, `makefile`, `.mk` | `#` starts a comment, but recipes are passed to a shell; backslash continuation and recipe context matter. A `#` inside a recipe may be interpreted by the shell, not Make. `make` directives/functions are executable build logic. |
| Dockerfile | `Dockerfile`, `*.Dockerfile` | `#` comments; parser directives such as `# syntax=...` and `# escape=...` must appear at the top before ordinary instructions and affect parsing/build behavior. `RUN` commands are shell commands. |
| YAML | `.yaml`, `.yml` | `#` starts a comment outside quoted/scalar content; comments are not part of the YAML data model and are commonly lost on parse/serialize. `#` within quoted strings or block scalar content is data. YAML has no general executable directives, but tags/constructors and consuming tools can have effects. |
| TOML | `.toml` | `#` comments outside strings; there is no block-comment syntax. `#` inside strings is data. TOML itself is data, though applications can interpret values as configuration or commands. |
| INI (dialect-dependent) | `.ini`, `.cfg`, `.conf` | Often `;` and/or `#` line comments, but exact rules vary by parser; some permit comments only at line start, others treat `;` in values differently. Do not assume a universal INI grammar. |
| `.env` / dotenv | `.env`, `.env.*` | Often `#` line comments, with quoting, interpolation, `export`, and inline-comment rules varying by implementation. `#` in an unquoted value may or may not start a comment. These files carry data/secrets, not portable shell syntax. |
| Nginx config | `nginx.conf`, `*.conf` | `#` comments; directives ending in `;` configure a running server. A valid comment must not accidentally swallow or split a directive. |
| Apache httpd config | `httpd.conf`, `*.conf` | `#` line comments; directives and included files alter server behavior. Backslash continuation and quoted arguments matter. |
| CMake | `CMakeLists.txt`, `.cmake` | `#` line comments; bracket arguments/comments use `[=[ ... ]=]` forms with matching `=` counts. CMake commands execute at configure time; `#[[...]]` is a bracket comment. |
| Terraform / HCL | `.tf`, `.tfvars`, `.hcl` | `#`, `//`, `/* ... */`; blocks do not nest. Terraform files are declarative input that can create/modify infrastructure; comments do not neutralize resource blocks. |
| Nix | `.nix` | `#` line comments; `/* ... */` block comments (nesting behavior is supported by Nix). Nix expressions remain executable/evaluable configuration. |
| Salt / Ansible YAML | `.sls`, `.yml`, `.yaml` | YAML `#` comments, but playbooks/states are action-bearing configuration. Jinja templates may embed another language; add comments in the correct layer and account for templating. |

## Markup, style, and embedded-language comments

| Language / format | Common extensions | Syntax and caveats |
|---|---|---|
| HTML | `.html`, `.htm` | `<!-- ... -->`; no nesting. Avoid `--` within comment content. Comments can affect legacy parsers, conditional-comment handling, templates, or minifiers; script/style regions have their own syntax. |
| XML | `.xml`, `.xsl`, `.svg`, `.xhtml` | `<!-- ... -->`; no nesting, and `--` is forbidden inside comment content. Comments cannot appear inside a start tag. DTDs/entities are not comments and can have processing/security implications. |
| SGML | `.sgml`, `.dtd` | `<!-- ... -->`, with SGML-specific delimiter rules; not a safe shortcut for XML syntax. |
| CSS | `.css` | `/* ... */`; no `//` line comments in standard CSS. Comments can be preserved/removed by processors; `/*! ... */` is conventionally retained by some minifiers. CSS is often embedded in HTML/JS with other comment grammars. |
| SCSS | `.scss` | `//` and `/* ... */`; `//` is generally removed from compiled CSS, while block comments may be emitted. Interpolation and nested syntax complicate placement. |
| Sass (indented) | `.sass` | `//` silent comments and `/* ... */` loud comments; emitted CSS differs. It is not the same syntax as SCSS despite shared concepts. |
| Less | `.less` | `//` and `/* ... */`; line comments are generally stripped, block comments may survive compilation. |
| Markdown | `.md`, `.markdown` | No standard comment syntax. HTML comments often work in common renderers, but support/visibility varies and comments may survive source exports. Code fences contain the fenced language's syntax, not Markdown comments. |
| MDX | `.mdx` | Markdown plus JSX/JavaScript; HTML comments may not behave as expected in JSX. Use JSX comments `{/* ... */}` in JSX regions and respect MDX parser/version. |
| reStructuredText | `.rst` | `..` starts a comment/directive block at indentation-sensitive positions. Directives (`.. code-block::`, `.. include::`) are interpreted by doc tooling and may include files or otherwise transform output; they are not harmless comments. |
| AsciiDoc | `.adoc`, `.asciidoc` | `//` line comments; block comments use `//// ... ////`. Directives/macros such as `include::` are active processing instructions, not comments. |
| LaTeX | `.tex`, `.sty`, `.cls` | `%` comments to end of line; `%` also suppresses the line ending/whitespace. TeX expands macros before ordinary reading, so a comment marker introduced through expansion is not a safe assumption. |
| TeX / plain TeX | `.tex` | `%` to line end with TeX-specific category-code and macro behavior; changing catcodes can change comment parsing. Not all `%`-looking text is inert. |
| GraphQL | `.graphql`, `.gql` | `#` to line end in SDL and query documents. Comments are not GraphQL descriptions; quoted descriptions are schema data/docs and appear in introspection. Tool directives such as `@deprecated` are part of the language, not comments. |
| Protocol Buffers | `.proto` | `//`, `/* ... */`; comments can feed generated documentation. `option`, `reserved`, and field declarations are schema, not comments. |
| OpenAPI / Swagger YAML | `.yaml`, `.yml`, `.json` | YAML comments only in YAML serialization; strict JSON has none. `description` fields are data. OpenAPI extensions/operations may drive code generation or requests. |
| reStructuredText/Sphinx | `.rst` | `..` comment blocks, but `.. directive::` and roles are interpreted by Sphinx. A directive can include, execute, or generate content, depending on configuration. |

## SQL, database, and query-language comments

| Language / format | Common extensions | Syntax and caveats |
|---|---|---|
| SQL (portable baseline) | `.sql` | `--` to line end is broadly supported; `/* ... */` is common. Dialects differ on nesting, line endings, and placement. SQL comments may be extracted by tools; comments do not disable adjacent statements. |
| PostgreSQL SQL | `.sql` | `--`, `/* ... */` (nested). `/*+ ... */` is not a standard PostgreSQL optimizer hint; extensions/tools may assign meaning. `COMMENT ON` is an SQL statement that stores database metadata, not lexical comment syntax. |
| MySQL / MariaDB SQL | `.sql` | `#`, `--` (the latter requires following whitespace/control character), `/* ... */`. `/*! ... */` versioned comments can execute SQL; `/*+ ... */` optimizer hints affect plans. Never assume a block comment is inert. |
| Oracle SQL | `.sql`, `.pls` | `--`, `/* ... */`; optimizer hints use `/*+ ... */` immediately after statement keywords. `COMMENT ON` stores schema metadata and is executable SQL. |
| SQLite SQL | `.sql` | `--`, `/* ... */`; comments are treated as whitespace, but comments do not protect following SQL from execution. `--` continues to line end. |
| PL/SQL | `.pls`, `.sql`, `.pkb`, `.pks` | Oracle SQL comment forms; `/*+ ... */` optimizer hints can affect execution plans; `COMMENT ON` is a statement. |
| T-SQL (SQL Server) | `.sql` | `--`, `/* ... */` (nested block comments supported). `GO` is a client batch separator, not SQL comment syntax; tooling may split batches. `OPTION` hints are SQL clauses, not comments. |
| BigQuery SQL | `.sql` | `--`, `#`, `/* ... */`; scripting statements and client tooling execute code. Hint syntax and comment support depend on context. |
| Hive / Spark SQL | `.sql` | Commonly `--` and `/* ... */`; dialect and client differences apply. Hints such as `/*+ ... */` are actionable planner input. |
| GraphQL query language | `.graphql`, `.gql` | `#` line comments; directives like `@skip`/`@include` are query semantics, not comments. |

## Data formats: especially JSON versus JSONC/JSON5

| Format | Common extensions | Comment status and caveats |
|---|---|---|
| JSON (RFC 8259) | `.json` | **No comments.** `//` and `/* ... */` are invalid outside strings. Do not add comments to package manifests, API payloads, or config just because a nearby tool accepts them. Put explanations in a schema/documentation or a designated data field if the contract permits. |
| JSONC | `.jsonc` (sometimes `.json`) | A parser-specific JSON-like dialect commonly permitting `//` and `/* ... */`; trailing commas may or may not be allowed. JSONC is not standard JSON; confirm the exact parser and settings. A file named `.json` is not automatically JSONC. |
| JSON5 | `.json5` | A distinct JSON superset with comments (`//`, `/* ... */`), trailing commas, unquoted identifier keys, single-quoted strings, and other relaxed syntax. Not valid strict JSON; a JSON5 parser is required. |
| JSON Lines / NDJSON | `.jsonl`, `.ndjson` | One strict JSON value per line; comments are not part of the standard format. A header/comment line breaks many readers. |
| CSV | `.csv` | No universal comment syntax. `#` may be a literal field value or an application-specific preamble; adding a comment row can corrupt imports. |
| TSV | `.tsv` | No universal comment syntax; tabs/newlines and header expectations matter. |
| XML-based office formats | `.xml` | XML comment rules apply, but changing a signed, canonicalized, or schema-validated document can invalidate it. |
| TOML | `.toml` | `#` comments; no block comments. See above—valid syntax does not make application-specific configuration inert. |

## Directives, pragmas, and “comments” that tools act on

Comment-like text can be consumed by compilers, interpreters, preprocessors, linters, IDEs, build systems, bundlers, formatters, test runners, schedulers, query planners, or documentation generators. Treat it as a potential **instruction channel**, not as decoration.

- **Compiler/interpreter or source directives:** C/C++ `#include`, `#if`, `#pragma` are not comments; Go `//go:build` / `//go:generate`; Rust `#![...]` / `#[...]`; Haskell `{-# ... #-}`; Python encoding cookies and `# type: ignore`; PowerShell `#requires`. Some directives are syntactically comments but semantically active to tools.
- **Lint/type/format controls:** `// eslint-disable`, `/* eslint ... */`, `# noqa`, `# pylint: disable`, `# type: ignore`, `//noinspection`, `// prettier-ignore`, `# fmt: off`, `// swiftlint:disable`, and similar annotations alter checks or output. Only add them intentionally and narrowly; do not suppress diagnostics to make a comment fit.
- **Build/deploy/scheduler controls:** Dockerfile parser directives; shell `#SBATCH` / `#PBS`; CI workflow comments recognized by provider-specific commands; Nginx/Apache/CMake/Terraform source is configuration, not prose. A valid comment may still be parsed by a surrounding tool.
- **SQL hints and executable comments:** MySQL/MariaDB `/*! ... */` may execute; `/*+ ... */` hints may alter query planning in several databases. A comment marker is not proof of inertness.
- **Documentation and tests:** Javadoc, KDoc, rustdoc, Scaladoc, NatSpec, doctests, Markdown/RST directives and examples can generate public docs, compile/run examples, include files, or execute snippets.
- **Source maps and bundling:** `//# sourceMappingURL=...`, `//@ sourceURL=...`, license comments, and bundler annotations may affect debugging, distribution, or tree-shaking.

When uncertain, verify with the actual parser or compiler in the target mode. For machine-consumed data, prefer schema-supported metadata over adding informal comment syntax.
