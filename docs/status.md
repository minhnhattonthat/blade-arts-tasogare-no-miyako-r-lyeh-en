# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build next (phase 4 extract done 2026-11-22). Last build:
  `build/blade_arts_en.bin` 2026-11-22, sha1 c266b85e (= original, no edits), smoke ok.
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
- **Next (phase 5, engine spike + marker build):** font decision (ASCII letters collide with control codes `b t e i g
  [ @ \`: needs an escape or new glyph range, and a VWF or half-width font: `docs/re/text.md`); find the SOL decoder
  and renderer (watch the flag word 7->5); then `build.py patches()` inserts `[id]` markers (SOL via `sol.pack`, raw
  strings in place within `room`) and the width gate per box type. Boss lines (6) have no pointer found: keep in place.
- **Open for later phases (not blocking):**
  - Inventory (ITEM list), item box contents, nerves and story flags are not mapped: phase 8 stress saves need them
    (`tools/debug/save_layout.md` lists the leads: 0x800BABD0 table, add-item code 0x8003874C).
  - 19 map packs never finish loading from a direct warp (list in `docs/re/debug.md`); reach them via the previous map
    if phase 8 text coverage needs them.
  - The ending's CAST roll shows Japanese names (ENDINGP; part of G3, check whether TIM or text in phase 8).
  - Map packs and states: regenerate with `warp_all.py --states` after any engine/font/graphics change.
- **Open bugs:** none.
- **Waiting on the user:** nothing (all once-per-project answers came with the dispatch: `docs/decisions.md`).
