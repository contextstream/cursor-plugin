# ContextStream — project knowledge that carries forward

<img src="https://contextstream.io/logo-hex.png" alt="ContextStream" width="96" />

**Know what changed. Respect what was decided. Continue without rebuilding the brief.**

Connect your existing project knowledge to your agent through hosted MCP and
OAuth. This package supplies seven focused workflows; the hosted service supplies
retrieval, memory, search, and available graph/answer capabilities. It complements
native agent memory with knowledge created across tools.

**Release status:** package under review. Live Cursor/Grok acceptance and public
marketplace approval remain separate gates. No Grok installation or feature parity
is claimed by the presence of these files. See [Grok setup](docs/grok-bot.md).

## Start with one useful result

Authenticate through the host, choose an existing authorized project, then ask:

> Brief me on this project and the decision I should know before making a change.
> Show the sources and anything you could not verify.

Already connected? Do not repeat setup: go straight to the appropriate skill.
New or empty workspace? Use [first-run guidance](docs/first-run.md) or the
[synthetic Harbor Export demo](examples/harbor-export/README.md).

## Skills

| Skill | User outcome |
| --- | --- |
| [context-check](skills/context-check/SKILL.md) | Connection, project, and knowledge readiness; one useful next step |
| [project-brief](skills/project-brief/SKILL.md) | Current state or recent changes interpreted for the reader, with sources |
| [decision-check](skills/decision-check/SKILL.md) | Catch conflicts between a plan and current approved constraints |
| [project-resume](skills/project-resume/SKILL.md) | Recover a work thread and distinguish completed, unverified, and remaining work |
| [change-impact](skills/change-impact/SKILL.md) | Combine code search, available dependency evidence, and project decisions |
| [project-handoff](skills/project-handoff/SKILL.md) | Draft a useful handoff; save only the authorized artifact and verify the result |
| [memory-review](skills/memory-review/SKILL.md) | Inspect stale/conflicting knowledge and record approved, evidence-bound corrections |

Only load the skill the task needs. These are workflows, not seven new servers.
A missing graph or optional answer tool is reported honestly; it does not break
basic retrieval or turn an incomplete check into a confident answer. See the
[source-reviewed capability map](docs/capability-map.md).

## Requirements and privacy

Use your own ContextStream account and an authorized project with relevant
knowledge. The client must support this package's remote MCP/OAuth setup.
A cloud Bot cannot automatically access a laptop's checkout. This plugin installs
no watcher, executable MCP process, background schedule, or telemetry collector.

**Read-first is a workflow policy, not read-only authorization.** Hosted queries
and supplied context are processed, and transcript persistence can apply under
service settings. Read [data handling](docs/data-handling.md) before private use.
Business-record writes and public sharing require specific authorization.
The backend and host, not the Markdown instructions, enforce permissions.

The package is MIT licensed. ContextStream [service usage](https://contextstream.io/pricing)
and your client subscription are separate. No Coflow or ContextCode installation
is required. Do not include customer records in a public Bot template.

## Install in Cursor

When this version is available in the marketplace, install ContextStream through
Customize and authenticate in the browser. This README is not a listing-status
assertion. For local testing, follow [Cursor's plugin guide](https://cursor.com/docs/plugins):
copy the reviewed repository contents, including `.cursor-plugin`, into a new
`~/.cursor/plugins/local/contextstream` directory. Review existing installations
before replacing them. Reload and verify one server, one rule, and seven skills.
Do not bypass administrator restrictions; an installed marketplace copy may take
precedence over a same-name local copy. Resolve duplicate MCP registrations.
Use the host's `/` skill selector; do not assume identical namespacing across clients.

## MCP-only clients

```json
{
  "mcpServers": {
    "contextstream": {
      "url": "https://mcp.contextstream.io/mcp"
    }
  }
}
```

Client syntax can differ. This alone installs neither skills nor the Cursor rule.
Never paste credentials into chat or commit them. Follow the current
[MCP documentation](https://contextstream.io/docs/mcp) for optional native/local sync.

## Grok Bot

The [Project Brief & Handoff profile](bots/project-brief-handoff.md) routes normal
requests into the workflows. It is a human-readable template, not an undocumented
import manifest. Use the [supported setup and test path](docs/grok-bot.md).

## Validate before release

Python 3.10+, no dependencies or credentials needed for offline checks:

```sh
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -v
```

An optional [protocol probe](docs/protocol-probe.md) checks initialization and
advertised tools, without calling project tools. A probe pass is NOT a workflow
or OAuth-browser pass. Complete [manual validation](docs/manual-validation.md) and
the [scenario evaluation and fail-closed release gate](docs/evaluation.md).

Follow the [marketplace checklist](docs/marketplace-launch.md) only after review.
No script in this repository publishes, merges, submits, sends outreach, or buys usage.
Support: support@contextstream.io. [License](LICENSE).
