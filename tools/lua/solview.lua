-- SOL message viewer (phase 8 text coverage + visual QA): shows any SOL.SRP message in the game's own renderer.
-- Run by tools/solview.py. Loads the host state SVSTATE (taken just before the intro's first message lookup), and at
-- the lookup 0x80078728 copies the target's sector from the built SOL.SRP (SVSOL) into the game's 1-sector buffer,
-- writes the block's last-index table to struct +0x10, the old block id to 0x800D7BDA and n to a0
-- (docs/re/text.md §Renderer). Window geometry is in the string (subtitle / WS / choice), so the host doesn't matter.
-- Per target: one shot per page (<id>_NN.png, QUIET frames into each page wait), then the page is turned through the
-- game's own confirm path; "SV end" at the end of text (or when the host asks for its next message), "SV timeout"
-- after SVMAX frames. Logs "TEXT <key>" for textcover.py. Needs --debugger.
local mem = PCSX.getMemPtr()
local function u8(a) return mem[bit.band(a, 0x1FFFFF)] end
local function w8(a, v) mem[bit.band(a, 0x1FFFFF)] = v end
local function w16(a, v) w8(a, v % 256); w8(a + 1, math.floor(v / 256) % 256) end
local function u32(a) return u8(a) + 256 * u8(a + 1) + 65536 * u8(a + 2) + 16777216 * u8(a + 3) end
local SOLST = 0x800D9C28   -- struct: +0 buffer ptr, +5 sectors in buffer, +0x10 s16 last-index table
if SVHOST then   -- host-state run (with warp.lua): only report when the first lookup comes
  L.on_exec(0x80078728, function() L.log("SV lookup f" .. L.frame) end)
else
local T = dofile(SVTBL)
local sol = assert(io.open(SVSOL, "rb"))
local QUIET, AGAIN, MAXF = SVQUIET or 30, SVAGAIN or 60, SVMAX or 1800
local i, state, t0, page, cur = 0, "load", 0, 0, nil
local win, last, moved, push = nil, nil, 0, false

L.on_exec(0x80078728, function()
  if state == "armed" then
    cur = T[i]
    sol:seek("set", cur.off)
    local d = sol:read(0x800)
    local buf = u32(SOLST)
    assert(u8(SOLST + 5) >= 1 and buf >= 0x80000000, "SOL buffer not loaded")
    for j = 1, 0x800 do w8(buf + j - 1, d:byte(j)) end
    for j = 1, #cur.tbl + 1 do w16(SOLST + 0x10 + 2 * (j - 1), cur.tbl[j] or 0) end
    w16(0x800D7BDA, cur.blk)
    PCSX.getRegisters().GPR.n.a0 = cur.n
    L.log(string.format("TEXT %08X", cur.key))
    L.log(string.format("SV start %s f%d", cur.id, L.frame))
    state, t0, page, win, last, moved, push = "show", L.frame, 0, nil, nil, L.frame, false
  elseif state == "show" then
    -- the host's timer asked for its next message before ours ended (long voiced lines): the rest is cut.
    -- Tried and failed: returning 0 from the lookup (the host spins inside one frame), and handing the host the
    -- rest of ours (flags 5 + CSA0 written before the current page: the new window draws nothing).
    L.log("SV host moved on " .. cur.id)
    state = "done"
  end
end)
-- window open: a0 = window struct
L.on_exec(0x80015360, function() if state == "show" then win = PCSX.getRegisters().GPR.n.a0 end end)
-- page wait in the window update (0x80015DE0..): `s1 & window+0xB8` (confirm mask) clears the wait; the intro host
-- never passes the pad there, so a press is injected by OR-ing the window's own mask into s1
L.on_exec(0x80015DF0, function()
  local r = PCSX.getRegisters().GPR.n
  if push and r.s0 == win then
    r.s1 = bit.bor(r.s1, u8(win + 0xB8) + 256 * u8(win + 0xB9))
    push = false
  end
end)

local function shot()
  page = page + 1
  L.shot(string.format("%s_%02d.png", cur.id, page))
end

L.on_frame(function(n)
  if state == "load" then
    i = i + 1
    if i > #T then L.log("SV all done"); L.finish(0); return end
    PCSX.loadSaveState(Support.File.open(SVSTATE))
    state, t0 = "armed", n
  elseif state == "armed" then
    if n - t0 > 600 then L.fail("no message lookup within 600 frames of the host state") end
  elseif state == "show" then
    -- window +0x83 low nibble: 0 parsing, 1 waiting at a page break, 2 end of text (parser 0x80016098 handlers).
    -- QUIET frames into a wait: shot; at a page break, push (again every AGAIN frames if it didn't take)
    if SVFAST and win then w8(win + 0x13, 0) end   -- no per-character delay / iNNN pause (the host's timer is short)
    local p = win and bit.band(u8(win + 0x83), 0xF)
    if p ~= last then
      if SVDEBUG then L.log(string.format("SV wait %s f%d", tostring(p), n - t0)) end
      last, moved = p, n
    end
    local q = n - moved
    if (p == 1 or p == 2) and q == QUIET then
      shot()
      if p == 2 then L.log("SV end " .. cur.id .. " pages " .. page .. " f" .. (n - t0)); state = "load"; return end
    end
    if p == 1 and q >= QUIET and (q - QUIET) % AGAIN == 0 then push = true end
    if n - t0 >= MAXF then shot(); L.log("SV timeout " .. cur.id .. " pages " .. page); state = "load" end
  elseif state == "done" then
    shot()
    L.log("SV end " .. cur.id .. " pages " .. page .. " f" .. (n - t0))
    state = "load"
  end
end)
end
