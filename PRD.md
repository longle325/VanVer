# Vanver PRD

## 1. Product Summary

**Product name:** Vanver

**Description:** Vanver is a gamified Vietnamese literature learning app that helps students discover literary characters through swipe cards, chat with source-grounded AI character personas, complete character challenges, and compete on a leaderboard.

**Core promise:** Make Vietnamese literature feel less like memorization and more like emotionally connecting with characters.

**Primary users:** Grade 10-12 Vietnamese students who find literature boring, hard to remember, or too dependent on sample essays.

**Secondary users:** Literature teachers who want a more engaging way to help students understand character motivation, relationships, themes, and historical context.

## 2. Problem

Many high school students approach Vietnamese literature as a memorization subject. They often remember sample essay structures but struggle to connect emotionally with characters, understand motivations, or explain themes in their own words.

Vanver reframes literature study as character discovery. Students meet characters through visually engaging profile cards, choose who to explore, ask questions in conversational form, and prove understanding through short challenges.

## 3. Goals

### Product Goals

- Increase student engagement with Vietnamese literary characters.
- Help students remember characters through personality, conflict, voice, quote, relationship, and context.
- Encourage active understanding instead of passive memorization.
- Provide a lightweight game loop that motivates repeated study.
- Keep AI responses grounded in approved literary sources and teacher-reviewed notes.

### MVP Goals

- Deliver a working swipe-card discovery experience.
- Include the curated Vietnamese literary characters from `Content_reference.csv`.
- Let users unlock a character chat after swiping right.
- Provide a source-grounded chatbot experience for selected characters.
- Include five challenge questions per character.
- Award points for discovery and challenge completion.
- Display a simple leaderboard.

## 4. Non-Goals

- Full school account management.
- Teacher dashboard and assignment workflows.
- Real-money rewards or competitive ranking beyond demo leaderboard.
- Large-scale automated ingestion of all Vietnamese literature texts.
- Perfect long-form essay grading.
- Fully native mobile UI separate from the web app.

## 5. Core User Journey

1. User opens Vanver.
2. User enters a username and selects a grade level.
3. User sees the discovery deck.
4. User swipes left to skip or right to match with a character.
5. Swiping right unlocks that character in the matched list.
6. User enters the character chat.
7. User asks questions about the character.
8. User accepts the character challenge.
9. User answers five questions.
10. User receives score, explanations, points, and leaderboard update.
11. User repeats the loop with another character.

## 6. Key Features

### 6.1 Onboarding

**Description:** A short first-run screen where the user enters a username and chooses a grade level.

**MVP Requirements:**

- Username input.
- Grade selection: 10, 11, 12.
- Store user profile locally.
- Route user to discovery screen after completion.

**Future Requirements:**

- Class code entry.
- Teacher-created cohorts.
- Login and cloud sync.

### 6.2 Character Swipe Cards

**Description:** Users browse literary characters through swipeable profile cards. The experience should feel like character discovery, not dating.

The Thúy Kiều card is generalized into a reusable character card component for every character in the deck.

**Content source:** Use `Content_reference.csv` as the canonical source for character profile and visual-design content. Each character card must be generated from the CSV fields: `Tên`, `Tác phẩm`, `Tác giả`, `Image or illustration`, `Dòng bio ngắn`, `Quote nổi tiếng`, `Tính cách`, `Những mâu thuẫn về cảm xúc nếu có`, `Bối cảnh xã hội`, and `Câu hỏi challenge`.

**Card content:**

- Tên nhân vật.
- Tác phẩm.
- Tác giả.
- Hình ảnh hoặc minh họa dựa trên prompt CSV `Image or illustration`.
- Bio từ `Dòng bio ngắn`.
- Trích dẫn nổi tiếng.
- Tính cách.
- Mâu thuẫn cảm xúc từ `Những mâu thuẫn về cảm xúc nếu có`.
- Bối cảnh xã hội hoặc lịch sử từ `Bối cảnh xã hội`.

All user-facing card content, including section labels, generated captions, fallback text, and difficulty-level labels, must be written in Vietnamese.

**MVP Requirements:**

- Use the manually curated character profiles in `Content_reference.csv` for the MVP character deck.
- Include the five CSV characters in the initial MVP deck: Chí Phèo, Mị, Xuân Tóc Đỏ, Lục Vân Tiên, and Thúy Kiều.
- Treat the CSV set as the approved first content batch; add new characters only after the same fields are completed and reviewed.
- Generate or select a distinct profile image for every CSV character from the `Image or illustration` field.
- Left swipe skips the current card.
- Right swipe adds character to matched list.
- Right swipe unlocks chat route for that character.
- Empty state when deck is completed.

**Acceptance Criteria:**

- User can move through the deck without page reload.
- Matched characters persist during the session.
- Right-swiped characters are accessible from chat or matched list.
- Character profile content matches `Content_reference.csv` and is manually reviewed before shipping.

### 6.3 Character Chatbot

**Description:** After matching with a character, users can chat with the character. The chatbot responds in the voice of the character while staying grounded in source texts and curated notes.

**AI Behavior:**

- Speak in a style that reflects the character's personality, social background, emotional conflict, and literary context.
- Use source-grounded answers whenever possible.
- Avoid inventing major plot details.
- Admit uncertainty when the available sources are insufficient.
- Separate interpretation from factual source detail when needed.

**Knowledge Sources:**

- Original literary text excerpts.
- Selected quotes.
- Curated character analysis.
- Historical and social context notes.
- Author notes.
- Teacher-reviewed summaries.

**MVP Requirements:**

- Chat screen for matched characters.
- Source-grounded response generation from a small curated knowledge base.
- Streaming response behavior through SSE or simulated streaming if backend is not yet connected.
- Persistent `Làm thử thách` action in the chat header.
- Basic refusal or uncertainty behavior for unsupported questions.

**Acceptance Criteria:**

- User cannot chat with a character before matching.
- Chat responses are tied to the selected character.
- Chat output does not present unsupported claims as fact.
- Chat UI handles loading, streaming, error, and empty states.

### 6.4 Character Challenge

**Description:** Users take a short quiz after chatting with a character. The challenge tests understanding beyond surface-level facts.

**Question Types:**

- Multiple choice.
- Quote identification.
- Motivation analysis.
- Relationship analysis.
- Theme connection.
- Short explanation.

**MVP Requirements:**

- Five questions per character.
- Four out of five correct answers required to fully unlock a character.
- Correct answer and explanation shown after submission.
- Points awarded based on score.
- Completion status saved locally.

**Acceptance Criteria:**

- User can submit one answer per question.
- Score is calculated correctly.
- Explanations are shown for all questions after submission.
- Passing score unlocks character completion state.

### 6.5 Points and Leaderboard

**Description:** Users earn points by discovering characters, completing challenges, and answering accurately. A leaderboard shows user rank.

**MVP Point System:**

- Match with a character: +10 points.
- Complete a challenge: +50 points.
- Pass a challenge with at least 4/5: +40 bonus points.


**MVP Requirements:**

- Track total points for current user.
- Show a simple leaderboard based on total points.
- Include demo users to make the leaderboard feel populated.
- Update leaderboard after challenge submission.

**Future Requirements:**

- Weekly leaderboard.
- Class leaderboard.
- School leaderboard.
- Friend group leaderboard.
- Streak bonuses.
- Badges and collection progress.

### 6.6 Matched Characters Collection

**Description:** Users can view all characters they have discovered, see unlock progress, and return to chat or challenge flows.

**MVP Requirements:**

- Display all right-swiped characters.
- Show character name, work, image, unlock state, challenge state, and discovery progress.
- Let users open the character chat from a collection card.
- Show clear states for partially unlocked, challenge pending, and fully unlocked characters.

**Acceptance Criteria:**

- Collection only shows matched characters.
- Character status updates after challenge completion.
- All labels, filters, badges, and empty states are written in Vietnamese.

### 6.7 Language and Localization

**Description:** The app is for Vietnamese high school literature learning, so all user-facing product language must be Vietnamese.

**MVP Requirements:**

- All navigation, buttons, labels, empty states, errors, onboarding text, challenge text, chat helper text, leaderboard labels, and profile/collection status text must be in Vietnamese.
- Literary work titles, character names, author names, and excerpts must use correct Vietnamese diacritics.
- HTML document language should be `vi`.
- Any English placeholder copy from early mockups is not shipped in the app UI.
- Internal code identifiers, route names, API names, and developer comments may remain English.

**Required Vietnamese UI Terms:**

- Discover: `Khám phá`
- Matched Characters / Collection: `Nhân vật đã chọn` or `Bộ sưu tập nhân vật`
- Leaderboard: `Bảng xếp hạng`
- Profile: `Hồ sơ`
- Take Challenge: `Làm thử thách`
- Submit: `Nộp bài`
- Points: `Điểm`
- Streak: `Chuỗi ngày`
- Fully Unlocked: `Đã mở khóa hoàn toàn`
- Challenge Pending: `Chưa hoàn thành thử thách`
- Recently Added: `Mới thêm gần đây`
- Vietnamese Classics: `Văn học Việt Nam`

## 7. MVP Content Requirements

The MVP should use `Content_reference.csv` as the first approved character profile database. Final selection can still change based on available public-domain texts, licensing, and teacher review, but the default character-design source is the CSV.

Initial CSV character set:

- Chí Phèo from *Chí Phèo* by Nam Cao.
- Mị from *Vợ chồng A Phủ* by Tô Hoài.
- Xuân Tóc Đỏ from *Số đỏ* by Vũ Trọng Phụng.
- Lục Vân Tiên from *Lục Vân Tiên* by Nguyễn Đình Chiểu.
- Thúy Kiều from *Truyện Kiều* by Nguyễn Du.

Each character should include:

- Profile card data mapped from CSV fields.
- A visual prompt or image brief from `Image or illustration`.
- A short, student-friendly bio from `Dòng bio ngắn`.
- A quote from `Quote nổi tiếng`.
- Personality design notes from `Tính cách`.
- Emotional-conflict notes from `Những mâu thuẫn về cảm xúc nếu có`.
- Social and historical context from `Bối cảnh xã hội`.
- Three to seven source snippets or curated notes.
- Five challenge questions derived from `Câu hỏi challenge`; Thúy Kiều currently includes six candidate questions, so choose the best five for MVP or support six-question challenges for that character only if product scoring is updated.
- Correct answers and explanations.
- Character voice instructions for chat.

## 8. Information Architecture

### Screens

- Onboarding.
- Discovery deck.
- Character chat.
- Character challenge.
- Results modal or results screen.
- Leaderboard.
- Matched characters or collection view.

### Primary Routes

- `/onboarding`
- `/discover`
- `/characters/:characterId/chat`
- `/characters/:characterId/challenge`
- `/leaderboard`
- `/collection`

## 9. Technical Direction

### Frontend

- React + TypeScript.
- Vite.
- React Router.
- Tailwind CSS.
- Radix UI or shadcn/ui primitives.
- Lucide icons.
- Framer Motion.
- Zustand for client state.
- TanStack Query for API state.
- React Hook Form for onboarding and challenge forms.
- `react-tinder-card` for swipe interactions.

### Mobile Wrapper

- Capacitor for iOS and Android packaging.
- Capacitor Preferences for local profile/session persistence.
- Optional Capacitor HTTP if CORS becomes a blocker.
- Capacitor splash/status bar plugins for native polish.

### Backend/API

MVP can start with local mock data and mock endpoints, then move to a real API.

Recommended API shape:

- `GET /deck` returns character cards.
- `GET /characters/:id` returns character detail.
- `POST /match` records a matched character.
- `POST /chat` streams character response with SSE.
- `GET /characters/:id/challenge` returns challenge questions.
- `POST /characters/:id/challenge/submit` validates answers and returns score, explanations, and points.
- `GET /leaderboard` returns ranked users.

### RAG Direction

The MVP can use a small curated knowledge base per character. Each character should have source snippets, interpretation notes, and a prompt profile. Retrieval can initially be keyword-based or embedding-based depending on available backend scope.

The chatbot should receive:

- Character persona instructions.
- Retrieved source snippets.
- Curated notes.
- User message.
- Guardrail instructions.

## 10. Design Direction

Vanver uses the Modern Literary design direction — an aged-parchment, wood-and-gold palette with Noto Serif display type — now implemented in the app's stylesheets under `frontend/src/styles/`. The original static HTML/screenshot mockups have been removed; the shipped screens are the reference.

The interface should feel:

- Literary and emotionally rich.
- Focused and calm enough for study.
- Game-like through progression, feedback, and motion.
- Clearly framed as character discovery, not dating.

Important UI principles:

- Use Vietnamese-friendly typography.
- Keep cards visually strong, similar to literary profile covers.
- Make challenge feedback clear and educational.
- Use subtle animation for swipe, chat streaming, and score reveal.
- Avoid making the product feel like a generic social app.
- Replace all English placeholder text from the mockups with Vietnamese before shipping.

## 11. Success Metrics

### Engagement

- Number of characters viewed.
- Match rate per character.
- Chat messages per matched character.
- Challenge start rate.
- Challenge completion rate.

### Learning

- Average challenge score.
- Retry improvement.
- Percentage of users passing with at least 4/5.
- Most missed question categories.

### Retention

- Repeat sessions.
- Characters completed per user.
- Leaderboard return visits.

## 12. Risks and Mitigations

### Risk: AI hallucination

Mitigation: Use curated source snippets, retrieval before answering, strict prompt guardrails, and uncertainty responses.

### Risk: Product feels like dating instead of learning

Mitigation: Use "discover", "match", "unlock", and "collection" language carefully. Avoid romantic framing and focus on literary connection.

### Risk: Students use chat to get sample essays

Mitigation: Chat should guide understanding, cite source context, ask reflective follow-ups, and avoid generating full canned essays in MVP.

### Risk: Content quality bottleneck

Mitigation: Start with the reviewed `Content_reference.csv` character set and a repeatable content schema. Add teacher review before expanding.

### Risk: Leaderboard discourages weaker students

Mitigation: Future versions should support personal progress, badges, streaks, and class-level leaderboards.

## 13. Implementation Task Breakdown

### Phase 0: Project Setup

- Initialize Vite React TypeScript app.
- Configure Tailwind CSS.
- Add React Router.
- Add Zustand.
- Add TanStack Query.
- Add Framer Motion.
- Add Lucide icons.
- Add React Hook Form.
- Add `react-tinder-card`.
- Set up base folder structure: `components`, `routes`, `data`, `stores`, `api`, `types`, `lib`.

### Phase 1: Product Data Model

- Define TypeScript types for user profile, character, source snippet, chat message, challenge question, challenge result, and leaderboard entry.
- Create seed character data from `Content_reference.csv`.
- Add one image reference or generated illustration per CSV character using the `Image or illustration` brief.
- Create seed challenge data from the CSV `Câu hỏi challenge` field, with five MVP questions per character.
- Create demo leaderboard data.
- Add validation helpers for challenge scoring.

### Phase 2: App Shell and Navigation

- Build responsive app layout.
- Add route configuration.
- Add bottom navigation or compact header navigation.
- Implement route guards for onboarding and locked chat routes.
- Add persistent local storage for username, grade, matches, points, and completed challenges.
- Use Vietnamese labels for all navigation items: `Khám phá`, `Nhân vật đã chọn`, `Bảng xếp hạng`, `Hồ sơ`.

### Phase 3: Onboarding

- Build username input and grade selector.
- Validate required fields.
- Save profile to Zustand and local persistence.
- Navigate to discovery after onboarding.

### Phase 4: Discovery Swipe Deck

- Build character card component.
- Build swipe deck screen with `react-tinder-card`.
- Implement left and right swipe actions.
- Add match animation and points update for right swipe.
- Add empty deck state.
- Add collection access for matched characters.

### Phase 5: Character Chat

- Build chat route and message list.
- Add message input and send behavior.
- Build mock chat API that retrieves relevant snippets from local character data.
- Simulate SSE chunking or wire actual SSE if backend exists.
- Add source-grounded prompt behavior in the mock layer.
- Add loading and error states.
- Add persistent `Làm thử thách` button.
- Translate quick prompts, helper text, source labels, and CTAs to Vietnamese.

### Phase 6: Challenge Flow

- Build challenge route.
- Render five questions.
- Support multiple choice and short answer fields.
- Validate submission.
- Show results modal with score, explanations, pass/fail state, and points earned.
- Save challenge completion state.
- Prevent duplicate point awards for repeated submissions unless retry rules are defined.
- Write all challenge questions, explanations, and result messages in Vietnamese.

### Phase 7: Matched Characters Collection

- Build collection route.
- Render matched characters in a responsive grid.
- Show unlock progress, challenge status, and fully unlocked state.
- Add sorting by recently added and completion progress.
- Translate all collection labels, badges, filters, and status text to Vietnamese.
- Let users open chat or challenge from each collection card.

### Phase 8: Leaderboard

- Build leaderboard route.
- Merge current user score with demo leaderboard users.
- Sort users by total points.
- Highlight current user.
- Update ranking after match and challenge events.
- Translate leaderboard tabs, columns, stats, rank labels, and demo user display text to Vietnamese.

### Phase 9: Polish and Design Pass

- Apply Modern Literary color and typography direction.
- Audit against the shipped Modern Literary design direction.
- Replace any remaining English placeholder UI copy with Vietnamese.
- Set document language to Vietnamese with `lang="vi"`.
- Add motion for deck, chat typing, challenge submission, and score reveal.
- Verify mobile layout.
- Verify text does not overflow cards, buttons, or challenge options.
- Add empty, loading, and error states across screens.

### Phase 10: Capacitor Wrapper

- Add Capacitor.
- Configure app name and bundle identifier.
- Add iOS and Android platforms.
- Configure status bar and splash screen.
- Replace web local storage with Capacitor Preferences where appropriate.
- Run web build and sync native projects.

### Phase 11: QA

- Test onboarding from fresh state.
- Test left and right swipes.
- Test collection status updates.
- Test chat route lock behavior.
- Test each character challenge.
- Test point calculation.
- Test leaderboard sorting.
- Test persistence after refresh.
- Test mobile viewport layout.
- Test that all user-facing UI text is Vietnamese.
- Test production build.

## 14. Suggested First Engineering Milestone

The first milestone should produce a complete local-only prototype:

- Onboarding.
- Seeded character deck.
- Swipe matching.
- Matched character collection.
- Matched character chat with mock grounded responses.
- One fully implemented challenge.
- Basic points.
- Leaderboard with demo users.

After this milestone works end to end, expand from one complete character challenge to all characters in `Content_reference.csv`, then add new teacher-reviewed profiles as needed.

## 15. Current Prototype Progress

As of 2026-05-07, the local static prototype has implemented:

- Standalone Vietnamese onboarding/start screen matching the supplied screenshot direction.
- Authenticated app shell aligned to the reference sidebar and top metric treatment.
- Discovery, collection, chat, challenge, and leaderboard screens implemented.
- Local profile creation with username and grade selection.
- Vite development server support through `npm run dev`.
- Seeded discovery deck for the five MVP CSV characters.
- Swipe and button-based match/skip behavior with local persistence.
- Matched character collection, guarded chat routes, five-question challenge flows, points, leaderboard, profile, and demo reset.

Remaining prototype gaps:

- Browser screenshot verification is still needed after local browser tooling is available.
- Some characters still use generated CSS art placeholders where a concrete image asset was not provided.
- Chat response simulation is local and non-streaming.
- Data remains inline in `app.js` rather than a dedicated seed module or typed store.
