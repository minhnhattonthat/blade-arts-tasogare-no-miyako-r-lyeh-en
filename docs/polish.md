# Polish pass (Minor review findings, deferred)

One line per finding: `- [ ] id - note`. The polish pass ticks each `[x]` (fixed, or `waived: reason`); the release
script refuses to run while any line is unticked. Lines ticked "fixed (phase-6 review)" were Important per the
reviewer brief and fixed before phase 7 (harness review of phase 6).

Polish pass done 2026-11-22: fixes in batch `work/tl/p01.out.tsv` (`tools/polish.py`, merged with
`tools/batches.py merge p01 --overwrite`, which copies each fix to every string with the same JP and form; 168
strings changed, sol.132.109 put back to "...Nothing." since it answers "what's wrong?"). "fixed (p01)" below.

## b001 (review 2026-11-22, `work/qa/review/b001.report.md`: Approved; Important sol.5.3 fixed)
- [x] sol.10.1 - fixed (p01): "You put me through hell, pal!"
- [x] sol.10.5 - fixed (p01): "Well~, you're the one who said you'd go deeper, Rei."
- [x] sol.10.10 - fixed (p01): "...Maybe you were the one half asleep, hm~?"
- [x] sol.10.11 / 11.2 - fixed (p01): "You're noisy." / "...That's the message." (no guessed "kid" / "he")
- [x] sol.4.3 / 5.4 - fixed (p01): "to keep the island from being unlawfully seized" ("volcanic" dropped for width)
- [x] sol.4.4 / 5.5 - fixed (p01): "reportedly set sail"
- [x] sol.4.5 - fixed (p01): "set out"
- [x] sol.1.5 - waived: optional; "Got Jade Tablet Fragment 4." matches the other numbered pick-ups
- [x] sol.7.19 - fixed (p01): "Then I've gotta hurry all the more!!"
- [x] sol.7.21 - fixed (p01): "You're going out of your way to point me there."
- [x] sol.9.11 - fixed (p01): "Hiding in there won't save yooou!"
- [x] sol.9.12 - fixed (p01): "Damn, here they come again!"
- [x] sol.8.1 - waived: optional; "Backup!" reads naturally
- [x] sol.7.0 - waived: optional; the trailing ぞ adds nothing in English
- [x] sol.9.15 - waived: the JP names ステータス in caps-style button text (START, MENU); the screen is the status menu
  (STATUS:0D928 "Exit Status Mode.")

## b002/b003 (review 2026-11-22: Approved)
- [x] sol.15.10 - fixed (phase-6 review): "Hey now, out of my way, boy."
- [x] sol.14.4 - fixed (p01): "Good work." (and its copy 15.3)
- [x] sol.14.0 / sol.21.3 - waived: a camp member, not Rei; the gruff なんだ？ fits "Who the hell's"
- [x] sol.15.30 - fixed (p01): "So why would the head of Dawn Security come all the way out..."
- [x] sol.17.0 - fixed (phase-6 review): "you sent over"
- [x] sol.17.23 - waived: story pass ch02 found the "Sorry." (17.23) / "Forgive me." (34.37) pair works
- [x] sol.19.21 - fixed (p01): "Not that it makes up for it, but in exchange, I'll give you this!"

## b004/b005 (review 2026-11-22: b004 Needs fixes -> 28.125, 28.74 fixed; b005 Approved)
- [x] sol.28.31 - fixed (p01): "If you slack, everyone pays for it, so you'd better try hard, okay?"
- [x] sol.28.87 - fixed (p01): "...Am I really that untrustworthy?" (= 147.111, same JP)
- [x] sol.28.77 - fixed (p01): "Quite the prankster... I mean, you got here fast..." (= 147.101; double space gone)
- [x] sol.28.34 - fixed (p01): "...So much for trust." (= 147.59, same JP)
- [x] sol.28.23 - fixed (p01): "Whoa, this is..."
- [x] sol.28.149 - waived: "Prestage" matches the G6 Prestage title card drawn in game
- [x] sol.43.10 - fixed (phase-6 review): Nakamura "You wretch... still alive, are you..." (125.93 aligned)
- [x] sol.43.20 / 34.0 - fixed (phase-6 review): 隊長 -> Captain, 大将 -> boss (glossary rows)
- [x] sol.42.28 - fixed (p01): "Demon or serpent, let's see what crawls out..." (125.74 the same)
- [x] sol.38.0 vs 42.22 - waived: the JP itself shortens the item name in the switch message
- [x] sol.34.21 - fixed (p01): "I don't have that kinda pull."

## b014-b016 (review 2026-11-22: Approved; Important 138.57, 138.29, 147.101, 147.102 fixed)
- [x] sol.132.48 - fixed (p01): "neither of us is a ghost."
- [x] sol.132.60 - fixed (p01): "Keep talkin' like that, and you can go out there alone." (two lines for width)
- [x] sol.138.88 - fixed (p01): "Be... care..." (= 81.16; the JP cuts off)
- [x] sol.138.50 - fixed (p01): "and they still haven't cleared out the DSON guys."
- [x] sol.138.34 - fixed (phase-6 review): "I shall commend you for pursuing us this far."
- [x] sol.138.122 - fixed (p01): "I'd settled the score for everyone"
- [x] sol.145.0 - fixed (p01): "the atmosphere's all different..."
- [x] sol.147.34 - fixed (p01): "There are more Guardians up ahead, right?" (all copies)
- [x] sol.147.26 - waived: "homeland" is the wording of the same line in 24.26 / 26 / 117; 郷 = home ground

## b006-b009 (review 2026-11-22: all Approved)
- [x] sol.49.8 - fixed (p01): "You're clearly not all right!"
- [x] sol.49.17 - fixed (p01): "over one measly human dying"
- [x] sol.48.8/48.9 - fixed (p01): 48.9 "But when they really do it..."
- [x] sol.53.18 - fixed (p01): "Man, you've sure got a soft spot for her, Gramps." (no "dirty old man")
- [x] sol.59.5 - fixed (phase-6 review): "You wretch!\\I hold my tongue, and you prattle on and on!"
- [x] sol.56.12 - waived: 零クン "Rei-kun" kept, glossary amended
- [x] sol.56.14 - fixed (p01): "Come to think of it, I feel like I forgot to say something..."
- [x] sol.58.10 - fixed (phase-6 review): "There was someone called "Millers"..."
- [x] sol.62.81 / 74.44 - fixed (p01): "Yes... I was made... given life by Basetet, my mother..."
- [x] sol.62.98 / 78.56 - waived: "someone" stands in for the JP's unstated object without guessing who
- [x] sol.28.60/62, 119.60/62 - fixed (phase-6 review): "stele"
- [x] sol.81.16 vs sol.138.88 - fixed (p01): both "Be... care..."
- [x] sol.69.6 - fixed (p01): "Damn it!"
- [x] sol.70.26 - waived: story pass ch03 reads "You always were that kind of person" as right for でしたね

## b010-b013 (review 2026-11-22: b011 Needs fixes -> 104.21/22/26 eugenics fixed; rest Approved)
- [x] sol.81.98 - waived: D11, one "..." per pause
- [x] sol.81.62 - fixed (p01): 81.38-40 wording ("It can transfer itself", "mind waves")
- [x] sol.100.7 - fixed (p01): "Heard something move..." (= 147.12, same JP)
- [x] sol.103.7/103.8 - fixed (p01): "Open the vents?" / "Close the vents?"
- [x] sol.104.7 - fixed (p01): "mind-control everyone in the world and rule it?"
- [x] sol.113.27/113.40 - fixed (p01): "...Like I had time to go hunting for junk in a mess like that, idiot."
- [x] sol.125.74 - fixed (p01): "Demon or serpent, let's see what crawls out..."
- [x] sol.125.99 - fixed (p01): "You take hostages, and that's all you say!?" (width)

## b017-b019 (review 2026-11-22: all Approved; b018 Important LOADSAVE:00CF8, STATUS:00748/0082C fixed)
- [x] sol.147.146 - fixed (p01): "Damn, so there was a trap after all!!"
- [x] sol.147.118 - fixed (p01): "is pretty fragile too."
- [x] sol.147.106/107 - fixed (p01): pages start "Then keep pushing..." / "Then press..."
- [x] sol.147.115 - fixed (p01): "Not a cute bone in her body."
- [x] sol.147.156 - fixed (solview VQA): "as dinner"
- [x] sol.147.147 - fixed (p01): "Why'd I listen to that idiot's..."
- [x] sol.166.25 vs 166.10 - fixed (phase-6 review): "Self-taught punk." (glossary 我流)
- [x] sol.166.9 - fixed (p01): "had no fixed form"
- [x] sol.169.4 - fixed (p01): "but it's a bit late for that"
- [x] LOADSAVE:002A0 - fixed (p01): "Bigachuuu!!"
- [x] LOADSAVE:003C4/00A08/00A98/00CAC - fixed (p01): "Checking Memory Card..." etc.
- [x] LOADSAVE:00770 - fixed (p01): "The Memory Card was removed."
- [x] LOADSAVE:00540/00C54/00790/008E8 - fixed (p01): "At least 1 free block (in slot 1).", "Blade Arts data in slot
  1." (list items under a "needs" header; no "1+")
- [x] STATUS:0DAD0 - fixed (p01): "Gives the Punisher the power of flight."
- [x] STATUS:01028 - fixed (p01): final period
- [x] STATUS:00AD8 - fixed (phase-6 review): "A fragment of a tablet made of jade."

## Voiced line vs its text-panel replay (phase-6 harness review, Minor 9)
- [x] sol.69.1 / 138.29 - fixed: both "Hm... you wretch!"
- [x] sol.43.10 / 125.93 - fixed: both "You wretch... still alive, are you..."
- [x] sol.28.78 / 147.102 - fixed: same wording
- [x] sol.1.0 - fixed (p01): "I am the keeper of the sword's memory..." (all 19 copies)
- [x] sol.17.0 - fixed (p01): "our company's core operations"
- [x] sol.138.34 - fixed (p01): "But you have become far too much of an eyesore..."
- [x] sol.43.20 - waived: optional; "this boy" keeps Marion's tone
- [x] all - done by the story pass (ch05 / ch06 read 125, 138, 147, 159 against the JP and their originals); the
  drifts it found are the lines below and in p01

## Visual QA of the SOL sheets (2026-11-22, `work/qa/solview/verdicts/`)
- [x] sol.46.x / 125.x - fixed (p01): "Gravity Elevator" capitalised everywhere (b042's form)
- [x] sol.104.x / 106.x - fixed (p01): double quotes
- [x] sol.42.x - waived: the JP itself says 起動プレート there

## Story pass (phase 9, `docs/reviews/story.report.md`)
- [x] sol.15.23 - fixed (p01): "my hands are too dirty to see my daughter."
- [x] sol.17.11 - fixed (p01): final period
- [x] sol.24.57 (+26.57 and copies) - fixed (p01): "Wouldst thou preserve the sword's memory?"
- [x] sol.48.2 - fixed (p01): "Activated the mechanism..."
- [x] sol.48.4 - fixed (p01): "Riding this should take me to the upper level."
- [x] sol.28.95 - fixed (p01): "Whoa-aah!" (= 147.117)
- [x] sol.62.11 (+72.11) - fixed (p01): "the one that brought forth all life..."
- [x] sol.81.62 - fixed (p01): 81.38-40 wording
- [x] sol.86.1 - fixed (p01): "The woman... on that pedestal?" (= 81.20)
- [x] sol.104.29, sol.106.14 - fixed (p01): double quotes
- [x] sol.113.30 - fixed (p01): "...Why, this is...!"
- [x] sol.138.107 - fixed (p01): "mind waves"
- [x] sol.138.88 - fixed (p01): "Be... care..."
- [x] sol.132.111 - fixed (p01): "...It's all right." (= 61.24; 132.109 stays "...Nothing." = 61.22)
- [x] sol.147.27-48 (+159/166/169/173 copies) - fixed (p01): the sanctuary girl in modern formal English like 24.27-48
  ("Your journey...", "you", "the path where there is none")
