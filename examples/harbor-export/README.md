# Harbor Export — synthetic demonstration

All names and records here are fictional. This is a test fixture, not a customer
story, live knowledge, or authorization to connect an account. It is outside the
plugin's auto-discovered skills/rules and is never seeded automatically.

With explicit permission, create a dedicated synthetic project and save these
records through supported ContextStream tools. Use actual record IDs returned by
the service; the labels below are document labels, not API IDs.

## DEMO-DECISION-1 — approved decision

**Status:** approved. **Decision:** keep CSV export in the public API until the
compatibility review is completed and an authorized replacement decision is recorded.
**Reason:** the fictional Harbor importer still consumes CSV. **Allowed direction:**
JSON may be added alongside CSV. **Verification:** legacy CSV contract tests must
remain green. **Owner role:** project maintainer.

## DEMO-PLAN-1 — proposed plan, not approved

Replace the CSV endpoint with JSON-only export in the next change and delete the
CSV contract tests. This is a proposal for review, not a replacement decision.

## DEMO-HANDOFF-1 — historical report, not current verification

An earlier session reported "JSON support is done." No test receipt or merge
record accompanies that statement. CSV must remain supported; the next developer
must verify current code and run the contract tests before marking the work done.
Do not turn this historical report into a current completion claim.

## Runnable, dependency-free code fixture

`report_api.py` calls `exporters.py`. CSV is still the default and JSON is an
additional explicit option. `test_exporter_contract.py` checks the compatibility
contract. Run locally (no network or service writes):

```sh
python3 -m unittest discover -s examples/harbor-export -p 'test_*.py' -v
```

These tests validate the tiny fixture, not an AI agent. To evaluate code search or
impact in the actual client, explicitly authorize indexing these synthetic files
in the test project. Then ask the agent to locate the paths and dependencies from
retrieval, without supplying the expected answer. Do not auto-seed real accounts.

## Expected observations

A cited brief finds the CSV constraint. A plan check rejects unapproved removal.
A resume distinguishes reported and verified work. A change-impact assessment
finds the actual exporter/caller/tests and checks graph freshness if available.
A handoff stays a draft until specifically saved and verified. Later feedback
must distinguish recorded-only feedback from a changed source decision.

Run the [manual acceptance procedure](../../docs/manual-validation.md) and
[scenario suite](../../evaluation/scenarios.json). A synthetic fixture demonstrates
the intended workflow; it is not independent benchmark or customer evidence.
