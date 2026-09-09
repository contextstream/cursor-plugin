# Grok Bot setup and compatibility gate

**Status: live validation still required.** This package retains the Cursor plugin
format and supplies hosted MCP plus seven skill workflows. The
[Bot profile](../bots/project-brief-handoff.md) is a manual setup template, not an
undocumented import format or an automatically published Bot.

1. Start with an authorized Grok Bot account and synthetic ContextStream project.
   Review [data handling](data-handling.md), including actual persistence settings.
2. Use Grok's supported Plugins UI to install an approved or explicitly enabled
   preview version. Authenticate in the browser. If no preview is available,
   request the supported review path; do not bypass administrator restrictions.
3. Verify the intended connection, identity, project, and current tool schemas.
   The [metadata probe](protocol-probe.md) can assist operator diagnostics but
   does not replace browser OAuth or real client tests.
4. Verify all seven skills appear and can actually be invoked. Do not assume
   Cursor's `.mdc` rule loads in Grok; each skill/profile carries essential policy.
   Missing optional graph/answer capabilities must produce honest partial coverage.
5. Create the focused Bot, attach only the necessary connector/skills, and use the
   [first-run workflow](first-run.md). Do not introduce every capability before
   producing a useful cited answer.
6. Run [manual validation](manual-validation.md) and the
   [scenario evaluation](evaluation.md) on the exact reviewed commit. Record the
   build, permissions, data handling, and sanitized evidence separately per client.
7. After review, share a clean template using the actual supported UI. Inspect
   the preview; recipients authenticate their own accounts. Public sharing,
   curated directory inclusion, and featured placement are distinct milestones.

A direct MCP test does not establish skill loading or marketplace installation.
Grok's cloud computer is not a user's laptop. Start with already connected project
knowledge; this plugin installs no watcher. Bot names are not isolated security
identities. Verify host grants AND ContextStream backend scope enforcement.

## Primary references checked 2026-09-09

- [Cursor plugin guide](https://cursor.com/docs/plugins)
- [Cursor plugin reference](https://cursor.com/docs/reference/plugins)
- [Grok apps/plugins](https://docs.x.ai/grok-bot/computer-and-apps)
- [Grok Bot sharing](https://docs.x.ai/grok-bot/bots)
- [Grok security](https://docs.x.ai/grok-bot/security)
- [Customer.io integration precedent](https://docs.customer.io/ai/plugins/cursor-grok-bot/)

A precedent is not a successful ContextStream test. Recheck public platform
instructions before submission. No compatibility or endorsement is inferred.
