# Metadata-only protocol probe

`scripts/probe_mcp.py` makes no requests unless `--network` is supplied. It posts
only `initialize`, `notifications/initialized`, and paginated `tools/list` to the
fixed `https://mcp.contextstream.io/mcp` endpoint. It never executes a project tool,
reads project content, seeds data, writes memory, publishes, or buys usage.

```sh
python3 scripts/probe_mcp.py --network
```

An unauthenticated denial is expected when the deployment requires a credential.
For an operator-owned test credential obtained through a supported flow, set
`CONTEXTSTREAM_MCP_TOKEN` privately in the process environment. The script does
not implement browser OAuth, refresh credentials, read a client credential store,
or accept a token on the command line. Never paste tokens into chat, shell
history, screenshots, reports, or this repository. Do not repurpose a credential
issued for a different resource or bypass an organization's approval controls.

The probe refuses redirects and environment-provided proxies, bounds response
bytes/time/tool counts/pagination, parses JSON or SSE responses, negotiates its
supported Streamable HTTP protocol versions, and propagates session/version
headers privately. It makes no automatic retries. Enterprise proxies, legacy
HTTP+SSE, and newer unrecognized protocol versions require an explicit review;
a diagnostic limitation must not be called a product failure.

Output contains only fixed feature flags/counts and protocol metadata, never raw
response bodies, schemas, tokens, or session identifiers. `credential_supplied`
means only that a credential was provided, not that its grants were validated.
`protocol_ok` does not mean actual project retrieval succeeded. An access gate
can still occur when calling a tool. Verify in the real client using the
[manual tests](manual-validation.md) and [evaluation gate](evaluation.md).

The diagnostic intentionally does not issue session DELETE or client shutdown
mutations; a short-lived server session may remain until its normal expiry.
Network requests can still appear in ordinary service access logs.

Protocol references: [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports),
[lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle),
and [tool listing](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).
No full protocol-conformance claim is made.
