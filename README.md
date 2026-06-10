<div align="center">
  <img src="https://contextstream.io/400logo.png" alt="ContextStream" width="120" />

  # ContextStream for Cursor

  **Stop starting AI agents cold.**

  Persistent project memory, semantic code search, and grounded context for Cursor — decisions, lessons, runbooks, and prior sessions surfaced automatically, before your agent touches the repo.

  [Website](https://contextstream.io) · [Docs](https://contextstream.io/docs/mcp) · [Pricing](https://contextstream.io/pricing)
</div>

---

## What changes when you install this

Every new Cursor session starts with everything your team already learned. ContextStream turns repo decisions, guardrails, prior fixes, runbooks, and agent corrections into shared project memory your next AI coding session can use from the first message.

- **Smart context on every turn** — one `context` call returns task-relevant rules, prior decisions, and lessons from past mistakes, pre-ranked for the current message.
- **Semantic + keyword code search** — ask "where do we handle authentication?" and get ranked, indexed answers with file paths and line numbers. No grep chains, no reading ten files.
- **Memory that persists across sessions** — decisions, lessons, docs, plans, tasks, and full session transcripts are captured, indexed, and recalled when relevant.
- **Code graph intelligence** — dependency blast radius, circular dependencies, unused code, and complexity trends over your whole codebase.
- **Team knowledge fusion** — shared workspace memory, skills, and structured entities (tickets, incidents, releases, OKRs) across your whole team, plus integrations for GitHub, Slack, Notion, Linear, Jira, and Figma.

## Install

### Native binary (recommended)

The engine is a single Rust binary — no Node, npm, or npx required — with a built-in setup wizard, local index watcher, native Cursor agent hooks, rules generation, and self-update. None of that comes through a hosted URL, which is why this is the configuration we recommend:

```bash
# macOS / Linux
curl -fsSL https://contextstream.io/scripts/mcp.sh | bash
```

```powershell
# Windows
irm https://contextstream.io/scripts/mcp.ps1 | iex
```

Then run the wizard — it detects Cursor and writes the MCP config, rules, and hooks for you:

```bash
contextstream-mcp setup
```

Or configure manually in `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "contextstream": {
      "command": "contextstream-mcp",
      "args": [],
      "env": {
        "CONTEXTSTREAM_API_KEY": "${CONTEXTSTREAM_API_KEY}"
      }
    }
  }
}
```

Grab an API key at [contextstream.io](https://contextstream.io). Prebuilt binaries ship for macOS (Apple Silicon + Intel), Linux (x64 + arm64), and Windows.

### Zero-install option (hosted)

Prefer not to install anything? Point Cursor at the hosted streamable-HTTP endpoint and sign in via OAuth:

[![Add to Cursor](https://img.shields.io/badge/Add%20to-Cursor-blue?style=for-the-badge)](https://cursor.com/install-mcp?name=contextstream&config=eyJ0eXBlIjoiaHR0cCIsInVybCI6Imh0dHBzOi8vbWNwLmNvbnRleHRzdHJlYW0uaW8vbWNwP2RlZmF1bHRfY29udGV4dF9tb2RlPWZhc3QiLCJoZWFkZXJzIjp7IlgtU291cmNlLU5hbWUiOiJjdXJzb3ItcGx1Z2luIiwiWC1Tb3VyY2UtVmVyc2lvbiI6IjAuMi4wIn19)

```json
{
  "mcpServers": {
    "contextstream": {
      "type": "http",
      "url": "https://mcp.contextstream.io/mcp?default_context_mode=fast"
    }
  }
}
```

The hosted endpoint covers the core tool surface; native Cursor hooks, the setup wizard, local index watching, and rules generation require the binary.

## Tools your agent gets

`init` · `context` · `search` · `session` (lessons, recall, plans) · `memory` (docs, decisions, tasks, transcripts) · `graph` (code health) · `project` · `workspace` · `vcs` (GitHub/GitLab/Bitbucket) · `integration` (Slack, Notion, Linear, Jira, Figma) · `media` (images, video, audio, PDFs) · `skill` · `entity` (tickets, incidents, releases, OKRs) · `qa` (cited workspace Q&A) · and more.

Your AI uses these automatically. You just code.

## How it works

ContextStream is a managed service. This plugin is the public Cursor packaging; the engine is a closed-source, high-performance Rust MCP server (stdio + streamable HTTP) — sub-100 ms p50 context retrieval on the hot agent-loop path in internal benchmarks. The same binary powers Claude Code, Windsurf, VS Code/Copilot, Codex CLI, OpenCode, Cline, Roo Code, Kilo Code, Aider, and Antigravity — your memory follows you across every tool.

## Links

- Homepage: https://contextstream.io
- Docs (Cursor setup): https://contextstream.io/docs/mcp#cursor-vscode
- Quickstart: https://contextstream.io/quickstart
- Support: support@contextstream.io

## License

This plugin packaging is MIT licensed. The ContextStream service is a commercial product — see [pricing](https://contextstream.io/pricing).
