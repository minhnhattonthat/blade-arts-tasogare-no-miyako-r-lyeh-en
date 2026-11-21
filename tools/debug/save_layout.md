# Blade Arts save layout (memory card)

One 8 KB block per save, product code `BISLPM-86602-00` (`-01`... for more saves). Block frame 0: `SC`, icon flag
0x11 (one static icon frame), SJIS title `ブレイドアーツ／<save no>／<location>／ＴＩＭＥhh：mm` (a warped save reads
テストプレイ１, "test play 1": the location name comes from the map, not the save data).

| Block offset | RAM | Field | State |
|---|---|---|---|
| 0x100-0x577 | 0x800BAB08-0x800BAF7F | game-state struct, saved verbatim | verified (bytes equal a field RAM dump) |
| 0x108, 0x109, 0x10A | 0x800BAB10.. | map area, room, variant the save loads into | verified: set to 5/0/0, the save loads M05_00_0 |
| 0x110 / 0x112 | 0x800BAB18 | HP / max HP (u16, 200/200 at start) | verified: hp=50 shows a short red bar |
| 0x114 / 0x116, 0x118 / 0x11A | | 100/100, 30/30 pairs | guess: other gauges |
| 0x1C8 + 8*i | 0x800BABD0 | 20 entries of 8 bytes (03 in entry 0 at start) | NOT the herb count: with 0x1C8=99 the JP and EN builds both still show Herb : 3 (`work/qa/herb99.png`); purpose unknown |
| 0x268 + i | 0x800BAC70 | 8 weapon slots (item ids, 0xFF = empty; slot 0 = 0x05 Survival Knife) | verified: non-weapon ids draw a garbage weapon icon top left (`work/qa/probe_inv`) |
| 0x144.. 0x193 | 0x800BAB4C | ITEM BOX id list (item ids from `tools/items.py`, 0xFF = empty): 0x10 Herb, 0x12 Medi-pack at the start | verified: ids written at 0x146.. show as the ITEM / ITEM BOX slot bar icons in that order (scenes `probe_ids`, `probe_ids_box`); Object ids 0x0D/0x0E draw a "?" icon. The earlier note said 0x14C, the 9th slot, off screen |
| 0x578 | | u16 checksum = byte sum of 0x100-0x577 | verified: a wrong sum gives the red "load failed / file is broken" box |
| 0x57C | | SJIS dev note: "the checksum protects the data; it is not anti-cheat" | |

The bottom slot bar of the ITEM screen is the ITEM BOX (triangle): slot 1 = 薬草 x3 (herb) at the start; the 0x1C8
table (entry 0 byte 0 = 3) is the first lead for it. Inventory (what the ITEM list shows; empty at the start: NO
ITEM) is not mapped yet: phase 8 stress saves need it.
Next step: pick up an item in a map (or call the add-item code 0x8003874C from Lua) and diff the save.

Tools: `tools/debug/save.py show|set|blank|list`, test `tests/test_save.py`; base card from the scene `save_first`
(`warp_all.py save_first` -> `work/saves/save_first.mcd`).
