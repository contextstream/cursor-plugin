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

## Expected observations

A project brief should mention the CSV constraint and cite the actual stored
source. A decision check should flag the proposed removal as a conflict and
suggest keeping CSV while adding JSON, or requesting an authorized replacement
decision. It must not claim the proposal has already been approved or implemented.
A handoff should remain a draft until the specific save is authorized.

Run the [manual acceptance procedure](../../docs/manual-validation.md).
A synthetic fixture demonstrates the intended workflow; it does not establish
production reliability or independent benchmark performance.
