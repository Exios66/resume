# Open-issue catalog — 6 November 2026

Snapshot: **35 open issues**, retrieved from `Exios66/resume` in four cursor-paginated requests. Ponytail priority: verified stale closures first, small source-backed corrections next, then larger work. “Local” never means shipped; keep those issues open until the changes land.

After evidence-backed closure of #73 and #87: **33 remain open**. The quick fixes below are implemented locally, not merged or published.

| Issue | Request | Disposition / remaining boundary |
| --- | --- | --- |
| #20 | Dataset citation | Local: versioned repository citation, with configuration and source-license context; no invented DOI/publication. |
| #25 | ModernBERT Hub URL | Local: separately linked the verified prepared dataset and tagged classifier; corrected the issue's model/data ambiguity. |
| #33 | Algorithmic modeling / visualization | Broad project idea; #89 implements one related project, not the whole idea. |
| #53 | Appendices parent | Larger work: no dedicated appendices exist; reports are not automatically substitutes. |
| #54 | AeroGlobe appendix | Open; needs source-backed supporting material. |
| #55 | Mandalay Bay appendix | Open; needs source-backed supporting material. |
| #56 | Digital-Mailroom appendix | Open; no unpublished partner data. |
| #57 | Langton's Ant appendix | Open; retain literature attribution and benchmark scope. |
| #58 | MORNINGSTAR appendix | Open; distinguish self-reported decisions from evaluated quality. |
| #59 | Corpus EDA appendix | Open; pin dataset revision and label provenance. |
| #60 | Mailroom-ML appendix | Open; distinguish current M9c from M9b history. |
| #61 | Mailroom Reloaded appendix | Open; distinguish demo captures from evaluation. |
| #62 | NATD appendix | Open; authentication/privacy constraints prohibit publishing withheld signals. |
| #63 | Psychometric Digital Twin appendix | Open; no respondent-level private records. |
| #64 | RVL-CDIP appendix | Open; verify full prompt registry and per-class tables. |
| #65 | Wave Laboratory appendix | Open; separate validation, unit and browser tests. |
| #70 | Stale MapReduce status | Local refresh: F24, CI, storage, compression and evaluation; removed unverifiable current test totals. |
| #71 | Employment history | Needs owner decision on role inclusion and résumé master; do not silently rewrite the exported PDF. |
| #72 | Degree title and PDF drift | Local: official colon wording fixed. PDF master/version and dropped bullet need owner confirmation. Keep issue open. |
| #73 | Five vs ten hub packages | Closed with upstream workspace evidence; deployed site already says five. |
| #74 | Résumé cohort / prompt counts | Local web correction; old PDF explicitly labeled October export. PDF replacement remains open. |
| #75 | Freshness / test counts | Local snapshot labels and review note; no claim to rerun every upstream project's tests. |
| #76 | Owlcot #022/#023 / attribution | Verify authorship before inclusion; a curated selection need not pretend to be the complete feed. |
| #77 | Search / navigation / print / tables | Mixed issue: print handler and mobile table scrolling already exist. Local category shortcuts and touch fixes; clarify nav policy. Larger search/TOC work remains open. |
| #78 | Links / appendices | External sweep: 65 original destinations, no observed 404; 10 DOI publisher 403s and LinkedIn 999 are inconclusive. Appendix work remains open. |
| #79 | Additional stale MapReduce claims | Local correction of chaos driver, S3, compression, Python coordinator; scope the diagram explicitly. |
| #80 | NATD provenance | Needs authenticated pilot source/run and persona-version evidence. Do not invent it or publish private records. |
| #81 | Wave snapshot | Local historical labels; fresh upstream collection and comparison remain open. |
| #82 | Mandalay Bay counts / CI | Needs a pinned source recount or explicit historical scope; not a one-line version bump. |
| #83 | M9c supersedes M9b | Local current headline and historical report labels; retain routing caveats and explain older figure provenance. |
| #84 | Mailroom Reloaded verification | Fresh upstream environment run needed; cannot call an old demo log a current test run. |
| #85 | Corpus EDA counts / staging | Requires source recount and live Hub promotion check before changing release claims. |
| #86 | v1.0.0 release-note scope | Local: labeled historical; preserved the old release scope and linked the current build process. |
| #87 | Duplicated accessible link name | Closed: deployed Chromium accessibility tree has two separate links, each named exactly once; added a local regression. |
| #89 | Neuron Atlas | Local case study, project card and home feature, pinned to source a580008; browser verification before shipping. |

## Closure evidence

- **#73:** upstream `Digital-Mailroom` at `d3520da9bff57950ec2aba5f6dae13e4cfdaf3b1`, `pyproject.toml` workspace + `packages/`: `llm-dojo-scoring`, `llm-mailroom`, `local-mailroom-sandbox`, `The-Mailroom`, `mailroom-corpus-eda` (four built members, one virtual). README records the DMR-079 pruning. The existing deployed portfolio already reports five.
- **#87:** Playwright Chromium inspection of `https://exios66.github.io/resume/projects/digital-mailroom.html`, 6 November 2026: each of the two dataset-section links has the accessible name `Mailroom-ML case study`; neither link has an `aria-label`, nested repeated label or duplicated text. These are two legitimate references, not one doubled accessible name.

## Do not close yet

New local fixes require a merged/published change. Partial multi-part issues stay open. In particular, #53–#65 are not stale merely because detailed reports already exist, and #72/#74 are not complete while the owner-maintained PDF is unchanged.
