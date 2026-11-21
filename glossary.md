# Glossary - Blade Arts: Tasogare no Miyako R'lyeh

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: when a JP form (whole kana/kanji run) is in a line, one of the EN forms
(separated by `/`) must be in its English, and no `Avoid` spelling may appear.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Nakamura-sama). Name order: Western (given name first). Name+honorific pairs:
  ナカムラ様, リズィちゃん, キキ君, and Ranfa's teasing 零クン (Rei-kun); ミスター/ドクター become Mr./Dr.
- Romanisation source: official English where it exists, else an earlier fan patch, else Hepburn without macrons
  (none official or patched found: MobyGames credits use the same Hepburn forms, Rei Shido / Ranfa / Landers).
- Credits: English.
- Register: modern American English for the cast; the archaic voices (sword spirit, Basetet, the Primordial One's
  cult) stay archaic. Sound effects / interjections: English equivalents (ぐっ -> "Ngh!", くそっ -> "Damn!").
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation: 「」 -> "...", 『』 -> '...', ‥‥ / ・・・ -> "..." (one ellipsis however long the JP run), ！？ -> !?,
  ～ -> ~, ＜X＞ headings keep the fullwidth ＜＞ (the font has no < >). Button symbols ○ △ □ × stay as the fullwidth
  JP glyphs ("Press ○ twice"); L1/R1/L2/R2/START/SELECT in ASCII.
- Characters not in the English font: # $ < > @ \ ^ _ ` { | }. Use "and" for &? (& is fine), "No." for #.
- Voices:
  - Rei (零): rough, cocky, sarcastic young treasure hunter; swears mildly (てめぇ -> "you bastard"/"pal", くそっ ->
    "Damn it!"), drops g's sparingly ("ain't" no). Short, punchy sentences.
  - Ranfa (蘭花/藍花): bright, teasing radio navigator, friendly-bossy with Rei; casual ("Hey, Rei!", "okay?").
  - Bridget: quiet, polite, enigmatic girl (少女 "the girl" before she is named).
  - Walter Landers: measured, scholarly, older man; formal but warm toward Bridget.
  - Marion: mocking, sing-song menace ("Oh my, you're still alive?"), calls Rei "darling"/"boy" where アナタ/ボウヤ.
  - Tindalos: arrogant, archaic villain (うぬぅ -> "Grr...", 貴様 -> "you wretch").
  - Basetet / sword spirit / ancient voices: solemn archaic ("Sheathe thy sword...", 汝 -> thou/thee, 我 -> I).
  - Dr. Sanderson ("Doc"): gruff old scientist; Zagnus: smug corporate security chief.
  - News readers (t0 subtitles in the intro): neutral broadcast English.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 零 / シドウレイ / 志道零 | Rei | | hero, full name Rei Shido; speaker label "Rei:" | Ray / Zero |
| シドウ | Shido | | ミスター・シドウ -> Mr. Shido | Shidou / Shidoh |
| 蘭花 / 藍花 / ランファ | Ranfa | | navigator (both kanji spellings are the same person) | Lanfa / Ranka |
| ブリジット | Bridget | | the girl; Bridget Landers | Brigitte |
| ウォルター | Walter | | Walter Landers, Bridget's father | |
| ランダース | Landers | | family name | Randers |
| マリオン | Marion | | | Marian |
| ティンダロス | Tindalos | | | |
| サンダーソン | Sanderson | | Dr. Sanderson; ドク -> "Doc" | Saunderson |
| ナカムラ | Nakamura | | | |
| ザグナス | Zagnus | | | Zagunas |
| リズィ / リズ | Lizzie / Liz | | リズィ -> Lizzie, リズ -> Liz | Lizzy |
| メリンダ | Melinda | | | |
| パット | Pat | | | |
| パトリシア | Patricia | | Patricia Millers | |
| ミラーズ | Millers | | | |
| マヤ | Maya | | | |
| キキ | Kiki | | キキ君 -> Kiki-kun | |
| ジッティ | Jitty | | | |
| バセテト | Basetet | | ancient guardian deity | Bastet |
| ジイ | Gramps | | ジイさん: the old man Rei runs errands for | |
| パニッシャー | Punisher | | | |
| ガーディアン | Guardian | | | |
| 原初の者 | Primordial One | | | |
| クトゥリュウ | Cthulhu | | | Kuturyu |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ルルイエ | R'lyeh | | | Ruruie |
| セイレム | Salem | | セイレム島 -> Salem Island | |
| ドーン・セキュリティ | Dawn Security | | the security company | |
| イースター | Easter | | Easter Island | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| スフィア | Sphere | | sword-mounted orb that holds an Art | |
| アーツ | Art / Arts | | sphere attacks | |
| アーツパワー | Arts Power | | | |
| ネルウス | Nervus | | power poured into spheres | |
| 剣の記憶 | Memory of the Sword / Memories of the Sword / sword's memory | | save points | |
| 翡翠版 / 翡翠板 | Jade Tablet | | 翡翠版のカケラ -> Jade Tablet Fragment | |
| 輝玉 | Gleaming Orb | | 青の輝玉 Blue Gleaming Orb, 紅の輝玉 Crimson Gleaming Orb | |
| 原初の結晶 | Primordial Crystal | | | |
| 蹟剣 | Relic Sword | | | |
| 蹟玉 | Relic Orb | | | |
| 蹟棒 | Relic Rod | | | |
| トニトルス | Tonitrus | | sphere | |
| テンペリエス | Temperies | | sphere | |
| フォルテス | Fortes | | sphere | |
| グラヴェス | Graves | | sphere | |
| イグニス | Ignis | | sphere | |
| ユーデクス | Iudex | | tablet | Judex |
| レーゲース | Leges | | tablet | |
| ユーディキウムー | Iudicium | | tablet | |
| サンクティオー | Sanctio | | tablet | |
| ビィクトル | Victor | | tablet | |
| トリウンプス | Triumphus | | tablet | |
| アートレーター | Atrator | | tablet | |
| ムンドウス | Mundus | | ＜＞ heading, block 91/92 | |
| テツラ | Terra | | ＜＞ heading (JP typo of テッラ) | |
| アリエース | Aries | | | |
| アクアーリウス | Aquarius | | | |
| タウルス | Taurus | | | |
| スコルピウス | Scorpius | | | |
| シグヌム | Signum | | | |
| リーブラ | Libra | | | |
| ゲミニー | Gemini | | | |
| カプリユルヌス | Capricornus | | | |
| レオー | Leo | | | |
| カンケル | Cancer | | | |
| ウイルゴー | Virgo | | | |
| サギタリウス | Sagittarius | | | |
| ピスケース | Pisces | | | |
| メモリーカード | Memory Card | | | |
| パスコード | passcode | | | |
| イ・ルム / イ＝ルム | I-Rum | | the system Walter built (see synopsis) | |
| 制裁者 | Punisher | | Rei's sword (also パニッシャー) | |
| 尊厳者 | Majesty | | Nakamura's sword, from Basetet | Exalted One |
| ＤＳＯＮ | DSON | | Nakamura's armed security force | |
| 獅堂 | Shido | | 獅堂零 -> Rei Shido | |
| 摩耶 | Maya | | | |
| グノフ＝ケー | Gnoph-Keh | | | |
| 翡翠盤 | Jade Disc | | not the Jade Tablet | |
| 石板 / 石版 | Tablet / tablet | | named ones: "Iudex Tablet" etc. | Stone Slab |
| 孔雀石の石板 | Malachite Tablet | | | |
| 巨石像の石版 | Colossus Tablet | | | |
| 黄色い石板 / 石黄の石板 | Yellow Tablet | | one item | Orpiment |
| 紅の石像 | Crimson Statue | | | Crimson Stone Statue |
| 青の石像 / 蒼の石像 | Blue Statue | | one item | Azure |
| 石の把手 | Stone Handle | | | |
| 銅のプレート | Copper Plate | | | |
| 起動プレート | Activation Plate | | 操作盤起動プレート -> Control Panel Activation Plate | |
| 起動カード | Activation Card | | | start-up card |
| 重力エレベーター / 重力エレベータ | Gravity Elevator / gravity elevator | | | |
| 研究棟 | research facility | | | |
| 記憶の石碑 | Memory Stele | | plain 石碑 -> stele | |
| 石碑 | stele | | never "stone tablet" (that is 石板) | |
| 隊長 | Captain / captain | | Nakamura as DSON's commander; 隊長さん -> "the captain" | |
| 大将 | boss | | Rei's slangy おまえんとこの大将 | |
| 我流 | self-taught | | 我流が -> "self-taught punk" | Amateur |
| 優性思想 | eugenics / master-race | | Nakamura's ideology (block 104) | elitist |
| 剣の神殿 | Temple of the Sword | | | |
| Ｃ４爆弾 | C4 | | C4 Bomb | |

## Decisions from earlier batches
- 零クン (Ranfa teasing) -> "Rei-kun" (b008 review).
- 石碑 -> stele, 隊長 -> Captain, 大将 -> boss, 我流 -> self-taught (phase-6 review, rows above).
- ミラー / ミラーズ both point at Patricia Millers: "Millers" (sol.58.10, 89.26).
- Ellipsis: one "..." per pause, never 4+ dots (D11; `batches.py check` lints it).
- Save prompt 汝、剣の記憶をとどめる事を欲するか？ -> "Wouldst thou preserve the sword's memory?" (19 copies).
- 貴様 from any villain -> "you wretch", never "you bastard" (Rei's てめぇ only).
