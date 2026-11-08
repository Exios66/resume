# Ideas backlog (prune as they land)

Done: copy button, scroll-region access, stacked tables, 404 page, résumé contact, search titles, tap targets,
tiny text, separators, balanced headings, wbr in table-cell code, stack classifier (prose column 45+, row label
12+, two-row grids, five-column grids), sticky first column + scroll edge, scoped tabular-nums, AUC / band /
v0 content fixes, labelled prose rows, compact phone header, duplicate back link removed, mobile checks at
375 px dark (segment 4).

Open:
1. Layout findings are 0. The one accepted finding is the "Graduate research, UW–Madison" heading widow
   (UW–Madison is a single unit).
2. Projects page jump links have large row gaps on phones; consider chip styling.
3. Report contents box column misalignment (run 38 removed the duplicate back link; alignment still open).
4. Content consistency (owner facts needed): unify date formats; "Simulations" shortcut vs "Side projects &
   interests" heading; expand "DSHB" on first use.
5. Audit coverage: real Firefox/WebKit, real devices and screen readers were never checked.
6. New audit segments from issue 106 still available: more viewports (768/414), performance budget, chart and
   diagram contrast, link and asset integrity, metadata (titles, canonical, og:image), print layout, reduced
   motion, other engines.


## Next batch after runs 44–49
- Completed: new 414/768 coverage, tablet prose tables, undergraduate credential structure, SVG rendered label-size coverage and readable figures; PR candidates now include durable screenshots and quantitative keep rationale.
- Next visualization audit segment: SVG text/essential mark contrast in both themes (axe excludes much SVG), then forced colors and reduced motion checks. Keep the audit fixed within each segment.
- Next features: report contents alignment, Projects category chips, page-type labels in search results. These are currently metric-blind; define independent visitor-facing evaluation before experimenting.
- Prose backlog: shorten repeated introductory inventories and make report takeaways easier to scan, preserving all claims and source-backed metrics. Owner facts still needed for the open content-accuracy issues.
- Continue screenshots for every progressing PR candidate, with before/after metrics and reason for keeping it. Never publish evidence under docs/.
