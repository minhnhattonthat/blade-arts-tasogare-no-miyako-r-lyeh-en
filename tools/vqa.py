"""Visual QA by `codex exec` (read-only), one run per qa_gate chunk: the worker setup has no subagents.

  python -X utf8 tools/vqa.py work/qa/chunks/chunk_*.txt [--verdicts work/qa/verdicts] [--jobs 3]

Per chunk: the prompt is docs/visual-qa-brief.md plus each sheet's id, path and its .txt sidecar (expected text per
tile, tools/solview.py --report); the sheets go in as images. Codex can't write in its sandbox, so it returns the
verdict lines and this writes <verdicts>/<chunk stem>.tsv, only when every id of the chunk got one ok/issue line
(else the raw answer is kept as <stem>.raw.md and the chunk counts as failed). Exit 1 if any chunk failed.
"""
import argparse, concurrent.futures as cf, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAIL = """
## Output (this run)
You can't write files here. Instead end your answer with one line per sheet id, exactly:
VERDICT<TAB>id<TAB>ok|issue<TAB>note
(a real tab character between fields; the note says which tile and what is wrong, or is empty for ok).

## Sheets in this chunk
"""


def run(chunk, verdicts):
    rows = [ln.split("\t") for ln in chunk.read_text(encoding="utf-8").splitlines() if "\t" in ln]
    prompt = (ROOT / "docs" / "visual-qa-brief.md").read_text(encoding="utf-8") + TAIL
    images = []
    for k, (sid, path) in enumerate(rows, 1):
        p = Path(path)
        side = p.with_suffix(".txt")
        prompt += f"\n### Image {k}: id {sid}\n"
        if side.exists():
            prompt += "Tiles (tile, shot, expected text):\n" + side.read_text(encoding="utf-8")
        images.append(f"--image={p.resolve()}")
    out = verdicts / f"{chunk.stem}.raw.md"
    out.unlink(missing_ok=True)
    cmd = [shutil.which("codex"), "exec", "-s", "read-only", "--skip-git-repo-check", "-C", str(ROOT), *images,
           "-o", str(out), "-"]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=3600)
    ans = out.read_text(encoding="utf-8") if out.exists() else ""
    got = {}
    for ln in ans.splitlines():
        m = re.match(r"\s*VERDICT\s*\t\s*(\S+)\s*\t\s*(ok|issue)\s*(?:\t(.*))?$", ln)
        if m:
            got[m[1]] = (m[2], (m[3] or "").strip())
    missing = [sid for sid, _ in rows if sid not in got]
    if missing or r.returncode:
        return chunk.stem, f"FAILED (exit {r.returncode}, {len(missing)} ids without a verdict): {out}"
    (verdicts / f"{chunk.stem}.tsv").write_text(
        "".join(f"{sid}\t{got[sid][0]}\t{got[sid][1]}\n" for sid, _ in rows), encoding="utf-8")
    out.unlink()
    issues = [f"  {sid}: {got[sid][1]}" for sid, _ in rows if got[sid][0] == "issue"]
    return chunk.stem, f"{len(rows) - len(issues)} ok, {len(issues)} issue" + "".join("\n" + i for i in issues)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chunks", nargs="+")
    ap.add_argument("--verdicts", default="work/qa/verdicts")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    verdicts = Path(a.verdicts)
    verdicts.mkdir(parents=True, exist_ok=True)
    bad = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for stem, msg in ex.map(lambda c: run(Path(c), verdicts), a.chunks):
            print(f"{stem}: {msg}", flush=True)
            bad += msg.startswith("FAILED")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
