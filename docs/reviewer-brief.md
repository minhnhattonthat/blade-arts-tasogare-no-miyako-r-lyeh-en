# Translation reviewer brief - Blade Arts: Tasogare no Miyako R'lyeh

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, font characters, px width, page counts of voiced lines) is already enforced
by `tools/batches.py check` - judge translation quality. Return the report as your final message: the controller
saves it. Read long files in parts (offset/limit ~60 lines): an output-trimming plugin stubs whole-file reads above
~4 KB.

## Inputs (paths in your dispatch)
- Pairs file `work/qa/review/<batch>.pairs.txt`: every entry as `>> id | form limit | JP` then the English, in script
  order (neighbours are context). Codes are in braces (`{b4}`, `{i060}`, `{eNNNNN}` voice); `\\` = line break,
  `@@` = page break. Read ALL of it, in passes.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, `docs/synopsis.md` (rough outline; the script wins).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; voice matches the style reference.
- Things players caught that reviewers missed: jokes losing their punch; abbreviated names or terms; awkward stock
  phrases ("... GET!"); a reveal given away early.
- Voice: Rei's rough swagger (てめぇ, 〜やがる), Ranfa's teasing brightness, Marion's purring menace, Tindalos's
  archaic arrogance (貴様, うぬ), the ancients' thou/thee register, soldiers' stretched shouts. Register flattened into
  neutral prose is Important, not Minor.
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, wrong speaker, broken codes in effect)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, a voice flattened, joke dead)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN` (suggested EN with the same codes, `\\` and `@@`).
### Assessment
Approved | Needs fixes - one sentence why.
