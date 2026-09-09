# ContextStream — shared project knowledge for AI agents

<img src="https://contextstream.io/logo-hex.png" alt="ContextStream" width="96" />

**Your agents should know what your team already knows, even when the work started elsewhere.**

This Cursor plugin connects to ContextStream's hosted OAuth MCP and packages
three focused skills. It also includes a Grok Bot profile and validation guide.
**Grok Bot compatibility, marketplace approval, and Bot-directory inclusion are
separate release gates; adding these files does not establish any of them.**

## Three useful jobs

| Skill | Ask it to | Result |
| --- | --- | --- |
| [project-brief](skills/project-brief/SKILL.md) | Catch me up on this project | Relevant changes, decisions, blockers, and source references |
| [decision-check](skills/decision-check/SKILL.md) | Check this plan against our decisions | Conflicts, missing evidence, and questions for human judgment |
| [project-handoff](skills/project-handoff/SKILL.md) | Prepare the next person's handoff | Current state, verified work, constraints, and next steps |

Skills complement an agent's native memory; they do not claim that other agents
lack memory. They retrieve knowledge from the user's authorized ContextStream
project. Drafting a brief or handoff does not authorize publishing it.

## Requirements and data handling

Use a ContextStream account with access to the intended project and knowledge
already connected or indexed. The receiving client must support this plugin's
MCP transport and OAuth. A plugin installation does not provision sources or
make a laptop's checkout available to a cloud Bot.

**Read-first is a workflow policy, not a read-only credential.** Hosted calls
process the query and supplied content; transcript persistence can still apply
under service settings. Review [data handling](docs/data-handling.md) before
using private material. Start with the [synthetic demo](examples/harbor-export/README.md).

The package is MIT licensed. ContextStream's hosted service has its own
[account and usage terms](https://contextstream.io/pricing); a Cursor or Grok
subscription does not pay for that service. No Coflow or ContextCode install is
required for these skills.

## Cursor installation

When this version is available in your marketplace, install ContextStream from
Customize, then authenticate its MCP connection. If it is not available, use the
local development route below. This README is not a statement of listing status.

For local testing, clone this repository at the reviewed PR commit, then copy
its contents (including `.cursor-plugin`) into a new directory named
`~/.cursor/plugins/local/contextstream`. Do not overwrite an existing installation
without reviewing it. Reload Cursor and check that one MCP server, one rule,
and all three skills appear in Customize. Administrators may disallow local
imports; do not bypass that policy. An installed marketplace copy can take
precedence over a local copy with the same name.

Authenticate in the browser when prompted. Review and resolve duplicate
ContextStream MCP registrations rather than enabling multiple copies blindly.
Select the desired skill from `/` in chat and specify the authorized project.

Cursor's [plugin guide](https://cursor.com/docs/plugins) documents local imports;
its [reference](https://cursor.com/docs/reference/plugins) documents the format.

## MCP-only connection

Clients supporting remote MCP and OAuth can use the existing configuration:

```json
{
  "mcpServers": {
    "contextstream": {
      "url": "https://mcp.contextstream.io/mcp"
    }
  }
}
```

An MCP-only connection **does not install these skills or the Cursor rule**.
Client configuration syntax can differ. Use the client's supported setup path;
do not paste credentials into a conversation or add them to this repository.

The optional native client supports local indexing and editor-specific setup.
It is separate from this package; follow the current
[MCP documentation](https://contextstream.io/docs/mcp) when local sync is needed.

## Grok Bot preparation

Use the [Grok Bot guide](docs/grok-bot.md) and
[Project Brief & Handoff profile](bots/project-brief-handoff.md).
The profile is human-readable setup material, **not** an undocumented Grok
import manifest. Do not assume Cursor's local-plugin folder or `.mdc` behavior
transfers to Grok. Record actual behavior before advertising compatibility.

## Development and release

Python 3.10+ is sufficient; validation installs no packages, uses no credentials,
and makes no network calls:

```sh
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -v
```

These checks validate packaging and documented prompt contracts, **not** model
behavior, service authorization, OAuth, or marketplace acceptance. Complete the
[manual acceptance tests](docs/manual-validation.md) before release, then follow
the [marketplace launch checklist](docs/marketplace-launch.md).

Support: support@contextstream.io. See [LICENSE](LICENSE) for package licensing.
ContextStream branding and the hosted service are not licensed by the package's MIT grant.
