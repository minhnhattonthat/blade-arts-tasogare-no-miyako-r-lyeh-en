-- Log every text window the renderer starts (EXE 0x80015360: a0 = window struct, a1 = text), with its geometry, for
-- the width gate (docs/re/text.md §Renderer) and text coverage. Needs --debugger (exec hook).
--   emu.py ... --debugger --script tools/lua/textwin.lua      (warp_all.py --debugger --probe tools/lua/textwin.lua)
-- Line: "TEXTWIN f<frame> cols=<n> lines=<n> pitch=<px> lineh=<px> x0=<n> centre=<0/1> text=<letters>"; text is the
-- English letters of the first 40 bytes (marker builds start with [id]) or the Shift-JIS bytes as hex.
local mem = PCSX.getMemPtr()
local function u8(a) return mem[bit.band(a, 0x1FFFFF)] end
local function s16(a) local v = u8(a) + 256 * u8(a + 1); if v >= 0x8000 then v = v - 0x10000 end; return v end

L.on_exec(0x80015360, function()
  local r = PCSX.getRegisters().GPR.n
  local w, t = r.a0, r.a1
  local s, hex = {}, {}
  for i = 0, 39 do
    local c = u8(t + i)
    if c == 0 or (c == 10 and u8(t + i + 1) == 10) then break end
    if c >= 0xA0 then s[#s + 1] = string.char(c - 0x80) end
    hex[#hex + 1] = string.format("%02X", c)
  end
  local text = #s > 0 and table.concat(s) or table.concat(hex)
  L.log(string.format("TEXTWIN f%d cols=%d lines=%d pitch=%d lineh=%d x0=%d centre=%d at=%08X text=%s", L.frame,
    s16(w + 0x40), s16(w + 0x42), u8(w + 0x0F), u8(w + 0x11), s16(w + 0x3C), bit.band(u8(w + 0x2A), 1), t, text))
end)
