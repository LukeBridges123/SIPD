"""
UI Package for SIPD.

Provides theme, components, and screen implementations.
"""

from .theme import UITheme, DEFAULT_THEME
from .components import Button, ParameterControl, StrategyWeightControl
from .simulator_ui import SimulatorUI
from .stats_ui import StatsUI
from .mix_ui import MixUI
from .matchup_ui import MatchupUI
from .payoff_ui import PayoffUI

__all__ = [
    'UITheme', 'DEFAULT_THEME',
    'Button', 'ParameterControl', 'StrategyWeightControl',
    'SimulatorUI', 'StatsUI', 'MixUI', 'MatchupUI', 'PayoffUI'
]
