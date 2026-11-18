# Humor playbook for code comments

Comments exist to help a future reader understand code. Humor is optional seasoning, never the reason a comment exists. A joke should carry accurate information about behavior, constraints, trade-offs, or a useful failure mode; if removing the joke removes the only useful content, rewrite it. **Comment density is not a quota:** no dial requires adding comments, and a file that needs no comment should get none.

## The four dials

Use the requested dial as an upper bound on how many otherwise-useful *new* comments get a light humorous turn. The fractions are approximate selection guidance, not a demand to manufacture comments. Count only comments that would still be worth keeping in a neutral voice; comments that merely narrate syntax are not eligible.

| Dial | Humorous share of eligible new comments | Per-function cap | Per-file cap | Voice |
|---|---:|---:|---:|---|
| **Serious** | 0 | 0 | 0 | Direct, precise, neutral. |
| **Dry** | About 1/8 | 1 | 1 | Understated, restrained, brief. |
| **Playful** | About 1/4 | 2 | 2 | Light wit, still subordinate to explanation. |
| **Chaos** | About 1/2 | 2 | 3 | More surprising or energetic phrasing, while remaining truthful, readable, and professional. |

For a region with *N* eligible new comments, use `floor(N × dial share)`, then apply the per-function and per-file caps. **Round down**; at Dry only, if there are at least 3 eligible new comments, allow one humorous comment even though `floor(N/8)` would be zero. Serious always remains zero. The dry exception and all caps are ceilings, not targets. If the result is zero, write neutrally. When counting spans are ambiguous (e.g. nested/local functions), choose the stricter cap.

Examples of the arithmetic: Dry with 1–2 eligible comments yields 0; with 3–7 it can allow 1, but never more than 1 in a function or file. Playful with 3 eligible comments yields 0, with 4 yields at most 1, and with 8 yields at most 2 before caps. Chaos with 3 yields 1, with 6 yields 3 before the file cap of 3. A comment may be funny without being counted only if the humor is incidental; do not evade the cap by relabeling jokes.

## Quality bar: humor that still does work

Prefer jokes that are attached to a concrete fact: a boundary, a non-obvious invariant, a deliberately deferred action, a compatibility constraint, or an error path. A future reader should be able to learn something actionable even when they do not find the line funny.

- Keep it short enough that the explanation is still the first thing a skimmer sees.
- Punch up at complexity, constraints, or the code's behavior—not at users, coworkers, protected groups, or someone who will maintain it.
- Make the statement testable against the code. Avoid anthropomorphism that implies guarantees the implementation does not make.
- Use a joke only where the behavior is stable enough that the joke will not become a misleading fossil.
- Remove it if it obscures a security, data-loss, privacy, concurrency, or failure warning.
- Do not turn comments into a conversation with the reader or author; avoid “obviously,” “just,” “simply,” and blame.

Good pattern: `// No retry after the final attempt; we have already spent the whole allowance.` The plain fact (no final sleep/retry) survives the light turn.

Weak pattern: `// Magic happens here.` It describes nothing. Better: state which value is derived and from what inputs.

Weak pattern: `// This will never fail.` Unless the implementation and its contract prove that claim, it is false confidence rather than humor.

## Three-zone kill list

These are stop signs. Do not add humor in any zone; keep comments factual, and add them only when needed.

1. **Safety, security, and trust boundaries:** authentication/authorization, cryptography, secrets, input validation, sandboxing, permissions, serialization of untrusted data, injection defenses, privacy, audit trails, and incident response. A joke can make a guardrail appear optional or trivial.
2. **Failure, correctness, and irreversible effects:** financial calculations, billing/payments, data deletion/migration, persistence, backups, transaction boundaries, reliability-critical retries/timeouts, concurrency/race handling, resource cleanup, error recovery, and user-visible guarantees. Keep caveats literal and unambiguous. A low-stakes illustrative retry helper is not automatically high-consequence; judge the actual use and audience.
3. **Human-sensitive or high-stakes outcomes:** medical, legal, accessibility, safety-critical control, moderation/abuse, employment, identity, and other decisions affecting a person's rights or wellbeing. Neutral, respectful language only.

A zone can apply to a single line inside an otherwise playful file. Use the local behavior—not the file's overall tone—to decide. A comment that documents a safety invariant should never be made cute merely to meet a dial.

## No-joke zones (even outside the three zones)

Keep comments serious around public API contracts and compatibility promises; privacy or telemetry behavior; performance limits that protect availability; race conditions and ordering guarantees; fallback behavior; feature flags/rollouts; data formats and units; legal/compliance requirements; tests describing a known regression; TODOs tied to ownership or deadlines; generated code; and comments that may be surfaced directly to customers. Humor is also a poor fit when the code is already hard to parse, when readers are under incident pressure, or when international teams may misread idiom.

## Light joke seeds (adapt only when accurate)

These are prompts, not canned comments. Replace the generic wording with the actual invariant; omit if the punchline implies anything untrue.

- A timer reset: “Each call restarts the clock; the quiet period begins again.”
- A boundary check: “The upper bound is exclusive, so the endpoint stays outside.”
- A linear backoff: “The wait grows one step at a time, not exponentially.”
- A deduplication key: “Rows with the same key share one slot; unrelated keys keep theirs.”
- A cached value: “This cache is only as fresh as its invalidation path.” (Usually keep this one serious; stale data can be consequential.)
- A deliberate final-attempt behavior: “The last failure gets reported; there is no extra nap after it.” (Avoid humor in reliability-critical retry logic.)
- A parser workaround: “This branch exists for the older parser, not for decoration.” (Only if compatibility is verified.)

Seeds are never license to add a comment where code is already clear. Do not introduce false certainty, invent an invariant, or attach a joke to an implementation detail you have not checked.

## Review checklist

Before shipping a humorous comment, ask: Is this comment independently useful? Is every factual claim true for edge cases? Does it obey the dial budget and per-function/file caps? Is this outside a kill/no-joke zone? Could a rushed reader mistake the joke for a guarantee? Would the comment still be useful in a neutral voice? If any answer raises doubt, make it neutral or delete it.
