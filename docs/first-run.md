# First-run experience: one project, one useful answer

Target: a user should reach a cited, relevant project answer without learning
seven feature names. This is a UX target, not a measured setup-time claim.

1. Connect through the host's supported plugin/OAuth flow and acknowledge the
   hosted data handling once. Never ask for an API token in chat.
2. Reuse an existing verified project binding. Otherwise ask which project the
   user intends and show only minimal authorized selection information.
3. Check available knowledge only as needed. Distinguish connected, indexing,
   empty, stale/partial, denied, and ready; a tools/list pass is not project readiness.
4. Answer one real question using evidence. Offer the single next useful action,
   such as checking a proposed change or preparing a handoff. Do not run every skill.

## Empty and failure states

| State | Useful response | Do not do |
| --- | --- | --- |
| No connection | Explain the supported browser sign-in step | Request a secret in chat |
| Wrong/ambiguous project | Ask one precise selection question | Silently choose the first project |
| Empty project | Offer one source connection or the synthetic demo | Pretend there are decisions or auto-import files |
| Index building/stale | State observed coverage and what can be answered | Declare complete code coverage |
| Missing graph | Give a qualified search-based result | Fabricate a dependency graph |
| Revoked permission | Stop that scope and explain reauthorization | Reuse cached restricted content |
| Budget exhausted | Report the limit and preserve a private draft | Buy credits or retry endlessly |
| No skill loader | Explain MCP-only vs skill install | Claim all workflows are installed |

## Progressive detail

Default to a short useful answer with sources; expand for requested depth or a
consequential contradiction. Role-specific briefs change interpretation, not the
underlying facts. Multiple projects require an explicit request and per-source
attribution. Never convert a useful first session into a surprise shared write.

Use [the demo](../examples/harbor-export/README.md) for a reproducible starting
point, not as proof of a live customer outcome.
