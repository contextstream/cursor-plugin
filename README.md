<div align="center">
  <img src="https://contextstream.io/400logo.png" alt="ContextStream" width="120" />

  # ContextStream for Cursor

  **Stop starting AI agents cold.**

  Persistent project memory, semantic code search, and grounded context for Cursor — decisions, lessons, runbooks, and prior sessions surfaced automatically, before your agent touches the repo.

  [Website](https://contextstream.io) · [Docs](https://contextstream.io/docs/mcp) · [Pricing](https://contextstream.io/pricing)

  [![Add to Cursor](https://img.shields.io/badge/Add%20to-Cursor-blue?style=for-the-badge)](cursor://anysphere.cursor-deeplink/mcp/install?name=contextstream&config=eyJ0eXBlIjoiaHR0cCIsInVybCI6Imh0dHBzOi8vbWNwLmNvbnRleHRzdHJlYW0uaW8vbWNwP2RlZmF1bHRfY29udGV4dF9tb2RlPWZhc3QiLCJoZWFkZXJzIjp7IlgtU291cmNlLU5hbWUiOiJjdXJzb3ItcGx1Z2luIiwiWC1Tb3VyY2UtVmVyc2lvbiI6IjAuMS4wIn19)
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

### Option 1 — Hosted (this plugin)

Installing this plugin connects Cursor to the hosted ContextStream MCP endpoint (`https://mcp.contextstream.io/mcp`). Sign in via OAuth, or grab an API key at [contextstream.io](https://contextstream.io).

### Option 2 — Native binary (recommended for hooks + local indexing)

The native engine is a single Rust binary — no Node, npm, or npx required — with a built-in setup wizard, local index watcher, and agent lifecycle hooks:

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

Prebuilt binaries ship for macOS (Apple Silicon + Intel), Linux (x64 + arm64), and Windows.

## Tools your agent gets

`init` · `context` · `search` · `session` (lessons, recall, plans) · `memory` (docs, decisions, tasks, transcripts) · `graph` (code health) · `project` · `workspace` · `vcs` (GitHub/GitLab/Bitbucket) · `integration` (Slack, Notion, Linear, Jira, Figma) · `media` (images, video, audio, PDFs) · `skill` · `entity` (tickets, incidents, releases, OKRs) · `qa` (cited workspace Q&A) · and more.

Your AI uses these automatically. You just code.

## How it works

ContextStream is a managed service. This plugin is the public Cursor packaging; the engine is a closed-source, high-performance Rust MCP server (stdio + streamable HTTP) serving sub-100 ms p50 context retrieval on the hot agent-loop path. The same binary powers Claude Code, Windsurf, VS Code/Copilot, Codex CLI, OpenCode, Cline, Roo Code, Kilo Code, Aider, and Antigravity — your memory follows you across every tool.

## Links

- Homepage: https://contextstream.io
- Docs (Cursor setup): https://contextstream.io/docs/mcp#cursor-vscode
- Quickstart: https://contextstream.io/quickstart
- Support: support@contextstream.io

## License

This plugin packaging is MIT licensed. The ContextStream service is a commercial product — see [pricing](https://contextstream.io/pricing).
