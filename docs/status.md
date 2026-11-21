# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (text recon done; graphics-text sweep half done). Last build: none yet (2026-11-21).
- **Done:**
  - Step 0: template, guard hook proven (sed -i blocked), pre-commit runs `tools/check.py` and rejects a failing test,
    `rom.sha1` (Redump .bin/.cue), PCSX-Redux + SCPH-5500 BIOS fetched, mkpsxiso/armips in `tools/`, smoke route
    `tools/routes/boot.txt` boots the original to the subtitled intro (exit 0), Lua probe logging works.
    Not verified: keyboard input in the PCSX-Redux GUI (no interactive session); `tools/emu-config/` not created
    (emu.py writes PCSX settings per run).
  - Phase 1 text: no earlier fan patch exists (web search 2026-11-21). All dialogue is `DATA/SOL.SRP` (SJIS XOR 0x8C,
    3351 strings, per-sector string pages) parsed by `tools/sol.py`; raw SJIS in EXE (item names), STATUS.BIN,
    LOADSAVE.BIN, BOSS0P/3P.BIN. Font = 1297-glyph table + 4-plane 1bpp TIM in DATA1.PAC. Notes: `docs/re/text.md`.
  - Phase 1 graphics: UI TIMs reviewed; Japanese in TITLEP subtitle, STICON button labels, ENDINGP staff roll
    (`docs/re/graphics.md`).
- **Next (to finish phase 1):**
  1. Read sweep sheets `work/gfx/sweep_data/sheet_0000-0011, 0014-0016` (rebuild with the timsweep command in
     graphics.md if work/ is gone) and list Japanese cells; render every CLUT of STICON.BIN.
  2. Run `tools/timsweep.py` over `work/disc/tree/M0/*.PAC` and review (map signs/monitors).
  3. Optional for phase 1, needed by phase 5: trace the SOL.SRP loader/XOR decoder (watch flag 7->5 at 0x801DBE1C).
  Then phase 2 (debug tool: warp by map id `Mxx_yy_z` / SOL block).
- **Open bugs:** none.
- **Waiting on the user:** nothing (all once-per-project answers came with the dispatch: `docs/decisions.md`).
