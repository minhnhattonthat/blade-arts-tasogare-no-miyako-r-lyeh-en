# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator, in progress (started 2026-11-22; phase 7 review minors fixed first, commit 1af6d3c).
  Last good build: `build/blade_arts_en.bin` 2026-11-22 (after 1af6d3c), smoke ok (`work/qa/smoke`); with G1/G6/G8
  graphics: `build/gfx/blade_arts_en.bin` (title/intro/thanks warps ok).
- **Phase 8 so far:**
  - Text coverage infra: `build.py` writes `build/strings.tsv` (3643 keys: SOL `5BBBNNNN` = old block id + message n,
    raw `(file no.<<24)|addr`, from the write log so relocated strings carry their EXE address) and
    `build/textcover_tbl.lua`; probe `tools/lua/textcover.lua` (needs --debugger; `--var TCTBL='<abs path>'`,
    `TCDEBUG=1` logs every raw read). Both halves verified: SOL (intro `TEXT 50040000` = sol.4.0) and raw
    (status_item / status_system_0 log `TEXT 02157098`, `020B9240`, `021576C8`, matching `textwin.lua`'s new `at=`
    text address; `work/qa/cov_t3`). Report: `python -X utf8 $SKILL/scripts/textcover.py work/qa/cover
    work/qa/strings_cover1.tsv --waive docs/text_unshown.tsv`.
  - Coverage: the first sweep (`work/qa/cover/warp`, 06:31 build) finished only 61/307 scenes (the rest never ran:
    the runner died with the previous session). The other 246 (`work/qa/cover_todo.txt`, all map scenes +
    load_lowhp) were restarted 07:10 as the event tour into `work/qa/cover/events` (log `work/qa/cover_events.out`):
    `warp_all.py $(cat work/qa/cover_todo.txt) --cue build/blade_arts_en.cue --jobs 5 --debugger --probe
    tools/lua/textwin.lua --probe tools/lua/textcover.lua --var "TCTBL='<abs>/build/textcover_tbl.lua'" --var
    CIRCLE_EVERY=40 --var AFTER_FRAMES=6000 --out work/qa/cover/events --timeout 1200`. It runs ~10 min per scene
    (~8 h at 5 jobs): if `work/qa/cover/events/summary.tsv` is missing it is still running or died; re-run only the
    names without a proof.png. Report over both: `python -X utf8 $SKILL/scripts/textcover.py work/qa/cover
    work/qa/strings_cover1.tsv --waive docs/text_unshown.tsv`. Don't rebuild `build/` (main) while it runs: build
    graphics tests into `build/gfx` (`build.py --out build/gfx`).
  - Graphics text: pipeline built (`tools/gfx.py`, `tools/gfx_draw.py`, `gfx/gfx.tsv`, `tests/test_gfx.py`, OFL fonts
    in `fonts/ofl/`). Done in game: G1 title, G8 thanks, G6 Prestage (prologue title card), G7 all 14 stage cards,
    G5 flashback subtitles. G2 drawn, not yet seen in game. G3 not started. Per-row state and evidence:
    `docs/re/graphics.md` §Redraw status. `tools/clutfit.py` recovers a runtime-built CLUT from a JP screenshot (G7).
    Last gfx build `build/gfx/blade_arts_en.bin` 07:18 sha1 2e5a28bc..., smoke ok (`work/qa/smoke_gfx`).
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
- **Next (phase 8):** read the event-tour coverage (above) when it ends, waivers; graphics: G3 ending staff roll
  (`DATA/ENDINGP.BIN` @74E8, 4bpp 1188x500, black-on-white blocks of headings + kanji names; romanize per D3; the
  intro credits texture `M0/M02_10_0.PAC` @88CA4 already has English spellings for shared staff, e.g. 土田賢治 =
  Kenji Tuchida, Yoshitaka Oura, Nobuteru Yuuki: reuse them), G2 in-game shot; tours with visual-QA verdicts
  (`qa_gate.py`), stress saves, `inkbox.py` on choices. Card title: English location + ／TIME (D12), check the LOAD
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
