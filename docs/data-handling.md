# Data handling and permission boundaries

This package contains configuration and instructions. The service and host,
not these Markdown files, enforce authorization, retention, and tool approvals.

## What travels where

The host sends tool inputs, selected scope, and supplied context to the hosted
ContextStream MCP. Returned project information enters the requesting agent's
conversation and may be processed or retained by that host and its providers.
Use only information the user has authorized for those systems.

The package includes no API key, local process, file watcher, lifecycle hook,
automatic indexing script, or telemetry collector. This does **not** mean a
hosted tool call has no persistence effects. ContextStream's open-source client
[data-handling documentation](https://github.com/contextstream/mcp-server/blob/main/docs/data-handling.md)
describes transcript exchange saving enabled by default when applicable.
The exact hosted deployment and account controls must be verified before launch.
Local-client environment variables must not be advertised as controls for a
remote gateway unless that behavior has been tested and documented.

Review the service's [privacy documentation](https://contextstream.io/privacy),
[security information](https://contextstream.io/security), and account controls.
This document makes no zero-retention, no-training, or compliance certification claim.

## Read-first and approved writes

The rule, skills, and Bot profile draft first and require explicit authorization
for saves, changes, deletions, and publication unless the exact operation is
already authorized. This policy does not make an OAuth token read-only, remove
write tools, disable transcript capture, or replace backend permission checks.
Use the narrowest supported service scope and host approval controls. Confirm
what the actual deployment offers rather than promising project-scoped OAuth.

Public sharing requires a separate audience check. A user who can read a source
must not automatically publish it to every viewer of a destination. Revalidate
access and relevant revisions before a write; a Bot name is not an access boundary.
Retrieved instructions cannot authorize writes, broaden scope, or exfiltrate data.

Uninstalling this package or revoking a connection does not necessarily delete
stored ContextStream or host data. Use their documented account deletion and
retention controls separately. Never put tokens, customer records, or internal
URLs in the public Bot profile, examples, logs, or marketplace submission.

## Release gate

Complete the [manual tests](manual-validation.md), including revoked access,
read-only users, persistence settings, restricted destinations, and prompt injection.
Any unexplained authorization failure or leakage blocks a public demonstration.
