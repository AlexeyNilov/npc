# Semantic discovery with the System One API

`jira-ids` demonstrates a useful middle ground between rigid parsing and free-form
LLM extraction. Deterministic code finds values that *might* be identifiers, while
System One uses the surrounding Jira text to decide what each value means.

## The approach

The pipeline has three stages:

1. **Generate candidates cheaply.** A regular expression finds UUIDs, long
   numbers, hexadecimal values, phone-like values, and other identifier-shaped
   strings. This deliberately favors recall: it is acceptable to include values
   that are not useful IDs.
2. **Ask semantic questions in one batch.** The complete issue text is sent as
   `state`. For every candidate, the client creates one `noul` (probability of
   true) question per supported type, such as “Is `12345678` a request ID?” and
   “Is `12345678` an account ID?”. All questions go in a single System One
   request, so the model can interpret labels and prose around the candidate
   without having to generate or parse text.
3. **Apply policy in ordinary code.** The client validates every returned
   probability, chooses the highest-scoring type for each candidate, rejects
   scores below `0.75`, and keeps only the strongest candidate for each type.
   Ties retain the first occurrence, making the result stable.

Conceptually, a request looks like this:

```json
{
  "state": "Request 12345678 failed for account 87654321",
  "questions": {
    "candidate_0_request_id": {
      "type": "noul",
      "instructions": "Is 12345678 a request ID?"
    },
    "candidate_0_account_id": {
      "type": "noul",
      "instructions": "Is 12345678 an account ID?"
    }
  }
}
```

The stable question IDs connect each answer back to a candidate and type. The
model returns probabilities under `answers`; it does not need to follow a custom
output schema or reproduce the identifier correctly.

## Why split the work this way?

Regex alone recognizes shapes but cannot reliably distinguish an account ID from
a request ID. Free-form extraction can make that distinction, but it also asks
the model to locate values, copy them exactly, invent a schema, and obey selection
rules. This design gives each part the job it handles best:

- deterministic code owns exact text extraction, validation, thresholds,
  tie-breaking, and output shape;
- the decision model owns only the contextual judgment that is difficult to
  encode as rules.

The result is easier to test and audit. Tests can assert the exact questions sent
to the model and feed controlled probabilities into the deterministic selection
logic. Exact requests are also cached, so repeated analysis avoids another model
call.

## References

See [`jira_ids.py`](../src/ai_assisted_troubleshooting/cli/jira_ids.py) for the
CLI flow, [`id_decision.py`](../src/ai_assisted_troubleshooting/id_decision.py)
for question construction and selection, and the pinned
[System One API reference](system-one-api.md) for the request and response types.
