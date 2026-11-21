# Debug tool RAM map (phase 2)

Addresses are for the dump in `rom.sha1`. gp = 0x800CAB68 (set at 0x8003FE24).

## Programs (top-level overlays) - verified

| Address | Meaning |
|---|---|
| 0x800CB0C0 s16 (gp+0x558) | current program |
| 0x800CB094 s16 (gp+0x52C) | program switch request (1 = switch at the next main-loop check, 0x80013EA4) |
| 0x800CB0CC s16 (gp+0x564) | next program |

Program table 0x800B22E4, 16 bytes each (name ptr, init, main, flags): 0 TITLEP, 1 GAME, 2 LOGOP, 3 ROLLDEMO,
4 GAMOVERP, 5 THANKSP, 6 ENDINGP, 7/8 GAME again, 9-12 BOSS0P-BOSS3P. Overlays load `\DATA\<name>.BIN`.
Boot runs 0 -> 2 -> 0 (title) -> 1 (New Game). **verified:** a request for 3/4/5/6 from the title runs that overlay
(ending with cast roll, thanks screen, attract demo, boss game over); the same request from the field (program 1)
jumps to the BIOS reset vector (0xBFC00000), so warp.lua only switches programs from the title.

## GAME program modes - verified

| Address | Meaning |
|---|---|
| 0x800D7910 s16 | game mode; +2 sub-state, +4 sub-sub (counters), +0xE next program for mode 5 |
| 0x800BAB10 u8 x3 | current map: area, room, variant -> file `M0\M%02d_%02d_%x.PAC` (format string 0x80011474, builder 0x8003869C) |

Mode handlers: table 0x800B7D84, called from 0x800357B0. 0 title/attract (inside GAME), 1 new-game init, 2 map load,
3 field, 4 status menu (STATUS), 5 fade then switch to program [+0xE] (0 = title), 6/9/10 do nothing, 7 game over
(GAME OVER / TITLE / TRY AGAIN, then mode 5), 8 requests program 4 (crashes the recompiler when forced from the
field), 11 leftover debug menu (draws with FntPrint, invisible in this build; its stage list is below).

**Warp (verified):** write the map id while mode is 1 (New Game init, ~frame 2340 from a cold boot); mode 2 then loads
that map instead of the intro (M02_10_0). Map variants (`_z`) are event states: M02_00_4 plays its event at once.
Some maps are script stubs that load another map during mode 2 (M50_00_0 -> M50_03_0 stage-clear card,
M50_05_0 -> M05_01_4): the choice depends on story state not yet mapped.

Set-next-map function 0x800382CC (a0 area, a1 room, a2 variant; 0x80 bit = keep; then position/angle vectors):
probably what door and script commands call (guess: callers not traced).

## Leftover debug stage menu (EXE data) - verified as data, not reachable

Records of 0x2C bytes from 0x800B8128 to 0x800BA1FC: name ptr, ..., +0x1C a small number (0x0A-0x32, rising with
the stage: guess story progress or a sound bank), +0x24 6 = selectable / 7 = header. Headers: "stage start"
(M02_10_0, M03_01_0, M02_05_0, M02_00_0, M02_01_0, M03_00_1, M04_00_0 ... M10_03_0), "events" (M02_00_4,
M02_00_6, M02_01_3, M06_02_2, M07_02_1, M03_02_2), "boss" (M09_03_1, M07_02_3, M03_02_3, M05_01_2, M06_02_1,
M93_16_0), "big boss" (M03_20_0..3), "dev" (M91_00..03 and a full per-area list). scenes.tsv names these.

## Items - partly verified

Item table 0x800B50F0, 16 bytes per item until id 0xFF: u8 id, u8 type, .., u32 flags, EN name ptr, JP name ptr
(the EN names are dev labels: "Jade Plate1", "Holy Liquid"; the game shows the JP ones). The game keeps the table
pointer at 0x800B253C and the count at 0x800B2556 (setter 0x8001821C). Inventory location: not found yet.

## Saves - verified

The save is the RAM struct 0x800BAB08-0x800BAF7F verbatim (map id at +8, HP at +0x10): `tools/debug/save_layout.md`.
The stage-clear card (M50_03_0, reached from M50_00_0) offers SAVE; `warp_all.py save_first` writes a real save.

## Not found yet

- Story progress / event flags (what M50_00_0 reads to pick a card).
- Inventory (the ITEM list) and nerves (the published GameShark code 8015DA44 for nerves does not hold nerves in a
  field state). Add-item code 0x8003874C (writes 0x800BAC70 + slot) and item-box code 0x800387F8 are leads.
- The status menu has ITEM / SYSTEM (sound, vibration) / EXIT only at the start; more entries may appear later.
