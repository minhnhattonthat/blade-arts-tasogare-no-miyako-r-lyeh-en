# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/en11.txt | drawn for the owner's Nage Libre translation, copied from the owner's monster-guardians repo (`font/en11.txt`) | MIT, same owner | yes | all English text: 11x11 glyph slots 1297+ of DATA1.PAC 119 (VWF, `tools/font.py`) | none (rows 1-11 of the 13-row art used) |
| fonts/ofl/cinzel_Cinzel[wght].ttf | github.com/google/fonts `ofl/cinzel` (main, 2026-11-22) | SIL OFL 1.1 (`fonts/ofl/cinzel_OFL.txt`) | yes | title subtitle (G1), thanks screen line (G8), `tools/gfx_draw.py` | none |
| fonts/ofl/lato_Lato-Regular.ttf | github.com/google/fonts `ofl/lato` (main, 2026-11-22) | SIL OFL 1.1 (`fonts/ofl/lato_OFL.txt`) | yes | title (c) line (G1) | none |
| fonts/ofl/crimsontext_CrimsonText-Regular.ttf | github.com/google/fonts `ofl/crimsontext` (main, 2026-11-22) | SIL OFL 1.1 (`fonts/ofl/crimsontext_OFL.txt`) | yes | intro credits heading "Prestage" (G6) | none |
