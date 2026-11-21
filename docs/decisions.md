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
| D9 | 2026-11-22 | Phase 6 translators: in-session subagents or translate alone (Orca worker; codex out of quota) | subagents, self | Coordinator: "everything is pre-approved, decide with sensible defaults". Default per skill + AGENTS.md: translate-retro-game:translator / reviewer subagents. |
| D10 | 2026-11-22 | Names with no official/patch English | Hepburn (D2) | Rei Shido, Ranfa (蘭花/藍花/ランファ, not Lanfa), Bridget/Walter Landers, Basetet (not Bastet), Zagnus, Lizzie; Latin-styled katakana (spheres, tablets, zodiac) -> Latin (Tonitrus, Iudex, Aries...). Matches MobyGames' credit spellings. Register: modern English, archaic thou/thee for the ancients. |
| D11 | 2026-11-22 | Ellipsis style (batches split between "..." and "......", 265 lines) | one "..." per pause; keep "......" for long pauses | One "..." per pause however long the JP run (glossary rule as written; long runs read as typos in English and cost width). 4+ dot runs collapsed in 277 lines (codes untouched; sample before/after: sol.53.8 "Yeah, you're right......" -> "Yeah, you're right..."), `batches.py check` rejects 4+ dots. Bulk rewrite covered by D6 pre-approval; touched-line sample re-reviewed. |
| D12 | 2026-11-22 | Memory-card title: the in-game LOAD list draws the card title (prefix stripped), so its location part must be English; the BIOS card manager reads it as Shift-JIS | keep location JP (load list Japanese); English letter bytes (BIOS shows mojibake); fullwidth SJIS English (does not fit 64 bytes) | English letter bytes (in-game text wins; the BIOS manager is outside the game). Prefix ブレイドアーツ／ stays JP (loader matches it); tail ／ＴＩＭＥ -> ／TIME (6 bytes) so every location fits: 63 - 32 - 6 = 25 bytes, checked by build.py. README must mention the BIOS title. Verify the LOAD list in game (phase 8). |
| D13 | 2026-11-22 | BOSS0P/3P lines (no pointer found) longer than their slot | relocate (no pointer), shorten | Shortened to fit (0E0FC "Something there?", 0E118 "You kidding?", 0E16C/1A0/1D0/1EC); meaning kept. |
