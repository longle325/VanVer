# LitMatch character image prompts

Prompts and image rules for the LitMatch character cards, written for ChatGPT image generation or any DALL·E / SDXL-class model.

Style direction targets the two reference images in `mock style images/`: aged Vietnamese parchment / Đông Hồ folk woodblock + Hàng Trống classical scroll painting. The cultural guardrails block exists because gpt-image models otherwise default to Chinese tropes for "Asian historical figure" — keep that block in the prompt; it makes a measurable difference.

## Level image rule

Each character has three images per level. The current structure is phase-based: Level 1, Level 2, and Level 3 each map to one distinct story phase from `docs/ke-hoach-giai-doan-cap-do-nhan-vat.md`. A fully populated character has nine active images total.

Level 1 files use each character's base naming convention:

```text
public/characters/<character-id>.png
public/characters/<character-id>-2.png
public/characters/<character-id>-3.png
```

`mi`, `thuy-kieu`, and `xuan-toc-do` use `-1`, `-2`, `-3` for Level 1.

Level 2 and Level 3 files use this convention:

```text
public/characters/<character-id>-level-2-1.png
public/characters/<character-id>-level-2-2.png
public/characters/<character-id>-level-2-3.png
public/characters/<character-id>-level-3-1.png
public/characters/<character-id>-level-3-2.png
public/characters/<character-id>-level-3-3.png
```

Images must preserve the same physical identity, face shape, age/body continuity where canon allows, clothing lineage, and cultural setting, then evolve the image through the planned phase: scene, emotional state, lighting, symbolic props, costume wear/details, border complexity, and narrative stakes.

The level progression must be visually obvious even without UI labels:

- **Level 1:** first planned story phase, usually the character's early identity or baseline canonical state.
- **Level 2:** second planned story phase, with a visible change in plot pressure, environment, props, and emotional state.
- **Level 3:** third planned story phase, with the highest emotional stakes or strongest symbolic/canonical consequence.

For the three images inside a level, keep the same character identity and upgrade tier, but vary the camera and moment: portrait, action/emotion beat, and symbolic environment beat.

Do **not** bake explicit level UI into the artwork: no stars, no badges, no "Level 2" / "Level 3" text, no numeric marks, no progress bars, and no decorative rank icons. If the product needs stars or level labels, add them programmatically in the app UI.

Each image should match the aspect ratio of that character's active set. Use cover-crop normalization rather than padding, so generated images do not show extra side or top gutters.

**Recommended size:** Match the existing Level 1 canvas for that character. The current Level 1 file names are:

| Character | File path |
| --- | --- |
| Chí Phèo | `public/characters/chi-pheo.png` |
| Mị | `public/characters/mi-1.png` |
| Xuân Tóc Đỏ | `public/characters/xuan-toc-do-1.png` |
| Lục Vân Tiên | `public/characters/luc-van-tien.png` |
| Thúy Kiều | `public/characters/thuy-kieu-1.png` |

---

## Shared style block (already inlined in each prompt below — no need to add separately)

```
Vietnamese folk illustration in the Đông Hồ woodblock + Hàng Trống classical scroll-painting tradition. Aged parchment paper background with subtle warm sepia and ochre tones, faint paper grain texture, soft hand-painted brush edges. Decorative botanical border ornaments in muted sage green and gold (bamboo leaves, plum blossoms, lotus). Warm natural palette: parchment cream, deep cinnabar red, gold ochre, ink brown, muted jade. Single subject portrait, three-quarter or frontal view, expressive face conveying inner emotion, gentle painterly shading, no harsh photorealism, no anime, no manga, no comic-book gloss. Production-quality book illustration. Strictly Vietnamese cultural setting and clothing — explicitly NOT Chinese, NOT Japanese, NOT Korean.

IMPORTANT cultural constraints — strictly Vietnamese, never Chinese:
- Clothing must be authentic Vietnamese period dress: áo dài, áo tứ thân, áo bà ba, áo ngũ thân, khăn mỏ quạ, khăn xếp, nón lá, nón quai thao — NOT Chinese hanfu, NOT Chinese cheongsam/qipao, NOT Chinese mandarin robes with dragon embroidery, NOT Chinese officials' caps with side wings.
- Hair style must be Vietnamese: women with long black hair styled with hairpin, búi tóc bun at the nape, or a turban (khăn vấn); men with traditional Vietnamese topknot or short hair under a khăn xếp wrapped turban.
- Architecture in any background must be Vietnamese: red-tile village house with curved eaves, communal đình, bamboo grove, palm trees, water buffalo, lotus pond, Vietnamese village gate.
- Avoid all Chinese visual cliches: no panda motifs, no Chinese dragons, no Chinese characters/calligraphy on signage, no qipao mandarin collars, no rice-hat style typically associated with Chinese peasants.
- Skin tone is warm Southeast Asian, not pale East Asian.
```

---

## 1. Chí Phèo — `chi-pheo.png`

```
Vietnamese folk illustration in the Đông Hồ woodblock + Hàng Trống classical scroll-painting tradition. Aged parchment paper background with subtle warm sepia and ochre tones, faint paper grain texture, soft hand-painted brush edges. Decorative botanical border ornaments in muted sage green and gold (bamboo leaves, plum blossoms, lotus). Warm natural palette: parchment cream, deep cinnabar red, gold ochre, ink brown, muted jade. Single subject portrait, three-quarter or frontal view, expressive face conveying inner emotion, gentle painterly shading, no harsh photorealism, no anime, no manga, no comic-book gloss. Production-quality book illustration. Strictly Vietnamese cultural setting and clothing — explicitly NOT Chinese, NOT Japanese, NOT Korean.

IMPORTANT cultural constraints — strictly Vietnamese, never Chinese:
- Clothing must be authentic Vietnamese period dress: áo dài, áo tứ thân, áo bà ba, áo ngũ thân, khăn mỏ quạ, khăn xếp, nón lá, nón quai thao — NOT Chinese hanfu, NOT Chinese cheongsam/qipao, NOT Chinese mandarin robes with dragon embroidery, NOT Chinese officials' caps with side wings.
- Hair style must be Vietnamese: women with long black hair styled with hairpin, búi tóc bun at the nape, or a turban (khăn vấn); men with traditional Vietnamese topknot or short hair under a khăn xếp wrapped turban.
- Architecture in any background must be Vietnamese: red-tile village house with curved eaves, communal đình, bamboo grove, palm trees, water buffalo, lotus pond, Vietnamese village gate.
- Avoid all Chinese visual cliches: no panda motifs, no Chinese dragons, no Chinese characters/calligraphy on signage, no qipao mandarin collars, no rice-hat style typically associated with Chinese peasants.
- Skin tone is warm Southeast Asian, not pale East Asian.

Subject: Chí Phèo (Nam Cao, 1941).

Portrait of CHÍ PHÈO, a male peasant from a Northern Vietnamese rural village in the late colonial era (1930s–1940s, before the August Revolution). Late twenties to early thirties, gaunt face, sharp cheekbones, criss-crossing scars across his face from drunken brawls, stubble, sun-darkened skin from rice-field labor, eyes simultaneously feral and wounded — the face of a man broken by the colonial-era prison and village landlord oppression but still searching for his lost humanity.

Clothing: torn brown peasant tunic (áo nâu sồng) of coarse fabric, frayed at the collar and sleeves, wrapped sash at the waist; bare feet or simple worn straw sandals. He carries an old earthenware liquor bottle in one hand. Stagger in his stance — half-defiant, half-defeated.

Background: a Northern Vietnamese village (Làng Vũ Đại) at dusk — thatched-roof rural houses, bamboo grove, an old brick lò gạch (brick kiln) silhouette in the far distance, communal village gate. Muted earth tones with a single warm ochre lantern glow.

Mood: tragic, raw, the soul of a wronged peasant who once dreamed of being a "lương thiện" (decent) human being. Echoes the Đông Hồ folk style framing of the reference images, with botanical scroll ornaments around the edges.
```

---

## 2. Mị — `mi-1.png`

```
Vietnamese folk illustration in the Đông Hồ woodblock + Hàng Trống classical scroll-painting tradition. Aged parchment paper background with subtle warm sepia and ochre tones, faint paper grain texture, soft hand-painted brush edges. Decorative botanical border ornaments in muted sage green and gold (bamboo leaves, plum blossoms, lotus). Warm natural palette: parchment cream, deep cinnabar red, gold ochre, ink brown, muted jade. Single subject portrait, three-quarter or frontal view, expressive face conveying inner emotion, gentle painterly shading, no harsh photorealism, no anime, no manga, no comic-book gloss. Production-quality book illustration. Strictly Vietnamese cultural setting and clothing — explicitly NOT Chinese, NOT Japanese, NOT Korean.

IMPORTANT cultural constraints — strictly Vietnamese, never Chinese:
- Clothing must be authentic Vietnamese period dress: áo dài, áo tứ thân, áo bà ba, áo ngũ thân, khăn mỏ quạ, khăn xếp, nón lá, nón quai thao — NOT Chinese hanfu, NOT Chinese cheongsam/qipao, NOT Chinese mandarin robes with dragon embroidery, NOT Chinese officials' caps with side wings.
- Hair style must be Vietnamese: women with long black hair styled with hairpin, búi tóc bun at the nape, or a turban (khăn vấn); men with traditional Vietnamese topknot or short hair under a khăn xếp wrapped turban.
- Architecture in any background must be Vietnamese: red-tile village house with curved eaves, communal đình, bamboo grove, palm trees, water buffalo, lotus pond, Vietnamese village gate.
- Avoid all Chinese visual cliches: no panda motifs, no Chinese dragons, no Chinese characters/calligraphy on signage, no qipao mandarin collars, no rice-hat style typically associated with Chinese peasants.
- Skin tone is warm Southeast Asian, not pale East Asian.

Subject: Vợ chồng A Phủ (Tô Hoài, 1952).

Portrait of MỊ, a young H'Mông ethnic-minority woman from the highlands of Northwest Vietnam (Tây Bắc, Hồng Ngài area) in the pre-1954 period. Late teens to early twenties. She is sitting on a low wooden stool, half-turned, spinning hemp thread at a small spinning device beside a tiny square window in a dark, smoke-stained timber house. Her gaze is fixed wordlessly on the distant mountains through the small window — the look of a woman whose grief has gone numb but whose spirit is just beginning to wake.

Clothing: traditional Black H'Mông / Flower H'Mông Vietnamese highland dress — dark indigo-dyed pleated skirt with hand-embroidered geometric red, yellow, and white motifs at the hem; embroidered apron; indigo blouse with cross-stitch trim; silver collar necklace and silver bracelets; black hair wrapped tightly with a colorful hand-woven turban (khăn) typical of H'Mông women in Vietnam. Strictly Vietnamese H'Mông attire — NOT generic Chinese minority garb.

Background: terraced rice fields and pine-covered limestone mountains of Northwest Vietnam visible through the small square window; smoke-stained timber walls inside; a wooden weaving frame in the corner. Cool muted palette of indigo, slate, sage, with a single warm shaft of mountain light through the window.

Mood: quietly resilient, sorrowful but with a flicker of awakening — she still has her youth, she still wants to live, even after years as a debt-slave daughter-in-law. Đông Hồ-style frame with botanical scroll ornaments.
```

---

## 3. Xuân Tóc Đỏ — `xuan-toc-do-1.png`

```
Vietnamese folk illustration in the Đông Hồ woodblock + Hàng Trống classical scroll-painting tradition. Aged parchment paper background with subtle warm sepia and ochre tones, faint paper grain texture, soft hand-painted brush edges. Decorative botanical border ornaments in muted sage green and gold (bamboo leaves, plum blossoms, lotus). Warm natural palette: parchment cream, deep cinnabar red, gold ochre, ink brown, muted jade. Single subject portrait, three-quarter or frontal view, expressive face conveying inner emotion, gentle painterly shading, no harsh photorealism, no anime, no manga, no comic-book gloss. Production-quality book illustration. Strictly Vietnamese cultural setting and clothing — explicitly NOT Chinese, NOT Japanese, NOT Korean.

IMPORTANT cultural constraints — strictly Vietnamese, never Chinese:
- Clothing must be authentic Vietnamese period dress: áo dài, áo tứ thân, áo bà ba, áo ngũ thân, khăn mỏ quạ, khăn xếp, nón lá, nón quai thao — NOT Chinese hanfu, NOT Chinese cheongsam/qipao, NOT Chinese mandarin robes with dragon embroidery, NOT Chinese officials' caps with side wings.
- Hair style must be Vietnamese: women with long black hair styled with hairpin, búi tóc bun at the nape, or a turban (khăn vấn); men with traditional Vietnamese topknot or short hair under a khăn xếp wrapped turban.
- Architecture in any background must be Vietnamese: red-tile village house with curved eaves, communal đình, bamboo grove, palm trees, water buffalo, lotus pond, Vietnamese village gate.
- Avoid all Chinese visual cliches: no panda motifs, no Chinese dragons, no Chinese characters/calligraphy on signage, no qipao mandarin collars, no rice-hat style typically associated with Chinese peasants.
- Skin tone is warm Southeast Asian, not pale East Asian.

Subject: Số đỏ (Vũ Trọng Phụng, 1936).

Portrait of XUÂN TÓC ĐỎ ("Red-Haired Xuân"), a wiry, sun-burnt Vietnamese street hustler-turned-fake-celebrity in 1930s colonial Hà Nội (Hanoi). Lean build, sallow tan skin, his trademark sun-bleached coppery-red hair (the source of his nickname), and a smug half-smirk crossed with mock-bowing showmanship — the face of a complete opportunist who learned to weaponize the empty fashions of the colonial bourgeoisie.

Clothing: an absurdly over-the-top imitation of 1930s European tennis-club fashion as worn by status-hungry Vietnamese urbanites of the colonial period — a too-tight white linen sport jacket, mismatched striped trousers, a loud bow tie or oversized cravat, a stiff celluloid collar shirt slightly askew, a straw boater hat tilted at a cocky angle, and an oversized wooden tennis racket tucked under one arm. The outfit is satirical — meant to look just-off-correct, the way a parvenu wears Western clothes for show.

Background: a 1930s colonial Hanoi street scene — French-colonial yellow-walled storefronts, signs in mixed Vietnamese (chữ Quốc ngữ) and French ("Âu hóa", "Tân thời", "Thể thao"), a rickshaw, a cyclo, and well-dressed bourgeois Vietnamese passers-by in long áo dài and ô (parasols). Architecture is French-colonial Indochinese (NOT Chinese pagoda). Ochre and dust-tone palette with red flag accents.

Mood: satirical, theatrical, faintly absurd — the visual punchline of Vũ Trọng Phụng's social satire. Đông Hồ folk-print framing on the page.
```

---

## 4. Lục Vân Tiên — `luc-van-tien.png`

```
Vietnamese folk illustration in the Đông Hồ woodblock + Hàng Trống classical scroll-painting tradition. Aged parchment paper background with subtle warm sepia and ochre tones, faint paper grain texture, soft hand-painted brush edges. Decorative botanical border ornaments in muted sage green and gold (bamboo leaves, plum blossoms, lotus). Warm natural palette: parchment cream, deep cinnabar red, gold ochre, ink brown, muted jade. Single subject portrait, three-quarter or frontal view, expressive face conveying inner emotion, gentle painterly shading, no harsh photorealism, no anime, no manga, no comic-book gloss. Production-quality book illustration. Strictly Vietnamese cultural setting and clothing — explicitly NOT Chinese, NOT Japanese, NOT Korean.

IMPORTANT cultural constraints — strictly Vietnamese, never Chinese:
- Clothing must be authentic Vietnamese period dress: áo dài, áo tứ thân, áo bà ba, áo ngũ thân, khăn mỏ quạ, khăn xếp, nón lá, nón quai thao — NOT Chinese hanfu, NOT Chinese cheongsam/qipao, NOT Chinese mandarin robes with dragon embroidery, NOT Chinese officials' caps with side wings.
- Hair style must be Vietnamese: women with long black hair styled with hairpin, búi tóc bun at the nape, or a turban (khăn vấn); men with traditional Vietnamese topknot or short hair under a khăn xếp wrapped turban.
- Architecture in any background must be Vietnamese: red-tile village house with curved eaves, communal đình, bamboo grove, palm trees, water buffalo, lotus pond, Vietnamese village gate.
- Avoid all Chinese visual cliches: no panda motifs, no Chinese dragons, no Chinese characters/calligraphy on signage, no qipao mandarin collars, no rice-hat style typically associated with Chinese peasants.
- Skin tone is warm Southeast Asian, not pale East Asian.

Subject: Lục Vân Tiên (Nguyễn Đình Chiểu, mid 19th century).

Portrait of LỤC VÂN TIÊN, a young Vietnamese Confucian scholar-knight from 19th-century Nam Bộ (Southern Vietnam) — the embodiment of the Vietnamese ideal of "trung-hiếu-tiết-nghĩa" (loyalty, filial piety, integrity, righteousness). Late teens to early twenties, handsome, clean-faced, sun-warmed Southeast Asian skin, calm and resolute expression, dark eyes lit with chivalric resolve.

Pose: caught mid-action striking down a band of bandits ("đảng cướp Phong Lai") in a forest clearing, gripping a wooden quarterstaff (or a long staff/đoản côn) in a powerful sweeping arc. Behind him in the deep background, a small ornate palanquin (kiệu) with curtain drawn, carrying Kiều Nguyệt Nga whom he is rescuing.

Clothing: traditional Vietnamese áo ngũ thân or áo dài of a Nguyễn-dynasty Southern scholar — long-sleeved robe in deep indigo or muted blue/teal silk, tied with a wide cloth sash, white inner robe collar showing; loose matching trousers; black khăn đóng (folded turban) on his head; cloth shoes. He looks like a Nam Bộ Vietnamese scholar of the mid-1800s — strictly NOT a Chinese wuxia warrior, NOT in Chinese hanfu or warlord armor, NOT carrying a curved Chinese jian sword.

Background: a Mekong-delta-region forest path with palm trees, banana leaves, and tropical Southern Vietnamese vegetation — bamboo grove, a wooden temple gate (đình) in the haze. Warm dusk light. Brushed in the painterly Đông Hồ / Hàng Trống folk style with botanical scroll edges.

Mood: heroic, upright, the moral idealism of Nguyễn Đình Chiểu's Nam Bộ folk-poem hero.
```

---

## 5. Thúy Kiều — `thuy-kieu-1.png`

```
Vietnamese folk illustration in the Đông Hồ woodblock + Hàng Trống classical scroll-painting tradition. Aged parchment paper background with subtle warm sepia and ochre tones, faint paper grain texture, soft hand-painted brush edges. Decorative botanical border ornaments in muted sage green and gold (bamboo leaves, plum blossoms, lotus). Warm natural palette: parchment cream, deep cinnabar red, gold ochre, ink brown, muted jade. Single subject portrait, three-quarter or frontal view, expressive face conveying inner emotion, gentle painterly shading, no harsh photorealism, no anime, no manga, no comic-book gloss. Production-quality book illustration. Strictly Vietnamese cultural setting and clothing — explicitly NOT Chinese, NOT Japanese, NOT Korean.

IMPORTANT cultural constraints — strictly Vietnamese, never Chinese:
- Clothing must be authentic Vietnamese period dress: áo dài, áo tứ thân, áo bà ba, áo ngũ thân, khăn mỏ quạ, khăn xếp, nón lá, nón quai thao — NOT Chinese hanfu, NOT Chinese cheongsam/qipao, NOT Chinese mandarin robes with dragon embroidery, NOT Chinese officials' caps with side wings.
- Hair style must be Vietnamese: women with long black hair styled with hairpin, búi tóc bun at the nape, or a turban (khăn vấn); men with traditional Vietnamese topknot or short hair under a khăn xếp wrapped turban.
- Architecture in any background must be Vietnamese: red-tile village house with curved eaves, communal đình, bamboo grove, palm trees, water buffalo, lotus pond, Vietnamese village gate.
- Avoid all Chinese visual cliches: no panda motifs, no Chinese dragons, no Chinese characters/calligraphy on signage, no qipao mandarin collars, no rice-hat style typically associated with Chinese peasants.
- Skin tone is warm Southeast Asian, not pale East Asian.

Subject: Truyện Kiều (Nguyễn Du, early 19th century).

Portrait of THÚY KIỀU, the classical Vietnamese literary heroine from Nguyễn Du's "Truyện Kiều" (early 1800s). Young woman of extraordinary beauty in her late teens / early twenties — oval face described by Nguyễn Du as "khuôn trăng đầy đặn nét ngài nở nang", "làn thu thủy nét xuân sơn" (autumn-pool eyes, spring-mountain brows). Long, glossy, jet-black hair flowing past her shoulders, decorated with a single carved jade or wooden hairpin. Soft sad expression, lowered gaze, brimming with quiet sorrow — the look of a woman who has accepted her fate but never relinquished her inner light.

Pose: seated on a low carved wooden bench, gracefully holding a Vietnamese moon lute (đàn nguyệt — two-stringed long-necked lute used in ca trù and ceremonial music), one hand resting on the strings as if mid-pluck. Her gaze is turned outward toward the river beyond. Truyện Kiều's setting is officially Ming China but Vietnamese readers have always visualized her in Vietnamese dress; this illustration follows that Vietnamese visual tradition (the way Đông Hồ and Hàng Trống prints depicted her).

Clothing: classical Vietnamese áo tứ thân (four-panel gown) or refined áo ngũ thân in soft jade-green, peach, and rose silk, with a long flowing inner skirt; a yếm (Vietnamese silk halter undergarment) showing in soft rose at the neckline; a wide cloth sash; soft cloth slippers. A delicate silk shawl drapes from her shoulders. NOT a Chinese hanfu, NOT a qipao — strictly Vietnamese áo tứ thân court-style.

Background: lầu Ngưng Bích (Ngưng Bích pavilion) on a high cliff overlooking the misty Tiền Đường river at twilight, distant mountains, lotus pond foreground, a single crane flying past, willow branches. Soft dusk palette of jade, rose, gold, pale ink-blue.

Mood: melancholic, refined, lyric — "tài mệnh tương đố" — the great Vietnamese national heroine of the human heart. Đông Hồ folk-print framing.
```

---

## After you have the PNGs

1. Drop active Level 1/2/3 files into `public/characters/` with the filename convention above.
2. Verify every file has the same dimensions and aspect ratio as that character's active set.
3. Update `src/data/characters.ts` only if the naming convention changes.
