Blade Arts: Tasogare no Miyako R'lyeh - English translation patch v{VERSION}
============================================================================

Unofficial English fan translation of Blade Arts: Tasogare no Miyako R'lyeh (PlayStation, Enix, 2000, SLPM-86602).
https://github.com/minhnhattonthat/blade-arts-tasogare-no-miyako-r-lyeh-en

This zip holds only the patch ({PATCH}) and this README. No game data is included, and
pre-patched images will never be provided: you need your own dump of the Japanese disc.

BASE IMAGE (Redump "Blade Arts - Tasogare no Miyako R'lyeh (Japan)", single track, MODE2/2352)
  File:   Blade Arts - Tasogare no Miyako R'lyeh (Japan).bin
  Size:   711,352,992 bytes
  CRC32:  A355EE12
  MD5:    8768ac868bba4298f076fa2df9e22a73
  SHA-1:  c266b85e1af7fa57605814e0c47fd68f002998c8
Any other dump (another revision, a different track layout, an already-patched copy) will not work.

PATCHING
  1. Apply {PATCH} to "Blade Arts - Tasogare no Miyako R'lyeh (Japan).bin" with xdelta3 or Delta Patcher
     (https://github.com/marco-calautti/DeltaPatcher):
       xdelta3 -d -B 711352992 -s "Blade Arts - Tasogare no Miyako R'lyeh (Japan).bin" {PATCH} "Blade Arts (English).bin"
  2. Copy the original .cue next to the new .bin, rename it to "Blade Arts (English).cue"
     and change the FILE line inside it to "Blade Arts (English).bin".
  3. Check the result:  CRC32 {PATCHED_CRC32}
                        SHA-1 {PATCHED_SHA1}

PLAYING
  Tested in PCSX-Redux (nightly 32338.20261121.15) with the SCPH-5500 BIOS. Boot the patched disc from a cold
  start; savestates made with the Japanese disc carry its old text and code. Start a new game: memory-card saves from
  the Japanese game are untested. Circle confirms; Start skips the sword intro.

WHAT IS TRANSLATED
  Story dialogue and voiced-scene subtitles (all 3351 script messages) ... English
  Menus, items, Spheres, memory-card and system messages ................ English
  Title screen, stage title cards, flashback subtitles .................. English (redrawn)
  Ending staff roll, thank-you screen ................................... English (redrawn)
  Voice acting .......................................................... Japanese audio, English subtitles

KNOWN ISSUES
  - The memory-card title starts with the Japanese game name (the game looks for it) and the location part is
    plain English letters, so the console's own memory-card manager shows that part as garbled characters.
    The game's LOAD list shows it correctly.
  - A few lines keep the Japanese layout's leading spaces and sit slightly right of centre, as in the original.
  - Staff names in the credits have no furigana on the disc; some readings are best guesses.
  Report bugs (with a savestate or memory card if you can):
  https://github.com/minhnhattonthat/blade-arts-tasogare-no-miyako-r-lyeh-en/issues

CREDITS
  Translation, hacking and tools: minhnhattonthat.
  Made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
  Fonts: an 11-px pixel font drawn for this project's author; Cinzel, Lato and Crimson Text (SIL Open Font
  Licence 1.1) for the redrawn title screen, thank-you screen and title cards.
  Blade Arts: Tasogare no Miyako R'lyeh is (c) Enix (now Square Enix). This is an unofficial fan work, not
  affiliated with them.
