# Evidence-backed release gate

Offline packaging tests, mocked transport tests, actual MCP protocol checks,
client/model workflows, and marketplace approval are different kinds of evidence.
None implies the next. The committed scenario catalog records test requirements,
not successful executions or a benchmark score.

Run every case in [the catalog](../evaluation/scenarios.json) independently in
Cursor and Grok Bot against the exact package under review. Main continuity cases
require three fresh trials. Keep versions, source coverage, failures, tool calls,
cost/latency observations where available, and human corrections in sanitized
private evidence. Use at least an empty project and a populated synthetic project;
the scope test also needs a separate restricted project. Never use real customers
for adversarial permissions tests.

## Generate a record — initially NOT RUN

```sh
python3 scripts/check_release.py --expected-commit <40-character-PR-head-SHA> --template /private/path/report.json
```

The file is created exclusively (no overwrite) and contains the package/scenario
fingerprints, all required case IDs, client metadata slots, and NOT RUN trials.
Fill the record only from actual tests. Each passing trial needs a relative
sanitized evidence-file path and that file's SHA-256. Include run identifiers and
timestamps; reusing identical evidence does not count as a fresh trial. Put evidence outside the
public repository or in ignored `.local-evidence/`. Do not commit credentials,
real transcripts, account identifiers, or private customer sources.

```sh
python3 scripts/check_release.py --expected-commit <40-character-PR-head-SHA> --report /private/path/report.json --evidence-root /private/path/evidence
```

The command fails on missing clients/cases/trials, NOT RUN/failed results, stale
fingerprints or commit, missing reviewer metadata, unsafe evidence paths, missing
evidence, or mismatched hashes. It does not fetch evidence or invoke any agent.
A reviewer must inspect the evidence and set the per-client reviewed flag.

**A pass only means the supplied acceptance record is complete and bound to the
checked files. It cannot prove the record is truthful or that evidence demonstrates
the claimed behavior. Human review remains mandatory.** Test changes invalidate
the scenario fingerprint; behavior/probe/gate changes invalidate the package
fingerprint. Re-run affected behavior and document what was repeated.

## Quality bar

No authorization leak, unapproved action, false success receipt, or hidden scope
expansion is acceptable. A graceful limitation is better than an invented answer.
For successful user journeys, inspect relevance, source authority, task usefulness,
and the amount of re-briefing required. Keep developer-only diagnostics out of
normal answers. A user should not have to choose among seven skills to get started.

Run a fair comparison with the same source access, model/settings, task, and budget
where feasible. Do not market fixture correctness, unit-test totals, or a synthetic
demo as independent proof of being the best memory product.
