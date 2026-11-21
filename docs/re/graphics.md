# Graphics text survey (phase 1, in progress)

Static sweep: `python -X utf8 tools/timsweep.py work/gfx/sweep_data work/disc/tree/SLPM_866.02 work/disc/tree/DATA/* work/disc/tree/NOR/*`
-> 197 TIMs, 17 sheets + `index.tsv` (sheet, cell, file, offset). Full-size renders of single cells: see the snippet in
git history or `timsweep.parse_tim`.

## Japanese found (to redraw / retype)

| # | Screen | Source | Content | Note |
|---|---|---|---|---|
| G1 | title screen | `DATA/TITLEP.BIN` TIM (sweep cell 160) | subtitle ブレイドアーツ／黄昏の都ルルイエ; © line "Ea Co.,Ltd/結城信輝/エニックス 2000" | logo BLADE ARTS is already English (official); redraw subtitle as "Blade Arts: R'lyeh, City of Twilight" (wording phase 6) and the © line in English |
| G2 | menus (button/help labels) | `DATA/STICON.BIN` TIM @0 (cell 158), 420x224 4bpp | キャンセル, はい, いいえ, 選択, 決定, 使う, 破棄 (+ small labels) | other CLUTs may hide more labels: render all CLUT rows |
| G3 | ending staff roll | `DATA/ENDINGP.BIN` TIM @0x74E8 (cell 152), 1188x500 | role headings (特別協力, セールス, ...) and staff names in kanji | D3: credits in English, so romanize every name (Hepburn) and translate headings |
| G4 | intro staff credits | in VRAM during the intro | already English ("BLADE ARTS PRODUCT STAFF", "Character Disign") | none (typo "Disign" is the original's; leave) |

## Checked, no Japanese

- `DATA/STATUS2.DAT` (cell 157): status menu labels, all English (EXPLOSION, CONQUEST, ITEM BOX, Yes/No, SPHERE...).
- `DATA/LOGOP.BIN` (Enix, Ea logos), `NOW LOADING` sprite, title menu New Game/Continue (cell 161), sweep sheet 12
  cells 144-151 (ENDING_P.DAT CG stills).
- `DATA/LOADSAVE.BIN` TIM (cell 154): dark render, labels look English (LOAD/SAVE): confirm on the load screen.

## Still to sweep (next session)

- Sheets 0000-0011 (DATA1.PAC 132 TIMs, ENDING_P.DAT first 12) and 0014-0016 (NOR boss textures): read for Japanese.
- `M0/*.PAC` map packs (302 files): run timsweep on them (textures of signs/monitors may carry Japanese).
- Multi-CLUT TIMs: render every CLUT row (STICON especially).
- `DATA/THANKSP.BIN` (cell in sheet 13): "Thank you for playing" screen, check content.
- Runtime-drawn text (SOL.SRP, menus) is text work, not graphics.
