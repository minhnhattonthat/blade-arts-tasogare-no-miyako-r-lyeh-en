"""Run tools/debug/warp.lua for every scene in tools/debug/scenes.tsv (or the named ones), each from a cold boot.

  python -X utf8 tools/debug/warp_all.py [NAME|PREFIX* ...] [--cue build/blade_arts_en.cue] [--jobs 3] [--states]
      [--shot-every 120] [--out work/qa/warp]

Per scene: <out>/<name>/ (shots, proof.png, log.txt), with --states also work/states/<name>.sstate.
Scenes named save_* leave the card the game wrote in work/saves/<name>.mcd (the base for tools/debug/save.py edits);
run them before the scenes whose sav column reads those cards (run `warp_all.py "save_*"` first).
Writes <out>/summary.tsv (name, ok, arrival frame, map it settled on, program, error) and <out>/proofs*.png (every proof.png in one sheet).
Exit 1 if any scene failed to arrive. Regenerate the state library after engine/font/graphics changes: --states.
"""
import argparse, concurrent.futures as cf, csv, fnmatch, os, re, shutil, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, 'tools'))
sys.path.insert(0, os.path.join(REPO, 'tools', 'debug'))
from skill import SKILL  # noqa: E402
import save  # noqa: E402

ORIG = 'rom/Blade Arts - Tasogare no Miyako R\'lyeh (Japan).cue'


def scenes():
    with open(os.path.join(REPO, 'tools/debug/scenes.tsv'), encoding='utf-8', newline='') as f:
        rows = [r for r in csv.reader(f, delimiter='\t') if r and not r[0].startswith('#')]
    head = rows[0]
    assert head == ['name', 'map', 'mode', 'prog', 'poke', 'after', 'frames', 'sav', 'note'], head
    for r in rows[1:]:
        assert len(r) == len(head), r
    return [dict(zip(head, r)) for r in rows[1:]]


def card_in(sc, out):
    """out/card_in.mcd for the scene. Every run gets its own card, never PCSX's shared portable one: "blank"
    (default), a card path, or "<save scene>+field=v,0xOFF=v" = work/saves/<save scene>.mcd edited by save.py."""
    os.makedirs(out, exist_ok=True)
    sav, _, edits = (sc['sav'] or 'blank').partition('+')
    if sav == 'blank':
        data = save.blank()
    else:
        src = os.path.join(REPO, 'work/saves', sav + '.mcd') if '/' not in sav else os.path.join(REPO, sav)
        data = open(src, 'rb').read()
        if edits:
            data = save.edit(data, edits.split(','))
    sav = os.path.join(out, 'card_in.mcd')
    open(sav, 'wb').write(data)
    return sav


def run(sc, a):
    out = os.path.join(a.out, sc['name'])
    cmd = [sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'emu.py'), a.cue, '--out', out,
           '--script', os.path.join(REPO, 'tools/debug/warp.lua'),
           '--var', "SCENE='%s'" % sc['name'], '--var', 'REPO=[[%s]]' % REPO.replace('\\', '/'),
           '--frames', '30000', '--timeout', str(a.timeout)]
    if a.shot_every:
        cmd += ['--shot-every', str(a.shot_every), '--sheet']
    for p in a.probe:
        cmd += ['--script', p]
    for v in a.var:
        cmd += ['--var', v]
    if a.debugger:
        cmd += ['--debugger']
    if a.states:
        cmd += ['--state-out', os.path.join(REPO, 'work/states', sc['name'] + '.sstate')]
    cmd += ['--sav', card_in(sc, out)]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding='utf-8', errors='replace')
    card = os.path.join(out, 'memcard1.mcd')
    if p.returncode == 0 and sc['name'].startswith('save_') and os.path.exists(card):
        os.makedirs(os.path.join(REPO, 'work/saves'), exist_ok=True)
        shutil.copyfile(card, os.path.join(REPO, 'work/saves', sc['name'] + '.mcd'))
    log = ''
    try:
        log = open(os.path.join(out, 'log.txt'), encoding='utf-8', errors='replace').read()
    except OSError:
        pass
    m = re.search(r'WARP arrived \S+ frame (\d+) map (\S+) prog (\d+)', log)
    ok = p.returncode == 0 and m is not None and os.path.exists(os.path.join(out, 'proof.png'))
    err = [x for x in (p.stdout + p.stderr).splitlines() if 'Lua error' in x or x.startswith('exit ')]
    return (sc['name'], ok, m.group(1) if m else '', m.group(2) if m else '', m.group(3) if m else '',
            '' if ok else (err or ['?'])[0])


def flat(png):
    from PIL import Image, ImageStat
    return ImageStat.Stat(Image.open(png).convert('L')).stddev[0] < 6


def proof(d):
    """proof.png, or the last non-flat shot after arrival when the proof frame lands in a fade or flash."""
    p = os.path.join(d, 'proof.png')
    if not flat(p):
        return p
    m = re.search(r'WARP arrived \S+ frame (\d+)', open(os.path.join(d, 'log.txt'), encoding='utf-8').read())
    shots = sorted(f for f in os.listdir(d) if re.match(r'f\d{6}\.png$', f) and int(f[1:7]) >= int(m.group(1)))
    for f in reversed(shots):
        if not flat(os.path.join(d, f)):
            return os.path.join(d, f)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='*')
    ap.add_argument('--cue', default=ORIG)
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--states', action='store_true')
    ap.add_argument('--shot-every', type=int, default=120)
    ap.add_argument('--timeout', type=int, default=240)
    ap.add_argument('--out', default='work/qa/warp')
    ap.add_argument('--probe', action='append', default=[], help='extra emu.py --script (e.g. a RAM-dump probe)')
    ap.add_argument('--var', action='append', default=[], help='extra emu.py --var NAME=LUA')
    ap.add_argument('--debugger', action='store_true', help='emu.py --debugger (exec hooks: tools/lua/textwin.lua)')
    a = ap.parse_args()
    todo = [s for s in scenes() if not a.names or any(fnmatch.fnmatch(s['name'], n) for n in a.names)]
    if not todo:
        sys.exit('no scene matches %s' % a.names)
    os.makedirs(a.out, exist_ok=True)
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda s: run(s, a), todo))
    with open(os.path.join(a.out, 'summary.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['name', 'ok', 'arrived', 'map', 'prog', 'note'])
        w.writerows(res)
    proofs = [proof(os.path.join(a.out, r[0])) for r in res if r[1]]
    if proofs:
        subprocess.run([sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'sheet.py'), *proofs,
                        '--out', os.path.join(a.out, 'proofs.png'), '--div', '2'], cwd=REPO, capture_output=True)
    bad = [r for r in res if not r[1]]
    print('%d/%d scenes arrived; summary %s' % (len(res) - len(bad), len(res), os.path.join(a.out, 'summary.tsv')))
    for r in bad:
        print('FAIL', r[0], r[-1])
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
