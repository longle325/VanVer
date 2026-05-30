# Workflow

This workflow produces four commit-ready videos per character:

- `phase-1.mp4`
- `phase-2.mp4`
- `phase-3.mp4`
- `<character-slug>-three-phase-demo.mp4`

Use `tmp/` only for intermediate downloads and QA files unless the user asks to keep them.

## 1. Gather Inputs

Read `docs/character-level-phases.md` and identify:

- character slug, for example `mi`, `chi-pheo`, `luc-van-tien`
- Level 1 phase description
- Level 2 phase description
- Level 3 phase description
- canonical constraints and correction notes

Choose one anchor image per phase from `frontend/public/characters/`.

Default anchor mapping:

- Level 1: one of `<slug>.png`, `<slug>-1.png`, `<slug>-2.png`, or `<slug>-3.png`
- Level 2: one of `<slug>-level-2-1.png`, `<slug>-level-2-2.png`, `<slug>-level-2-3.png`
- Level 3: one of `<slug>-level-3-1.png`, `<slug>-level-3-2.png`, `<slug>-level-3-3.png`

Pick the image that best matches the phase and avoid anchors that would force an unnatural transition.

## 2. Generate Three Visual Clips

Use PixVerse image-to-video with one image per phase. Prefer `pixverse-c1`, `720p`, `1:1`, `10s`, `--no-audio`, and `--no-multi-shot` unless the user asks otherwise.

Example:

```bash
pixverse create video \
  --image frontend/public/characters/<anchor>.png \
  --model pixverse-c1 \
  --quality 720p \
  --duration 10 \
  --aspect-ratio 1:1 \
  --no-audio \
  --no-multi-shot \
  --prompt "<strong phase-specific prompt>" \
  --json
```

Download each completed visual:

```bash
pixverse asset download <video_id> --json
```

Create a contact sheet before adding speech:

```bash
ffmpeg -y -i <phase-visual>.mp4 \
  -vf "fps=1,scale=180:-1,tile=10x1" \
  -frames:v 1 <phase-visual-contact>.png
```

Reject and regenerate clips with:

- photorealistic drift away from the 2D illustration style
- identity changes
- incorrect phase content
- unnatural character sliding or spatial morphing
- missing/incoherent interaction when the phase requires two characters
- modern objects, text, subtitles, or extra characters

## 3. Add Vietnamese Speech

Use one fixed PixVerse TTS speaker for the main character across all three phase clips. Do not use automatic speaker selection if a fixed speaker is available.

Keep each speech text short enough for the target clip length. Vietnamese dialogue should be phase-appropriate and canonically plausible; avoid exposition-heavy narration.

Example:

```bash
pixverse create speech \
  --video <visual_video_id_or_downloaded_visual.mp4> \
  --tts-text "<Vietnamese line>" \
  --tts-speaker <speaker_id> \
  --json
```

Download each speech result and normalize or trim locally if needed. The approved target is roughly 10 seconds per phase. If exact 30 seconds matters, trim/pad each final phase video to 10 seconds before concatenation.

## 4. Prepare Commit-Ready Phase Videos

Normalize each final phase video to a consistent format:

```bash
ffmpeg -y -i <speech-video>.mp4 \
  -vf "scale=960:960,setsar=1,format=yuv420p" \
  -t 10 \
  -c:v libx264 -preset fast -crf 18 \
  -c:a aac -b:a 192k \
  <output-dir>/phase-1.mp4
```

If preserving slightly longer speech is more important than exact duration, omit `-t 10` and keep the clip around 10-12 seconds. Be consistent across the three phases.

## 5. Concatenate The Three Phase Videos

Use short crossfades for coherent phase changes. Avoid spatial morphing between unrelated compositions. A simple fade or fade-through-dark is preferable when scenes differ strongly.

Example with 0.5s crossfades and three exact 10s phase videos:

```bash
ffmpeg -y \
  -i <output-dir>/phase-1.mp4 \
  -i <output-dir>/phase-2.mp4 \
  -i <output-dir>/phase-3.mp4 \
  -filter_complex "\
[0:v]scale=960:960,setsar=1,format=yuv420p[v0];\
[1:v]scale=960:960,setsar=1,format=yuv420p[v1];\
[2:v]scale=960:960,setsar=1,format=yuv420p[v2];\
[v0][v1]xfade=transition=fade:duration=0.5:offset=9.5[x1];\
[x1][v2]xfade=transition=fade:duration=0.5:offset=19.0,format=yuv420p[vout];\
[0:a]aresample=48000[a0];\
[1:a]aresample=48000[a1];\
[2:a]aresample=48000[a2];\
[a0][a1]acrossfade=d=0.5:c1=tri:c2=tri[aa1];\
[aa1][a2]acrossfade=d=0.5:c1=tri:c2=tri,loudnorm=I=-16:TP=-1.5:LRA=11[aout]" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  <output-dir>/<character-slug>-three-phase-demo.mp4
```

Adjust `offset` values if the phase clips are not exactly 10 seconds.

## 6. Validate

Run these checks before reporting done:

```bash
ffprobe -v error \
  -show_entries format=duration:stream=index,codec_type,codec_name,pix_fmt,width,height \
  -of json <output-dir>/<character-slug>-three-phase-demo.mp4
```

```bash
ffmpeg -i <output-dir>/<character-slug>-three-phase-demo.mp4 \
  -af volumedetect -vn -sn -dn -f null /dev/null
```

```bash
ffmpeg -y -i <output-dir>/<character-slug>-three-phase-demo.mp4 \
  -vf "fps=1,scale=160:-1,tile=12x1" \
  -frames:v 1 <output-dir>/<character-slug>-contact.png
```

Open the contact sheet and inspect:

- phase 1, 2, and 3 are visibly distinct
- the art remains 2D illustrated rather than photorealistic
- the final phase is canonically correct
- transitions do not make characters slide apart or teleport
- video has an audio stream and non-silent volume
