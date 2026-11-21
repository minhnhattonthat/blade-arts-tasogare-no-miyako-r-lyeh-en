-- Blade Arts warp: cold boot -> any scene, no save needed. Run through tools/debug/warp_all.py, or by hand:
--   emu.py ROM.cue --out D --script tools/debug/warp.lua --var "SCENE='m03_00_0'" --var "REPO=[[H:/abs/repo]]" --frames 20000
-- or skip the table: --var "MAP='M03_00_0'" [--var MODE=4] [--var PROG=6] [--var "POKE='800D7910=0007'"]
-- Scene table: tools/debug/scenes.tsv (name, map, mode, prog, poke, after, frames, sav, note); RAM: docs/re/debug.md.
--   sav (runner only): memory card for the run, "blank" = a fresh formatted card; the card the game wrote lands in
--         <out>/memcard1.mcd, and warp_all.py copies it to work/saves/<scene>.mcd for scenes named save_*.
--   map:  New Game, then the map id is replaced while the game is in mode 1 (new-game init) -> the game loads that
--         map (variant = event state) and starts its event; arrival = 30 frames past the load (modes 1/2). Some
--         maps are script stubs that load another map at once (most M50_*): the log names the map it settled on.
--   mode: after arrival, force game mode (4 status menu, 7 game over).
--   prog: from the title screen, request program PROG (3 ROLLDEMO, 4 GAMOVERP, 5 THANKSP, 6 ENDINGP). Switching
--         program from the field resets the console, so these never take a map.
--         map LOAD[:Mxx_yy_z]: title -> Continue -> load the first save of the card (sav column / emu.py --sav);
--         with a map id, fail unless the save lands there.
--   poke: "ADDR=VV" bytes or "ADDR=VVVV" halfwords, comma separated, applied at arrival.
--   after: route run at arrival ("120 -;6 circle;..."), then CIRCLE_EVERY=N (var, default off) presses circle
--         every N frames (emu.py's own --mash would also fire on the title, before the warp).
--   frames: frames after arrival before proof.png and quit (default 900).
-- Opt-in GOD=1 re-applies GOD_POKE every frame after arrival (e.g. HP; fill in once HP is mapped).
-- Logs "WARP arrived <scene> frame N"; L.fail if the scene is never reached within LIMIT frames (default 8000).

local MODE_A, MAP_A, PROG_A, PREQ_A, PNEXT_A = 0x0D7910, 0x0BAB10, 0x0CB0C0, 0x0CB094, 0x0CB0CC
local mem = PCSX.getMemPtr()
local function s16(a) local v = mem[a] + 256 * mem[a + 1]; if v >= 0x8000 then v = v - 0x10000 end; return v end
local function poke(spec)
  for addr, val in spec:gmatch("(%x+)=(%x+)") do
    local a, v = tonumber(addr, 16) % 0x200000, tonumber(val, 16)
    mem[a] = v % 256
    if #val > 2 then mem[a + 1] = math.floor(v / 256) % 256 end
  end
end

if SCENE and not (MAP or MODE or PROG) then
  local f = assert(io.open((REPO or ".") .. "/tools/debug/scenes.tsv", "r"), "scenes.tsv not found: pass REPO")
  local found = false
  for line in f:lines() do
    local c = {}
    for x in (line .. "\t"):gmatch("([^\t]*)\t") do c[#c + 1] = x end
    if c[1] == SCENE then
      found = true
      local function g(i) return (c[i] or "") ~= "" and c[i] or nil end
      MAP, MODE, PROG = g(2), tonumber(g(3) or ""), tonumber(g(4) or "")
      POKE, AFTER = POKE or g(5), AFTER or g(6)  -- --var wins over the table
      AFTER_FRAMES = AFTER_FRAMES or tonumber(g(7) or "")
    end
  end
  f:close()
  assert(found, "unknown scene " .. SCENE)
end
SCENE = SCENE or MAP or ("mode" .. tostring(MODE))
AFTER_FRAMES = AFTER_FRAMES or 900
LIMIT = LIMIT or 8000

local ar, rr, vr
local LOAD, EXPECT = false, nil  -- LOAD[:Mxx_yy_z]: title -> Continue -> first save on the card -> its field
if MAP and MAP:match("^LOAD") then LOAD, EXPECT, MAP = true, MAP:match("^LOAD:(%S+)"), nil end
if MAP then
  local a, r, v = MAP:match("^M(%d%d)_(%d%d)_(%x)$")
  assert(a, "MAP must look like M03_00_0: " .. tostring(MAP))
  ar, rr, vr = tonumber(a), tonumber(r), tonumber(v, 16)
end

-- same timing as tools/routes/boot.txt (cold boot, SCPH-5500): Start skips the sword intro, up+circle = New Game.
-- Pressed before the menu is up, up+circle lands on Continue instead, so this is timed and mode 1 is checked.
local title_route = { { "-", 1300 }, { "start", 6 }, { "-", 700 }, { "up", 6 }, { "-", 20 }, { "circle", 6 } }
local state, arrived, t, saw_logo = "boot", nil, 0, false

local function arrive(n)
  arrived = n
  L.log(string.format("WARP arrived %s frame %d map M%02d_%02d_%x prog %d", SCENE, n, mem[MAP_A], mem[MAP_A + 1],
    mem[MAP_A + 2], s16(PROG_A)))
  if POKE then poke(POKE) end
  if MODE then mem[MODE_A] = MODE; mem[MODE_A + 1] = 0; for i = 2, 5 do mem[MODE_A + i] = 0 end end
  if AFTER then
    for step in AFTER:gmatch("[^;]+") do
      local fr, keys = step:match("^%s*(%d+)%s+(%S+)")
      L.press(keys, tonumber(fr))
    end
  end
  state = "there"
end

L.on_frame(function(n)
  local mode, prog = s16(MODE_A), s16(PROG_A)
  if prog == 2 then saw_logo = true end
  if state == "boot" then
    if PROG or LOAD or not MAP and not MODE then
      -- title program (0) after the logos (2): the title screen is up ~200 frames later
      if saw_logo and prog == 0 then
        t = t + 1
        if t == 900 then
          if PROG then mem[PNEXT_A] = PROG; mem[PNEXT_A + 1] = 0; mem[PREQ_A] = 1; mem[PREQ_A + 1] = 0 end
          state = PROG and "switch" or LOAD and "cont" or "x"
          if not PROG and not LOAD then arrive(n) end
        end
      end
    elseif t == 0 then
      t = 1; for _, s in ipairs(title_route) do L.press(s[1], s[2]) end
    end
    if prog == 1 and mode == 1 then
      if MAP then mem[MAP_A] = ar; mem[MAP_A + 1] = rr; mem[MAP_A + 2] = vr end
      state, t = "loading", 0
    end
  elseif state == "cont" then
    -- the title cursor starts on Continue; circle opens LOAD, picks slot 1 and confirms. A refused save
    -- (bad checksum: red "file is broken" box) keeps prog 0 and the run fails at LIMIT.
    if prog == 0 and L.route_done() then L.press("circle", 6); L.press("-", 250) end
    if prog == 1 and mode == 3 then
      t = t + 1
      if t == 930 then
        local got = string.format("M%02d_%02d_%x", mem[MAP_A], mem[MAP_A + 1], mem[MAP_A + 2])
        if EXPECT and got:upper() ~= EXPECT:upper() then L.fail("save loaded into " .. got .. ", expected " .. EXPECT) end
        arrive(n)
      end
    end
  elseif state == "switch" then
    if prog == PROG then t = t + 1; if t == 960 then arrive(n) end end  -- 60 frames after the switch
  elseif state == "loading" then
    -- a map's own script may send the game on at once (M50_00_0 -> M50_03_0): arrival is wherever it settles
    if mode ~= 1 and mode ~= 2 then
      t = t + 1
      if t == 30 then arrive(n) end
    end
  end
  if arrived then
    if GOD and GOD_POKE then poke(GOD_POKE) end
    if (CIRCLE_EVERY or 0) > 0 and L.route_done() and (n - arrived) % CIRCLE_EVERY == 0 then L.press("circle", 6) end
    if n == arrived + AFTER_FRAMES then
      L.shot("proof.png")
      if STATE_OUT then L.save_state(STATE_OUT) end  -- emu.py --state-out: the scene's savestate
      L.log("final frame " .. n)
      L.finish(0)
    end
  elseif n >= LIMIT then
    L.fail(string.format("WARP never arrived at %s (prog %d mode %d map M%02d_%02d_%x)", SCENE, prog, mode,
      mem[MAP_A], mem[MAP_A + 1], mem[MAP_A + 2]))
  end
end)
