# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SIPD (Spatial Iterated Prisoner's Dilemma) is a Python cellular automaton simulation of the spatial iterated prisoner's dilemma. Each cell contains a strategy, plays the prisoner's dilemma against its 8 neighbors, and adopts the most successful neighbor's strategy in the next generation.

## Commands

```bash
# Run the GUI application
python3 main.py

# Run basic test simulation
python3 test.py

# Web/Android packaging (requires pygbag)
pygbag main.py
```

## Controls

- **SPACE**: Advance to next generation
- **ESC**: Quit

## Architecture

**Three core modules:**

- `strategies.py` - Game logic and strategy definitions
  - `Game` class with payoff matrix (standard prisoner's dilemma)
  - `Strategy` class wrapping callable strategy functions
  - `compute_matchup_table()` pre-computes all strategy pairs
  - Available strategies: Always Cooperate, Always Defect, Tit-for-Tat, Pavlov, Revenger, Tit-for-Two-Tats

- `grid.py` - 2D grid cellular automaton with wrapping edges
  - `Grid.update_grid()` is the core evolution step
  - Cells copy the strategy of their highest-scoring neighbor (ties favor current strategy)

- `main.py` - Pygame visualization
  - Configurable parameters: grid size (`n, m`), rounds, noise, mutation_rate (line 18-23)
  - Color mapping for strategies defined in `colors` dict

## Adding a New Strategy

1. Define strategy function in `strategies.py` (takes history, returns 'C' or 'D')
2. Create `Strategy` object with name and function
3. Add to `strategies` list in `main.py`
4. Add color mapping in `colors` dict in `main.py`

## Game Parameters (in main.py)

- `n, m` - Grid dimensions (default: 50x50)
- `rounds` - IPD rounds per matchup (default: 1000)
- `noise` - Probability of action flip during play (0-1)
- `mutation_rate` - Probability of random strategy change per generation (0-1)
