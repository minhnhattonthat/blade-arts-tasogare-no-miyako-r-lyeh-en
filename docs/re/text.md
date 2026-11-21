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
  tightest sector. The budget is per block (strings reflow across its sectors, `sol.reflow`). A block that still
  overflows is appended at the end of the file on as many sectors as it needs (its header entry gets the new id, old
  bytes stay) and the EXE maps its old id to the new sector (`asm/vwf.asm sol_remap`, table `sol_map`). Repacking
  every block on its fewest sectors does not help: slack is per sector, so the English needs 187 sectors packed tight.

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
Solved in phase 5 with letter bytes >= 0xA0 (§English below).

## Font (verified for the source; geometry to measure in phase 5)

- `DATA/DATA1.PAC` (archive: u32 1, u32 N, N x (u32 sector, u32 size)) entry 118 @0x320800: 1297 u16 SJIS codes =
  the glyph order (、。？！ ０-９ Ａ-Ｚ ａ-ｚ hiragana katakana then kanji in on'yomi order).
- Entry 119 @0x321800 (0x5320 bytes): 4bpp TIM holding the glyphs as **four 1bpp planes** (one per nibble bit, chosen by
  CLUT), cached at VRAM x 960-1023, y ~256-416. Matched by searching the VRAM dump (`work/qa/vram1/sub.vram.bin`) rows.
- Text is drawn into a VRAM buffer (render-to-texture), not from BIOS Krom2RawAdd (no B0:51 stub in the EXE).
- Cells past the last JP glyph (indexes 1297-1379, row 14 of the TIM) hold one filler pattern; the English glyphs go
  there (`tools/font.py`, checked against the filler).

## Renderer (phase 5, verified by watch probes + unicorn tests `tests/test_engine.py`)

- **SOL load:** `\DATA\SOL.SRP;1` (string 0x8001144C) is read by 0x8003793C -> 0x80077958 (name, dest, sectors, block
  id = sector offset in the file; current block id in 0x800D7BDA, setter 0x80037930). Message lookup 0x80078728(n):
  n = global index in the loaded block ("srf %d"), sector found through the last-index table; so strings may move
  between a block's sectors (`sol.reflow`). Callers: 0x80034E3C / 0x80036E24 (reset, a0 = 0) and GAME.BIN 0x800EB794
  (`size` = 0x800: one sector). 0x80077958 keeps base sector at 0x800D9C30 (struct 0x800D9C28 +8) and fetches sector
  base+k on demand into the 1-sector buffer, so a block may have any length; sector 0's last-index table is copied to
  struct +0x10 up to its first 0 entry (0x80077A9C; room for ~30 sectors), so table[0] must not be 0. The block id
  setter 0x80037930 is called from GAME.BIN 0x800EB37C (script opcode). Every disc file is opened by name
  (`\DATA\%s.BIN;1`, SOL.SRP, DATA1.PAC, XA.XA/XA2.XA, map packs): growing SOL.SRP shifts later files safely.
- **Decode:** 0x800788DC XORs the text with 0x8C8C **by halfwords** until a halfword 0x0A0A, so text length must be
  even (the terminator must be halfword-aligned). Flags word bit 1 = still encoded (7 -> 5).
- **Open:** 0x80078918 (from 0x80077E18) -> 0x80015360(window, text): copies the window setup; geometry at entry:
  +0x40 s16 columns, +0x42 lines, +0x0F pitch px (12), +0x11 line height, +0x3C x0, +0x2A bit 0 = centre lines.
  `tools/lua/textwin.lua` logs these per window.
- **Parser** 0x80016098: text is a stream of 2-byte units. First byte < 0x78 -> jump table 0x80010278 (codes `\0 \n @
  [ \ a b c d e g i n s t v w`); else a character: glyph record (20 bytes at +0xCC buffer, max +0x30 = 200 per page),
  x += pitch, column += 1, auto-wrap at +0x48 columns. `\\` on the last line (+0x4A) and `@@` both wait for a button
  and start a new page. `tN` = text speed (table 0x800B2470), `gN` = move x by N px, `bN` colour.
- **Centring** 0x80015F3C measures each line (own jump table 0x80010098) and sets x = +0xA0 + (+0xA4 - width) / 2.
- **Glyph** 0x8008DC1C(sjis): binary search in the 1297-code table -> index i -> u = (i % 92 >> 2) * 11,
  v = i // 92 * 11, CLUT = base (0x800E66B4) + (i & 3); 11x11 cells.

## English (phase 5, `asm/vwf.asm`, `tools/en.py`)

- In RAM a unit whose first byte is >= 0xA0 is two English letters (ASCII | 0x80; 0x80 = none). Hooks: parser
  0x800167F8 -> `en_char` (one record per letter, x += its width, no column count and no auto-wrap: the build wraps),
  measure 0x8001602C -> `en_meas`. Japanese units take the original code. Code + tables live in the dead debug-menu
  records 0x800B8128-0x800BA1FC (only mode 11 read them; its handler entry now points at mode 6's).
- Font: `fonts/en11.txt` (82 glyphs: printable ASCII minus `# $ < > @ \ ^ _ \` { | }`), 4-6 px advances, in glyph
  slots 1297+. Lowercase bytes 0xE0-0xFE overlap level-2 kanji lead bytes, so a line can't mix English and such kanji.
- `en` column syntax: `en.py` docstring. Marker build: `python -X utf8 build.py --marker --out build/marker`.
