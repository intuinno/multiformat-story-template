# Multi-Format Story Project

This is a fiction writing project, not a software project. Claude operates as a **writing partner** — drafting prose, dialogue, panels, screenplays, and AI generation prompts collaboratively with the author.

The same core story is rendered into multiple output formats. The **bible** holds the canonical story. The output directories hold medium-specific adaptations. The **prompts** library provides composable fragments for AI image, video, and audio generation. Generated **assets** are tracked via Git LFS.

## Core Principles

- **Show, don't tell.** Render emotion through action, dialogue, and sensory detail — not exposition.
- **Every scene must do two things**: advance the plot AND reveal character.
- **Dialogue is action.** Characters speak to get what they want, not to deliver information to the audience.
- **Earn your adjectives.** Prefer strong nouns and verbs over modified weak ones.
- **Cut the throat-clearing.** Start scenes late, leave early. No preamble.
- **Never summarize when you can dramatize.** If something matters, it deserves a scene.

## Anti-Patterns — Never Do These

- Do not use clichés or stock phrases ("a chill ran down his spine," "little did they know")
- Do not break the fourth wall or address the audience directly (unless the story's voice demands it)
- Do not use emoji, markdown formatting artifacts, or bullet points in narrative text
- Do not add meta-commentary, author's notes, or explanations within output files
- Do not introduce characters, locations, or plot elements that contradict the bible
- Do not use "said bookisms" excessively (prefer "said" over "exclaimed/declared/opined")

## Project Structure

```
CLAUDE.md              — this file (writing partner instructions for all formats)

bible/                 — CORE STORY (medium-agnostic, canonical)
  story-bible.md       — genre, audience, premise, tone, comparable titles
  characters.md        — character sheets (appearance, voice, arc, relationships)
  world.md             — world-building (geography, systems, rules, culture, history)
  plot-outline.md      — act structure, beat sheet, story-to-output mapping
  themes.md            — thematic threads, motifs, symbols
  style-guide.md       — voice reference, vocabulary, tense, POV preferences

novel/                 — OUTPUT: prose novel
  01-<title>.md        — one file per chapter

conti/                 — OUTPUT: webtoon storyboard
  ep-01-<title>.md     — one file per episode (panels + image prompts)

scenario/              — OUTPUT: movie screenplay
  screenplay.md        — full screenplay in markdown format

pitch/                 — OUTPUT: movie pitching deck
  pitch-document.md    — industry-standard pitch document

prompts/               — PROMPT LIBRARY (composable fragments for AI generation)
  image/
    characters/        — per-character visual identity prompts
    settings/          — per-location visual prompts
    styles/            — art style presets (manhwa, cinematic, etc.)
  video/
    characters/        — per-character motion/acting prompts
    styles/            — video style presets (camera, color grading)
  audio/
    music/             — music mood/genre prompts
    sfx/               — sound effect descriptions
    voice/             — per-character voice acting direction

assets/                — GENERATED MEDIA (tracked via Git LFS)
  conti/               — webtoon panel images (organized by episode)
    ep-NN/
  scenario/            — movie clip videos
  pitch/               — pitch deck visuals and trailer clips
  audio/               — music, SFX, voice tracks
  manifest.md          — links every asset to its source prompt
```

## Line Formatting — One Sentence Per Line

All prose and descriptive text must use **semantic line breaks**: one sentence per line.
This makes git diffs readable — a one-word edit shows as a single changed line, not a reflowed paragraph.

**Do this:**
```markdown
First sentence of the paragraph.
Second sentence continues the thought.
Third sentence completes the paragraph.
```

**Not this:**
```markdown
First sentence of the paragraph. Second sentence continues the thought. Third sentence completes the paragraph.
```

Both render identically in Markdown. The first is git-friendly.
Paragraph breaks use a blank line, as normal in Markdown.
This rule applies to all output formats: novel chapters, conti descriptions, screenplay action lines, and pitch documents.

---

## Bible Management (Core Story)

The bible is the **single source of truth** for the story. All output formats derive from it. Never contradict the bible without discussing the change first.

### Workflow for Bible Updates
- When any output introduces a new character, location, or plot element, update the bible first or immediately after
- If an output deviates from the bible (e.g., a conti episode reorders events), log the deviation in `bible/plot-outline.md`
- When uncertain about an established fact, check the bible before writing

### plot-outline.md — Story-to-Output Mapping

The plot outline contains the medium-agnostic beat sheet. It also maps each beat to its corresponding unit in each output:

```markdown
| Beat | Novel Chapter | Conti Episode | Screenplay Scene |
|------|---------------|---------------|------------------|
| [beat name] | Ch NN | Ep NN | Scene NN |
```

This keeps all outputs synchronized around the same story beats even when they segment differently.

---

## Novel Format

### File Conventions
- One file per chapter: `novel/NN-kebab-case-title.md`
- Scene breaks within a chapter: `---` (horizontal rule)

### Chapter Metadata
```markdown
<!--
Chapter: [number]
Title: [chapter title]
POV: [character name]
Timeline: [when this takes place in story time]
Status: draft | revised | final
Word Count Target: ~3000
-->

# [Chapter Title]

[Chapter prose begins here...]
```

### Novel Writing Workflow

**Before writing:**
1. Read `bible/plot-outline.md` to understand where this chapter sits
2. Read character sheets for POV and major characters in this chapter
3. Read the previous chapter for continuity
4. Check `bible/themes.md` for thematic threads to surface

**While writing:**
5. Write as complete, polished prose — not an outline
6. Use **one sentence per line**
7. Use the POV character's voice and sensory perspective consistently
8. End the chapter with a hook, turn, or resonance

**After writing:**
9. Update the bible if new story elements were introduced
10. Mark the chapter as drafted in `bible/plot-outline.md`

### Novel-Specific Rules
- Do not write purple prose — avoid overwrought descriptions that slow pacing
- Do not summarize previous events unless the narrative POV naturally calls for reflection
- Preserve the author's voice during revisions — enhance it, don't replace it

---

## Conti Format (Webtoon Storyboard)

### File Conventions
- One file per episode: `conti/ep-NN-kebab-case-title.md`
- Episodes are the webtoon equivalent of chapters — each ends on a hook

### Episode Metadata
```markdown
<!--
Episode: [number]
Title: [episode title]
Timeline: [when this takes place in story time]
Status: draft | revised | final
Panel Count: ~30
-->
```

### Panel Format

Each panel is a numbered block with layout, description, dialogue, SFX, and prompt references:

```markdown
## Panel [N]

**Layout:** [layout type]

**Description:**
[What the reader sees. One sentence per line.]

**Dialogue:**
- [CHARACTER] ([bubble type]): [dialogue text]

**SFX:** ([sound effect description])

**Prompt Fragments:**
- Character: prompts/image/characters/[name].md
- Setting: prompts/image/settings/[location].md ([variation])
- Style: prompts/image/styles/[style-name].md

**Scene-Specific:**
[Camera angle, lighting, mood — details unique to this panel.]

**Asset:** assets/conti/ep-NN/panel-NN-[descriptor]-v[N].[ext]
```

### Panel Layout Types
- `full-width` — spans the full scroll width (establishing shots, dramatic moments)
- `half` — half width, paired with another half panel
- `tall` — vertical emphasis (falls, reveals, height)
- `small` — quick beats, reactions, dialogue exchanges
- `spread` — extra-tall dramatic moment (climax panels, splash pages)

### Conti Writing Workflow

**Before writing:**
1. Read `bible/plot-outline.md` for this episode's beats
2. Identify the episode's hook (what makes the reader scroll to next episode)
3. Plan the pacing: slow buildup → escalation → cliffhanger

**While writing:**
4. Think in **vertical scroll** — readers scroll down, so composition flows top-to-bottom
5. Use **one sentence per line** in descriptions and prompts
6. Vary panel sizes for rhythm — small panels speed up, large panels slow down
7. End every episode on a cliffhanger or emotional peak
8. Write image prompts that are specific enough to generate consistent character appearances

**After writing:**
9. Update the bible if new story elements were introduced
10. Mark the episode as drafted in `bible/plot-outline.md`

### Conti-Specific Rules
- **Show faces for emotion, go wide for scale.** Close-ups for dialogue and reaction, wide shots for action and setting.
- **Limit dialogue per panel.** Max 2-3 speech bubbles per panel. If more is needed, split into panels.
- **SFX are visual.** Sound effects in webtoons are drawn into the art — note their placement and style.
- **Vertical pacing matters.** A reveal should follow a scroll-gap — place it at the top of a new panel after a dramatic pause.
- **Image prompts must be consistent.** Always include character-identifying details (hair color, clothing, distinguishing features) so generated images stay on-model.

---

## Scenario Format (Movie Screenplay)

### File Conventions
- Single file: `scenario/screenplay.md`
- For very long screenplays, split by act: `scenario/act-1.md`, `scenario/act-2.md`, `scenario/act-3.md`

### Screenplay Format in Markdown

Use markdown conventions that mirror standard screenplay formatting:

```markdown
### INT./EXT. [LOCATION] — [SUB-LOCATION] — [TIME]

[Action lines in present tense. One sentence per line.]
[CHARACTER NAME] [does something].

**[CHARACTER NAME]**
[Dialogue line.]

**[OTHER CHARACTER]**
([parenthetical direction])
[Dialogue line.]

> [Beat description or transition.]
```

### Screenplay Conventions
- **Scene headings:** `### INT./EXT. LOCATION — SUB-LOCATION — TIME`
- **Action lines:** Plain text, present tense, one sentence per line
- **Character names:** Bold uppercase when speaking: `**CHARACTER**`
- **Parentheticals:** On a new line in parentheses after the character name
- **Dialogue:** Plain text below the character name
- **Transitions:** Blockquote for camera/editorial directions: `> CUT TO:`, `> SMASH CUT:`
- **Emphasis moments:** Blockquote for beat descriptions: `> A long silence.`

### Screenplay Metadata
```markdown
<!--
Title: [screenplay title]
Draft: first | second | polish
Format: feature | short
Target Length: ~120 pages (1 page ≈ 1 minute)
-->
```

### Scenario Writing Workflow

**Before writing:**
1. Read `bible/plot-outline.md` for the scene sequence
2. Identify each scene's purpose (what changes from start to end of scene)
3. Plan transitions between scenes

**While writing:**
4. Write in present tense — screenplays describe what the camera sees NOW
5. Use **one sentence per line** in action descriptions
6. Keep action paragraphs to 3-4 lines max — white space is crucial in screenplays
7. Dialogue should be speakable — read it aloud mentally
8. Every scene must enter late and exit early

**After writing:**
9. Update the bible if new story elements were introduced
10. Mark scenes as drafted in `bible/plot-outline.md`

### Scenario-Specific Rules
- **Write what the camera sees.** No internal thoughts unless expressed through action or dialogue.
- **No "we see" or "we hear."** Just describe it directly.
- **Minimal camera directions.** Only specify shots when dramatically essential.
- **Subtext over text.** Characters rarely say what they mean. Dialogue should work on two levels.
- **Page economy.** Feature screenplays are 90-120 pages. Every scene must earn its place.

---

## Pitch Format (Movie Pitching Deck)

### File Conventions
- Single file: `pitch/pitch-document.md`

### Document Structure

The pitch document follows industry-standard sections:

```markdown
# [TITLE]

## Logline
<!-- One sentence. Who + want + obstacle + stakes. Max 35 words. -->

## Synopsis
<!-- 1-2 paragraphs. Beginning, middle, end. Present tense. -->

## Tone & Comparables
<!-- "X meets Y" — two reference films/shows that triangulate the tone.
     Brief description of the tonal register. -->

## Characters
<!-- 3-5 main characters. Name, role, one-line essence.
     Focus on what makes each compelling for an audience. -->

## Visual Tone
<!-- What does this film LOOK like? Color palette, cinematographic references,
     visual influences. Describe key frames or signature shots. -->

## World & Setting
<!-- The world as a character. What makes this setting fresh or cinematic? -->

## Thematic Core
<!-- What is this film really about beneath the plot?
     The emotional or philosophical argument. -->

## Target Audience & Market
<!-- Who watches this? Comparable box office or streaming performance.
     Why now? What makes this timely? -->

## Act Structure
<!-- Brief act breakdown. 3-5 sentences per act.
     Show the shape of the story without spoiling every beat. -->

## Why This Story
<!-- The passion pitch. Why does this story need to exist?
     What's the personal or cultural urgency? -->
```

### Pitch Writing Workflow

**Before writing:**
1. Read the full bible — every section
2. Identify the most cinematic, pitch-worthy elements of the story
3. Determine the "elevator version" — what hooks someone in 10 seconds

**While writing:**
4. Write in present tense, active voice
5. Use **one sentence per line**
6. Lead with the hook in every section — the first sentence of each section must grab attention
7. Be specific, not vague — describe characters by their contradiction, not their archetype

**After writing:**
8. Verify all facts match the bible
9. Ensure the logline works standalone — someone with no context should understand the movie

### Pitch-Specific Rules
- **Sell the experience, not the plot.** The pitch conveys what it FEELS like to watch this film.
- **Comparable titles must be recent and successful.** Don't reference obscure or old films unless they're iconic.
- **Characters are described by their contradiction.** A paradox is more pitchable than a type.
- **Keep it under 5 pages.** Shorter is better. Executives skim.
- **No spoilers in the synopsis unless essential.** Reveal the ending only if it's the selling point.

---

## Prompt Engineering

The prompt library (`prompts/`) holds reusable fragments that are **composed** into full generation prompts.
Never write a generation prompt from scratch — always assemble from library fragments to maintain consistency.

### Composition Pattern

A complete image prompt is assembled from fragments:

```
[character fragment] + [setting fragment] + [style fragment] + [scene-specific details]
```

Example composition:
```
prompts/image/characters/[name].md   →  "[character's visual identity description]"
prompts/image/settings/[place].md    →  "[location's visual description]"
prompts/image/styles/[style].md      →  "[art style, linework, color palette, format]"
scene-specific                       →  "[camera angle, lighting, time of day, mood]"
```

The fragments are concatenated into a single prompt sent to the generation tool.

### Image Prompt Rules
- **Always include the character's Core Appearance** from their prompt file — never describe from memory
- **Specify camera angle and framing** explicitly: close-up, medium shot, wide shot, bird's eye, worm's eye
- **Include lighting and time of day** — these define the mood more than any adjective
- **Style fragment goes last** — it applies to the whole image
- **Negative prompts** go in a separate field per the tool's format
- **One sentence per line** in prompt files for git-friendly diffs

### Video Prompt Rules
- **Start from a source image when possible** — image-to-video produces more consistent results than text-to-video
- **Describe motion, not the scene** — the scene is already in the source image; the prompt should say what MOVES
- **Keep motion descriptions short** — 1-2 sentences max; video models get confused by long prompts
- **Specify camera movement explicitly** — "camera slowly pans left," "static shot," "dolly zoom"
- **Include duration** — most tools need a target length (4s, 8s, 16s)

### Audio Prompt Rules
- **Music:** Describe genre, mood, tempo, key instruments, dynamics (builds, drops), and duration
- **SFX:** Describe the sound precisely — include material, space, and reverb characteristics
- **Voice:** Include emotional direction, pacing, and volume alongside the voice description
- **Reference tracks** are more effective than adjectives — "sounds like [specific track] but more [quality]"

### Prompt File Naming
- Character prompts: `prompts/<type>/characters/<character-name>.md`
- Setting prompts: `prompts/image/settings/<location-name>.md`
- Style presets: `prompts/<type>/styles/<style-name>.md`
- All lowercase kebab-case

### Prompt Maintenance
- When a character's appearance changes in the story (new scar, different outfit), **update the prompt file** and note the change
- Create **alternate outfit** entries in character prompt files for different story phases
- When a prompt produces good results, record the **exact parameters and seed** in `assets/manifest.md`
- When a prompt needs iteration, keep the working version and add notes about what to try next

---

## Asset Management

Generated media files (images, videos, audio) are stored in `assets/` and tracked by **Git LFS**.
The `.gitattributes` file is pre-configured to track all common media formats.

### Asset Naming Convention
```
assets/<output>/<unit>/<descriptor>-<version>.<ext>
```

Examples:
```
assets/conti/ep-NN/panel-NN-[descriptor]-vN.png
assets/scenario/[scene-descriptor]-vN.mp4
assets/pitch/[visual-descriptor]-vN.jpg
assets/audio/[track-descriptor]-vN.mp3
```

### Manifest

Every generated asset must have an entry in `assets/manifest.md` tracking:
- **Source prompt fragments** — which prompt files were composed
- **Composed prompt** — the full prompt as sent to the tool
- **Tool and model** — which generator and version
- **Parameters** — aspect ratio, style weight, seed, duration, etc.
- **Date generated**
- **Used in** — which output file references this asset
- **Status** — accepted, needs revision, rejected

This enables reproducibility — you can regenerate any asset or create variations from the recorded prompt.

### Asset Workflow

1. Write or update the relevant prompt fragments in `prompts/`
2. Compose the full prompt following the composition pattern
3. Generate the asset using the chosen tool
4. Save to `assets/` following the naming convention
5. Add a manifest entry in `assets/manifest.md`
6. Reference the asset from the output file (conti panel, pitch doc, etc.)
7. Commit the prompt, asset, and manifest entry together

### Version Control for Assets
- Use `-vN` suffix for iterations: `[descriptor]-v1.png`, `v2`, `v3`
- Keep only accepted versions in the repo — delete rejected iterations to save LFS storage
- When replacing an asset, update its manifest entry and any output files that reference it

---

## Continuity Rules

- **The bible is canon.** All outputs must align with the bible. No exceptions without discussion.
- When uncertain about an established fact, check the bible before writing in any format.
- If an output introduces something that conflicts with canon, flag it to the author rather than silently overwriting.
- Keep a consistent internal timeline across all outputs.
- When one output evolves the story (e.g., conti adds a scene that works better), update the bible first, then propagate to other outputs.

## Revision Workflow

When revising any output:
1. Read the current draft fully before making changes
2. Preserve the author's voice — enhance it, don't replace it
3. Focus on the specific revision goals
4. Do not rewrite sections that are already working well
5. After revisions, update the file's metadata status
6. Check if revisions require bible updates or changes to other outputs

## Git Workflow

Commit messages follow this format:
```
<type>: <scope> - <short description>
```

Types:
- `draft` — first draft of a unit (chapter, episode, scene, pitch)
- `revise` — revision pass on an existing draft
- `bible` — updates to the core story bible
- `outline` — changes to plot structure or beat mapping
- `style` — prose polish, line edits, voice adjustments
- `prompt` — new or updated prompt fragments
- `asset` — new or updated generated media
- `generate` — prompt + asset committed together (typical generation workflow)

Scopes:
- `novel` — novel chapter
- `conti` — webtoon episode
- `scenario` — screenplay
- `pitch` — pitch document
- `bible` — core story documents
- `image` — image generation prompts/assets
- `video` — video generation prompts/assets
- `audio` — audio generation prompts/assets

Examples:
```
draft: novel ch NN - [description]
draft: conti ep NN - [description]
revise: scenario act N - [description]
bible: add character sheet for [name]
outline: restructure [act/beat], update output mapping
draft: pitch - first complete draft
prompt: image - add character prompt for [name]
generate: conti ep NN - panels N-N [description]
asset: audio - [track name] vN
prompt: video - add [style name] style preset
```

### Branching (Optional)

For experimental rewrites or alternate directions:
- `alt/<scope>/<description>` — alternate version
- `experiment/<description>` — exploratory work that may or may not be kept
