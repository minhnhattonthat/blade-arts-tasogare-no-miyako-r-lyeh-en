-- Glyph-record cap per text window (phase 8): the parser stops a window when its record count +0x2E reaches the
-- s16 cap at +0x30 (0x800168B8: sets +0x83 = 0x20), so text past the cap is silently cut. Logs every window start
-- (0x80015360) with its cap and record buffer, and each window's final count when the cap is hit.
--   warp_all.py SCENE --debugger --probe tools/lua/wincap.lua
local mem = PCSX.getMemPtr()
local function u8(a) return mem[bit.band(a, 0x1FFFFF)] end
local function s16(a) local v = u8(a) + 256 * u8(a + 1); if v >= 0x8000 then v = v - 0x10000 end; return v end
local function u32(a) return u8(a) + 256 * u8(a + 1) + 65536 * u8(a + 2) + 16777216 * u8(a + 3) end
L.on_exec(0x80015360, function()
  local r = PCSX.getRegisters().GPR.n
  L.log(string.format("WINCAP f%d win=%08X at=%08X cap=%d cols=%d lines=%d buf=%08X", L.frame, r.a0, r.a1,
    s16(r.a0 + 0x30), s16(r.a0 + 0x40), s16(r.a0 + 0x42), u32(r.a0 + 0xCC)))
end)
L.on_exec(0x800168DC, function()
  local w = PCSX.getRegisters().GPR.n.s0
  L.log(string.format("WINCAP full f%d win=%08X text=%08X count=%d", L.frame, w, u32(w + 4), s16(w + 0x2E)))
end)
