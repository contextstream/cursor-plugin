# Capability map and provenance

Source review: 2026-09-09, public MCP commit
`f1236e7b6c65e4babc2276f7ec6e85d8c936096f`.
This is source evidence, NOT confirmation that the hosted deployment exposes
all capabilities to this account or that Grok uses them successfully. Discover
actual tool schemas and use their parameter names and enum values at runtime.

| Workflow | Source-reviewed foundation | Important boundary |
| --- | --- | --- |
| Readiness | help auth/version/tools, selected-project state | Tool presence and connection are not content readiness |
| Audience briefs | answer query/recent_changes, context, search | Logical scope never grants access; state observed freshness |
| Decision checks | context, recalled decisions, original sources | Newer proposal does not supersede approval |
| Resume | session recall, task/decision refresh | Old "done" does not prove merged or currently verified |
| Change impact | indexed search and graph dependencies/impact/related | Graph missing/stale must be disclosed |
| Handoff | existing memory/session saves and receipts/read-back | Only the authorized artifact; no implicit publication |
| Memory review | graph contradictions, answer receipt/feedback | recorded_only is not a changed decision or proven propagation |

## Reviewed source

- [Registry](https://github.com/contextstream/mcp-server/blob/f1236e7b6c65e4babc2276f7ec6e85d8c936096f/crates/mcp-tools/src/registry.rs): grouped tool surfaces and access-gate handling.
- [Answer API surface](https://github.com/contextstream/mcp-server/blob/f1236e7b6c65e4babc2276f7ec6e85d8c936096f/crates/mcp-tools/src/domains/answer.rs): actions `query`, `recent_changes`,
  `receipt`, `feedback`; explicit logical scope and bounded responses. Query
  requests are sent once, not transparently replayed. Avoid reflexive retries.
- [Session and grounding](https://github.com/contextstream/mcp-server/blob/f1236e7b6c65e4babc2276f7ec6e85d8c936096f/crates/mcp-tools/src/domains/session.rs): init, context, capture,
  recall; hosted scope differs from local filesystem scope.
- [Graph](https://github.com/contextstream/mcp-server/blob/f1236e7b6c65e4babc2276f7ec6e85d8c936096f/crates/mcp-tools/src/domains/graph.rs): dependencies, impact, related, freshness,
  and contradictions. Use actual schemas rather than invented action names.
- [Help](https://github.com/contextstream/mcp-server/blob/f1236e7b6c65e4babc2276f7ec6e85d8c936096f/crates/mcp-tools/src/domains/help.rs): supported auth/tools/version reads. Do not use
  billing as a pretext for changing a subscription; this plugin never purchases.

## Feedback, not magical learning

Receipt-bound feedback signals include relevance, wrong-project, and superseded
feedback when exposed by the actual tool. Use identifiers from a real receipt,
not values invented from a title. A recorded-only acknowledgement reports exactly
that. Changing a durable decision or universal rule requires separate explicit
authority and verified effects. Never advertise instant account-wide learning.

## No unnecessary execution layer

This package retains the existing hosted endpoint and client format. It adds
skill instructions and diagnostics, not a competing MCP proxy, scheduler,
backend database, or new credential store. New clients still need live acceptance.
