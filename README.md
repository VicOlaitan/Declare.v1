# Declare

A casino-style card game of memory, strategy, and bluffing. Built with Python + Pygame.

---

## About the Game

Declare is a strategic card game where players race to get rid of their high-value cards while sabotaging their opponents. The game combines memory, risk assessment, and tactical decision-making into an engaging casino experience. Each player starts with a hand of cards, and through smart play and special powers, they try to minimize their remaining card values.

The game features unique mechanics like reactive pairing — when any player plays a card, opponents have a brief window to respond with matching cards from their known cards. Powerful card ranks grant abilities like peeking at hidden cards, swapping positions with opponents, or even skipping your turn entirely. Red Kings are especially valuable as they're worth zero points, while Black Kings can be paired automatically.

Play against configurable AI opponents that adapt their strategy based on difficulty level, making every game a fresh challenge whether you're a casual player or a card game enthusiast.

---

## Features

- 2-4 player support with human and AI opponents
- Configurable AI difficulty (Easy/Medium/Hard)
- Reactive pairing interrupt mechanic — react to other players' plays
- Multiple card layout modes: Line, Square, and Free-form drag
- In-game settings menu with numerous customization options
- Casino felt aesthetic with animated card backs
- Peek phase memorization at game start
- Swap position tracking with visual highlight
- Comprehensive game log for move tracking

---

## Screenshots

```
+------------------------------------------+
|                                          |
|      [SCREENSHOTS COMING SOON]           |
|                                          |
|   The game features a casino-style       |
|   green felt table with elegant card     |
|   designs and smooth animations.         |
|                                          |
+------------------------------------------+
```

---

## Quick Start

```bash
pip install pygame>=2.5.0
python -m declare.main
```

or simply:

```bash
python main.py
```

---

## Controls

| Input | Action |
|-------|--------|
| Mouse click on card slots | Select and play cards |
| Number keys (1-9) | Select action buttons |
| P | Peek at cards (when available) |
| S | Open settings menu |
| Escape | Cancel targeting mode |
| Space / Enter | Confirm actions |

---

## How to Play

### Goal
End with the lowest sum of unpaired card values. If you get rid of all your cards, you automatically win.

### Card Values

| Card | Value |
|------|-------|
| Ace | 1 |
| 2-10 | Face value |
| Jack | 11 |
| Queen | 12 |
| Red King | 13 |
| Black King | 0 (zero!) |

### Setup
1. Each player receives 4 cards face-down (configurable: 2-6 cards)
2. Players peek at their bottom cards (configurable: 0-4 cards, capped at hand size)
3. Remaining cards form the draw pile

### Turn Flow
1. **Draw** — Draw one card from the pile
2. **Decide** — Choose an action:
   - Play a card to the table
   - Use a power (if your drawn card has one)
   - Pair cards from your hand
   - Discard a card
   - Declare (end the game early)
3. **Resolve** — Execute the chosen action
4. **End Turn** — Pass to the next player

### Pairing
Same-rank cards can be paired (maximum 2 cards per pair). When you pair an opponent's card, they must take one of your cards in exchange. All paired cards go to the discard pile.

### Reactive Pairing
When ANY player plays a card, all other players have a brief window (~3 seconds, configurable) to reactively drop a matching card from their known cards. This is a key strategic mechanic — watch your opponents' plays carefully! Wrong guesses result in drawing a penalty card.

### Powers

| Card Rank | Power | Description |
|-----------|-------|-------------|
| 7, 8 | Peek Own | Briefly see one of your face-down cards |
| 9, 10 | Peek Opponent | Briefly see one of any opponent's face-down cards |
| Jack | Skip | Draw but play no card (turn ends) |
| Queen | Unseen Swap | Exchange a card with an opponent without revealing it |
| Red King | Seen Swap | Show the card you're swapping before exchanging |
| Black King | Zero Value | Automatically paired if possible, otherwise plays as 0-point card |

### Declaration
On your turn, you may declare when your estimated hand total is 10 or less. All players reveal their hands and sum their values. The player with the lowest sum wins the game.

---

## Settings

| Setting | Options | Description |
|---------|---------|-------------|
| AI Delay | Fast / Normal / Slow | How long AI opponents "think" before acting |
| Peek Duration | Short / Normal / Long | How long peeked cards remain visible |
| Peek Phase | 3s / 5s / 10s / Infinite | Time to view your starting cards |
| Animations | ON / OFF | Enable or disable card animations |
| Show Own Score | Yes / No | Display your running score during play |
| Show Known Marker | Yes / No | Show gold triangle on known card backs |
| Show Game Log | Yes / No | Display recent game actions |
| Confirm Declare | Yes / No | Require confirmation before declaring |
| AI Difficulty | Easy / Medium / Hard | Per-player AI skill level |
| Layout Mode | Line / Square / Free | How cards are arranged on the table |
| Cards Per Hand | 2 / 3 / 4 / 5 / 6 | Number of cards each player starts with |
| Peek Cards | 0 / 1 / 2 / 3 / 4 | How many cards you peek at game start (capped at hand size) |
| Reaction Window | 2s / 3s / 5s | Time window to reactively pair to played cards |

---

## Game State Machine

```
                           MENU
                             |
                             v
                          SETUP
                             |
                             v
                      +-----------+
                      | PEEK_PHASE|
                      +-----------+
                             |
                             v
               +-------------+-------------+
               |                           |
               v                           v
          TURN_START                   REACTION_WINDOW
               |                           |
               v                           |
             DRAW                          |
               |                           |
               v                           |
           DECIDE                          |
               |                           |
               v                           |
       +-------+-------+                   |
       |       |       |                   |
       v       v       v                   |
   PLAY_CARD USE_POWER PAIRING             |
       |       |       |                   |
       +-------+-------+                   |
               |                           |
               v                           |
        POWER_RESOLVE                      |
               |                           |
               v                           |
          PAIR_CHECK                       |
               |                           |
               v                           |
          TURN_END                         |
               |                           |
               +----+  +-------------------+
               |    |  |
               v    v  v
           GAME_OVER
```

The REACTION_WINDOW state can interrupt during any player's turn action, allowing reactive pairing before the turn concludes.

---

## Architecture

```
declare/
├── game/                    # Core game logic
│   ├── game_manager.py      # Main game orchestration and state machine
│   ├── player.py            # Player class and hand management
│   ├── ai.py                # AI opponent decision making
│   └── rules.py             # Game rules and validation
├── ui/                      # Rendering and screens
│   ├── renderer.py          # Main rendering engine
│   ├── screens.py           # Menu, setup, and game screens
│   ├── settings.py          # Settings UI and persistence
│   └── animations.py        # Card animations and transitions
├── config.py                # Constants, colors, dimensions, and settings
├── main.py                  # Game loop and event handling
└── README.md                # This file
```

### Key Modules

- **game_manager.py** — Orchestrates game flow, handles state transitions, and coordinates between players
- **player.py** — Manages player state, hand cards, known cards, and score tracking
- **ai.py** — Implements AI decision logic with difficulty-based strategy selection
- **rules.py** — Validates moves, calculates scores, and enforces game rules
- **renderer.py** — Draws all game elements including cards, table, and UI elements
- **screens.py** — Manages different game screens (menu, setup, gameplay, game over)
- **settings.py** — Handles configuration persistence and settings UI
- **animations.py** — Card movement, flipping, and special effect animations
- **config.py** — Central configuration for colors, dimensions, timings, and defaults

---

## Roadmap

- [x] Reactive pairing interrupt mechanic
- [x] Configurable hand size and peek count
- [x] Swap position tracking with brief highlight
- [ ] Web demo via Pygbag + GitHub Pages
- [ ] Additional card back designs
- [ ] Sound effects and ambient casino audio
- [ ] Multi-round tournament mode

---

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Links

GitHub Repository: https://github.com/jucish2019-a11y/declare