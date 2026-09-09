# Grok Bot setup and compatibility gate

**Status: not live-validated by this change.** These are operator instructions,
not a promise of installation availability, approval, or automatic distribution.

## What is being packaged

The existing Cursor plugin format is retained. It supplies hosted MCP plus three
skills, while [the Bot profile](../bots/project-brief-handoff.md) is set up manually.
No Grok-specific JSON schema, publishing API, or local import command is assumed.

Customer.io documents a plugin distributed through Cursor that also works in Grok
Bot. That is an ecosystem precedent, not proof that ContextStream's OAuth,
transport, rules, or skills work identically in Grok.

## Operator path

1. Use an authorized Grok Bot account and a synthetic ContextStream project.
   Read [data handling](data-handling.md); verify the service's actual retention
   settings before sending sensitive information.
2. In Grok's supported Plugins UI, locate the approved or explicitly enabled
   preview version of ContextStream. Add it and complete OAuth in the browser.
   If unavailable, request the supported preview/review path from the platform
   team. Do not bypass account or administrator restrictions.
3. Verify exactly one intended ContextStream connection, the authenticated
   identity, and the allowed project. Check the exposed tools and their schemas.
4. Verify all three skills are actually available through Grok's supported skill
   controls. Do not assume Cursor's `.mdc` rule is loaded. The skills and profile
   carry their own scope and write-approval guidance.
5. Create a focused Bot using the supplied profile and attach only the intended
   connector/skills. Select the synthetic project and request a cited brief.
6. Complete [manual validation](manual-validation.md). Record the build, plugin
   commit, server version, test identity, coverage, and sanitized evidence.
7. Only after review, generate a public share link from a clean template and
   inspect its preview. A share link is not curated marketplace inclusion.

A direct MCP connection alone tests neither marketplace installation nor skill
loading. A successful Cursor test does not count as a Grok acceptance result.
Grok's cloud environment is separate from a user's local checkout; start with
knowledge already indexed in ContextStream. This package installs no watcher.
Bots and connectors are not isolated identities: test the actual account-wide
host permissions plus ContextStream's backend authorization.

## References checked 2026-09-09

- [Cursor plugin authoring and local tests](https://cursor.com/docs/plugins)
- [Cursor manifest and component reference](https://cursor.com/docs/reference/plugins)
- [Grok plugins and cloud computer](https://docs.x.ai/grok-bot/computer-and-apps)
- [Grok Bot profiles and public sharing](https://docs.x.ai/grok-bot/bots)
- [Grok security model](https://docs.x.ai/grok-bot/security)
- [Customer.io's Cursor/Grok plugin precedent](https://docs.customer.io/ai/plugins/cursor-grok-bot/)

Review current platform documentation again before submission; UI and eligibility
can change. No marketplace team has approved this package through this PR.
