; English VWF for the text window renderer (docs/re/text.md §Renderer, §English).
; Assembled by build.py with armips onto a copy of SLPM_866.02; en_tables.asm is generated from tools/en.py.
; A text unit whose first byte is >= 0xA0 holds two letters (ASCII | 0x80, 0x80 = none); each visible letter becomes
; one glyph record (same layout as the game's) and advances x by its own width. JP units take the original path.

.psx
.open EXE_IN, EXE_OUT, 0x80010000 - 0x800

; Free space: the leftover debug stage menu records (0x800B8128-0x800BA1FC), only read by game mode 11, which nothing
; enters; its handler is pointed at mode 6's (does nothing) so the area can never be read as records.
FREE_START equ 0x800B8128
FREE_END   equ 0x800BA1FC

.org 0x800B7DB0                 ; mode handler table 0x800B7D84 entry 11
    .word 0x800365C0            ; = entry 6

; --- parser (0x80016098): normal-character path, s0 = window, s1 = text, s2 = next glyph record
.org 0x800167F8                 ; was: lh v1,0(s1) / addiu v0,zero,0x4081
    j    en_char
    nop

; --- line-width measure for centred windows (0x80015F3C): s1 = window, a1 = text, s2 = running x
.org 0x8001602C                 ; was: addiu s4,s4,1 / lbu v1,0xF(s1)
    j    en_meas
    nop

; --- SOL.SRP block load (0x8003793C): a3 = block id (its sector in the original file) -> sector in the repacked file
.org 0x8003796C                 ; was: jal 0x80077958 (delay slot sra a2,s1,0xB stays)
    jal  sol_remap

.org FREE_START
sol_remap:                      ; a3 < SOL_MAP_N: a3 = sol_map[a3]; then the original call
    sltiu at, a3, SOL_MAP_N
    beqz at, @@out
    sll  t0, a3, 1
    la   t1, sol_map
    addu t1, t1, t0
    lhu  a3, 0(t1)
@@out:
    j    0x80077958
    nop

en_char:
    lbu  t0, 0(s1)
    nop
    sltiu at, t0, 0xA0
    beqz at, @@en
    nop
    lh   v1, 0(s1)              ; Japanese: replay the two replaced instructions
    j    0x80016800
    addiu v0, zero, 0x4081
@@en:
    li   t7, 0
@@loop:
    addu t0, s1, t7
    lbu  t0, 0(t0)
    nop
    andi t0, t0, 0x7F           ; 0 = pad: no glyph, no advance
    beqz t0, @@next
    sll  t1, t0, 2
    la   t2, en_glyph
    addu t1, t1, t2
    lw   t1, 0(t1)
    nop
    beqz t1, @@adv              ; space: advance only
    nop
    lh   t2, 0x2E(s0)           ; records used / max (the game's own check)
    lh   t3, 0x30(s0)
    nop
    slt  t2, t2, t3
    beqz t2, @@full
    nop
    lw   v0, 0xC4(s0)
    lhu  v1, 0x22(s0)
    ori  v0, v0, 0x10
    sw   v0, 0xC4(s0)
    sh   v1, 6(s2)
    lw   v0, 0x18(s0)
    lui  t2, 0x800E
    sw   v0, 8(s2)
    lw   v0, 0x4C(s0)           ; x | y << 16
    lh   t2, 0x66B4(t2)         ; CLUT base of the font (0x8008DD20)
    sw   v0, 0xC(s2)
    sll  t2, t2, 16
    addu t1, t1, t2
    sw   t1, 0x10(s2)
    lbu  v0, 0xB(s0)
    nop
    sh   v0, 0(s2)
    andi v0, v0, 7
    beqz v0, @@counted          ; per-glyph fade timing, copied from 0x80016864
    nop
    lhu  v1, 0x28(s0)
    lh   v0, 0x2C(s0)
    ori  v1, v1, 1
    sll  v1, v1, 16
    sra  a2, v1, 16
    sll  v0, v0, 12
    div  v0, a2
    mflo a2
    lhu  v0, 0x34(s0)
    nop
    sh   v0, 2(s2)
    lh   v0, 0x34(s0)
    nop
    mult v0, a2
    mflo v1
    sra  v0, v1, 12
    sh   v0, 4(s2)
    lhu  v0, 0x36(s0)
    nop
    addiu v0, v0, 1
    sh   v0, 0x36(s0)
@@counted:
    lhu  v0, 0x2E(s0)
    addiu s2, s2, 0x14
    addiu v0, v0, 1
    b    @@adv
    sh   v0, 0x2E(s0)
@@full:
    li   v0, 0x20
    sb   v0, 0x83(s0)
@@adv:
    la   t1, en_width
    addu t1, t1, t0
    lbu  t1, 0(t1)
    lhu  v0, 0x4C(s0)
    nop
    addu v0, v0, t1
    sh   v0, 0x4C(s0)
@@next:
    addiu t7, t7, 1
    sltiu at, t7, 2
    bnez at, @@loop
    nop
    j    0x800169B8             ; common tail: speed budget, loop on (s1 += 2); no column count, no auto-wrap
    nop

en_meas:
    lbu  t0, 0(a1)
    nop
    sltiu at, t0, 0xA0
    bnez at, @@jp
    andi t0, t0, 0x7F
    la   t1, en_width
    addu t2, t1, t0
    lbu  t2, 0(t2)
    lbu  t0, 1(a1)
    addu s2, s2, t2
    andi t0, t0, 0x7F
    addu t2, t1, t0
    lbu  t2, 0(t2)
    nop
    j    0x8001604C
    addu s2, s2, t2
@@jp:
    addiu s4, s4, 1
    j    0x80016034
    lbu  v1, 0xF(s1)

.align 4
.include EN_TABLES              ; en_glyph: 128 words, en_width: 128 bytes; sol_map: SOL_MAP_N halfwords
.align 4
vwf_end:                       ; build.py places relocated raw strings from here to FREE_END

.if . > FREE_END
    .error "VWF code overflows the free area"
.endif

.close
