# Blade Arts: Tasogare no Miyako R'lyeh English translation

Unofficial English fan translation of **Blade Arts: Tasogare no Miyako R'lyeh** (PlayStation, Enix, 2000): the source
text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
or memory card helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story (all 3351 script messages, voiced-scene subtitles included) | Translated |
| Menus, items, Spheres, memory card and system messages | Translated |
| Title screen, stage title cards, flashback subtitles, ending staff roll, thank-you screen | Translated (redrawn) |
| Name entry | None in the game |
| Voice acting | Japanese audio, English subtitles |

Known issues: none known; see [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched disc

Needs Python 3.12+ and your own dump of the Japanese game (Redump "Blade Arts - Tasogare no Miyako R'lyeh (Japan)",
SLPM-86602).

```sh
git clone https://github.com/minhnhattonthat/blade-arts-tasogare-no-miyako-r-lyeh-en
cd blade-arts-tasogare-no-miyako-r-lyeh-en
# copy your dump to: rom/Blade Arts - Tasogare no Miyako R'lyeh (Japan).bin (+ .cue)
#   (711352992 bytes, SHA-1 c266b85e1af7fa57605814e0c47fd68f002998c8; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # unpacks once, -> build/blade_arts_en.bin/.cue
python -X utf8 tools/check.py                          # tests + text lint
```

`tools/mkpsxiso/` (mkpsxiso/dumpsxiso 2.30) and `tools/armips/` are not in git: put those releases there first.

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Enix's (now Square Enix) and is included
only so the translation can be checked against it. Blade Arts: Tasogare no Miyako R'lyeh is (c) Enix; this project is
not affiliated with them. Do not share patched disc images.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
