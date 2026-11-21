# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All D1-D7 came pre-answered in the owner's Orca dispatch brief (standing answers for every one-shot project).

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-21 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer. |
| D2 | 2026-11-21 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist (e.g. title logo "BLADE ARTS"), else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-21 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-21 | Abbreviations | engine work first (default), abbreviate | Skill default: full names and terms; engine work (VWF, wider boxes) before abbreviating; abbreviation only as a flagged last resort. |
| D5 | 2026-11-21 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-21 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, report at the end. |
| D7 | 2026-11-21 | Existing saves / memory cards | use user's, build debug tool | None provided; build the debug tool as usual. |
| D8 | 2026-11-21 | Publishing | - | Never run `gh release create`, never change repo visibility; the run ends at a built, verified release zip. Commits are pushed to main at each phase end. |
