---
name: three-phase-character-video
description: Generate repo-ready 30-second character demo videos from the existing three narrative phases: create one roughly 10-second PixVerse image-to-video clip per phase from existing character images, add consistent Vietnamese speech, concatenate the three phase clips, and save the three individual phase videos plus the final combined video for commit. Use this for Husky literary-character video demos and do not use the discarded six-clip workflow.
---

# Three-Phase Character Video

Use this skill when generating character videos for the literary-character project.

The approved workflow is:

1. Read the character's three phase descriptions from `docs/character-level-phases.md`.
2. Pick one existing repo image anchor per phase from `frontend/public/characters/`.
3. Generate three roughly 10-second image-to-video clips with PixVerse.
4. Add Vietnamese speech with one consistent speaker for the main character.
5. Save the three final phase videos and the final concatenated video in a repo-relative output folder.

Do not use the six-clip/two-per-phase workflow. Treat that experiment as discarded.

## Required References

- For the exact workflow and commands, read `references/workflow.md`.
- For prompt constraints and voice rules, read `references/prompting.md`.
- For output naming and commit scope, read `references/output-layout.md`.

## Hard Rules

- Use PixVerse for video generation, transitions, and speech/lip-sync only.
- Do not use PixVerse to generate still images. If a still image must be created or fixed, use the Codex/OpenAI image tool.
- Use existing repo images as anchors unless the user explicitly asks for new still images.
- Do not include absolute machine paths in prompts, scripts, files, commits, or documentation.
- Keep each character's face, clothing, art style, and voice consistent across all three clips.
- Validate the result with screenshots/contact sheets before reporting done.

## Reference Demo

The Mị demo `mi-three-phase-demo-v2.mp4` is the reference for this workflow: three phase videos, each based on one phase anchor, then concatenated into a single three-phase character demo. Its source intermediates are a useful local reference if present, but the skill itself must stay path-agnostic and repo-relative.
