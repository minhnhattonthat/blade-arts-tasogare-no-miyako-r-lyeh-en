"""Translation lint (tools/batches.py): the rules catch what they should, and every shipped English line passes them."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import batches  # noqa: E402

ENTRIES = batches.index()


def test_braced_keeps_codes():
    for e in ENTRIES.values():
        if batches.needs_english(e) and e["id"] != "sol.132.110":  # its bare b counts as b4 on purpose
            assert batches.code_atoms(e["jp"], True) == batches.code_atoms(batches.braced(e["jp"]), False), e["id"]


def test_rules():
    e = ENTRIES["sol.125.59"]  # t4b6マリオン：b0心配しないでも良いわよ‥‥i060@@t4b6マリオン：b0シゴトしてくれたら、\\...
    good = "{t4b6}Marion:{b0} Don't you worry...{i060}@@{t4b6}Marion:{b0} Do your job,\\\\and I'll kill you nicely...{i060}"
    assert batches.problems(e, good, batches.glossary()) == []
    assert any("control codes" in p for p in batches.problems(e, good.replace("{i060}", "", 1), []))
    assert any("lines on a page" in p for p in batches.problems(e, good.replace(",", "\\\\a\\\\b", 1), []))
    assert any("px >" in p for p in batches.problems(e, good.replace("Do your job", "W" * 80), []))
    assert any("glossary" in p for p in batches.problems(e, good.replace("Marion", "Marian"), batches.glossary()))
    voiced = ENTRIES["sol.5.0"]  # eNNNNN: page count must match
    assert any("voiced" in p for p in batches.problems(voiced, "{CSA0t0e01005}One page only.", []))
    assert any("not in the font" in p for p in batches.problems(e, good.replace("Marion:", "Marion#"), []))
    assert any("ellipsis" in p for p in batches.problems(e, good.replace("worry...", "worry......"), []))
    assert batches.problems(e, good.replace("Do your", "...Do your"), []) == []  # "..." after @@ is a new pause
    assert any("stub last line" in p for p in batches.problems(e, good.replace("nicely...", "nicely,\\\\ok"), []))
    indented = ENTRIES["sol.147.88"]  # t3b4　零：... the JP indents the speaker
    assert any("leading blank" in p for p in batches.layout_problems(indented, indented["en"].replace("　", "", 1)))


def test_shipped_english_passes():
    assert batches.main(["check"]) == 0
