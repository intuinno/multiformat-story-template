# Character Visual Prompts

Each file defines one character's visual identity for image generation.
These fragments are composed with style and setting prompts to build complete panel prompts.

## File Format

```markdown
# [Character Name]

## Core Appearance
[Unchanging physical traits: face, body, hair, distinguishing features.
 Written as prompt-ready description.]

## Default Outfit
[Their standard clothing/armor/gear.]

## Alternate Outfits
[Named outfit variations for different story phases or scenes.]

## Expression Library
[Key expressions with prompt-ready descriptions:
 - neutral, angry, afraid, determined, grief, joy, etc.]

## Pose Notes
[How this character carries themselves: posture, gestures, body language.]
```

## Consistency Rule

When generating any image containing this character, ALWAYS include the Core Appearance fragment.
Never describe the character from memory — always pull from this file.
