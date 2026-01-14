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
- **S**: Toggle stats view (or click Stats/Grid button)
- **M**: Toggle mix view (or click Mix/Grid button)
- **U**: Toggle matchup view (or click Matchup/Grid button)
- **Y**: Toggle payoff view (or click Payoff/Grid button)
- **ESC**: Quit (or return to grid from other views)
- **Double-click parameter values**: Edit directly

## Architecture

The codebase is organized into modular components:

### Core Modules

- **`strategies.py`** - Game logic and strategy definitions
  - `Game` class with payoff matrix (standard prisoner's dilemma)
  - `Strategy` class wrapping callable strategy functions
  - `compute_matchup_table()` pre-computes all strategy pairs
  - Available strategies: Always Cooperate, Always Defect, Tit-for-Tat, Pavlov, Revenger, Tit-for-Two-Tats, Generous, Prober

- **`grid.py`** - 2D grid cellular automaton with wrapping edges
  - `Grid.update_grid()` is the core evolution step
  - `Grid.populate_randomly(weights)` initializes grid with optional weighted distribution
  - Cells copy the strategy of their highest-scoring neighbor (ties favor current strategy)

- **`main.py`** - Application entry point and game state
  - `SimulationState` class manages simulation parameters, board state, census history, strategy weights, and payoff matrix
  - `main()` async function contains event loop with screen switching (simulator/stats/mix/matchup/payoff)
  - Delegates rendering to UI modules (`SimulatorUI`, `StatsUI`, `MixUI`, `MatchupUI`, `PayoffUI`)

### UI Package (`ui/`)

Modular UI components for visualization and interaction:

- **`ui/theme.py`** - Centralized styling
  - `UITheme` class with colors, fonts, layout constants
  - `DEFAULT_THEME` instance

- **`ui/components.py`** - Reusable UI widgets
  - `Button` - Clickable button with hover states
  - `ParameterControl` - Parameter adjustment with +/- buttons and text input
  - `StrategyWeightControl` - Slider control for adjusting strategy weights

- **`ui/simulator_ui.py`** - Main simulation screen
  - `SimulatorUI` class handles all rendering and UI interaction
  - Grid visualization, sidebar legend, parameter panel, control buttons

- **`ui/stats_ui.py`** - Statistics/census view
  - `StatsUI` class displays population analytics
  - Census bars showing current percentage of each strategy
  - Time series chart tracking strategy proportions over generations
  - Layout adapts dynamically to number of strategies

- **`ui/mix_ui.py`** - Strategy mix configuration view
  - `MixUI` class for configuring initial strategy distribution
  - Slider controls for each strategy's weight (0-10 range)
  - Weights determine relative probability; percentages shown for clarity
  - "Reset to Equal" button restores uniform distribution

- **`ui/matchup_ui.py`** - Strategy matchup table view
  - `MatchupUI` class displays how each strategy performs against every other
  - Color-coded grid: green (high score) to red (low score)
  - Hover over cells to see exact scores
  - Helps visualize which strategies dominate others

- **`ui/payoff_ui.py`** - Payoff matrix editor view
  - `PayoffUI` class allows editing the game's payoff matrix
  - 2x2 grid with +/- buttons for each value (Player 1 and Player 2 payoffs)
  - "Reset to Default" button restores standard Prisoner's Dilemma values
  - Supports experimenting with different game types (Chicken, Stag Hunt, etc.)

- **`ui/__init__.py`** - Clean import interface

## Adding a New Strategy

1. Define strategy function in `strategies.py` (takes history, returns 'C' or 'D')
2. Create `Strategy` object with name and function
3. Add to `strategies` list in `SimulationState.__init__()` in `main.py`
4. Add color mapping in `SimulationState.colors` dict in `main.py`

## Game Parameters

Parameters are managed by `SimulationState` in `main.py`:

- `grid_rows`, `grid_cols` - Grid dimensions (default: 50x50)
- `rounds` - IPD rounds per match (default: 100)
- `matches` - Number of matches played between each strategy pair; results are averaged (default: 10)
- `noise` - Probability of action flip during play (0-1)
- `mutation_rate` - Probability of random strategy change per generation (0-1)

All parameters are editable via the UI (sidebar panel with +/- buttons or double-click to type).

## UI Customization

To modify appearance:
- Edit colors, fonts, or layout in `ui/theme.py`
- Button styles and component behavior in `ui/components.py`
- Rendering logic in `ui/simulator_ui.py`

## Multiple Views

The application supports five views:
- **Simulator view** - Main grid visualization with controls and parameters
- **Stats view** (S key or Stats button) - Population statistics with census bars and time series chart
- **Mix view** (M key or Mix button) - Configure initial strategy distribution before starting
- **Matchup view** (U key or Matchup button) - Visualize the strategy matchup table
- **Payoff view** (Y key or Payoff button) - Edit the game's payoff matrix

Census data is tracked in `SimulationState.census_history` (list of `{strategy_name: percentage}` dicts), recorded each generation via `record_census()`.

## Strategy Mix

The mix view allows configuring the initial distribution of strategies:
- Each strategy has a weight slider (0-10 range)
- Weights determine relative probability (e.g., weight 3 vs 1 means 3x more likely)
- Set weight to 0 to exclude a strategy entirely
- Press R or N after configuring to apply the new mix

Weights are stored in `SimulationState.strategy_weights` (dict of `{strategy_name: weight}`) and passed to `Grid.populate_randomly()` on simulation start.

## Matchup Table

The matchup view visualizes strategy performance in a color-coded grid:
- Each cell shows how the row strategy scores against the column strategy
- Colors range from green (high score/good) through grey (median) to red (low score/bad)
- Hover over any cell to see the exact numerical score
- The table is computed at simulation start based on rounds, matches, and noise parameters
- Useful for understanding which strategies dominate others and identifying rock-paper-scissors dynamics

The matchup table is stored in `Grid.matchups` as a 2D list where `matchups[i][j]` is the average score strategy i receives when playing against strategy j.

## Payoff Matrix

The payoff view allows customizing the game's payoff matrix:
- Matrix format: `matrix[row][col] = (player1_payoff, player2_payoff)` where row is P1's move, col is P2's move
- Row/Col 0 = Defect, Row/Col 1 = Cooperate
- Default is standard Prisoner's Dilemma: T=5, R=3, P=1, S=0 (Temptation > Reward > Punishment > Sucker)
- Press R or N after editing to apply changes to the simulation

The payoff matrix is stored in `SimulationState.payoff_matrix` and used to create a `Game` instance via `get_game()`.

Example game types by payoff relationships:
- **Prisoner's Dilemma**: T > R > P > S (default: 5, 3, 1, 0)
- **Chicken/Hawk-Dove**: T > R > S > P
- **Stag Hunt**: R > T > P > S
- **Deadlock**: T > P > R > S

## Future Extensions

The architecture supports additional screens/views:
- UI components are reusable across different screens
- Theme system allows easy visual customization
- New views can follow the `StatsUI`/`MixUI`/`MatchupUI`/`PayoffUI` pattern (class with `draw()` method)
- Strategy weights automatically adapt when new strategies are added
