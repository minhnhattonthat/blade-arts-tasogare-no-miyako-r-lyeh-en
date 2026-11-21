-- Raw-string viewer (phase 8 text coverage + visual QA): shows EXE/overlay strings in a real text window.
-- Run by tools/rawview.py. RVHOST=true: host run, logs "RV win f<frame> at=<text addr>" for every window start
-- (0x80015360: a0 = window struct, a1 = text). Else: per target of RVTBL ({id=, at=, key=}), load the host state
-- RVSTATE, and at the first window start whose text is RVAT, point a1 at the target's RAM address instead; the
-- window keeps the host's geometry (status help box 21x3, load/save message box). One shot per page wait
-- (<id>_NN.png, QUIET frames in), pages turned by OR-ing the window's confirm mask (as solview.lua); "TEXT <key>"
-- for textcover.py, "RV end|timeout <id> pages N". Needs --debugger.
local mem = PCSX.getMemPtr()
local function u8(a) return mem[bit.band(a, 0x1FFFFF)] end
local function w8(a, v) mem[bit.band(a, 0x1FFFFF)] = v end
if RVHOST then
  L.on_exec(0x80015360, function()
    L.log(string.format("RV win f%d at=%08X", L.frame, PCSX.getRegisters().GPR.n.a1))
  end)
else
local T = dofile(RVTBL)
local QUIET, AGAIN, MAXF = RVQUIET or 40, 60, RVMAX or 900
local i, state, t0, page, cur, win, last, moved, push = 0, "load", 0, 0, nil, nil, nil, 0, false

L.on_exec(0x80015360, function()
  local r = PCSX.getRegisters().GPR.n
  if state == "armed" and r.a1 == RVAT then
    cur = T[i]
    r.a1 = cur.at
    win = r.a0
    L.log(string.format("TEXT %08X", cur.key))
    L.log(string.format("RV start %s f%d", cur.id, L.frame))
    state, t0, page, last, moved, push = "show", L.frame, 0, nil, L.frame, false
  elseif state == "show" and r.a1 == RVAT then
    r.a1 = cur.at   -- hosts that rebuild their windows every frame (LOADSAVE)
  end
end)
L.on_exec(0x80015DF0, function()
  local r = PCSX.getRegisters().GPR.n
  if push and r.s0 == win then
    r.s1 = bit.bor(r.s1, u8(win + 0xB8) + 256 * u8(win + 0xB9))
    push = false
  end
end)

local function shot()
  page = page + 1
  L.shot(string.format("%s_%02d.png", cur.id:gsub("[/:]", "_"), page))
end

L.on_frame(function(n)
  if state == "load" then
    i = i + 1
    if i > #T then L.log("RV all done"); L.finish(0); return end
    PCSX.loadSaveState(Support.File.open(RVSTATE))
    for f, k in (RVPRESS or ""):gmatch("(%d+) ([^;]+)") do L.press(k, tonumber(f)) end   -- route after the load
    state, t0 = "armed", n
  elseif state == "armed" then
    if n - t0 > 600 then L.fail(string.format("no window with text %08X within 600 frames", RVAT)) end
  elseif state == "show" then
    w8(win + 0x13, 0)   -- no per-character delay
    local p = bit.band(u8(win + 0x83), 0xF)   -- 1 page wait, 2 end of text (solview.lua)
    if p ~= last then last, moved = p, n end
    local q = n - moved
    if (p == 1 or p == 2) and q == QUIET then
      shot()
      if p == 2 then L.log("RV end " .. cur.id .. " pages " .. page); state = "load"; return end
    end
    if p == 1 and q >= QUIET and (q - QUIET) % AGAIN == 0 then push = true end
    if n - t0 >= MAXF then shot(); L.log("RV timeout " .. cur.id .. " pages " .. page); state = "load" end
  end
end)
end
