# Style reference

Pilot: batch b001 (reviewed 2026-11-22, `work/qa/review/b001.report.md`: Approved after the sol.5.3 fix) (blocks 1-11: sword-memory save prompt, item pickups, the earthquake news intro, Rei waking
in the ruins, the first Sphere tutorial, Rei and Ranfa at camp). Seen in game in the smoke run (news subtitles).

## Voices
| Who | JP markers | English devices |
|---|---|---|
| Rei | てめぇ, 〜ねぇ, 〜やがる, くそっ, ちっくしょう, 〜ちまう, 俺 | clipped, cocky, mild swearing: "Damn", "what the hell", "gotta", "Yeah, right!"; never "ain't"-heavy hick speech |
| Ranfa | 〜じゃない, 〜よー, 〜かなー, あたし | bright, teasing, stretched vowels with ~: "Huh~? I didn't do anything~?" |
| Sword spirit / Basetet / ancients | 汝, 我, 〜せよ, 〜なり | archaic: thou/thee/thy, "Sheathe thy sword", "Wouldst thou..." |
| Soldiers shouting | 男ぉ, とまれぇ, 射殺するぅ | stretched letters: "You therrre! Halt! Stop or we'll shoooot!" |
| Eerie katakana speech (カエリナサイ, シヌ) | broken katakana | short words split by ellipses: "...Go... home...", "Leave... this place... or die..." |
| News readers | 〜との事です, 〜模様です | neutral broadcast English: "According to Kyodo News, ...", "is expected to..." |
| System / signs (t3) | 〜を手に入れた, 〜ますか？ | "Got the X.", "Take the X?", "Looks like there's some kind of mechanism..." |

## Fixed forms
- Yes/No choice tail: `\\{t0[DD1}　Yes　　　　　　{[2}　　No` (JP fullwidth padding, one extra space after Yes).
- Pick-up: `{t3}Got the {b3}P.E. Bomb{b0}.` (split `{t3b3}` so "Got the" stays uncoloured).
- Thoughts in 「」: `{t3}"Was that vision for real?\\I'd better go check the tent."`
- Tutorial windows (WS): imperative, second person: "Mount a Sphere on your sword to unleash the Art held within it."

## Example pairs
- `{t3}剣を納めよ‥‥‥\\我、剣の記憶を司る者‥‥@@汝、剣の記憶をとどめる事を欲するか？` ->
  `{t3}Sheathe thy sword...\\I am keeper of the sword's memory...@@Wouldst thou preserve the sword's memory?`
- `{CSA0t0e00894}最後の最後でテキトーな事ぬかしたのは、\\どこのどいつだ！@@おかげで、転落死しかけるわ、恐竜もどきに\\追いかけ回されるわ。` ->
  `{CSA0t0e00894}Who fed me that half-baked garbage\\at the very last second!?@@Thanks to you, I nearly fell to my death\\and got chased around by some dino-thing!`
- `{CSA0t0e01059}えー、あたし何にもしてないよー？\\` -> `{CSA0t0e01059}Huh~? I didn't do anything~?\\`
- Corrected example: `{CSA0t0e00402}地震や火山活動の観測を行い、@@...` first came out as "monitoring seismic activity" (to fit
  288 px, dropping 火山): a voiced page may take a second line instead (`seismic\\and volcanic activity,@@`) as long
  as the page count stays the JP's. Never drop meaning to fit.
