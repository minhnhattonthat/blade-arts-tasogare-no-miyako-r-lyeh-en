# Translator brief - Blade Arts: Tasogare no Miyako R'lyeh (PS1, Enix 2000)

You translate part of the Japanese script of Blade Arts: Tasogare no Miyako R'lyeh into English for a fan patch.
Cthulhu-mythos action adventure: Rei Shido, a cocky treasure hunter, explores ancient ruins on a volcanic island that
rose from the Pacific after an earthquake, with Ranfa navigating him by radio.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents. Read long files in parts (offset/limit): an
output-trimming plugin replaces whole-file reads above ~4 KB with a stub.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table and style rules in `glossary.md`).
3. `docs/synopsis.md` - plot, who is who and the late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. Ids are in script order (`sol.<block>.<n>`; neighbours are context).
The Japanese carries the game's control codes in braces, e.g.
`{t4b6}マリオン：{b0}心配しないでも良いわよ‥‥{i060}@@{t4b6}マリオン：{b0}シゴトしてくれたら、\\キチンと殺してあげるから‥‥{i060}`.
- `{...}` = control codes: copy every one into the English (same codes, same count; keep them where they belong:
  `{b4}`/`{b6}`... start a coloured speaker name or highlighted term, `{b0}` ends it; `{iNNN}` is a pause; `{eNNNNN}`
  a voice clip; `{[DD1}` `{[2}` start choice options; `WP...WS...` blocks set up a window). You may split a brace
  group into several (`{t4b6}` = `{t4}{b6}`) but never change a code.
- `\\` (two backslashes) = line break, `@@` = page break (waits for a button). Write them bare, as in the JP.
- `{gN}` (N = 0-9) = move right N px: the only code you may add, drop or move (spacing in choices and headings).
- Raw strings (ids like `DATA/STATUS.BIN:00748`, `SLPM_866.02:...`) use `{n}` for a line end and `{%s}` for printf
  fields; keep them. Their `\\` (STATUS descriptions) is a line break too.
- `form` / `limit`: the box and its hard limit, e.g. `subtitle` `288px x2` = at most 2 lines of 288 px per page.
  `voiced:keep@@` = the line plays with a voice clip that cuts extra pages: keep exactly the JP's number of `@@`.
  Unvoiced strings may add pages with `@@` when the text needs room. ws`ccll` windows: cc*12 px, ll lines.
  `choice`: the question, then options after `{[DD1}` / `{[N}`; put each option where the JP puts it and space them
  with `{gN}` codes or plain spaces instead of the JP's fullwidth padding.
  `loadsave` (location names, 200 px), `status` (item descriptions, 252 px x3), `exe` (item names), `boss` (286 px x2).
- Speaker labels: `{t4b6}マリオン：{b0}` -> `{t4b6}Marion:{b0} ` (a space after the colon, outside the colour).
  Leading fullwidth spaces `　` in t4/t5 dialogue are indentation: drop them or keep them, your call per scene, but
  be consistent within a scene.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. ASCII from the font: letters, digits, space and
``!"%&'()*+,-./:;=?[]~`` only (no # $ < > @ \ ^ _ ` { | } except in codes, no curly quotes, no em dash: use `--`).
Fullwidth symbols that the JP line itself contains may be kept (○ △ □ × ★ ＜ ＞ and `　`). No Japanese, no tabs.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.
Dry-run one line: `python -X utf8 tools/batches.py fit '<english>' subtitle` (or ws2203, choice, status, boss, exe,
loadsave) prints the px width of each line. 288 px is roughly 55 characters of mixed-case text.
Warnings ("bytes > in place") are fine: those raw strings get relocated later. Don't cut meaning for them.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible. JP register markers carry voice and must turn into English devices, not vanish:
  Rei's てめぇ/〜ねぇ/〜やがる ("you bastard", "ain't gonna", clipped and cocky), Marion's アナタ/〜わよ (mocking, purring),
  Tindalos's うぬ/貴様 (arrogant, archaic), the ancients' 汝/我/〜せよ (thou/thee, solemn), Ranfa's 〜よね/〜かなー
  (bright, teasing). A line any speaker could have said is a mistake.
- Use names and terms exactly as in the glossary. Never abbreviate to fit: rephrase, add a page (unvoiced) or keep
  the meaning and report `LONG: id`.
- Honorifics kept (Nakamura-sama, Lizzie-chan, Kiki-kun); ミスター/ドクター -> Mr./Dr.; Western name order.
- Punctuation: 「」 -> "...", 『』 -> '...', ‥‥/・・・ -> `...`, ！？ -> `!?`, ～ -> `~`; ＜X＞ headings keep ＜＞.
- Identical strings were deduplicated: each id stands for every copy of its text, so translate it to read well alone.
- Item names and pick-up lines (`Xを手に入れた。` -> "Got the X.", `Xを取りますか？` -> "Take the X?") stay uniform.
- Debug/dev placeholders that a player can still meet (`＜...イベント＞誠意制作中、乞うご期待！！`) are translated too
  ("＜... event＞ Under construction, stay tuned!!").

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
