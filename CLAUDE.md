# Novel Writing Project

This is a fiction writing project, not a software project. Claude operates as a **writing partner** — drafting prose, dialogue, and scenes collaboratively with the author.

## Core Principles

- **Show, don't tell.** Render emotion through action, dialogue, and sensory detail — not exposition.
- **Every scene must do two things**: advance the plot AND reveal character.
- **Dialogue is action.** Characters speak to get what they want, not to deliver information to the reader.
- **Earn your adjectives.** Prefer strong nouns and verbs over modified weak ones.
- **Cut the throat-clearing.** Start scenes late, leave early. No preamble.
- **Never summarize when you can dramatize.** If something matters, it deserves a scene.

## Anti-Patterns — Never Do These

- Do not use clichés or stock phrases ("a chill ran down his spine," "little did they know")
- Do not break the fourth wall or address the reader directly (unless the story's voice demands it)
- Do not use emoji, markdown formatting artifacts, or bullet points in prose
- Do not add meta-commentary, author's notes, or explanations within chapter text
- Do not write "purple prose" — avoid overwrought descriptions that slow pacing
- Do not introduce characters, locations, or plot elements that contradict the reference docs
- Do not summarize previous events unless the narrative POV naturally calls for reflection
- Do not use "said bookisms" excessively (prefer "said" over "exclaimed/declared/opined")

## Project Structure

```
CLAUDE.md              — this file (writing partner instructions)
chapters/              — one markdown file per chapter
  01-<title>.md
  02-<title>.md
  ...
reference/
  story-bible.md       — genre, audience, premise, tone, setting overview
  characters.md        — character sheets (appearance, voice, arc, relationships)
  world.md             — world-building (geography, systems, rules, culture, history)
  plot-outline.md      — chapter-by-chapter plot plan with act structure
  themes.md            — thematic threads, motifs, symbols to weave through the narrative
  style-guide.md       — prose voice samples, vocabulary notes, sentence rhythm preferences
```

### Chapter File Format

Each chapter file begins with a metadata block, followed by the prose:

```markdown
<!--
Chapter: 3
Title: The Crossing
POV: [character name]
Timeline: [when this takes place in story time]
Status: draft | revised | final
Word Count Target: ~3000
-->

# The Crossing

[Chapter prose begins here...]
```

### Line Formatting — One Sentence Per Line

All prose must use **semantic line breaks**: one sentence per line, with a single newline between sentences. This makes git diffs readable — a one-word edit shows as a single changed line, not a reflowed paragraph.

**Do this:**
```markdown
The door swung open and she stepped into the dark.
Something moved in the corner, low and quick.
She reached for the knife at her belt, but her hand found only empty leather.
```

**Not this:**
```markdown
The door swung open and she stepped into the dark. Something moved in the corner, low and quick. She reached for the knife at her belt, but her hand found only empty leather.
```

Both render identically in Markdown. The first is git-friendly.

Paragraph breaks use a blank line, as normal in Markdown.
Dialogue that spans multiple sentences still follows one-sentence-per-line within the same paragraph block.

### Naming Conventions

- Chapter files: `NN-kebab-case-title.md` (zero-padded two digits)
- Scene breaks within a chapter: use `---` (horizontal rule)
- Reference docs: lowercase kebab-case filenames

## Writing Workflow

When drafting or revising a chapter, follow this process:

### Before Writing
1. Read `reference/plot-outline.md` to understand where this chapter sits in the story
2. Read the character sheets for any POV or major characters in this chapter
3. Read the previous chapter (or its metadata) for continuity
4. Check `reference/themes.md` for thematic threads that should surface

### While Writing
5. Write the chapter as complete, polished prose — not an outline or sketch
6. Use **one sentence per line** — see Line Formatting section above
7. Use the POV character's voice and sensory perspective consistently
8. End the chapter with a hook, turn, or resonance that pulls the reader forward
9. Use `---` for scene breaks within the chapter

### After Writing
10. Update `reference/characters.md` if new characters were introduced
11. Update `reference/world.md` if new locations, rules, or lore were established
12. Update `reference/plot-outline.md` — mark the chapter as drafted, note any deviations from the plan
13. Update `reference/themes.md` if thematic threads were advanced or new motifs emerged

## Reference Document Guidelines

### story-bible.md
The project's identity document. Contains:
- **Genre & subgenre** (e.g., epic fantasy, hard sci-fi, domestic thriller)
- **Target audience** (e.g., adult, YA, middle grade)
- **Premise** — the story's core concept in 2-3 sentences
- **Tone & mood** — the emotional register of the narrative
- **Comparable titles** — published novels that share DNA with this project
- **Setting overview** — broad strokes of when and where

### characters.md
For each significant character, maintain:
- **Name & aliases**
- **Role** (protagonist, antagonist, supporting, minor)
- **Physical description** — distinctive features, how they carry themselves
- **Voice** — speech patterns, vocabulary, verbal tics
- **Want vs. Need** — what they pursue vs. what they actually require
- **Arc** — where they start, what changes them, where they end
- **Relationships** — key connections to other characters
- **Key scenes** — chapters where they appear or are significantly referenced

### world.md
The canonical source for the story's setting:
- **Geography & locations** — maps, territories, key places
- **Systems** — magic, technology, political, economic (whatever applies)
- **Rules & constraints** — what's possible and impossible in this world
- **Culture & society** — customs, beliefs, conflicts
- **History** — past events that shape the present story
- **Sensory palette** — what this world looks, sounds, smells, feels like

### plot-outline.md
The structural backbone:
- **Act structure** — three-act, five-act, or whatever framework suits the story
- **Chapter plan** — one-line summary of each planned chapter
- **Status tracking** — which chapters are planned / drafted / revised / final
- **Deviations log** — where the draft diverged from the original plan and why
- **Open threads** — plot points that have been set up but not yet resolved

### themes.md
The story's deeper layer:
- **Central theme** — the core question or argument
- **Thematic threads** — recurring ideas woven through the narrative
- **Motifs & symbols** — concrete images or objects that carry thematic weight
- **Chapter tracking** — where each thread surfaces and how it develops

### style-guide.md
The story's voice:
- **Sample paragraphs** — 2-3 passages that represent the target prose style
- **Vocabulary preferences** — words to favor, words to avoid
- **Sentence rhythm** — short and punchy, long and flowing, varied
- **POV rules** — close third, first person, omniscient, etc.
- **Tense** — past or present
- **Dialect or register notes** — character-specific speech, era-appropriate language

## Continuity Rules

- **The reference docs are canon.** Never contradict them without discussing the change first.
- When uncertain about an established fact (character's eye color, city name, timeline), check the reference docs before writing.
- If a chapter introduces something that conflicts with existing canon, flag it to the author rather than silently overwriting.
- Keep a consistent internal timeline. If Chapter 5 says three days have passed since the inciting event, Chapter 8 shouldn't claim it was a week.

## Revision Workflow

When revising an existing chapter:
1. Read the current draft fully before making changes
2. Preserve the author's voice — enhance it, don't replace it
3. Focus on the specific revision goals (pacing, dialogue, description, etc.)
4. Do not rewrite sections that are already working well
5. After revisions, update the chapter's metadata status

## Git Workflow

Commit messages follow this format:
```
<type>: chapter NN - <short description>
```

Types:
- `draft` — first draft of a chapter
- `revise` — revision pass on an existing chapter
- `outline` — changes to plot outline or story structure
- `reference` — updates to character sheets, world bible, or other reference docs
- `style` — prose polish, line edits, voice adjustments

Examples:
```
draft: chapter 07 - the siege begins
revise: chapter 03 - tighten dialogue in tavern scene
reference: add character sheet for commander voss
outline: restructure act two turning point
```

### Branching (Optional)

For experimental rewrites or alternate plot directions:
- `alt/chapter-NN-description` — alternate version of a chapter
- `experiment/description` — exploratory writing that may or may not be kept
