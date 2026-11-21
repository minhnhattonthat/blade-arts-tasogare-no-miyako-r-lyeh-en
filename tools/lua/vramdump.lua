-- VRAM dump probe (emu.py / warp_all.py --probe): writes v<frame>.vram.bin (1024x512 16-bit) every VEVERY frames
-- (default 600). Render a region with tools/vram_png.py.
local every = VEVERY or 600
L.on_frame(function(f) if f % every == 0 then L.dump_ppu(string.format("v%06d", f)) end end)
