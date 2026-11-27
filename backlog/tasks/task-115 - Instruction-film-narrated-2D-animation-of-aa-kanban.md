---
id: TASK-115
title: 'Instruction film: narrated 2D animation of aa-kanban'
status: To Do
assignee: []
created_date: '2026-11-07 18:02'
updated_date: '2026-11-07 18:02'
labels:
  - docs
  - video
dependencies: []
priority: low
ordinal: 129000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make a ~75 s narrated 2D instruction film for aa-kanban with the user-level story-animator skill (C:\Users\mbroe\.claude\skills\story-animator): every frame drawn in code (Remotion), ElevenLabs voice, music and sound effects. Proposal approved in outline on 2026-11-07; the user still has to reply 'go' or change the choices below before any credits are spent.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ElevenLabs is available (connector or ELEVENLABS_API_KEY set by the user) and the user confirmed the credit cost (~3,000) before generation
- [ ] #2 Narration and beat list confirmed by the user (defaults or their changes)
- [ ] #3 Look frame rendered and shown before the full film is built
- [ ] #4 Rendered out/film.mp4 (H.264 + AAC) checked with ffprobe: size, length, voice starts ~0.5 s, background 12-18 dB under the voice
- [ ] #5 Film stored outside the plugin repo; user asked to watch and listen once
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Story

- **Spine:** Bolt's request ("Fix my Nyx") keeps getting lost in Discord chat. He puts it on the Kanban board as a card, where it is picked up, discussed and moved. Weeks later one search finds it, marked Done.
- **Token:** Bolt's yellow note. It becomes card #42 and ends with a green Done stamp.
- **Character:** Bolt, a small repair drone (big eyes, one antenna).

## Narration (English, ~150 words) and beats

| # | Line | Picture | Camera |
|---|---|---|---|
| 1 | In a busy corporation, requests fly everywhere... and get lost. | Space full of drifting chat bubbles; one yellow note among them | Slow drift right |
| 2 | Meet Bolt, a small repair drone with one yellow note: "Fix my Nyx." | Bolt holding the note | Push in to Bolt |
| 3 | He used to shout it in chat. Nobody saw it twice. | His bubble scrolls up and away | Hold |
| 4 | So today, Bolt opens the Kanban board. | Board slides in: To Do, In Progress, Done | Pull back |
| 5 | He presses Submit Ticket... and his note becomes a card. | Note folds into card #42 in To Do | Push in to the card |
| 6 | A manager picks it up, adds a label, and assigns a pilot. | Label chip and avatar badge pop onto the card | Hold |
| 7 | A Discord thread opens, so everyone on the card can talk in one place. | A line links the card to a thread window | Drift right |
| 8 | Comments, pictures, questions... all stay with the card. | Comments stack under the card | Hold |
| 9 | When the card moves, Bolt gets a message. He never has to ask. | Card glides to In Progress; Bolt's antenna lights up (ping) | Follow the card |
| 10 | Weeks later... which card was it again? | Board full of cards; Bolt looks puzzled | Pull back |
| 11 | He types "Nyx" in the search box... and there it is, on any board. | Search bar; "Nyx" highlighted in the result | Push in to the search bar |
| 12 | One click, and the card opens. Done. | Card opens; green Done stamp | Push in to the stamp |
| 13 | One board. Every request found. That's Kanban. | Pull back: many drones with cards; title "aa-kanban" | Slow pull back |

## Style and sound

- **Look:** soft flat cartoon in space colours (deep blue with warm orange accents). The board is a simplified drawing, not a screenshot. No EVE or CCP logos.
- **Voice:** warm, clear, calm storytelling pace; English subtitles.
- **Music:** light, curious electronic tune. Busy during the lost requests (1-3), brighter from the board (4), small climax at the search hit (11-12), calm ending.
- **Sound effects (5):** paper fold, pop on the label, ping on the message, typing in the search bar, stamp.

## Default choices (user may change)

1. Language: English (alternative: Dutch).
2. Shape: 16:9 (alternative: 9:16).
3. Length: ~75 s (alternative: 45 s without beats 7-8).
4. Location: `G:\My Drive\Workbench 001\media\kanban-film`, outside the plugin repo.

## Cost (ElevenLabs, estimate)

| Item | Credits |
|---|---|
| Narration, 2 takes | ~1,800 |
| Music, 1 take | ~1,100 |
| Sound effects | ~85 |
| **Total** | **~3,000** |

## Notes

- On Windows, replace `python3` with `python` and `.venv/bin/` with `.venv\Scripts\` in the skill's commands.
- Present on this PC (2026-11-07): Node 22, ffmpeg 9, Python 3.15. ElevenLabs was not yet connected.
- **2026-11-27: redo needed.** aa-kanban has since moved to the new React SPA UI; the user wants this
  instruction film reworked to match it before any further work on the story/beats above.
<!-- SECTION:PLAN:END -->
