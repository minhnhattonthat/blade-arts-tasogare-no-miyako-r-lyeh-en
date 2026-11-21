# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build next (phase 2 debug tool done 2026-11-22). Last build: none yet.
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
- **Next (phase 3, identity build):** `mkpsxiso -y work/disc/layout.xml` from `work/disc/tree/` and compare the .bin
  sha1 with `rom.sha1` as a test; then `build.py` skeleton.
- **Open for later phases (not blocking):**
  - Inventory (ITEM list), item box contents, nerves and story flags are not mapped: phase 8 stress saves need them
    (`tools/debug/save_layout.md` lists the leads: 0x800BABD0 table, add-item code 0x8003874C).
  - 19 map packs never finish loading from a direct warp (list in `docs/re/debug.md`); reach them via the previous map
    if phase 8 text coverage needs them.
  - The ending's CAST roll shows Japanese names (ENDINGP; part of G3, check whether TIM or text in phase 8).
  - Map packs and states: regenerate with `warp_all.py --states` after any engine/font/graphics change.
- **Open bugs:** none.
- **Waiting on the user:** nothing (all once-per-project answers came with the dispatch: `docs/decisions.md`).
