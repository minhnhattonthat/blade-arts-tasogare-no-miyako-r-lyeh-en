# Skill gotchas

One line per gotcha: the skill reference file it belongs in, then the fact.

- platform-ps1.md: Blade Arts script text (DATA/SOL.SRP) is Shift-JIS XORed with 0x8C, so a raw SJIS scan of the disc finds only item names and menus; find it by dumping RAM while text shows, then searching the disc for the bytes next to the decoded text (here a string-offset table).
- platform-ps1.md: on this game's title screen circle confirms and cross does nothing, so `--mash-key cross` idles into the attract demo; check which button confirms before mashing.
- graphics.md §Survey: a TIM sweep drawn with each TIM's first CLUT hid Japanese twice here (stage-clear card and "on sale summer 2000" screen had all-black first CLUTs; some TIMs are flagged 16bpp over 4bpp data and draw as noise); re-draw every near-black or noisy TIM with palette indices as grey (`tools/timsweep.py --gray`). Dedup identical TIMs across map packs first (1525 -> 157 here).
- emulator-qa.md: a boot route timed from a play.py session's savestate is not frame-exact from a cold boot (the play state was taken late); retime routes on a cold `emu.py --sheet` run.
