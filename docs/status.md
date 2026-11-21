# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator, in progress (started 2026-11-22; phase 7 review minors fixed first, commit 1af6d3c).
  Last good build: `build/blade_arts_en.bin` 2026-11-22 (5 SOL typo fixes) with all graphics, sha1 bba57b635092...,
  smoke ok (`work/qa/smoke`).
- **Phase 8 so far:**
  - Text coverage infra: `build.py` writes `build/strings.tsv` (3643 keys: SOL `5BBBNNNN` = old block id + message n,
    raw `(file no.<<24)|addr`, from the write log so relocated strings carry their EXE address) and
    `build/textcover_tbl.lua`; probe `tools/lua/textcover.lua` (needs --debugger; `--var TCTBL='<abs path>'`,
    `TCDEBUG=1` logs every raw read). Both halves verified: SOL (intro `TEXT 50040000` = sol.4.0) and raw
    (status_item / status_system_0 log `TEXT 02157098`, `020B9240`, `021576C8`, matching `textwin.lua`'s new `at=`
    text address; `work/qa/cov_t3`). Report: `python -X utf8 $SKILL/scripts/textcover.py work/qa/cover
    work/qa/strings_cover1.tsv --waive docs/text_unshown.tsv`.
  - Coverage, SOL (all 3351 messages shown, 2026-11-22): the warp/event tour was dropped (it died at 8/246 scenes
    and the map scenes it finished logged 0-8 strings: events need story triggers). Instead `tools/solview.py`
    (+ `tools/lua/solview.lua`, test `tests/test_solview.py`) swaps every message into the intro at the message
    lookup from one savestate and turns its pages through the game's own confirm path (RE: `docs/re/text.md` §Page
    state). Run `work/qa/solview` (6 jobs, ~45 min, build 887644db), re-run of 35 host-cut ids with `--var
    SVFAST=true` in `jf00-03`. `solview.py --report --out work/qa/solview` -> `work/qa/solview_report.txt`: 3331
    messages show exactly the pages the lint expects; **20 long voiced lines are cut** by the intro's own timer
    before their last page (sol.132.98, 138.75/84/86/94/97/101/109/115/119/121, 147.54/56/58/61, 159.54/56/58/61,
    169.0): their last pages are unseen (tried: lookup returning 0 hangs the host; handing the host the rest of the
    message draws nothing). Next idea: a host whose script waits for the message end (a map event state), or find
    the intro script's wait counter. textcover over `work/qa` shows no SOL id missing.
  - Visual QA, SOL: 148 sheets (`work/qa/solview/sheets`, b<block>_sub = subtitle rows 1:1, 60 per sheet; _ws =
    whole screens) with a `.txt` sidecar of expected text per tile; manifest `work/qa/solview/manifest.tsv` (build
    recorded), brief `docs/visual-qa-brief.md`. **All 148 have verdicts (2026-11-22, reviewed in-thread; codex out
    of quota until 2026-11-26): 138 ok, 10 issue** (`work/qa/solview/verdicts/chunk_c3f4346d95b5_00[0-4].tsv`):
    - 5 text bugs, fixed in `script/sol` and rebuilt: sol.54.21 "a Activation" -> "an", sol.138.82 "now.." ->
      "now...", sol.147.101 / 159.101 "prankster.. / fast.." -> "...", sol.147.156 / 159.156 "AS dinner" -> "as".
      Re-run of those 6 on the new build: `work/qa/solview_fix` (see below for its verdict).
    - the rest = the 20 known host cuts (blank last pages in b132_sub_03, b138_sub_02/03, b147_sub_02,
      b159_sub_01/02, b169_sub_01).
    Standing ok calls worth knowing: t0 lines in blocks 125/147/159/166/169/173 sit right of centre because the
    JP's leading full-width spaces are kept (the JP line is shifted the same way: `work/qa/solview_jp125`, though
    solview on the original ROM decodes garbage glyphs, so only positions count); "<... Event> Under construction",
    "0987654321□1234567890", "I found the stone like stick" are the JP's own leftovers; Yes/No question lines in
    b100/b103 sit a little right of centre (check against the map's choice frame, Next item 4).
    The build changed after the tour (sha1 bba57b63...), so `qa_gate check` also needs either a full solview
    re-run (`tools/solview.py --jobs 6`, ~45 min, then `--report` + `qa_gate init ... --build`) or a `waive` once
    the fixed sheets are verified. Polish notes from this pass: `docs/polish.md` §Visual QA.
  - The old warp coverage (`work/qa/cover/warp`, 61 scenes) still counts for raw strings: 235 of 305 raw strings
    are unshown (`work/qa/raw_unshown.txt`: item names/descriptions, sphere/Art texts, save-slot location names,
    memory-card errors): next coverage target (needs the inventory mapped, or a forced-display hook like solview's).
  - Graphics text: pipeline built (`tools/gfx.py`, `tools/gfx_draw.py`, `gfx/gfx.tsv`, `tests/test_gfx.py`, OFL fonts
    in `fonts/ofl/`). Done in game: G1 title, G8 thanks, G6 Prestage (prologue title card), G7 all 14 stage cards,
    G5 flashback subtitles, G3 ending staff roll (all names, 3 CLUTs; `work/qa/gfx_g3b`; names in glossary §Credits,
    D14). G2 drawn, never seen in game (item popups are runtime text: looks unused). Per-row state and evidence:
    `docs/re/graphics.md` §Redraw status. `tools/clutfit.py` recovers a runtime-built CLUT from a JP screenshot.
    Last gfx build `build/gfx/blade_arts_en.bin` 2026-11-22 ~09:00 (commit 9c5e5f3 content) sha1 887644db89c5....
  - Stress saves (started): `tools/items.py` lists the EXE item table (ids, dev labels, JP names). Save offsets
    0x268 = weapon slots, 0x1C8 entry 0 = herb count (`tools/debug/save_layout.md`). Scenes `probe_inv`,
    `probe_inv_box` (load an edited save -> ITEM / ITEM BOX). Herb count 99 draws as ":程" on the EN build: run the
    same scene on the original (`--cue` default) to see whether the JP game breaks too (count may be 1 digit, max 9?).
    The ITEM list (key items) is still unmapped: next lead is a RAM diff around picking up a key item, or the STATUS
    overlay code that draws "NO ITEM".
  - G2 (STICON.BIN labels): TIM at VRAM (832,0), 4bpp 420x224; ink index 0, background 15 (the earlier note had them
    swapped). Row 1 キャンセル x 72-141, row 2 はい 3-32, いいえ 35-75, 選択 79-109, 決定 114-141, 使う 146-172, 破棄
    178-205. Sprite rects are not in a data table, so each English label (Cancel, Yes, No, Select, OK, Use, Drop) is
    drawn inside its JP label's extent. Not seen in game: the ITEM BOX circle popup (scenes `status_itembox_take*`)
    is runtime text, not these sprites; the labels may be unused. Find a screen that draws them (or prove unused).
- Earlier warp sample (title, intro, status, item, gameover, ending, thanks, rolldemo, boss game over, boss map,
  stage-clear, flashback + maps M03/M04/M06/M07) all arrive (`work/qa/p7sample`, `work/qa/p7grow`).
- **Done:**
  - Step 0: template, guard hook proven (sed -i blocked), pre-commit runs `tools/check.py` and rejects a failing test,
    `rom.sha1` (Redump .bin/.cue), PCSX-Redux + SCPH-5500 BIOS fetched, mkpsxiso/armips in `tools/`, smoke route
    `tools/routes/boot.txt` boots the original to the subtitled intro (exit 0), Lua probe logging works.
    Not verified: keyboard input in the PCSX-Redux GUI (no interactive session).
  - Phase 1: text in `DATA/SOL.SRP` (SJIS XOR 0x8C, `tools/sol.py`), raw SJIS in EXE/STATUS/LOADSAVE/BOSS overlays,
    font in DATA1.PAC (`docs/re/text.md`); graphics-text survey G1-G8 (`docs/re/graphics.md`).
  - Phase 2: `tools/debug/warp.lua` + `scenes.tsv` (307 scenes) + `warp_all.py` runner; every scene reached from a cold
    boot with a proof shot (`work/qa/warp/`, `work/qa/warpmaps/` proofs sheets). Method: write the map id during
    New-Game init (mode 1); programs (ending, thanks, attract demo, boss game over) are requested from the title;
    status menu / game over by forcing the game mode. Scenes: title, load (empty/with save), save screen, intro,
    status + ITEM / ITEM BOX / SYSTEM, game over (both kinds), ending (cast roll), thanks (G8), attract demo,
    stage-clear card, flashback, debug-menu event/boss maps, 282 of 301 map packs. RAM map: `docs/re/debug.md`.
    `tools/debug/save.py` (+ `save_layout.md`, `tests/test_save.py`): save = RAM struct 0x800BAB08, checksum = byte
    sum 0x100-0x577; edited saves (map, HP) load with no "file is broken" box (scenes `load_edit`, `load_lowhp`);
    a wrong checksum gives that box. `tools/re.py`: EXE disassembly / xref.
  - Phase 3: `build.py` (check rom, dumpsxiso once, patched files via `patches()` -> build/files + generated
    build/layout.xml with mkpsxiso `source=`, tree stays pristine). `tests/test_identity.py`: rebuild with SOL.SRP
    swapped in for itself = original sha1 (~6 s). A changed override changes the sha1 (checked once by hand).
  - Phase 4: `tools/extract.py` -> `script/sol/*.tsv` (95 blocks, 3351 strings) + `script/raw/*.tsv` (305 strings in
    EXE, STATUS, LOADSAVE, BOSS0P/3P, GAME.BIN; scanner + pointer xrefs `tools/rawtext.py`). `sol.pack()` rebuilds
    SOL.SRP from the TSV jp text byte-identical; every raw jp re-encodes to its bytes; coverage test: every kana run
    in the EXE and DATA/ files is in an extracted string or a hand-checked noise run (`tests/test_extract.py`).
    Overlay load address 0x80149800 (STATUS/LOADSAVE/BOSS*P). Format: `docs/re/text.md` §Script files.
    `warp_all.py --probe/--var` pass extra Lua probes (RAM dumps).
  - Phase 5: VWF in `asm/vwf.asm` (armips, hooks parser 0x800167F8 + centring measure 0x8001602C; code in the dead
    debug-menu records 0x800B8128); English letters = bytes >= 0xA0 in 2-byte units (`tools/en.py`, syntax in its
    docstring); 82 glyphs from `fonts/en11.txt` in free font slots 1297+ (`tools/font.py`); unicorn tests
    `tests/test_engine.py`. `build.py` now always applies EXE + font + SOL/raw en columns; `--marker` = marker script
    (`tools/marker.py`, ids + filler at the JP pixel width), `--qa-file` = per-line overrides. SOL strings reflow
    across their block's sectors (`sol.reflow`). Marker tour `work/qa/marker_tour` (warp_all --debugger --probe
    `tools/lua/textwin.lua`): every window shows its id/tag. Glyph torture line ok (`work/qa/z_torture*.png`).
    Width gate: `tbl/windows.tsv` (subtitle 288 px x 2, WS windows cc*12 x ll, choice 140, status 252 x 3, boss 286,
    load/save row 229). RE: `docs/re/text.md` §Renderer, §English.
  - Phase 6: `tools/batches.py` (split/check/merge/fit; identical strings deduped: 2426 unique of 3639; checks codes,
    px width, lines per page, voiced page count, glossary, honorifics, font charset; `tests/test_batches.py`),
    `tools/pairs.py` (reviewer pairs), briefs `docs/translator-brief.md` / `docs/reviewer-brief.md`, glossary,
    `docs/style-reference.md` (pilot b001), `docs/synopsis.md`. Batches in `work/tl/` (gitignored), reviews: every
    Important fixed; Minors in `docs/polish.md`.
  - Phase 7: raw strings in place or relocated to the EXE free area with data-word refs repointed (`build.py
    raw_texts`); card-title budget (D12), BOSS lines (D13). SOL.SRP overflow (10 blocks: 24 26 43 53 62 117 132 159
    173 176) solved by engine: `sol.pack` appends a block that outgrows its sectors at the end of the file (old bytes
    stay, header entry gets the new id; file 364544 -> 452608 bytes, later disc files shift: every file is loaded by
    name, warp sample ok) and `asm/vwf.asm sol_remap` hooks the loader's `jal 0x80077958` at 0x8003796C: a3 (block id
    = old sector, 0x800D7BDA) -> `sol_map[a3]` (generated, identity except moved blocks). Loader facts: the reader
    reads one sector at a time into a 1-sector buffer (a2 = 1) and fetches sector base+k on demand, so block length
    is free; sector 0's last-index table is copied up to its first 0 entry (0x80077A9C), so hdr_size grows with the
    sector count and sector 0 must hold 2+ strings (`pack_block` checks). Verified in game: English from moved blocks
    incl. sector-1 strings (`work/qa/p7grow` TEXTWIN logs). `tests/test_build.py`: romdiff with the write log on every
    patched file, EXE writes only in the free area / 4 hook sites, font writes in DATA1.PAC entries 118-119, built SOL
    = en column (all 3351 strings), sol_map = remap. `batches.py check`: 0 problems (100 warnings = raw strings over
    their in-place bytes, relocated by the build).
- **Next (phase 8):** (1) done: verdicts for the 148 SOL sheets (above); (2) the 20 cut voiced lines (the only
  open SOL issues; then re-run them, re-verdict those 8 sheets, and re-run/waive for the new build);
  (3) raw-string coverage (235 unshown) + stress saves (ITEM list mapping, herb-count check above); (4) choice
  boxes: `inkbox.py` on real in-map choice frames (solview shows choices without their frame); (5) a final tour of
  the menu/graphics scenes on the final build with verdicts. `build/` is now the full build (graphics included,
  sha1 887644db..., smoke ok 2026-11-22 08:0x). Card title: English location + ／TIME (D12), check the LOAD
  list and the title length in game. Moved SOL blocks 117, 132 (ending), 159, 173, 176 not yet seen in game after
  the remap (review minor 2): make them coverage targets.
- **Open for later phases (not blocking):**
  - Check in game (phase 8): choices where translators added `\\` before `{[DD1}` (sol.98.3, 100.3, 103.2), `{g9}`
    spaced options (72.5, 72.40), digit pickers (62.140-143, 69.22-25), sol.169.0 (voiced, @@ re-split, same screen
    count), sol.132.110 written `{CSA0t4b4}` (JP had a bare `b`), centring of t0 panel lines in blocks 125/147/159/166.
  - Memory-card title: LOADSAVE 0x22C "ブレイドアーツ／" is written into each save and 0x6D0/0xBDC must match it or the
    load list rejects the file (verified by bisecting the marker build): keep all three Japanese. The title also
    holds "／ＴＩＭＥ" and the location name, shown by the BIOS card manager in Shift-JIS: English location names
    in letter bytes are garbage there, but the in-game LOAD list draws the same title: decided English (D12).
  - warp_all with --debugger needs a longer --timeout (7 map scenes hit 240 s); run save_* before load*.
  - Lowercase letter bytes overlap level-2 kanji lead bytes (E0-EA): no line may mix English with those kanji.
  - Item names in the status menu draw in the 252 px description box via `%s%s：%s個` (needs a stocked inventory:
    phase 8 stress save).
  - Text coverage hook for phase 8: message lookup 0x80078728(n) + current block 0x800D7BDA (docs/re/text.md).
  - Inventory (ITEM list), item box contents, nerves and story flags are not mapped: phase 8 stress saves need them
    (`tools/debug/save_layout.md` lists the leads: 0x800BABD0 table, add-item code 0x8003874C).
  - 19 map packs never finish loading from a direct warp (list in `docs/re/debug.md`); reach them via the previous map
    if phase 8 text coverage needs them.
  - The ending's CAST roll shows Japanese names (ENDINGP; part of G3, check whether TIM or text in phase 8).
  - Map packs and states: regenerate with `warp_all.py --states` after any engine/font/graphics change.
- **Open bugs:** none.
- **Waiting on the user:** nothing (all once-per-project answers came with the dispatch: `docs/decisions.md`).
