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

references/            — REFERENCE MATERIALS (tracked via Git LFS)
  index.md             — file list with notes and sources
  overview.md          — visual catalog (inline images for quick browsing)
  images/              — actual reference files
    [prefix]-[NNN]-[description].[ext]

assets/                — GENERATED MEDIA (tracked via Git LFS)
  keyart/              — key art / concept art images
  sketch/              — model comparison sketches
  webtoon/             — webtoon panel images (organized by episode)
    ep-NN/
  conti/               — conti storyboard images (organized by episode)
    ep-NN/
  video/               — generated video clips
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

## Reference Management

외부에서 수집한 레퍼런스 자료(영화 스틸, 배우 사진, 무드보드, 아트 스타일 참고, 영상 클립 등)는 `references/` 폴더에 넣는다.
생성 결과물(`assets/`)과는 구분된다 — 레퍼런스는 영감과 방향 설정을 위한 외부 자료다.

### Naming Convention

```
[접두사]-[NNN]-[설명].[ext]
```

접두사로 파일명 소팅 시 용도별로 자동 그룹핑되고, 번호로 순서가 유지된다.

| 접두사 | 용도 |
|--------|------|
| `char` | 캐릭터 비주얼 (얼굴, 체형, 의상) |
| `mood` | 분위기/톤 (컬러 팔레트, 무드보드) |
| `motion` | 모션/연출/카메라워크 (영상 클립) |
| `setting` | 장소/배경 (건물, 거리, 자연) |
| `style` | 아트 스타일/채색/선화 |

예시:
```
char-001-주인공-얼굴참고.jpg
char-002-주인공-전신.png
mood-001-야경-골목길.png
setting-001-폐건물-외관.jpg
style-001-manhwa-채색참고.webp
motion-001-액션-칼싸움.mp4
```

### Reference Workflow

1. 레퍼런스 파일을 `references/images/`에 넣는다
2. 파일명을 `[접두사]-[NNN]-[설명].[ext]` 형식으로 짓는다
3. `references/index.md`에 출처와 참고 포인트를 메모한다
4. `references/overview.md`에 이미지를 추가한다 — Obsidian에서 전체 레퍼런스를 한눈에 훑어볼 수 있는 비주얼 카탈로그
5. 프롬프트 작성 시 레퍼런스를 참고하되, 프롬프트 파일(`prompts/`)에는 레퍼런스 파일을 직접 참조하지 않는다 — 프롬프트는 텍스트 기반으로 독립적이어야 한다

### Overview Page

`references/overview.md`는 모든 레퍼런스를 인라인 이미지로 보여주는 비주얼 카탈로그다.
Obsidian에서 열면 이미지가 렌더링되어 전체 레퍼런스를 빠르게 훑어볼 수 있다.

구성 규칙:
- 접두사별로 섹션을 나눈다 (`## char`, `## mood`, `## setting` 등)
- 캐릭터/장소별로 서브섹션을 만든다
- 이미지는 3열 마크다운 테이블로 배치한다
- 각 이미지 아래에 번호와 짧은 설명을 넣는다
- 레퍼런스 추가/삭제 시 overview.md도 반드시 함께 업데이트한다

### Reference vs Asset

| | 레퍼런스 (`references/`) | 에셋 (`assets/`) |
|---|---|---|
| 출처 | 외부 수집 | 직접 생성 |
| 용도 | 영감, 방향 설정 | 최종 결과물 |
| 재현성 | 불필요 | manifest로 재현 가능 |
| 네이밍 | `[접두사]-[NNN]-[설명]` | `[descriptor]-v[N]` |

---

## Asset Management

Generated media files (images, videos, audio) are stored in `assets/` and tracked by **Git LFS**.
The `.gitattributes` file is pre-configured to track all common media formats.

### Asset Naming Convention

**파일명으로 프롬프트 추적이 가능해야 한다.**
파일명의 각 세그먼트가 `prompts/` 라이브러리의 프롬프트 파일에 직접 매핑된다.

```
assets/<category>/<char>-<setting>-<style>-v<N>.<ext>
```

세그먼트 매핑:
- `<char>` → `prompts/image/characters/<char>.md`
- `<setting>` → `prompts/image/settings/<setting>.md`
- `<style>` → `prompts/image/styles/<style>.md`
- `-v<N>` → 버전 번호 (같은 프롬프트의 반복 생성)

Examples:
```
assets/keyart/dongsu-office-cinematic-v1.png
assets/webtoon/ep-01/dongsu-office-manhwa-v1.png
assets/conti/ep-NN/panel-NN-[descriptor]-vN.png
assets/video/clip01-office-comedy-hunyuan15i2v-v1.mp4
assets/scenario/[scene-descriptor]-vN.mp4
assets/pitch/[visual-descriptor]-vN.jpg
assets/audio/[track-descriptor]-vN.mp3
```

파일명만 보고 프롬프트를 찾는 예시:
`dongsu-office-cinematic-v1.png` →
- `prompts/image/characters/dongsu.md` (캐릭터 외모)
- `prompts/image/settings/office.md` (사무실 배경)
- `prompts/image/styles/cinematic.md` (영화적 스타일)
- `assets/manifest.md`의 해당 항목에서 조합된 최종 프롬프트, seed, 파라미터 확인

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

## ComfyUI Image & Video Generation

이미지/비디오 생성은 ComfyUI 서버의 REST API를 통해 수행한다. 모든 모델은 로컬 GPU에서 실행된다 (무료).
**유료 API 노드(Flux2Pro, GPT Image, Ideogram, Gemini 등)는 사용하지 않는다.**

### Server Configuration (4 ComfyUI Servers)

4개 서버를 동시에 사용하여 병렬 생성이 가능하다.
각 서버는 RTX 6000 Ada (48GB VRAM) 1장을 사용한다.

| Server | URL | GPU | 주요 모델 |
|--------|-----|-----|----------|
| **wright-a** | `wright.gazelle-galaxy.ts.net:8188` | RTX 6000 Ada | FLUX, SD3.5, z_turbo, Wan I2V MoE, HunyuanVideo 1.5 |
| **wright-b** | `wright.gazelle-galaxy.ts.net:8189` | RTX 6000 Ada | (wright-a와 동일) |
| **neumann-a** | `neumann.gazelle-galaxy.ts.net:8188` | RTX 6000 Ada | FLUX, SDXL (Juggernaut, RealVis, DreamShaper, Animagine) |
| **neumann-b** | `neumann.gazelle-galaxy.ts.net:8189` | RTX 6000 Ada | (neumann-a와 동일) |

**서버 자동 선택:** `--server` 미지정 시, 스크립트가 호환 서버의 큐를 확인하여 가장 한가한 서버를 자동 선택한다.

**서버 상태 확인:**
```bash
python3 scripts/generate_api.py servers
```

### Available Local Models — Image

| Model ID | Label | Steps | Server | Best For |
|----------|-------|-------|--------|----------|
| `flux-dev` | FLUX.1 Dev | 20 | all | 최고 품질 포토리얼 |
| `flux-dev-lora` | FLUX.1 Dev + Realism LoRA | 20 | all | 포토리얼 극강 (피부/조명/질감) |
| `flux-schnell` | FLUX.1 Schnell | 4 | all | 빠른 반복 실험 |
| `sd35` | SD3.5 Large | 28 | wright | 영화 포스터풍 |
| `juggernaut-xl` | Juggernaut XL v9 | 25 | neumann | 포토리얼 SDXL |
| `realvis-xl` | RealVisXL V4.0 | 25 | neumann | 사실적 인물 |
| `dreamshaperxl` | DreamShaper XL Turbo | 25 | neumann | 아트 스타일 |
| `animagine-xl` | Animagine XL 3.1 | 25 | neumann | 애니메이션 |
| `z-turbo` | z_image_turbo | 8 | wright | 웹툰, 빠른 프로토타입 |

### Available Local Models — Video

| Model ID | Label | Steps | FPS | Size | Server | Best For |
|----------|-------|-------|-----|------|--------|----------|
| `wan-i2v` | Wan 2.2 I2V 14B MoE | 20 | 16 | 832x480 | wright | 고품질 비디오 (듀얼 전문가) |
| `wan-i2v-rife` | Wan 2.2 I2V 14B MoE + RIFE 2x | 20 | 32 | 832x480 | wright | 부드러운 고품질 비디오 |
| `hunyuan15-i2v` | HunyuanVideo 1.5 I2V | 20 | 24 | 848x480 | wright | 시간적 일관성 최고 |
| `hunyuan15-i2v-rife` | HunyuanVideo 1.5 + RIFE 2x | 20 | 48 | 848x480 | wright | 초고FPS 비디오 |

**Wan 2.2 I2V MoE 아키텍처:** Wan I2V 14B는 단일 모델이 아닌 **Mixture of Experts (MoE)** 듀얼 전문가 구조이다.
High-noise expert가 초기 디노이징 (전체 구도/레이아웃), low-noise expert가 후기 디노이징 (디테일 정제)을 담당한다.
두 모델은 KSamplerAdvanced로 체이닝되어 순차적으로 실행된다 (steps 0→half: high noise, half→end: low noise).
ModelSamplingSD3 shift=8.0, cfg=3.5가 공식 기본값이다. CLIPVision은 사용하지 않는다.

### Model Files (설치 경로)

```
models/diffusion_models/
  flux1-dev-fp8.safetensors                         (17GB)  — FLUX.1 Dev
  flux1-schnell-fp8.safetensors                     (17GB)  — FLUX.1 Schnell
  z_image_turbo_bf16.safetensors                    (12GB)  — z_image_turbo (Lumina2 기반)
  wan2.2_i2v_high_noise_14B_fp16.safetensors         (28.6GB) — Wan 2.2 MoE High Noise Expert (FP16)
  wan2.2_i2v_low_noise_14B_fp16.safetensors          (28.6GB) — Wan 2.2 MoE Low Noise Expert (FP16)
  hunyuanvideo1.5_720p_i2v_cfg_distilled_fp8_scaled.safetensors (8.3GB) — HunyuanVideo 1.5 I2V

models/checkpoints/
  sd3.5_large_fp8_scaled.safetensors                (14GB)  — SD3.5 Large (all-in-one)

models/text_encoders/
  clip_l.safetensors                                (235MB) — CLIP-L (FLUX용)
  t5xxl_fp8_e4m3fn_scaled.safetensors               (4.9GB) — T5-XXL (FLUX용)
  qwen_3_4b.safetensors                             (7.5GB) — Qwen 3 4B (z_image_turbo용)
  umt5_xxl_fp8_e4m3fn_scaled.safetensors            (6.3GB) — UMT5-XXL (Wan 비디오용)
  qwen_2.5_vl_7b_fp8_scaled.safetensors             (9.4GB) — HunyuanVideo 텍스트 인코더
  byt5_small_glyphxl_fp16.safetensors               (419MB) — HunyuanVideo byt5 인코더

models/vae/
  ae.safetensors                                    (320MB) — VAE (FLUX, z_image_turbo 공유)
  wan_2.1_vae.safetensors                           (243MB) — VAE (Wan 비디오용)
  hunyuanvideo15_vae_fp16.safetensors               (2.4GB) — HunyuanVideo VAE

models/clip_vision/
  sigclip_vision_patch14_384.safetensors             (817MB) — HunyuanVideo CLIP Vision

models/loras/
  flux-realism-lora.safetensors                     (22MB)  — 포토리얼리즘 LoRA

models/controlnet/
  flux-dev-controlnet-union-pro.safetensors          (6.2GB) — Flux ControlNet (7가지 모드)

models/upscale_models/
  4x-UltraSharp.pth                                 (64MB)  — ESRGAN 4x 업스케일러

custom_nodes/ComfyUI-Frame-Interpolation/ckpts/rife/
  rife47.pth / rife49.pth                           (21MB)  — RIFE 프레임 보간 모델
```

**설치 서버:** wright-a, wright-b (Wan MoE, HunyuanVideo 1.5, RIFE 모두 설치) + neumann-a, neumann-b (SDXL 모델)

### ComfyUI Workflow 구성 — Image

**FLUX.1 Dev / Schnell:**
```
UNETLoader(weight_dtype=fp8_e4m3fn)
  → DualCLIPLoader(clip_l + t5xxl, type=flux)
  → CLIPTextEncode → FluxGuidance(guidance=3.5)  ← Dev만. Schnell은 guidance 불필요
  → EmptySD3LatentImage(width, height)
  → KSampler(steps=20/4, cfg=1.0, sampler=euler, scheduler=simple)
  → VAEDecode(ae.safetensors) → SaveImage
```

**SD3.5 Large:**
```
CheckpointLoaderSimple(sd3.5_large_fp8_scaled)
  → CLIPTextEncode (positive + negative)
  → EmptySD3LatentImage(width, height)
  → KSampler(steps=28, cfg=4.5, sampler=euler, scheduler=normal)
  → VAEDecode → SaveImage
```

**z_image_turbo (기존):**
```
UNETLoader(z_image_turbo_bf16)
  → CLIPLoader(qwen_3_4b, type=lumina2)
  → ModelSamplingAuraFlow(shift=3.0)
  → KSampler(steps=8, cfg=1.0, sampler=res_multistep, scheduler=simple)
  → VAEDecode(ae.safetensors) → SaveImage
```

### ComfyUI Workflow 구성 — Video

**Wan 2.2 I2V 14B MoE (듀얼 전문가):**
```
UNETLoader(high_noise_14B) + UNETLoader(low_noise_14B)
  → ModelSamplingSD3(shift=8.0) × 2 (각 모델에 적용)
  → CLIPLoader(umt5_xxl, type=wan) → CLIPTextEncode (positive + negative)
  → LoadImage → WanImageToVideo(width=832, height=480, length=81)
  → KSamplerAdvanced(high_noise, steps=20, cfg=3.5, start=0, end=10, noise=enable)
  → KSamplerAdvanced(low_noise, steps=20, cfg=3.5, start=10, end=10000, noise=disable)
  → VAEDecode(wan_2.1_vae) → [optional: RIFE VFI] → SaveAnimatedWEBP / VHS_VideoCombine
```

**HunyuanVideo 1.5 I2V:**
```
UNETLoader(hunyuanvideo1.5_i2v_cfg_distilled)
  → DualCLIPLoader(qwen_2.5_vl + byt5, type=hunyuan_video)
  → TextEncodeHunyuanVideo_ImageToVideo(prompt, src_image)
  → EmptyHunyuanLatentVideo(width=848, height=480, length=33)
  → KSampler(steps=20, cfg=1.0, sampler=euler, scheduler=simple)
  → VAEDecode(hunyuanvideo15_vae) → [optional: RIFE VFI] → VHS_VideoCombine
```

### Generation Scripts

**`scripts/generate_api.py`** — 멀티 서버, 멀티 모델 생성 스크립트

```bash
# 서버 상태 확인
python3 scripts/generate_api.py servers

# 단일 이미지 생성 (assets/sketch/에 저장)
python3 scripts/generate_api.py image \
  --model flux-dev --name test --seed 42 \
  --prompt "..."

# 스케치: 같은 프롬프트로 모든 모델 병렬 생성 (4서버 동시 사용)
python3 scripts/generate_api.py sketch \
  --name test --seed 42 \
  --prompt "..."

# 특정 모델만 스케치
python3 scripts/generate_api.py sketch \
  --models "flux-dev,juggernaut-xl,realvis-xl" \
  --name test --seed 42 --prompt "..."

# Wan 2.2 I2V MoE (듀얼 전문가, 832x480, 16fps, 5.1초)
python3 scripts/generate_api.py video \
  --model wan-i2v --source path/to/image.png \
  --name clip-01 --seed 42 --prompt "motion description"

# Wan 2.2 I2V MoE + RIFE (32fps, 부드러운 모션)
python3 scripts/generate_api.py video \
  --model wan-i2v-rife --source path/to/image.png \
  --name clip-01 --seed 42 --prompt "motion description"

# HunyuanVideo 1.5 (848x480, 24fps, 시간적 일관성 최고)
python3 scripts/generate_api.py video \
  --model hunyuan15-i2v --source path/to/image.png \
  --name clip-01 --seed 42 --prompt "motion description"

# 서버 수동 지정 (기본: 자동 선택)
python3 scripts/generate_api.py video \
  --model wan-i2v --server wright-a --source path/to/image.png \
  --name clip-01 --seed 42 --prompt "motion description"

# SeedVR2 비디오 업스케일 (기존 비디오 → 1080p+)
python3 scripts/generate_api.py video-enhance \
  --source assets/video/clip-01-v1.mp4 \
  --name clip-01 --resolution 1080

# 멀티패스: Flux+LoRA → 4x 업스케일 → img2img 정제 (2560x1440 최종)
python3 scripts/generate_api.py multipass \
  --name scene-01 --seed 42 \
  --prompt "..." \
  --width 2560 --height 1440 --denoise 0.35

# 4x UltraSharp 업스케일 (기존 이미지)
python3 scripts/generate_api.py upscale \
  --source assets/sketch/scene-01-base-v1.png \
  --name scene-01 --width 2560 --height 1440

# ControlNet (참조 이미지 기반 구도 유지 재생성)
python3 scripts/generate_api.py controlnet \
  --source reference.png --prompt "..." \
  --name scene-01 --cn-strength 0.6
```

**`sketch` 커맨드는 모든 이미지 모델을 4개 서버에 분산하여 동시 생성한다.**
결과는 `assets/sketch/`에 `{name}-{model}-v{N}.png` 형식으로 저장된다.

### Multi-Pass Workflow (Midjourney 이상의 품질)

`multipass` 커맨드는 3단계 파이프라인을 하나의 ComfyUI 워크플로로 실행한다:

1. **Base Generation** — Flux Dev + flux-realism-lora (1280x720, 20 steps)
   - Realism LoRA가 피부 질감, 조명, 디테일을 강화
2. **4x UltraSharp Upscale** — 픽셀 공간에서 5120x2880으로 업스케일 → lanczos로 최종 크기
   - ESRGAN 기반 업스케일러, 엣지를 선명하게 유지
3. **Img2img Refinement** — 업스케일된 이미지를 낮은 denoise(0.35)로 정제
   - 고해상도에서 세부 디테일 추가, 전체 구도 유지

**파라미터 가이드:**
- `--lora-strength 0.8` — LoRA 강도 (0.6~1.0, 높을수록 리얼리즘 강화)
- `--denoise 0.35` — 정제 강도 (0.2~0.5, 높을수록 변화 큼, 0.3~0.4 권장)
- `--width 2560 --height 1440` — 최종 해상도 (2K 기본값)

**ControlNet 워크플로:**
- 참조 이미지에서 Canny 엣지를 추출하여 구도를 유지하면서 재생성
- `flux-dev-controlnet-union-pro` 모델 사용 (7가지 컨트롤 모드 지원)
- `--cn-type` 옵션: canny, depth, openpose, tile, segment 등

### Video Enhancement Pipeline

비디오 품질 향상을 위한 도구:

1. **RIFE Frame Interpolation** — 프레임 보간으로 FPS 2배 (16→32fps 또는 24→48fps)
   - `-rife` 접미사 모델 사용: `wan-i2v-rife`, `hunyuan15-i2v-rife`
   - 비디오 생성과 동시에 실행 (단일 워크플로)
2. **SeedVR2 Video Upscaler** — AI 기반 비디오 해상도 업스케일
   - `video-enhance` 커맨드로 기존 비디오 후처리
   - 3B (빠름) 또는 7B-sharp (고품질) 모델 선택 가능

### Multi-Server Queue-Aware Selection

`--server` 미지정 시, 스크립트가 자동으로 가장 한가한 서버를 선택한다:
1. 모델에 호환되는 서버 목록을 확인 (비디오: wright-a/wright-b, 이미지: all 4)
2. 각 서버의 `/queue` API를 호출하여 running + pending 작업 수를 확인
3. 큐가 가장 짧은 서버를 선택
4. 서버가 모두 다운된 경우 에러 발생

수동 지정: `--server wright-a` 또는 `--server neumann-b`

### Model Selection Guide

**이미지:**
- **최고 품질 (Midjourney 대항)** → `multipass` (Flux+LoRA → 4x upscale → img2img)
- **키아트 최종본** → FLUX.1 Dev + Realism LoRA (`flux-dev-lora`)
- **키아트 초안** → FLUX.1 Schnell (4 steps, 5배 빠름)
- **구도 유지 재생성** → `controlnet` (참조 이미지 + Canny/Depth)
- **기존 이미지 고해상도화** → `upscale` (4x UltraSharp)
- **영화 포스터** → SD3.5 Large (독특한 미학)
- **포토리얼 인물** → Juggernaut XL 또는 RealVisXL (SDXL 기반)
- **아트/일러스트** → DreamShaper XL (스타일리시)
- **애니메이션** → Animagine XL (anime/manhwa)
- **웹툰 패널** → z_image_turbo (가장 빠름)
- **모델 비교** → `sketch` 커맨드로 전체 모델 동시 비교

**비디오:**
- **최고 시간적 일관성** → `hunyuan15-i2v` (HunyuanVideo 1.5, 떨림 없는 안정적 출력)
- **스타일리시한 모션** → `wan-i2v` (MoE 듀얼 전문가 14B, 역동적 모션)
- **부드러운 고품질** → `wan-i2v-rife` (MoE 14B + RIFE 32fps)
- **초고FPS** → `hunyuan15-i2v-rife` (HunyuanVideo + RIFE 48fps)
- **비디오 업스케일** → `video-enhance` (SeedVR2, 기존 비디오 → 1080p+)
- **모델 비교** → 같은 소스로 `wan-i2v` + `hunyuan15-i2v` 둘 다 생성 후 비교 권장

### Image Size Presets

| Category | Size | 용도 |
|----------|------|------|
| keyart | 1280x720 | 16:9 와이드 키아트, 배너 |
| keyart-poster | 720x1280 | 세로 포스터 |
| webtoon | 768x1024 | 웹툰 패널 (세로 스크롤) |
| webtoon-square | 1024x1024 | 정사각 패널 |

### Image Size Presets

| Category | Size | 용도 |
|----------|------|------|
| keyart | 1280x720 | 16:9 와이드 키아트, 배너 |
| keyart-poster | 720x1280 | 세로 포스터 |
| webtoon | 768x1024 | 웹툰 패널 (세로 스크롤) |
| webtoon-square | 1024x1024 | 정사각 패널 |

### Adding New Models

HuggingFace에서 ComfyUI 호환 모델을 다운로드하여 서버에 설치:
```bash
# SSH로 서버 접속
ssh wright.gazelle-galaxy.ts.net   # 또는 neumann.gazelle-galaxy.ts.net

# 모델 다운로드 (예: diffusion model)
cd ~/codegit/ComfyUI/models/diffusion_models/
wget https://huggingface.co/<org>/<repo>/resolve/main/<model>.safetensors
```
모델 추가 후 ComfyUI 재시작 없이 API 호출 시 자동 인식된다.
`scripts/generate_api.py`의 `IMAGE_MODELS` 또는 `VIDEO_MODELS` dict에 새 모델을 등록한다.
**모델 추가 후 반드시 `scripts/models.yaml`에도 등록한다** (아래 Model Sync 참고).

### Model Sync — 서버 간 모델 동기화

두 서버(wright, neumann)의 모델을 동일하게 유지하기 위한 도구.
`scripts/models.yaml`이 single source of truth이다.

```bash
# 각 서버의 현재 모델 목록 조회
python scripts/model_sync.py status

# manifest에 있는데 서버에 없는 모델 표시
python scripts/model_sync.py diff

# 누락된 모델을 서버에 직접 다운로드 (SSH + wget)
python scripts/model_sync.py sync

# manifest에 없는 모델 표시 (정리 대상)
python scripts/model_sync.py orphans
```

**모델 추가 워크플로:**
1. `scripts/models.yaml`에 새 모델 엔트리 추가 (name, url, size_gb)
2. `python scripts/model_sync.py diff` — 누락 확인
3. `python scripts/model_sync.py sync` — 다운로드
4. `scripts/generate_api.py`에 모델 등록

**모델 삭제 워크플로:**
1. `scripts/models.yaml`에서 해당 엔트리 제거
2. `python scripts/model_sync.py orphans` — 잔여 파일 확인
3. SSH로 서버에 접속하여 수동 삭제

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
- `ref` — new or updated reference materials

Scopes:
- `novel` — novel chapter
- `conti` — webtoon episode
- `scenario` — screenplay
- `pitch` — pitch document
- `bible` — core story documents
- `image` — image generation prompts/assets
- `video` — video generation prompts/assets
- `audio` — audio generation prompts/assets
- `ref` — reference materials

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
ref: add character reference images for [name]
ref: add mood board for [scene/setting]
```

### Branching (Optional)

For experimental rewrites or alternate directions:
- `alt/<scope>/<description>` — alternate version
- `experiment/<description>` — exploratory work that may or may not be kept
