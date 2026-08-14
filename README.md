<div align="center">
  <img src="https://contextstream.io/logo-hex.png" alt="ContextStream" width="120" />

  # ContextStream for Cursor

  **Stop starting AI agents cold.**

  Persistent project memory, semantic code search, and grounded context for Cursor — decisions, lessons, runbooks, and prior sessions surfaced automatically, before your agent touches the repo.

  [Website](https://contextstream.io) · [Docs](https://contextstream.io/docs/mcp) · [Pricing](https://contextstream.io/pricing)
</div>

---

## Marketplace install

This plugin connects Cursor to the hosted ContextStream MCP at `https://mcp.contextstream.io/mcp`. Sign in with OAuth when Cursor prompts you. No local binary and no API key in config.

After it is listed on the [Cursor Marketplace](https://cursor.com/marketplace), install **ContextStream** from Customize → Plugins.

Until then, add the repo as a local plugin or point Cursor at the hosted endpoint:

```json
{
  "mcpServers": {
    "contextstream": {
      "url": "https://mcp.contextstream.io/mcp"
    }
  }
}
```

Create an account at [contextstream.io](https://contextstream.io) if you do not have one.

## What you get

Every new Cursor session starts with what your team already learned. ContextStream turns repo decisions, guardrails, prior fixes, runbooks, and agent corrections into shared project memory.

- **Smart context on every turn** — one `context` call returns task-relevant rules, prior decisions, and lessons, pre-ranked for the current message.
- **Semantic + keyword code search** — ranked, indexed answers with file paths and line numbers.
- **Memory across sessions** — decisions, lessons, docs, plans, tasks, and transcripts are captured and recalled when relevant.
- **Code graph** — blast radius, cycles, unused code, complexity trends.
- **Team knowledge** — shared workspace memory plus GitHub, Slack, Notion, Linear, Jira, and Figma integrations.

The plugin also ships an always-on rule (`rules/contextstream.mdc`) so the agent uses ContextStream first, not last.

## Optional: native binary

The hosted endpoint covers the core tool surface. The native Rust binary adds a setup wizard, local index watcher, Cursor agent hooks, and rules generation. It is a separate install, not what this marketplace plugin ships:

```bash
curl -fsSL https://contextstream.io/scripts/mcp.sh | bash
contextstream-mcp setup
```

## Tools

`init` · `context` · `search` · `session` · `memory` · `graph` · `project` · `workspace` · `vcs` · `integration` · `media` · `skill` · `entity` · `qa`

## Links

- Homepage: https://contextstream.io
- Docs (Cursor): https://contextstream.io/docs/mcp#cursor-vscode
- Support: support@contextstream.io

## License

This plugin packaging is MIT licensed. The ContextStream service is a commercial product — see [pricing](https://contextstream.io/pricing).
