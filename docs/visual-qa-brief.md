# Visual-QA reviewer brief - Blade Arts: Tasogare no Miyako R'lyeh (PS1)

You review contact sheets from the English build's QA runs and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Beside each sheet, `<sheet>.txt`: one line per tile in row-major order, `tile<TAB>shot<TAB>expected text`
  (" / " between lines; codes stripped). Compare what the tile shows against it.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- `glossary.md` for names.

## Sheets
- `work/qa/solview/sheets/bNNN_sub_*`: subtitle-window messages of SOL block NNN, each tile the subtitle rows
  (y 192-238 of the 320x240 screen) at 1:1, one tile per page, 3 per row. Inline Yes/No choices draw here too.
- `bNNN_ws_*`: messages with their own window (WS code), whole 320x240 screens, one tile per page.
- They come from `tools/solview.py`: every message is swapped into the intro scene at its message lookup, so the
  game's renderer, font and window code draw it, but the scene behind it is always the intro.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 <skill>/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- Zoom into every Yes/No prompt and selection box.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame or the tile edge, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- the tile's text differs from its expected line (missing words, lines merged or split elsewhere);
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty tile where the .txt expects text;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- the intro's pictures (sea, cliffs, explosion, people) behind or over the text: the host scene, not the message;
- a choice box with no frame or no cursor (the frame and cursor come from the map script, not the string);
- the first option of a WS selection list sitting a few pixels left of the others (the cursor column);
- an expected line that is blank or only spaces: some messages are pauses or voice-only;
- a box mid-fade (text dimmer than usual).

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
