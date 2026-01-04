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
- **P**: Toggle play/pause (auto-step)
- **R**: Restart with same seed
- **N**: Restart with new seed
- **ESC**: Quit
- **Double-click parameter values**: Edit directly

## Architecture

The codebase is organized into modular components:

### Core Modules

- **`strategies.py`** - Game logic and strategy definitions
  - `Game` class with payoff matrix (standard prisoner's dilemma)
  - `Strategy` class wrapping callable strategy functions
  - `compute_matchup_table()` pre-computes all strategy pairs
  - Available strategies: Always Cooperate, Always Defect, Tit-for-Tat, Pavlov, Revenger, Tit-for-Two-Tats

- **`grid.py`** - 2D grid cellular automaton with wrapping edges
  - `Grid.update_grid()` is the core evolution step
  - Cells copy the strategy of their highest-scoring neighbor (ties favor current strategy)

- **`main.py`** - Application entry point and game state
  - `SimulationState` class manages simulation parameters and board state
  - `main()` async function contains event loop
  - Delegates rendering to UI module

### UI Package (`ui/`)

Modular UI components for visualization and interaction:

- **`ui/theme.py`** - Centralized styling
  - `UITheme` class with colors, fonts, layout constants
  - `DEFAULT_THEME` instance

- **`ui/components.py`** - Reusable UI widgets
  - `Button` - Clickable button with hover states
  - `ParameterControl` - Parameter adjustment with +/- buttons and text input

- **`ui/simulator_ui.py`** - Main simulation screen
  - `SimulatorUI` class handles all rendering and UI interaction
  - Grid visualization, sidebar legend, parameter panel, control buttons

- **`ui/__init__.py`** - Clean import interface

## Adding a New Strategy

1. Define strategy function in `strategies.py` (takes history, returns 'C' or 'D')
2. Create `Strategy` object with name and function
3. Add to `strategies` list in `SimulationState.__init__()` in `main.py`
4. Add color mapping in `SimulationState.colors` dict in `main.py`

## Game Parameters

Parameters are managed by `SimulationState` in `main.py`:

- `grid_rows`, `grid_cols` - Grid dimensions (default: 50x50)
- `rounds` - IPD rounds per matchup (default: 1000)
- `noise` - Probability of action flip during play (0-1)
- `mutation_rate` - Probability of random strategy change per generation (0-1)

All parameters are editable via the UI (sidebar panel with +/- buttons or double-click to type).

## UI Customization

To modify appearance:
- Edit colors, fonts, or layout in `ui/theme.py`
- Button styles and component behavior in `ui/components.py`
- Rendering logic in `ui/simulator_ui.py`

## Future Extensions

The architecture supports multiple screens/views:
- UI components are reusable across different screens
- Theme system allows easy visual customization
- `SimulatorUI` can be wrapped in a Screen abstraction when needed
