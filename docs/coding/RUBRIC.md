# Coding rubric — independent human raters

**Read this before opening any coding sheet.** Two people code independently. You must not
discuss items, compare intermediate answers, or look at the other rater's file until both
sheets are complete. The whole point is that the agreement statistic means something.

This package exists because three quantities in the study are **judgement calls**, not
computations. An automated heuristic can propose a label, but only a human can certify one,
and a language model cannot stand in for a human rater: an "agreement" statistic computed by
one model against itself is not inter-rater reliability, it is a self-consistency check
wearing a reliability statistic's clothing. So the study ships the sheets, the rubric, and the
κ script, and reports **no κ** until two humans have actually coded.

If you are the only rater available, code the sheets twice, at least 48 hours apart, without
looking at your first pass, and report the result as **intra-rater** agreement, clearly
labelled as such. Do not describe it as inter-rater.

---

## Task 1 — Is this mutant relevant to a business rule?

File: `coding/mutants_to_code.csv`

For each row you see a mutated class and method, the source line, and the mutation that was
applied. Decide:

| Label | Meaning |
|---|---|
| `yes` | The mutated behaviour is part of a **business rule**: pricing, eligibility, entitlement, policy, calculation, decision logic that a domain expert would recognise and could state in a requirements document. |
| `no` | The mutated behaviour is **plumbing**: serialisation, logging, framework glue, data transfer, formatting, iteration mechanics, configuration lookup. |

Rules of thumb, applied in order:

1. **Would a domain expert care?** If the mutation changed the price a customer pays, the
   answer is `yes`. If it changed how a message is logged, the answer is `no`.
2. **Ignore the test outcome.** You are coding the *mutant's location and behaviour*, not
   whether the suite killed it. A `yes` mutant that survived is the interesting case; do not
   let its status influence the label (the status is not shown to you anyway).
3. **Boundary counts.** Changing `>` to `>=` on a discount threshold is `yes`: it changes who
   gets the discount.
4. **When genuinely torn**, choose `yes` only if you could write the business rule in one
   sentence without referring to code. Otherwise `no`. Record the doubt in the `notes`
   column rather than agonising.

## Task 2 — Classify the step definition (D2)

File: `coding/stepdefs_to_code.csv`

For each row you see one step definition's body. Assign exactly one class:

| Label | Meaning |
|---|---|
| `STRONG_DIRECT` | Contains an assertion about the outcome, and the assertion could fail if the behaviour changed. |
| `STRONG_DELEGATED` | Contains no assertion itself, but calls another method in the same repository, at depth ≤ 2, that does. |
| `WEAK` | Contains an assertion **and** matches one of the weakening patterns below. |
| `NONE` | Neither asserts nor delegates to something that asserts. |

Weakening patterns:

- **W1 tautology** — both operands are textually identical (`assert x == x`).
- **W2 constant truth** — compares literals to literals (`assertTrue(true)`), or asserts a
  literal is not null.
- **W3 unreachable** — the assertion sits after an unconditional `return`/`throw`, or inside a
  branch whose condition is a literal.
- **W4 swallowed failure** — the enclosing `try` has a `catch` that neither rethrows nor fails.
- **W5 self-comparison** — a value compared to itself.

If the body is truncated in the sheet, say so in `notes` and code what you can see.

## Task 3 — Is this a mirror step? (D7)

Same file, second column.

A **mirror step** re-derives the *expected* value by repeating the production computation, so
that its oracle moves with the mutant. It is `yes` only if **all three** hold:

1. the asserted expected value is **computed**, not a literal;
2. that computation **references a domain-layer call** in the same body;
3. the **actual** value also comes from a domain-layer call.

A step that hard-codes `1700.00` is not a mirror. A step that computes
`expected = PriceCalculator.finalPrice(...)` and asserts it against
`pricing.finalPrice(...)` **is** a mirror, because both sides move together when the
calculation changes.

This is the hardest of the three tasks. If you cannot see the body, code `unclear` rather than
guessing; `unclear` is excluded from κ and its count is reported.

---

## Sheet mechanics

- Each sheet has an `item_id` column. **Do not edit it.** Join on it.
- Fill only the label column (`business_rule_relevant` / `stepdef_class` / `mirror`) and
  optionally `notes`.
- Use lowercase `yes`/`no`; use exactly the class labels above, in capitals.
- Leave a cell blank only if you genuinely cannot code the item; blank is treated as missing,
  not as `no`.

## What happens to your sheet

```powershell
python scripts/compute_irr.py `
  --a coding/mutants_to_code.completed.<raterA>.csv `
  --b coding/mutants_to_code.completed.<raterB>.csv `
  --label-column business_rule_relevant
```

The script reports Cohen's κ with a bootstrap 95 % confidence interval, the observed
agreement, and the marginal distributions. It refuses to compute if the two files disagree on
`item_id` coverage, because κ on mismatched item sets is meaningless.

Interpretation thresholds, declared in advance so they cannot be chosen after seeing the
number: κ < 0.41 substantial disagreement (the indicator is not yet a measurement);
0.41–0.60 moderate; 0.61–0.80 substantial; > 0.80 almost perfect. The protocol commits to
demoting any indicator whose κ falls below 0.61 to "exploratory, reliability-unconfirmed".
