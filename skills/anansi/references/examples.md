# Anansi examples

Examples illustrate choices, not a comment quota. Add a comment only when it gives the next reader context that the code does not already make obvious. Every claim must remain true of the code at hand.

## Robotic → useful

**Narrates visible syntax:**

```js
// Clear the timer.
clearTimeout(timer);
```

Usually omit it. If the reset behavior matters to a reader, explain the consequence:

```js
// Every new call resets the clock; `fn` fires only after things go quiet.
clearTimeout(timer);
```

Do not add the second comment unless the surrounding debounce implementation supports that behavior.

## Humor dials: alternatives, not a stack

Assume a debounce wrapper clears its pending timer and schedules `fn` after a quiet interval:

| Dial | Example | When to use |
|---|---|---|
| Serious | `// Reset the timer so fn runs after a quiet interval.` | Default for formal or high-stakes code; no humor. |
| Dry | `// Each call restarts the quiet period; the timer gets no uninterrupted time.` | Restrained, code-related wit where it fits. |
| Playful | `// New call, fresh countdown; the timer keeps getting bumped.` | Only when the project's tone supports it. |
| Chaos | `// The timer was nearly done; another call sent it back to the start.` | A higher-energy option, still accurate and useful. |

These are alternatives. The dial sets an upper bound, not a target. A comment must still convey useful information when the joke is removed.

## No-joke zones

Keep high-consequence comments literal and specific. Do not joke about security, money, medical logic, safety, irreversible operations, legal/compliance work, production incidents, or tool-consumed documentation.

```python
# Quantize to cents using the active Decimal context's rounding mode.
amount = amount.quantize(Decimal("0.01"))
```

Do not claim this rounds half-up unless the active context guarantees that mode. In particular, the supplied Cart example uses Decimal and monetary-looking values, so its added comments are intentionally serious.

```sql
-- Delete only rows whose migration status has been verified.
DELETE FROM legacy_records WHERE migration_status = 'verified';
```

Do not imply the earlier copy was correct, or that rollback is available, unless that is independently established.

## Supplied code examples

The user-provided snippets are included as matched source pairs; compare files with the same name:

- [`examples/before/python_cart.py`](../examples/before/python_cart.py) and [`examples/after/python_cart.py`](../examples/after/python_cart.py) — the supplied `Item`/`Cart` Decimal example, with serious comments on SKU merging and discount/quantization behavior.
- [`examples/before/retry.js`](../examples/before/retry.js) and [`examples/after/retry.js`](../examples/after/retry.js) — the supplied debounce and promise-based retry functions, including the user's comments about `this`, total attempts, the final error, and linear delay.

The other four same-named before/after pairs demonstrate Go, Rust, SQL, and Bash. Their `after` versions should differ only by comments (and preserve any required shebang). The audit script and unit tests verify supported pairs.
