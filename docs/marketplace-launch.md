# Marketplace launch checklist

## Positioning and listing copy

Plugin title: **ContextStream**

Description: **Shared project knowledge for AI agents. Create source-backed
project briefs, check plans against approved decisions, and prepare useful
handoffs through your authorized ContextStream connection.**

Bot: **Project Brief & Handoff — by ContextStream**.
The product complements native Bot memory with knowledge created across tools.
Do not claim Grok lacks memory, ContextStream is endorsed, or this PR establishes
live compatibility. Do not require Coflow or ContextCode to try the integration.
Package access is MIT licensed; hosted service usage and client subscriptions
are separate. Link current pricing rather than hard-code allowances.

## Distinct release gates

- [ ] Package checks pass on the exact proposed commit.
- [ ] Maintainer reviews the existing logo and confirms its public availability.
      The existing remote logo URL is retained in this PR; a committed approved
      asset is recommended before submission. Do not invent replacement branding.
- [ ] Cursor local smoke test passes; retain sanitized evidence.
- [ ] Grok supported preview/install path is established and tested.
- [ ] OAuth, permissions, skills, citations, writes, and revocation pass the
      [manual tests](manual-validation.md). Unknown is not pass.
- [ ] Submit or update the public repository through
      [Cursor's publishing form](https://cursor.com/marketplace/publish).
      Check for an existing submission before creating a duplicate.
- [ ] Record approval of this version separately from acceptance of an older version.
- [ ] Create and review a clean public Bot share link using the actual supported UI.
- [ ] Ask the Grok Bot team for the curated directory's review process; public
      sharing does not establish directory inclusion or featured placement.

Sources: [Cursor submission reference](https://cursor.com/docs/reference/plugins)
and [Grok Bot sharing documentation](https://docs.x.ai/grok-bot/bots).
Neither GitHub merge nor a successful local check submits this package.

## Demonstration and distribution

Use the [Harbor Export synthetic project](../examples/harbor-export/README.md).
Show a decision saved outside Grok, retrieved with evidence in a fresh Grok task,
then an explicitly approved handoff reused by another supported client. Show the
same evidence to any comparison baseline. Publish versions, failures, and limits;
do not describe a synthetic example as customer proof.

Recruit five consenting existing users for a pilot. Measure successful project
connection, useful cited briefs, and subsequent context reuse, not installs alone.
Do not add private prompt/transcript content to marketing analytics.

For creators, offer one practical workflow test instead of generic promotion.
The package should improve their Bot's access to project knowledge rather than
require a switch to ContextStream's own applications.

## Marketplace-team message draft — not sent

Subject: ContextStream plugin and Project Brief & Handoff Bot review

We maintain ContextStream's hosted OAuth MCP and a public Cursor plugin. We are
preparing a focused Bot that retrieves project decisions, constraints, and lessons
created across tools and returns source-backed briefs and handoffs. It complements
native Bot memory. What is the supported preview and review path for the plugin
in Grok Bot, and the separate submission process for curated Bot-directory inclusion?

Supply the reviewed repository commit, sanitized acceptance record, data-handling
information, and a working share link when available. Remove unverified claims
before sending. No message, submission, or public Bot is created by this package.
