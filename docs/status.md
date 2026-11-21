# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7. Insert, fit, check in progress (phase 6 translate done 2026-11-22: 19 batches, `batches.py check`
  0 problems; every batch reviewed incl. b001 (`docs/reviews/b001.report.md`); the harness phase-6 review's Important
  findings fixed and re-reviewed (`docs/reviews/fix01.report.md`): save prompt, 石碑/隊長/大将/我流 glossary rows,
  villain 貴様 "you wretch", Millers, ellipsis rule D11 (lint in `batches.py`). Minors in `docs/polish.md`).
  Last good build: pilot build (b001 only) 2026-11-22, smoke ok; marker build still builds (`--marker`).
  **Phase 7 so far:** raw strings done: `build.py raw_texts` writes in place up to the next 4-byte boundary, else
  moves the string into the EXE free area after `vwf_end` (asm/vwf.asm label, read from the armips `-sym` file) and
  repoints its data-word refs (all 88 movable ones are data words; `+k` refs were coincidental lui hits), zeroing the
  old bytes. Every write is logged (`Writes`, build/writes/*.txt); romdiff.py with those logs passes on the marker
  build for all 6 patched files. Card-title budget enforced (D12, tail ／TIME). BOSS lines shortened (D13).
  **Blocker for the full build: SOL.SRP block overflow** (`sol.pack` now lists all): blocks 24, 26, 117, 176 (2 sectors,
  need 3), 43, 53 (1 -> 2), 62, 159 (7 -> 8), 132 (6 -> 7), 173 (3 -> 4); ~1.2 KB over in total, 92 KB free elsewhere.
  Block id = sector offset, set by script opcodes through 0x80037930 (no jal callers: an opcode table), load at
  0x8003793C: `jal 0x80077958(name, dest, a2 = s1 >> 11 sectors, a3 = sector)` at 0x8003796C.
  Plan (D4: engine before cutting text): hook that jal -> remap table {old sector: new sector} in the EXE free area, and
  append the grown blocks at the end of SOL.SRP (old copy stays). First probe at runtime (Lua exec hook on 0x8003796C)
  what a2 (sectors read) and the dest buffer size are: a grown block (8 sectors for 62/159; header u16 table allows 2/4/8
  sectors by hdr_size 0x0C/0x10/0x18) must fit both. Fallback: trim English in those blocks (and dedupe identical
  strings inside a sector: offsets may share data; flags 7->5 marks decoded, so a shared string isn't re-XORed - verify).
  Then: full build, a romdiff test (tests/, writes inside allowed regions: text spans, pointer words, free area, hook
  sites, font), smoke.
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
- **Next (phase 7):** SOL block overflow (plan in the Phase field), then full build, romdiff test, smoke; then
  phase 8. Card title: English location + ／TIME (D12), check the LOAD list and the title length in game.
- **Open for later phases (not blocking):**
  - Check in game (phase 8): choices where translators added `\\` before `{[DD1}` (sol.98.3, 100.3, 103.2), `{g9}`
    spaced options (72.5, 72.40), digit pickers (62.140-143, 69.22-25), sol.169.0 (voiced, @@ re-split, same screen
    count), sol.132.110 written `{CSA0t4b4}` (JP had a bare `b`), centring of t0 panel lines in blocks 125/147/159/166.
  - SOL space is per block (7 sectors max for block 159; growing a block shifts later block ids): phase 7 lint must
    check per-block bytes; marker filler at JP width only overflowed block 159 (90%).
  - Memory-card title: LOADSAVE 0x22C "ブレイドアーツ／" is written into each save and 0x6D0/0xBDC must match it or the
    load list rejects the file (verified by bisecting the marker build): keep all three Japanese. The title also
    holds "／ＴＩＭＥ" and the location name, shown by the BIOS card manager in Shift-JIS: English location names
    in letter bytes would be garbage there; phase 7 must give the title a fullwidth/SJIS copy or keep it JP.
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
