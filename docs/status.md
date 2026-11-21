# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next (phase 1 recon done 2026-11-21). Last build: none yet.
- **Done:**
  - Step 0: template, guard hook proven (sed -i blocked), pre-commit runs `tools/check.py` and rejects a failing test,
    `rom.sha1` (Redump .bin/.cue), PCSX-Redux + SCPH-5500 BIOS fetched, mkpsxiso/armips in `tools/`, smoke route
    `tools/routes/boot.txt` boots the original to the subtitled intro (exit 0), Lua probe logging works.
    Not verified: keyboard input in the PCSX-Redux GUI (no interactive session); `tools/emu-config/` not created
    (emu.py writes PCSX settings per run).
  - Phase 1 text: no earlier fan patch exists (web search 2026-11-21). All dialogue is `DATA/SOL.SRP` (SJIS XOR 0x8C,
    3351 strings, per-sector string pages) parsed by `tools/sol.py`; raw SJIS in EXE (item names), STATUS.BIN,
    LOADSAVE.BIN, BOSS0P/3P.BIN. Font = 1297-glyph table + 4-plane 1bpp TIM in DATA1.PAC. Notes: `docs/re/text.md`.
  - Phase 1 graphics: static sweep of every TIM on the disc done (`docs/re/graphics.md`): Japanese in G1 title
    subtitle/©, G2 STICON button labels, G3 ending staff roll, G5 sepia flashback subtitles (M05_02), G6 intro credit
    heading プレステージ (M02_10/M03_01), G7 stage-clear card (M50, black CLUT), G8 THANKSP "on sale summer 2000".
    Tools: `tools/timsweep.py` (dedup, `--gray`), `tools/timshow.py` (one TIM, all CLUT rows); test `tests/test_tim.py`.
- **Next (phase 2, debug tool):**
  1. Find the room/map loader: map id `Mxx_yy_z` (M0 PAC name) and the current SOL block in RAM (watch with
     `lua/probes/watch.lua`; flag 7->5 at 0x801DBE1C seen during the SOL.SRP load).
  2. `tools/debug/warp.lua` taking `SCENE=` (map id or named scene) from a cold boot; scene list in `tools/debug/`
     covering title, each stage, stage-clear card (G7), flashback (G5), intro credits (G6), each boss, ending (G3),
     game over, load/save, status/item menus. One proof shot per entry.
  3. Save editor (`save.py`) for memory-card saves if the warp can't set items/flags.
  Optional (phase 5 needs it): trace the SOL.SRP loader/XOR decoder.
- **Open bugs:** none.
- **Waiting on the user:** nothing (all once-per-project answers came with the dispatch: `docs/decisions.md`).
