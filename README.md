# Through the Mind

Play Game Here: https://zvythrox.itch.io/through-the-mind


A top-down pixel game about generalized anxiety disorder. You play as Zee, an alien, through **5 levels** (one school day each).
Every level the anxiety gets worse. Each task switches into a different kind of mini-game

## Run
```
pip install pygame
python main.py
```

## Folder layout (put your art here)
```
main.py  game.py  world.py  pixel.py  ui.py  minigames.py  play.py
assets/
  title.png                      <- your title art (the "Through the Mind" image)
  miku/Idle/rotations/*.png      <- unzip Miku.zip into assets/miku/
  anika/   asher/   estella/   lamar/   noah/    <- unzip each zip into its folder
```
Each zip already contains `Idle/rotations/east.png ... south-west.png`, so unzipping it into `assets/<name>/` is enough.
If a folder is missing the game still runs and shows a placeholder figure.

## Controls
WASD / arrows move - E interact - Q or the Stats tab for levels - Esc pause - 1-9 / arrows + Enter in dialogue.

## Levels (symptoms stack up)
1. A Normal Day: muscle tension, constant low worry that drains energy
2. The What-Ifs: racing thoughts, decision paralysis, reassurance seeking
3. Under Pressure: shaky hands, racing heart, irritability, restless sleep (group presentation)
4. Tunnel Vision: panic attacks, dizziness, tunnel vision, avoidance of crowds
5. The Big Test: constant dread, frequent panic, exhaustion (exam)

## Task -> mini-game
- Classwork / exam: side-view arcade (catch answers, dodge worry clouds)
- Group presentation: steady-voice balance meter
- Homework: quiz with a "re-check it?" loop
- Lunch: timed choice with a growing thought spiral
- Counselor: worry-sorting card puzzle (can control / can't control)
- Bathroom stall and panic attacks: breathing rhythm game
- Bed: top-down "racing thoughts" defender

## Tuning
- `game.py`: `LEVELS` (severity `sev` per level), `WIN` goals, panic chances in `maybe_panic`.
- `ui.py`: palette (taken from your title art), `HERO` (which character you play).
- `world.py`: rooms and where each NPC stands.
