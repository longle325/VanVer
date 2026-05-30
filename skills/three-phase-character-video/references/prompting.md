# Prompting And Voice

## Visual Prompt Template

Use one prompt per phase. Keep it strict and concrete:

```text
STRICT 2D Vietnamese literary illustration, preserve the exact painted/inked storybook style of the anchor image, warm muted colors, ornamental texture, NOT photorealistic.

Character: <name>. Phase <n>: <phase description from docs/character-level-phases.md>.

Canonical requirements: <specific constraints>.

Motion: <simple natural motion that fits the phase>.

Identity lock: keep the same face, age, clothing, body type, and cultural setting as the anchor image. Keep the camera stable or use a slow push-in only.

Avoid: modern objects, extra characters, text, subtitles, fantasy effects, style change, face change, photorealism, abrupt spatial morphing, characters sliding apart.
```

## Phase Prompting Rules

- Level 1 should show the earliest canonical phase, not a weaker fantasy form.
- Level 2 should show the central conflict or transformation.
- Level 3 should show the strongest canonical/emotional phase.
- If the phase is tragic, the visual upgrade should come from composition, lighting, emotional stakes, and symbolism, not richer clothing or superhero styling.
- Do not import later-story traits into earlier phases.

Examples of canonical guardrails:

- Lục Vân Tiên is not blind during the Kiều Nguyệt Nga rescue phase.
- Mị is not fully liberated before the A Phủ rescue phase.
- Chí Phèo Level 3 should include moral awakening and the Bá Kiến dead end, not just more drunken violence.

## Two-Character Scenes

For scenes with two characters:

- State who moves and who stays fixed.
- State the physical relation between them.
- Avoid two-keyframe transitions if the two anchors have very different compositions.
- Prefer image-to-video from the final scene anchor when a transition would force unnatural spatial interpolation.

Example:

```text
A Phủ stays physically fixed in place, tied to the post. He does not slide, drift, stand up, or separate from Mị. Mị is the active mover: she kneels beside him, lowers both hands to the rope, cuts the rope slowly, then looks up with fear and resolve.
```

## Vietnamese Speech

Use concise Vietnamese lines. The goal is emotional character presence, not plot summary.

Rules:

- Use one fixed speaker ID for the main character across all three phases.
- Use gender-correct voices.
- Keep the same voice across phases unless the user explicitly asks for age/time changes.
- Avoid auto speaker selection once a suitable voice is known.
- Keep each line short enough for the clip; long lines can stretch the generated speech beyond 10 seconds.

For two-character dialogue, prefer one of these:

- one main-character line if lip-sync quality matters most
- two separate TTS tracks mixed locally if distinct voices matter more than perfect lip sync

Always verify the final video has an audio stream and non-silent volume.
