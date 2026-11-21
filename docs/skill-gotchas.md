# Skill gotchas

One line per gotcha: the skill reference file it belongs in, then the fact.

- platform-ps1.md: Blade Arts script text (DATA/SOL.SRP) is Shift-JIS XORed with 0x8C, so a raw SJIS scan of the disc finds only item names and menus; find it by dumping RAM while text shows, then searching the disc for the bytes next to the decoded text (here a string-offset table).
- platform-ps1.md: on this game's title screen circle confirms and cross does nothing, so `--mash-key cross` idles into the attract demo; check which button confirms before mashing.
- graphics.md §Survey: a TIM sweep drawn with each TIM's first CLUT hid Japanese twice here (stage-clear card and "on sale summer 2000" screen had all-black first CLUTs; some TIMs are flagged 16bpp over 4bpp data and draw as noise); re-draw every near-black or noisy TIM with palette indices as grey (`tools/timsweep.py --gray`). Dedup identical TIMs across map packs first (1525 -> 157 here).
- emulator-qa.md §Debug tool: grep the EXE for the map-file format string (`M%02d_%02d_%x`) and for leftover debug-menu strings first: here they gave the current-map variable (via the format call) and a full stage/event/boss list in minutes; a "SELECT Stage" menu drawn with FntPrint is invisible in a retail build, so reuse its data, not its screen.
- emulator-qa.md §Debug tool (PS1): forcing a top-level program/overlay switch from the field reset the console (PC 0xBFC00000) while the same request from the title worked; when an emu.py run "times out" with frames stopped, register an `ExecutionFlow::Pause` listener that logs the PC: a pause at 0xBFC00000 is a crash-reset, not a slow load.
- emulator-qa.md §emu.py: `--var MASH=...` is rejected (driver global); a warp script that needs its own circle-mash must use another name, and emu.py's `--mash` fires during boot too, before the warp.
- emulator-qa.md §Per-emulator (PCSX-Redux): the title menu's default cursor (Continue vs New Game) can depend on the memory card; give every scripted run its own card (`--sav` blank) instead of the portable card beside the exe.
- emulator-qa.md: a boot route timed from a play.py session's savestate is not frame-exact from a cold boot (the play state was taken late); retime routes on a cold `emu.py --sheet` run.
