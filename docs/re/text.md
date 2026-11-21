# Text (recon, phase 1)

Disc: `SLPM_866.02` (EXE, load 0x80010000, entry 0x8003FDA4), `DATA/` overlays and archives, `M0/*.PAC` (302 map packs),
`NOR/` (boss models), `STR/XA.XA` + `XA2.XA` (voice/music XA, 184+248 MB). Unpack: `dumpsxiso` (AGENTS.md).

## Where the Japanese is

| Source | What | Encoding | State |
|---|---|---|---|
| `DATA/SOL.SRP` (364 KB, 95 blocks, 177 sectors) | all dialogue, narration, intro subtitles, signs, Yes/No choices: 3351 strings, 215 KB | Shift-JIS XOR 0x8C | verified: decoded intro subtitle 昨日未明にチリより… matches RAM 0x801DBE00 while it shows (play session state `work/play/p1/0003`); `tools/sol.py` parses every block, 0 undecodable strings |
| `SLPM_866.02` 0xDB8-0x12F0 | item names (イバラの冠, ルーンストーン, 翡翠版のカケラ１..) + 0xAB878 何も起こらない・・・ | raw Shift-JIS | verified by scan (`tools/sjisscan.py`) |
| `DATA/STATUS.BIN` (overlay) | item descriptions, status-menu strings | raw Shift-JIS | extracted (below) |
| `DATA/LOADSAVE.BIN` (overlay) | save/load menu, memory-card messages, save-slot location names (ルルイエ２, 重力エレベータ上層１..) | raw Shift-JIS | extracted |
| `DATA/BOSS0P.BIN`, `BOSS3P.BIN` (overlays) | 6 boss-fight lines (何か・・・いる？, 長虫かよ・・・) | raw Shift-JIS | extracted |
| `DATA/GAME.BIN` | 2 debug error messages (配置物の削除が出来ません！) | raw Shift-JIS | extracted, debug only |

No other file holds XOR-0x8C text (searched every file for XORed `CSA0`, してい, ました). M0 PAC / DATA1.PAC / ENDING / THANKS
scan hits are pixel noise (ヨヨヨヨ runs).

## SOL.SRP format (verified by `tools/sol.py`, test `tests/test_recon.py`)

- Sector 0: u32 1, u32 N(=95), N x (u32 block_id, u32 byte_size). **block_id = the block's first sector in the file**
  (ids skip for multi-sector blocks: 11 is 2 sectors, next is 13). Blocks run back to back from 0x800.
- Every 0x800 sector of a block is a self-contained string page:
  - first sector: u32 hdr_size (0x0C/0x10/0x18), u32 0, u16 per sector = last global string index in that sector (0-pad)
  - later sectors: u32 8, u32 sector number within the block
  - then u16 offsets (from the sector start), one per string in the sector, padded to 4 bytes; then the strings.
- String: u32 flags (7 on disc; the game sets 5 after decoding in place), Shift-JIS bytes XOR 0x8C, raw `0A 0A`
  terminator (not XORed), NUL pad to 4. Walk whole characters to find the terminator: 中 = 92 86 XORs to 1E 0A.
  Block 132 string 110 (an ending line with a broken `b` code) has a XORed terminator (86 86); handled.
- Strings are presumably referenced by (block id, global index) from map scripts (guess: not yet traced). Keeping the
  block layout and index order means no external pointers change; only in-sector offset tables are rebuilt.
- **Packing (verified: `sol.pack` rebuilds the file byte-identical, `tests/test_extract.py`):** offsets table right
  after the sector header, padded to 4; each string = u32 flags + XORed text + `0A 0A 00 00` + NUL pad to 4; rest of
  the sector zero. The one odd string (132/110) keeps its raw tail `86 86 8C 00 00` only while its text is unchanged.
- **Space:** each string page is one 0x800 sector; total free 108,970 bytes over 177 sectors, min 2 bytes free in the
  tightest sector. Growing a block would renumber later block ids (= sector numbers): check how the loader seeks before
  relying on extra sectors (phase 5).

## Raw Shift-JIS strings (phase 4, `tools/rawtext.py`)

- Overlays STATUS, LOADSAVE, BOSS0P and BOSS3P all load whole at **0x80149800** (found in RAM dumps of the running
  overlay: `warp_all.py status load --probe <skill>/scripts/lua/probes/ramdump.lua`, and `PROG=9`/`12` from the
  title for BOSS0P/BOSS3P). GAME.BIN at 0x800EAB90 (debug messages only). EXE: file 0x800 = 0x80010000.
- 305 strings: EXE 62 (item names 0xDB8-0x12F0, short dev names 0xBB454.., 無し, 何も起こらない・・・, 2 debug lines),
  STATUS 93 (item and sphere descriptions, menu verbs, Yes/No, digit glyph table 0xFA98), LOADSAVE 142 (save-slot
  location names, memory-card messages, fullwidth digit strings, c555/cfff-prefixed menu items = colour codes), BOSS0P 2
  + BOSS3P 4 (`BKA2BKC111` + line; **no pointer found**: reached some other way, keep them in place), GAME.BIN 2.
- Strings can start right after a pointer table with no NUL before them (STATUS 0x748): the scanner starts a string
  at every referenced address too. Refs: data words, lui+addiu/ori (64-instruction window), gp-relative in the EXE.
- Odd bytes in real text: STATUS 0xE70 has a stray `0B` mid-line (written `{0B}`); EXE 0x2EC4 uses halfwidth kana.
- Coverage (`tests/test_extract.py`): every kana run that `sjisscan.py` finds in the EXE and every DATA/*.BIN/.DAT/.PAC
  is inside an extracted string or a hand-checked NOISE run; THANKSP, TITLEP, DATA1.PAC, ENDING_P.DAT and STATUS2.DAT
  hits are all pixel data (odd offsets, gibberish).

## Script files (phase 4, `tools/extract.py`)

`script/sol/<block>.tsv` (id `sol.<block>.<index>`, sector, jp, en, notes) and `script/raw/<file>.tsv` (id
`<file>:<offset>`, addr, room, refs, jp, en, notes). jp is the Shift-JIS text with the control codes inline; raw
strings write 0A as `{n}` and other control bytes as `{XX}`. `extract.py` never overwrites an existing file
without `--force`.

## Control codes (ASCII inside the SJIS text; counts over all strings)

| Code | Count | Meaning (guess unless noted) |
|---|---|---|
| `\\` (two backslashes) | 1985 | line break (verified: intro subtitle lines) |
| `@@` | 472 | new page / wait for button (verified: intro subtitle pages) |
| `CSA0` | ~1570 | string start / clear box, seen at the start of most dialogue |
| `tN` | ~1700 | text mode/box type (t0 subtitles, t3 signs/system, t4 dialogue) |
| `bN` | ~1360 | colour: `b3`..`b6` speaker/highlight, `b0` normal (零：, 少女：, item names) |
| `eNNNNN` | ~1330 | voice clip id (XA), 5 digits |
| `iNNN` | ~1150 | wait N frames (pauses inside a line) |
| `gN` | ~400 | ? (graphic/portrait or speed) |
| `[DDN` / `[N` | 112 / 264 | choice menu start / option (Yes/No) |
| `WP-nnn-nnnWSnnnnBSnnnn...FRAn nN tN sN cc.. dN` | ~55 | window position/size/frame setup |
| `aN`, `cf..`, `crrr` | few | ? |

**English can't use bare ASCII letters**: the parser treats `b`, `t`, `e`, `i`, `g`, `[`, `@`, `\` + digits as codes.
Phase 5 must add an escape or a separate English glyph range (and a VWF: the font is fixed-width 12-ish px full-width).

## Font (verified for the source; geometry to measure in phase 5)

- `DATA/DATA1.PAC` (archive: u32 1, u32 N, N x (u32 sector, u32 size)) entry 118 @0x320800: 1297 u16 SJIS codes =
  the glyph order (、。？！ ０-９ Ａ-Ｚ ａ-ｚ hiragana katakana then kanji in on'yomi order).
- Entry 119 @0x321800 (0x5320 bytes): 4bpp TIM holding the glyphs as **four 1bpp planes** (one per nibble bit, chosen by
  CLUT), cached at VRAM x 960-1023, y ~256-416. Matched by searching the VRAM dump (`work/qa/vram1/sub.vram.bin`) rows.
- Text is drawn into a VRAM buffer (render-to-texture), not from BIOS Krom2RawAdd (no B0:51 stub in the EXE).
- The XOR decode routine is not in the EXE or DATA overlays as `xori 0x8C` (todo: watch the flag word 7->5 at
  0x801DBE1C with `watch.lua` to find it; also find who reads SOL.SRP and by which id).
