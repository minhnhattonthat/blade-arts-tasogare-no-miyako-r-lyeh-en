-- Text coverage (skill references/emulator-qa.md §Text coverage): logs "TEXT <key>" once per string reached, keys as
-- in build/strings.tsv (build.coverage_tables). Needs --debugger.
--   SOL: message lookup 0x80078728 (a0 = n) with the old block id at 0x800D7BDA (the remap keeps old ids there).
--   Raw (EXE/overlay strings): a read breakpoint on each string's first byte; overlays share addresses, so the
--   string's first 4 bytes must match before its key is logged.
--   warp_all.py --debugger --probe tools/lua/textcover.lua --var "TCTBL='H:/.../build/textcover_tbl.lua'"
local mem = PCSX.getMemPtr()
local function u8(a) return mem[bit.band(a, 0x1FFFFF)] end
local seen = {}
local function hit(key)
  if not seen[key] then seen[key] = true; L.log(string.format("TEXT %08X", key)) end
end

L.on_exec(0x80078728, function()
  local n = PCSX.getRegisters().GPR.n.a0
  local b = u8(0x800D7BDA) + 256 * u8(0x800D7BDB)
  hit(0x50000000 + b * 65536 + bit.band(n, 0xFFFF))
end)

local by_addr = {}
for _, r in ipairs(dofile(TCTBL or "build/textcover_tbl.lua")) do
  local a = r[1]
  by_addr[a] = by_addr[a] or {}
  table.insert(by_addr[a], {r[2], r[3]})
end
for a, list in pairs(by_addr) do
  L.on_read(a, a, function()
    local s = string.format("%02x%02x%02x%02x", u8(a), u8(a + 1), u8(a + 2), u8(a + 3))
    if TCDEBUG then L.log(string.format("TCREAD %08X %s", a, s)) end
    for _, c in ipairs(list) do
      if string.sub(s, 1, #c[2]) == c[2] then hit(c[1]) end
    end
  end)
end
