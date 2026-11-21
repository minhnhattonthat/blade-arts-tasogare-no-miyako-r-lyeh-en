# Disc layout

- One MODE2/2352 data track, 711 MB .bin (Redump hashes in `rom.sha1`). `dumpsxiso` extracts 356 files + `layout.xml`.
- `SLPM_866.02` EXE (PS-X EXE, t_addr 0x80010000, size 0xBB800, pc 0x8003FDA4). `SYSTEM.CNF`. `3MIN.DMY` padding (27 MB).
- `DATA/`: `*P.BIN`/`*.BIN` overlays (TITLEP, LOGOP, LOADSAVE, STATUS, BOSS0-5P, ENDINGP, GAMOVERP, THANKSP, GAME,
  EQUIPCHG, ROLLDEMO, STICON), `DATA1.PAC` (common archive, 120 entries), `SOL.SRP` (script text), `STATUS2.DAT`,
  `STICON.DAT`, `ENDING_P.DAT` (ending CGs).
- `M0/Mxx_yy_z.PAC` (302): per-room packs. Header u32 1?, u32 count, then count x (u32 sector, u32 size); entry 0 is a
  sub-archive (u32 count, u32 offsets...: TIMs, models), entry 1 a VAB (sound). Verified on M00_00_0.PAC.
- `DATA1.PAC`: u32 1, u32 0x78 (120), then (u32 sector, u32 size) pairs from offset 8. Verified: sector x 0x800 +
  size tiles the file. Entry 117 = VAB, 118 = font glyph order, 119 = font TIM.
- `NOR/`: boss models/textures (.D, .TIM, .DM3, .RB).
- `STR/XA.XA`, `XA2.XA`: interleaved XA audio (voice; `eNNNNN` codes in the script are likely clip ids). No subtitle
  data inside (the `CSA0` hits there are ADPCM noise).
- Identity rebuild (phase 3): mkpsxiso 2.30 repacks the dumpsxiso tree + layout byte-identical (sha1 c266b85e, ~6 s).
  `build.py` swaps patched files in with `<file source=ABS>` in a generated `build/layout.xml`. A file that grows
  shifts every later LBA: savestates and any hard-coded sector numbers (EXE file table?) must be checked then.
