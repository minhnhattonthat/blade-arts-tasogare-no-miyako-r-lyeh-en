# Reverse-engineering notes

One file per subsystem. Mark every finding with how far it is proven: **verified** (and how) or **guess** (and why).
Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [text.md](text.md) | text sources, SOL.SRP format (XOR 0x8C), control codes, font table + font TIM, free space | format verified (parser + test); control-code meanings partly guessed; loader/decoder code not traced |
| [graphics.md](graphics.md) | graphics-text survey (TIM sweep) | static sweep done (all TIM files, incl. black-CLUT and 16bpp-flagged TIMs in grey); runtime checks listed for phase 8 |
| [debug.md](debug.md) | programs, game modes, map id, warp method, leftover debug stage list, saves | warp + save verified; inventory and story flags not found |
| [disc.md](disc.md) | disc layout, archives (PAC), overlays | verified headers |
