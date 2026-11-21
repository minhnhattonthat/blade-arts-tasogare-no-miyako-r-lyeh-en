# Blade Arts: Tasogare no Miyako R'lyeh (PS1, Enix 2000, SLPM-86602) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Setup once per clone: `git config core.hooksPath tools/hooks`
- Unpack:   `tools/mkpsxiso/dumpsxiso.exe -x work/disc/tree -s work/disc/layout.xml "rom/<cue>"` (run from repo root; tree is gitignored)
- Build:    `python -X utf8 build.py` -> build/blade_arts_en.bin/.cue (not written yet; checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/blade_arts_en.cue --out work/qa/smoke --route tools/routes/boot.txt --smoke` (original: `rom/*.cue`)
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/blade_arts_en.cue --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (phase 2; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (xdelta vs the .bin; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/Blade Arts - Tasogare no Miyako R'lyeh (Japan).bin/.cue` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`).
- Emulator: PCSX-Redux nightly 32338.20261121.15 (x64) in `tools/pcsx/` (from distrib.app via `$SKILL/scripts/fetch_emu.py pcsx`; gitignored). BIOS SCPH-5500 in `tools/bios/` (`fetch_emu.py psx-bios`). Disc tools: `tools/mkpsxiso/` (mkpsxiso/dumpsxiso 2.30), `tools/armips/`. Savestates: `work/states/`.
- Text: `script/` (TSV, phase 4). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Title screen: circle confirms, cross does nothing; Start skips the sword intro.
- Script text (`DATA/SOL.SRP`) is Shift-JIS XORed with 0x8C; game font is a 1297-glyph table in `DATA/DATA1.PAC` (docs/re/README.md).
- Gotchas for the skill: `docs/skill-gotchas.md`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
