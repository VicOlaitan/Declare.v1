from dataclasses import dataclass, field
from config import (
    DEFAULT_AI_DELAY, DEFAULT_PEEK_REVEAL_TIME, DEFAULT_PEEK_PHASE_SECONDS,
    DEFAULT_ANIMATIONS_ENABLED, DEFAULT_SHOW_OWN_SCORE, DEFAULT_SHOW_KNOWN_MARKER,
    DEFAULT_SHOW_GAME_LOG, DEFAULT_CONFIRM_DECLARE, DEFAULT_AI_DIFFICULTY,
    DEFAULT_LAYOUT_MODE,
)


@dataclass
class GameSettings:
    ai_delay: float = DEFAULT_AI_DELAY
    peek_reveal_time: float = DEFAULT_PEEK_REVEAL_TIME
    peek_phase_seconds: float = DEFAULT_PEEK_PHASE_SECONDS
    animations_enabled: bool = DEFAULT_ANIMATIONS_ENABLED
    show_own_score: bool = DEFAULT_SHOW_OWN_SCORE
    show_known_marker: bool = DEFAULT_SHOW_KNOWN_MARKER
    show_game_log: bool = DEFAULT_SHOW_GAME_LOG
    confirm_declare: bool = DEFAULT_CONFIRM_DECLARE
    layout_mode: str = DEFAULT_LAYOUT_MODE
    ai_difficulties: dict = field(default_factory=dict)

    def effective_anim_duration(self, base_duration: float) -> float:
        if not self.animations_enabled:
            return 0.01
        return base_duration

    def get_ai_delay_for(self, seat_index: int) -> float:
        return self.ai_difficulties.get(seat_index, DEFAULT_AI_DIFFICULTY)
