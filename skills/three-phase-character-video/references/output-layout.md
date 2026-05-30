# Output Layout And Commit Scope

Use repo-relative paths only. Do not write absolute local machine paths into generated files, docs, prompts, or commit messages.

## Recommended Output Directory

Default commit-ready location:

```text
frontend/public/character-videos/<character-slug>/
```

Recommended files:

```text
frontend/public/character-videos/<character-slug>/phase-1.mp4
frontend/public/character-videos/<character-slug>/phase-2.mp4
frontend/public/character-videos/<character-slug>/phase-3.mp4
frontend/public/character-videos/<character-slug>/<character-slug>-three-phase-demo.mp4
```

Optional QA artifacts, if the user wants them committed:

```text
frontend/public/character-videos/<character-slug>/<character-slug>-contact.png
frontend/public/character-videos/<character-slug>/<character-slug>-audio-check.txt
```

If the user wants the final demo at project root for quick review, copy it there too, but do not make root output the default for committed production assets.

## Temporary Files

Use `tmp/` for:

- PixVerse downloads
- raw visual clips
- raw speech clips
- contact sheets during iteration
- failed or discarded generations

Do not commit `tmp/` unless the user explicitly asks.

## Commit Scope

For a character-video commit, include only:

- the skill files if changed
- the three final phase videos
- the final concatenated video
- optional QA artifacts requested by the user

Avoid committing:

- unrelated knowledge-base notes
- old six-clip experiments
- failed generations
- local config, `.env`, cache files, or machine-specific paths

Before committing, run:

```bash
git status --short
```

Stage only the files directly related to the current video task.
