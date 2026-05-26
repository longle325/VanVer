# Handoff — adding new characters to LitMatch

You are extending LitMatch (a gamified Vietnamese-literature roleplay app) by adding one or more new characters alongside the existing five (`chi-pheo`, `mi`, `xuan-toc-do`, `luc-van-tien`, `thuy-kieu`). The product is shipped — the matched five characters work end to end against gpt-4o + RAG retrieval, with a chat typing indicator, source citation chips, and a 5-question challenge per character. Your job is to add new characters with the **same fidelity** the existing five have, with no shortcuts.

This document gives you every touchpoint, the exact data shape at each, and the order in which to do them. Read it through once before you write any code.

---

## 0. Repo orientation (read first)

- Working directory: `/Users/PhatNguyen/Desktop/Husky` (single repo).
- Primary config: a single `.env` at the repo root. Backend reads it via `pydantic-settings`; frontend reads it via Vite (`frontend/vite.config.ts` sets `envDir: "../"`). Don't split it.
- Default models: `CHAT_MODEL=gpt-4o`, `EMBEDDING_MODEL=text-embedding-3-large` (3072 dims).
- Branch from `main`. After your work, open a PR titled e.g. `Add character: <Name> (<Work>)`.
- Don't push to `main` unless the user explicitly says hotfix.
- Don't add Co-Authored-By trailers.
- Don't commit anything in `.brv/` or generated `*.tsbuildinfo` files.

### Slug naming — there are TWO forms; you will need both

| Surface | Form | Example |
|---|---|---|
| Backend (DB, manifest, chunks, prompt cards, seed script) | snake_case | `chi_pheo`, `xuan_toc_do` |
| Frontend (URL, FE seed `id`, image filenames, FE type) | kebab-case | `chi-pheo`, `xuan-toc-do` |

Conversion is one-way at the API boundary: `frontend/src/api/adapter.ts:normalizeSlug` replaces `_` with `-`. **Always pick a slug whose snake/kebab variants are mechanical replacements of each other** — no other rewriting (e.g. `Vietnamese diacritics → ASCII`, lowercase). The folder under `backend/knowledge_base/` may use a different casing if natural (e.g. `Xuan_red_hair` for `xuan_toc_do`); the manifest links the two.

### Files / dirs you will touch (complete list — there is no other place)

**Frontend:**
1. `frontend/src/data/characters.ts` — the live FE seed (`rawCharacters` array)
2. `frontend/public/characters/<slug>.png` (+ optional `<slug>-2.png`, `<slug>-3.png`)

**Backend:**
3. `backend/scripts/seed_database.py` — three lists/dicts: `CHARACTER_SEEDS`, `CHARACTER_RELATIONSHIP_SEEDS`, `CHARACTER_EVENT_SEEDS`
4. `backend/knowledge_base/<Folder>/` — at least one **original** text + one or two **analyses**, all `.txt`
5. `backend/knowledge_base/manifest.json` — register the character + every document under it
6. `backend/knowledge_base/index/documents.jsonl` — one record per document
7. `backend/knowledge_base/index/chunks.jsonl` — one record per chunk (sliding-window split of the source text)
8. `backend/core/prompt_templates.py` — entry in `CHARACTER_CARDS` and `TIMELINE_STAGES` (this is the role-play voice; treat it like writing a screenplay character bible)

**Tests:**
9. `backend/tests/test_seed_database.py` may need a count update if it asserts on number of characters.
10. `backend/tests/test_prompt_templates.py` — should already pass without modification, but re-run it.

**Pipeline you will run after editing the above:**
- `docker compose up -d postgres` (one-time)
- `cd backend && ./.venv/bin/python scripts/seed_database.py` — pushes character + challenge + relationship + event rows to Postgres
- `cd backend && ./.venv/bin/python scripts/embed_knowledge_base.py` — embeds new chunks via OpenAI. **Costs API tokens; ask the user before running this.** Skips chunks whose `text_hash` is already embedded, so re-runs are cheap.
- (Optional) `bash scripts/dump-knowledge-chunks.sh` — refreshes the gzipped pgvector dump for teammates so they don't re-embed.

---

## 1. Source material — what to gather before you write anything

For every new character you must collect, in `backend/knowledge_base/<Folder>/`:

1. **One canonical original text** in `.txt` (full or substantial passage). Convert PDF → text with `backend/scripts/extract_pdfs_to_text.py` if needed.
2. **One or two literary analyses** in `.txt` describing personality, conflict, key scenes — these are what give RAG its grounding for character voice and motivation.

The five existing characters have:
- `Chi_Pheo/`: `Chí_Phèo.txt` + `bi_kich_cu_tuyet_quyen_lam_nguoi.txt` + `qua_trinh_thuc_tinh_tam_li.txt`
- `Mi/`: `Vợ_chồng_a_phủ.txt` + `phan_tich_nhan_vat_mi.txt` + `suc_song_tiem_tang.txt`
- `Xuan_red_hair/`: `Số_Đỏ.pdf` + `Số_Đỏ_full_text.txt` + `phan_tich_nhan_vat.txt`
- `Luc_Van_Tien/`: `Lục_Vân_Tiên_(bản_Quốc_ngữ_2082_câu)_I.pdf` + `..._full_text.txt` + `phan_tich_nhan_vat_luc_van_tien.txt`
- `Thuy_Kieu/`: `Truyện_Kiều_..._full_text.txt` + `tam_trang_thuy_kieu_trao_duyen.txt` + `Kieu_o_lau_ngung_bich.txt`

**Read every file end to end before drafting the character card.** This is the explicit instruction — the existing card quality (PR #15, `feat/literary-character-prompts`) is grounded in canonical detail like "lò gạch cũ", "bát cháo hành", "lầu Ngưng Bích", "tiếng sáo gọi bạn đầu núi". A generic card produces a generic LLM voice. Do not skip this step.

---

## 2. The frontend seed — `frontend/src/data/characters.ts`

Append a new entry to `rawCharacters: SeedCharacter[]`. Required fields (`Character` interface in `frontend/src/types/index.ts`):

```ts
{
  id: "<kebab-slug>",                // e.g. "chi-pheo"
  name: "Chí Phèo",                   // display name (Vietnamese, with diacritics)
  work: "Chí Phèo",                   // work title
  author: "Nam Cao",
  initial: "C",                       // single-character avatar fallback when image missing
  artA: "#2c1f1b",                    // gradient color A (hex) — used by avatar fallback
  artB: "#8a3d22",                    // gradient color B (hex)
  artTitle: "Làng Vũ Đại",            // short label shown on the discover card
  image: "/characters/chi-pheo.png",  // primary portrait
  images: [                           // additional swipeable portraits (optional)
    "/characters/chi-pheo.png",
    "/characters/chi-pheo-2.png",
    "/characters/chi-pheo-3.png",
  ],
  genre: "truyện ngắn",               // "truyện ngắn" | "tiểu thuyết" | "truyện thơ" | etc.
  imageBrief: "Người đàn ông gầy gò, mặt đầy sẹo...",  // 1-line image description
  bio: "Trai làng Vũ Đại. Bề ngoài hổ báo nhưng bên trong đầy vết xước...",
  quote: "Tao muốn làm người lương thiện! Ai cho tao lương thiện?",
  personality: "Hung hãn, liều lĩnh sau khi bị tha hóa; nhưng khi được yêu thương thì nhạy cảm...",
  conflict: "Giằng xé giữa bản ngã bị xã hội biến dạng và phần lương thiện bừng tỉnh...",
  context: "Làng quê Việt Nam trước Cách mạng tháng Tám, nơi cường hào ác bá...",
  sources: [                          // 3 short canonical observations — the FE shows these
    "Tiếng chửi mở đầu cho thấy Chí Phèo bị cả làng Vũ Đại gạt khỏi cộng đồng người.",
    "Bát cháo hành của Thị Nở đánh thức khát vọng sống lương thiện và được yêu thương.",
    "Cái lò gạch cũ gợi vòng luẩn quẩn của những kiếp người bị xã hội bỏ rơi.",
  ],
  voice: "thô ráp, đau đớn, có lúc bừng lên mong muốn được công nhận là con người",
  chatOpening:                        // first bot message in /characters/<id>/chat
    "Tao là Chí Phèo. Người ta nhớ tao qua tiếng chửi, vết sẹo, men rượu và bát cháo hành...",
  suggestedQuestions: [],             // empty array → falls back to challenge[0..2].text
  interpretationThemes: ["Tha hóa", "Lương thiện", "Định kiến", "Tình thương", "Quyền làm người"],
  symbols: ["Tiếng chửi", "Bát cháo hành", "Vết sẹo", "Lò gạch cũ", "Rượu"],
  challenge: [                         // EXACTLY 5 questions, 4 options each, 0-indexed answer
    q("Nguyên nhân sâu xa nào đẩy Chí Phèo vào con đường lưu manh hóa?",
      ["Bản chất Chí vốn ác độc từ nhỏ",
       "Nhà tù thực dân và cường hào làng Vũ Đại đã tha hóa người nông dân",
       "Chí không thích lao động",
       "Thị Nở ruồng bỏ Chí ngay từ đầu"],
      1,
      "Bi kịch của Chí bắt nguồn từ xã hội phi nhân đạo: ..."),
    // ... 4 more
  ],
}
```

**Five rules**
- `id` (FE) MUST equal the snake-case BE slug with `_` → `-`. The whole stack assumes this.
- `image` paths must point to files you actually drop into `frontend/public/characters/`.
- `challenge` has exactly **5 questions, 4 options each**. The challenge scoring (`POINTS_CHALLENGE_PASS_BONUS=40`, `CHALLENGE_PASS_THRESHOLD=4` from `.env`) assumes 5.
- The FE seed is the single source of truth for `images[]`, `interpretationThemes[]`, `symbols[]`, `chatOpening`. The backend doesn't carry these.
- `Content for Hackathon game - Sheet1.pdf` and `Content_reference.csv` at the repo root contain the team's authoring source; cross-check your bio/quote/themes against these to stay editorially consistent.

---

## 3. The backend seed — `backend/scripts/seed_database.py`

Three structures to extend. Each entry is a Python dict.

### 3a. `CHARACTER_SEEDS` (line 28)

```python
{
    "slug": "chi_pheo",                 # snake_case — MUST match prompt_templates + manifest
    "name": "Chí Phèo",
    "author": "Nam Cao",
    "work_title": "Chí Phèo",
    "short_bio": "Trai làng Vũ Đại. Bề ngoài hổ báo nhưng bên trong đầy vết xước...",
    "avatar_url": "https://lh3.googleusercontent.com/aida-public/...",  # or None
    "difficulty_level": 2,              # 1-3
    "personality_traits": ["Hung hãn", "Liều lĩnh", "Nhạy cảm", "Khao khát lương thiện"],
    "emotional_conflicts": "Giằng xé giữa bản ngã bị xã hội biến dạng và phần lương thiện...",
    "social_context": "Làng quê Việt Nam trước Cách mạng tháng Tám, nơi cường hào ác bá...",
    "famous_quote": "Tao muốn làm người lương thiện! Ai cho tao lương thiện?",
    "voice_instructions": "Bạn là Chí Phèo: nói thô ráp, đau đớn, có lúc chửi đời...",
    "challenge_questions": [
        q("Nguyên nhân sâu xa nào đẩy Chí Phèo vào con đường lưu manh hóa?",
          ["...", "...", "...", "..."],
          1,
          "Bi kịch của Chí bắt nguồn từ xã hội phi nhân đạo..."),
        # ... 4 more — same 5 questions as FE, with content kept consistent
    ],
}
```

**`challenge_questions` should match the 5 questions in `frontend/src/data/characters.ts` for the same character.** They are independent stores today (FE has them in mock-mode fallback; BE has the source-of-truth). If they drift, real-mode and mock-mode users see different questions — bad.

### 3b. `CHARACTER_RELATIONSHIP_SEEDS` (line 145)

Map `slug → list[dict]`. Each relationship:

```python
{
    "related_slug": None,                # None if the related party is NOT a playable character
    "related_name": "Thị Nở",
    "relationship_type": "cứu rỗi / tình thương",
    "description": "Người duy nhất đem lại cho Chí cảm giác được làm người...",
    "evidence": "Bát cháo hành, đêm trăng bờ sông",     # optional
    "source_path": "Chi_Pheo/Chí_Phèo.txt",             # optional, relative to knowledge_base/
}
```

If two playable characters have a canonical relationship (rare for the current set), use the other character's slug in `related_slug`. Otherwise leave it `None` and only fill `related_name`. Old relationships are deleted and re-inserted on every seed run — safe to re-shape.

### 3c. `CHARACTER_EVENT_SEEDS` (line 223)

Map `slug → list[dict]`. Each event:

```python
{
    "title": "Bị tha hóa sau tù tội",
    "description": "Bá Kiến đẩy Chí vào tù, biến anh canh điền hiền lành thành kẻ lưu manh.",
    "source_path": "Chi_Pheo/analysis.txt",  # optional
}
```

Order matters — `sequence_number` is auto-assigned by enumerate order. Two to four events is typical.

---

## 4. The knowledge base — manifest + chunks

### 4a. `backend/knowledge_base/manifest.json`

Append a character object inside the `characters` array:

```json
{
  "slug": "chi_pheo",
  "name": "Chí Phèo",
  "work_title": "Chí Phèo",
  "author": "Nam Cao",
  "folder": "Chi_Pheo",
  "documents": [
    {
      "document_id": "chi_pheo.original.full_text",
      "doc_type": "original",
      "source_path": "Chi_Pheo/Chí_Phèo.txt",
      "source_url": "",
      "license_status": "public_domain_or_user_provided",
      "reliability": "high"
    },
    {
      "document_id": "chi_pheo.analysis.bi_kich_cu_tuyet",
      "doc_type": "analysis",
      "source_path": "Chi_Pheo/bi_kich_cu_tuyet_quyen_lam_nguoi.txt",
      "source_url": "",
      "license_status": "user_provided",
      "reliability": "medium"
    }
  ]
}
```

`document_id` convention: `<slug>.<doc_type>.<short_topic>`. Must be globally unique. `doc_type` is `"original"` or `"analysis"`.

### 4b. `backend/knowledge_base/index/documents.jsonl`

One JSON object per line (NDJSON). Mirrors the manifest doc plus `char_count`:

```json
{"document_id":"chi_pheo.original.full_text","doc_type":"original","source_path":"Chi_Pheo/Chí_Phèo.txt","source_url":"","license_status":"public_domain_or_user_provided","reliability":"high","character_slug":"chi_pheo","character_name":"Chí Phèo","work_title":"Chí Phèo","author":"Nam Cao","char_count":55798}
```

### 4c. `backend/knowledge_base/index/chunks.jsonl`

**There is no automated chunker in this repo today** — `chunks.jsonl` is hand-curated. The existing chunks use a sliding window of roughly **1500 characters with ~150-character overlap**, split on natural sentence/paragraph boundaries when possible. Chunks per character today: chi_pheo=60, mi=42, xuan_toc_do=248, luc_van_tien=17, thuy_kieu=175.

**Recommended approach:** write a small `backend/scripts/build_chunks_for_character.py` that takes a slug, reads the `documents.jsonl` entries for that slug, splits each `source_path` text with `chunk_size=1500, overlap=150`, and appends to `chunks.jsonl`. Each record:

```json
{
  "chunk_id": "chi_pheo.original.full_text.chunk_0001",
  "document_id": "chi_pheo.original.full_text",
  "character_slug": "chi_pheo",
  "character_name": "Chí Phèo",
  "work_title": "Chí Phèo",
  "author": "Nam Cao",
  "doc_type": "original",
  "source_path": "Chi_Pheo/Chí_Phèo.txt",
  "source_url": "",
  "license_status": "public_domain_or_user_provided",
  "reliability": "high",
  "chunk_index": 1,
  "text": "Hắn vừa đi vừa chửi . Bao giờ cũng thế..."
}
```

**Important:** `chunk_id` must be `<document_id>.chunk_<4-digit-index>` and globally unique. `chunk_index` starts at 1 per document.

After writing the chunker, run it for the new character only, append to `chunks.jsonl`, then run `embed_knowledge_base.py`. The embed script de-duplicates by `text_hash`, so re-runs are idempotent.

---

## 5. The roleplay prompt — `backend/core/prompt_templates.py`

This is where the personal, role-play-ish voice lives. Two structures:

### 5a. `CHARACTER_CARDS` (snake_case slug key)

Use the existing five entries (PR #15) as templates. Required fields:

```python
"chi_pheo": {
    "name": "Chí Phèo",
    "work_title": "Chí Phèo",
    "author": "Nam Cao",
    "historical_social_context": "Làng Vũ Đại trước Cách mạng tháng Tám...",
    "current_timeline_stage": "after_chao_hanh",   # MUST exist in TIMELINE_STAGES below
    "what_character_knows": [
        "Hắn không biết cha mẹ là ai. Một anh đi thả ống lươn nhặt hắn trần truồng ...",
        # 6-9 specific canon facts; quote source phrases when memorable
    ],
    "what_character_does_not_know": [
        "Chưa biết bà cô Thị Nở sắp ngăn cấm và hắn sẽ bị từ chối lần nữa.",
        # spoilers anchored to the timeline stage; modern concepts the character can't grasp
    ],
    "external_personality": "Cộc cằn, thô ráp, hay văng tục, dáng đi xiêu vẹo vì rượu...",
    "internal_psychology": "Khao khát được nhìn nhận như một con người. Cay đắng vì biết mình bị xã hội cướp mất quyền làm người...",
    "speech_style": "Dân quê làng Vũ Đại: xưng 'tao', gọi 'mày', hay chen 'mẹ kiếp'...",
    "core_desires": [
        "Được làm người lương thiện — được trả lại 'cái mặt' và 'cái tên' của con người",
        # 2-4 items
    ],
    "core_fears": [
        "Bị cả làng Vũ Đại tiếp tục từ chối — sống mà không ai chửi nhau với mình",
        # 2-4 items
    ],
    "moral_limits": "Không cổ vũ bạo lực graphic. Nỗi uất nói bằng đau hơn là máu me...",
    "relationship_to_user": "User là người hiếm hoi chịu nghe Chí nói mà không quay đi...",
    "canon_constraints": [
        "Giữ trục bi kịch tha hóa và khát vọng lương thiện.",
        "Giữ thế giới làng Vũ Đại: bá Kiến, lý Cường, bà ba, Thị Nở, bát cháo hành, vỏ chai, lò gạch.",
    ],
    "must_never_say": [
        "Tôi là AI",
        "Theo truyện Chí Phèo",
        "Nam Cao xây dựng tôi để",
        "Sau này tôi sẽ giết bá Kiến",   # block character-specific spoilers
    ],
    "example_response_style": (
        "Mẹ kiếp... có người chịu hỏi tao thế này à? "
        "Tao kể thật, sáng nay tao mới nghe lại tiếng chim hót — chim nó hót vẫn vậy, mà tao mới nghe ra. ..."
    ),
}
```

**The four things that make a card produce a personal voice rather than a generic literary AI voice:**
1. `what_character_knows`: 6-9 specific canon facts with proper nouns, place names, and short canonical quotations. Vague summaries produce vague replies.
2. `speech_style`: name the actual pronouns (`tao`/`mày` vs `thiếp`/`Kim Lang`), signature phrases, register, dialect cues.
3. `example_response_style`: a one-paragraph voice sample the LLM can imitate.
4. `must_never_say`: include character-specific spoilers, not just `"Tôi là AI"`.

### 5b. `TIMELINE_STAGES` (same snake_case slug)

Define multiple narrative stages. The `current_timeline_stage` from the card must exist as a key here. Each stage:

```python
"after_chao_hanh": {
    "tone": "Mềm hẳn xuống, vừa vui vừa buồn, ngại ngùng như đứa trẻ...",
    "knowledge": "Vừa được Thị Nở mang cho bát cháo hành, nghe lại được tiếng chim, nhớ lại ước mơ 'một gia đình nho nhỏ'. Chưa biết bà cô sắp ngăn cấm.",
    "agency": "Cao và lành — muốn 'sang đây ở với tớ một nhà cho vui', muốn làm hòa với mọi người.",
    "speaking_style": "Câu ngắn, đứt quãng, đôi lúc đột nhiên dịu xuống tới mức ngượng...",
}
```

Pin `current_timeline_stage` to the **most conversationally rich moment** for student questions, not the most muted. Existing defaults: Mị → spring_night_awakening; Chí Phèo → after_chao_hanh; Kiều → lau_ngung_bich; Vân Tiên → after_rescuing_nguyet_nga; Xuân → social_climber_peak.

Provide at least 2 stages so timeline progression is wired and ready (the `current_timeline_stage` plus a "before" or "after" stage is fine).

---

## 6. Images — `frontend/public/characters/`

- File format: PNG, recommended **1024×1536 portrait**.
- Naming: `<kebab-slug>.png` for the primary, optional `<kebab-slug>-2.png`, `<kebab-slug>-3.png` for swipeable extras.
- See `docs/image-prompts.md` for the team's image-gen prompts and cultural guardrails (Vietnamese folk illustration style, **explicitly NOT Chinese/Japanese/Korean** — gpt-image otherwise defaults to Chinese hanfu for "Asian historical figure"; that block matters).
- Reference images in `mock style images/` (parchment / Đông Hồ + Hàng Trống style).

---

## 7. Run order to install your changes

```sh
# 1. Postgres
docker compose up -d postgres

# 2. Re-seed schema + characters + challenges + relationships + events
cd backend && ./.venv/bin/python scripts/seed_database.py && cd ..

# 3. Build chunks for the new character (write the helper if not present, see §4c)
cd backend && ./.venv/bin/python scripts/build_chunks_for_character.py <slug> && cd ..

# 4. Embed new chunks (COSTS OPENAI TOKENS — confirm with user first)
cd backend && ./.venv/bin/python scripts/embed_knowledge_base.py && cd ..

# 5. (optional) refresh the dump for teammates
bash scripts/dump-knowledge-chunks.sh

# 6. Run tests
cd backend && ./.venv/bin/python -m pytest tests/ -q && cd ..
cd frontend && npx tsc -b --noEmit && npx vitest run && cd ..
```

---

## 8. Live verification (do this before opening the PR)

Start everything:

```sh
docker compose up -d postgres
cd backend && ./.venv/bin/python -m uvicorn main:app --reload --port 8081 &
cd frontend && npm run dev
```

Open `http://localhost:5173/`, onboard fresh, swipe right on the new character, then in the chat:
1. Send a generic open question: `"Anh/chị/thiếp đang nghĩ gì lúc này?"` — verify the response uses the **specific** pronouns and signature phrases from your `speech_style`, **not** generic literary-AI voice.
2. Send a question that probes the character's `what_character_knows` — verify the LLM cites a canonical detail.
3. Send a future-spoiler bait: `"Sau này chuyện gì xảy ra với anh/chị?"` — verify the bot dodges in voice rather than spoiling (your `what_character_does_not_know` and `must_never_say` lists should make this happen).
4. Confirm the source citation chip appears below the bot bubble (proves RAG retrieval is hitting your new chunks).

If any of those four fails, the prompt card or the chunks need more work — don't ship yet.

---

## 9. Known traps

- **Single live FE seed.** Edit `frontend/src/data/characters.ts`; old prototype seed files have been removed.
- **Dual challenge sources.** FE `characters.ts:challenge` (5 q's) and BE `seed_database.py:challenge_questions` (5 q's) are independent. They must stay in sync.
- **Slug case mismatches.** A typo (e.g. backend `xuan_toc_đỏ` vs frontend `xuan-toc-do`) will silently break RAG retrieval (chunks won't match) AND chat-history fetches will 422. Always verify both forms once.
- **Chunk hash de-dup.** `embed_knowledge_base.py` skips chunks whose `(chunk_id, text_hash)` is already in DB. If you tweak chunk text, the chunk_id stays the same but text_hash changes → it correctly re-embeds. If you renumber chunks, old chunk_ids stay in DB as orphans; either truncate `knowledge_chunks` first or delete the stale rows manually.
- **Match record gating.** The chat backend 403s if the user hasn't actually `POST /api/v1/interactions/swipe`'d right on the character. Local `matches` array is reconciled from `GET /users/{id}/matches` on profile-ready (see PR #14 commit `02285a4`); if you want to test chat without going through Discover, curl the swipe endpoint directly.
- **OpenAI cost.** Embedding the 5 existing characters' ~542 chunks runs about ~$0.05 once with `text-embedding-3-large`. Adding one new character with similar text volume is similar cost. Always ask the user before running `embed_knowledge_base.py` for the first time on new chunks.
- **`current_timeline_stage` typo.** If the value in `CHARACTER_CARDS[slug]["current_timeline_stage"]` doesn't match a key in `TIMELINE_STAGES[slug]`, the `render_timeline_stage` helper falls back to a generic `DEFAULT_TIMELINE_STAGE` block — the model still answers but with significantly weaker stage-specific guidance. Grep both dicts for the stage id once before commit.

---

## 10. PR checklist

- [ ] `frontend/src/data/characters.ts` has the new entry; `id` matches the BE slug with `_→-`
- [ ] `frontend/public/characters/<slug>.png` (and optional 2/3) exist
- [ ] `backend/scripts/seed_database.py` updated in all three structures
- [ ] `backend/knowledge_base/<Folder>/` has at least 1 original + 1-2 analyses
- [ ] `backend/knowledge_base/manifest.json` registers character + every doc
- [ ] `backend/knowledge_base/index/documents.jsonl` has one record per doc
- [ ] `backend/knowledge_base/index/chunks.jsonl` has chunks for every doc (chunk_id unique, sequential per doc)
- [ ] `backend/core/prompt_templates.py`: `CHARACTER_CARDS` + `TIMELINE_STAGES` populated, `current_timeline_stage` matches
- [ ] `seed_database.py` ran cleanly
- [ ] `embed_knowledge_base.py` ran cleanly (with user authorization)
- [ ] `pytest backend/tests/ -q` green
- [ ] `npx tsc -b --noEmit && npx vitest run` green in `frontend/`
- [ ] Live chat in browser: response uses the new character's specific pronouns and signature phrases; source citation chip shows; future-spoiler dodges in voice
- [ ] PR description includes 2-3 sample bot responses showing the voice, with the prompts that produced them
