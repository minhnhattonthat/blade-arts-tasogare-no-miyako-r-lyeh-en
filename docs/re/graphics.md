# Graphics text survey (phase 1, done 2026-11-21)

Static sweeps (all files with TIMs on the disc; `work/` is gitignored, rerun to rebuild):
- `python -X utf8 tools/timsweep.py work/gfx/sweep_data work/disc/tree/SLPM_866.02 work/disc/tree/DATA/* work/disc/tree/NOR/*`
  -> 197 TIMs, 17 sheets + `index.tsv` (sheet, cell, file, offset).
- `python -X utf8 tools/timsweep.py work/gfx/sweep_m0 work/disc/tree/M0/*.PAC` -> 1525 TIMs, 157 unique (identical
  pictures drawn once; `dup` rows in `index.tsv` name every other file holding the same picture), 14 sheets.
- `--gray` draws palette indices instead of CLUT colours: needed for TIMs whose first CLUT is all black (text hidden)
  and for TIMs whose header says 16bpp over 4bpp data (drawn as noise otherwise). Every near-black TIM (mean < 12 over
  all files) and every 16bpp-flagged TIM was re-drawn this way.
- One TIM full size, every CLUT row stacked: `python -X utf8 tools/timshow.py FILE HEXOFF OUT.png [--gray] [--zoom N]`.

## Japanese found (to redraw / retype)

| # | Screen | Source (file @ TIM offset) | Content | Note |
|---|---|---|---|---|
| G1 | title screen | `DATA/TITLEP.BIN` @5B58 (16bpp 320x480) | subtitle ブレイドアーツ／黄昏の都ルルイエ; © line "Ea Co.,Ltd/結城信輝/エニックス 2000" | logo BLADE ARTS is official English; redraw subtitle in English (wording phase 6) and the © line ("Ea Co.,Ltd/Nobuteru Yuki/Enix 2000") |
| G2 | menus (button/help labels) | `DATA/STICON.BIN` @0 (4bpp 420x224, 2 CLUT rows, same labels in both) | キャンセル, はい, いいえ, 選択, 決定, 使う, 破棄 | the rest (STATUS, Option, Information, Item, Sphere) is English |
| G3 | ending staff roll | `DATA/ENDINGP.BIN` @74E8 (4bpp 1188x500) | role headings (特別協力, セールス, ...) and staff names in kanji | D3: credits in English: romanize every name (Hepburn) and translate headings |
| G5 | flashback cutscene (sepia stills) | `M0/M05_02_0.PAC` @57070 (4bpp 960x239) | baked subtitles 「尊厳者・・・ 此処にあったか」 and 「何処かへ 移し、隠さねば・・・」 | same lines exist as text in SOL.SRP (3 hits for 尊厳者): check in phase 8 whether the game shows the texture or text |
| G6 | intro staff credits (map texture) | `M0/M02_10_0.PAC` @88CA4 (4bpp 1280x168); same word alone in `M0/M03_01_0.PAC` @8ACB8 (96x16) | heading プレステージ (rest of the credits already English) | "Prestage" (company); also 2 hits in SOL.SRP |
| G7 | stage clear card | `M0/M50_00_0.PAC` @401EC (4bpp 512x152, black CLUT: needs `--gray`), same TIM in M50_01..13, M60_00, M91_04 | "NEXT STAGE 魔力エレベーター下層", stage name 地下水路 (sharp + blurred glow copies), "STAGE CLEAR" | stage names are also text in SOL.SRP (地下水路 16 hits): phase 8 must show whether other stages' cards are drawn from text |
| G8 | "Thank you for playing" screen | `DATA/THANKSP.BIN` @F54 (4bpp 1000x224, black first CLUT) | 2000年 夏 発売予定 ("on sale summer 2000") | probably a demo leftover; translate anyway (D5) |

## Redraw status (phase 8)

Pipeline: `gfx/gfx.tsv` rows -> `tools/gfx_draw.py` (one drawer per row, OFL fonts in `fonts/ofl/`) writes
`gfx/<name>.png` -> `build.py` (`tools/gfx.py patch`) writes the TIM pixel blocks; `tests/test_gfx.py` (round trip,
copies identical, writes only inside pixel blocks). Originals: `python -X utf8 tools/gfx.py orig NAME`.

| Row | State |
|---|---|
| G1 title | done, English in cold-boot shot (`work/qa/gfx_title/title/proof.png`) |
| G8 thanks | done, English in game (`work/qa/gfx_g6g8/thanks/f002880.png`, drawn red by the screen's fade) |
| G6 Prestage | done: it is the prologue stage's title card at the end of the intro, English in game (`work/qa/gfx_g6long/intro/f009720.png`: intro warp with `--var AFTER_FRAMES=15000`, frame ~9700) |
| G5 flashback | done: the stills' subtitles are the texture (still Japanese on the text-only build). Still 1 = "The Majesty... So it was here..." (its trailing ・・・ at x 770 is drawn right of the line in game: cleared), still 3 = "I must move it somewhere / and hide it..."; English in game (`work/qa/gfx_g5`) |
| G7 stage cards | 14 different TIMs (M50_00..13 @401EC; M91_04 = M50_00, M60_00 = M50_12): big name + streaked copy + "NEXT STAGE <name>"; names = LOADSAVE location names (Jungle, Ruins, Gravity Elevator Upper/Lower, Underground City, Waterway, Research Ruins, Cave of Illusions, Temple of the Sword, Basetet, R'lyeh, Primordial One; M50_00 地下水路 Underground Channel, M50_01 プレステージ Prestage). TIM CLUT all 0x8000: the game builds the real ones, fitted from JP shots with `tools/clutfit.py` (card 00 name = plain ramp, cards 01-13 name = a shuffled ramp, the NEXT STAGE row another per group; palettes in `gfx_draw.py`). Done: rows card00..card13, English in game incl. the streak slide-in (`work/qa/gfx_g7`, `work/qa/gfx_g7_anim`) |
| G2 STICON | drawn (row `sticon`): each label inside its JP label's extent (Cancel, Yes, No, Select, OK, Use, Drop; Lato bold-ish); not seen in game: ITEM BOX take, ITEM -> circle on Herb (`status_item_use*`) all draw runtime text popups ("Take Out / Cancel"); the labels look unused |
| G3 ending staff roll | done (row `ending`): every JP line redrawn (names per glossary §Credits, CrimsonText 11, names at u 60 like the JP); English in game (`work/qa/gfx_g3`, `work/qa/gfx_g3b`). Each group is a sprite over u 0-159 of its 256-px column at screen x 160 (marker build `work/qa/g3_mark`: dot grid over the background), so lines end by u 158. Three CLUTs (clutfit on JP shots): the TIM's own; ROLL_B for the debugger group (column 3 y 383-496) and Planning/Directors (column 4 y 158-253): these look garbled with the TIM CLUT; ROLL_C for Fin and the © line. Fin, STAFF / ENIX STAFF / CAST, MBA, Paul Handelman were English already |

## Checked, no Japanese

- `DATA/STATUS2.DAT`: status menu labels, all English. `DATA/GAMOVERP.BIN` @7128: TITLE / TRY AGAIN, English.
- `DATA/LOGOP.BIN` (Enix, Ea logos; @AC84 in gray: Ea logo + "(c) Ea" only), `NOW LOADING` sprite, title menu
  New Game/Continue, `ENDING_P.DAT` CG stills, `DATA/LOADSAVE.BIN` (labels look English: confirm on the load screen).
- `DATA/DATA1.PAC` (132 TIMs): character face/body textures, weapon textures (decorative glyph strips, not
  Japanese), item icons, ASCII font (cell 130) and the Japanese font TIM (cell 131: text work, not graphics).
- `NOR/` boss textures (all, including 16bpp-flagged ones in gray), `M0/` map textures and character textures.
- `M0/M10_01_0.PAC` @86348: book page with illegible faux script (not Japanese).
- No FMV on the disc (`STR/` holds XA audio only).

## Left for phase 8 (runtime)

- Runtime-drawn text (SOL.SRP, menus, item names) is text work, not graphics.
- Confirm in game: G5 texture vs text, G7 card for other stages, LOADSAVE labels; any compressed graphics the static
  sweep can't see will show up on the QA tour.
