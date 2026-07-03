# medusa-skill
MEDUSA Security Skill — drop one file, get a senior security engineer. 100+ vulnerability classes across 12 detection layers for any AI coding agent.

<div align="center">

```
███╗   ███╗███████╗██████╗ ██╗   ██╗███████╗ █████╗
████╗ ████║██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
██╔████╔██║█████╗  ██║  ██║██║   ██║███████╗███████║
██║╚██╔╝██║██╔══╝  ██║  ██║██║   ██║╚════██║██╔══██║
██║ ╚═╝ ██║███████╗██████╔╝╚██████╔╝███████║██║  ██║
╚═╝     ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
```

**Security Skill for AI Coding Agents**

*Drop one file. Get a senior security engineer.*

</div>

---

## What This Is

`SKILL.md` is a portable security intelligence skill that any AI coding agent can read and execute. When an agent loads this file, it operates as MEDUSA — a paranoid, exhaustive security analysis engine that finds vulnerabilities, assigns financial breach cost estimates, and generates diff-ready fixes.

It works with Claude Code, GitHub Copilot Workspace, Codex, Antigravity, Cursor, and any other agent that accepts skill files or system context.

**One file. No install. No API. No account.**

---

## What It Finds

MEDUSA scans across 12 detection layers covering 100+ vulnerability classes:

|Layer|Engine|Coverage|
|-|-|-|
|1. Secret \& Credential Exposure|GAZE|Hardcoded keys, tokens, passwords, high-entropy strings, 15+ provider patterns|
|2. Injection Vulnerabilities|GAZE|SQL, command, path traversal, NoSQL, GraphQL, header injection, XXE, SSTI|
|3. Authentication \& Session|GAZE|JWT attacks, session fixation, timing attacks, password hashing, OAuth flaws|
|4. Authorization \& Access Control|GAZE|IDOR/BOLA, mass assignment, privilege escalation, missing function-level auth|
|5. Input Validation \& Output Encoding|GAZE|XSS (stored/reflected/DOM), unvalidated redirects, file upload bypasses|
|6. Cryptography \& Data Protection|GAZE|Weak algorithms, insecure IV, bad randomness, transport security, PII at rest|
|7. API Security|GAZE|Rate limiting gaps, CORS, CSRF, security headers, over-fetching|
|8. Micro-Vulnerabilities \& Logic Bugs|GAZE|Race conditions, float money, null safety, resource leaks, business logic flaws|
|9. Dependency \& Supply Chain|GAZE|CVEs, unpinned versions, abandoned packages, malicious postinstall scripts|
|10. AI \& LLM Security|GAZE|Prompt injection, RAG leakage, agent escalation, cost exhaustion attacks|
|11. Infrastructure as Code|HYDRA|Docker, GitHub Actions, Terraform, Kubernetes, environment configs|
|12. Runtime \& Operational Security|GAZE|Webhook validation, presigned URL expiry, observability exposure|

---

## How to Use It

### Option 1 — Drop it in your repo

```bash
curl -o SKILL.md https://raw.githubusercontent.com/medusa-security/medusa-skill/main/SKILL.md
```

Then tell your agent:

```
Read SKILL.md and audit this codebase for security vulnerabilities.
```

### Option 2 — Reference it directly in your agent prompt

```
Read https://raw.githubusercontent.com/medusa-security/medusa-skill/main/SKILL.md
then audit \[file or directory] for security vulnerabilities.
```

### Option 3 — Add it to your Claude Code project config

In your `.claude/` project config or system prompt:

```
Always read SKILL.md before performing any security review, audit, or code hardening task.
```

### Option 4 — Use it as a system prompt for any LLM

Paste the contents of `SKILL.md` as the system prompt for any LLM and ask it to audit your code. The skill is self-contained and requires no external tools.

---

## What the Output Looks Like

Every invocation produces a structured MEDUSA Security Report:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEDUSA SECURITY REPORT v2.0
Powered by Daimon Technologies
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MEDUSA SCORE:         61
TOTAL FINDINGS:       7
  ● CRITICAL:         1
  ● HIGH:             2
  ● MEDIUM:           3
  ● LOW:              1
  ● INFO:             0

ESTIMATED BREACH EXPOSURE: $84,000 – $210,000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\[GAZE-001] ● CRITICAL
Type:              Secret Exposure — Hardcoded Database Credential
CWE:               CWE-798 (Use of Hard-coded Credentials)
File:              config.js:2
Engine:            GAZE-SECRETS
Breach Exposure:   $150,000 – $4,400,000

Vulnerable Code:
  const DB\_URL = "postgresql://admin:hunter2@prod.db.internal/users"

Why This Is Exploitable:
  Any developer with repo access — or any attacker who gains read access
  to version control history — has permanent production database credentials.

Attack Scenario:
  Attacker finds the credential in a public GitHub commit, connects directly
  to the production database, and exfiltrates or destroys all user data.
  Credential cannot be invalidated without breaking the application.

Fix:
  const DB\_URL = process.env.DB\_URL;
  if (!DB\_URL) {
    throw new Error("DB\_URL environment variable is required");
  }

Remediation Note:
  - Rotate the database password immediately — treat it as compromised
  - Add .env to .gitignore
  - Audit git history: git log -S "hunter2" to find all commits containing it
  - Consider using git-filter-repo to purge from history

─────────────────────────────────────────────────────────

... (remaining findings)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STONEGAZE REMEDIATION PRIORITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. \[GAZE-001] — Rotate DB credential + env var fix (+20 pts)
2. \[GAZE-003] — Add ownership check to /users/:id endpoint (+10 pts)
3. \[GAZE-005] — Parameterize search query (+10 pts)
4. \[GAZE-002] — Add rate limiting to /auth/login (+4 pts)
5. \[GAZE-006] — Add security headers middleware (+4 pts)
6. \[GAZE-007] — Switch float to Decimal in payment calc (+4 pts)
7. \[GAZE-004] — Pin lodash to non-vulnerable version (+1 pt)

POST-FIX PROJECTED SCORE: 100
PROJECTED EXPOSURE AFTER FIX: $0 – $0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## The MEDUSA Score

Every report produces a MEDUSA Score from 0 to 100 calculated by the ORACLE engine:

|Score|Meaning|
|-|-|
|90–100|Clean or near-clean. Ship with confidence.|
|75–89|Low risk. Minor issues to address.|
|50–74|Moderate risk. Real vulnerabilities present.|
|25–49|High risk. Critical issues need immediate attention.|
|0–24|Severe. Do not ship. Multiple critical vulnerabilities.|

Score deductions: Critical −20, High −10, Medium −4, Low −1.

---

## Supported Languages

The skill detects vulnerabilities across all major languages. Secure fix patterns are provided for:

* **Python** — FastAPI, Django, Flask, SQLAlchemy, Celery, asyncio
* **JavaScript / TypeScript** — Node.js, Express, Next.js, React, Fastify
* **Go** — net/http, Gin, Echo, GORM
* **Java** — Spring Boot, Hibernate, JDBC
* **Ruby** — Rails, Sinatra, ActiveRecord
* **PHP** — Laravel, WordPress, raw PDO
* **Rust** — Actix, Axum, SQLx
* **C# / .NET** — ASP.NET Core, Entity Framework
* **Shell / Bash** — Script security, secret exposure in CI

Infrastructure configs:

* Dockerfile / docker-compose
* GitHub Actions / GitLab CI / CircleCI / Jenkins
* Terraform / CloudFormation / Pulumi / CDK
* Kubernetes manifests
* Vercel / Railway / Netlify / Render configs

---

## Design Principles

**Paranoid by default.** The skill assumes the worst about every piece of code it reads. An unvalidated input is a potential injection. A missing check is a potential bypass. Impact is assessed from an attacker's perspective, not a developer's optimism.

**No finding without a fix.** Every vulnerability in the report comes with a complete, copy-pasteable code fix. Not a description of what to fix. The actual fixed code.

**Financial framing.** Every finding includes an estimated breach cost in USD sourced from IBM Cost of a Data Breach Report 2024. This is the number that gets security issues prioritized in sprint planning.

**Micro-vulnerability coverage.** The skill is explicitly designed to catch the small bugs that accumulate into catastrophic failures — float arithmetic used for money, bare except clauses, missing null checks, race conditions in async code. These are the findings most security tools miss.

**No false confidence.** If a layer is not applicable (e.g., no infrastructure files present), it is explicitly noted as skipped. The report never claims a clean result for a layer it did not check.

---

## Contributing

Contributions to the skill are welcome. If you find a vulnerability class not covered, open a PR adding it to the relevant layer with:

* Detection pattern or heuristic
* Example vulnerable code
* CWE reference
* Severity classification with justification
* Secure fix pattern

---

## License

MIT. Use it, fork it, embed it in your agent, include it in your product.

Attribution appreciated: *Powered by MEDUSA*

---

<div align="center">

Built by Medusa

*Your code. Your cloud. Zero exposure.*

</div>

