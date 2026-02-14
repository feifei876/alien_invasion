import json
from pathlib import Path


class GameStats:
    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.game = ai_game
        self.reset_stats()
        self.high_scores = self._load_high_scores()
        self.high_score = self._get_current_high_score()

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def _load_high_scores(self):
        path = Path('high_scores.json')
        default = {'easy': 0, 'normal': 0, 'hard': 0}

        if not path.exists():
            return default

        try:
            scores = json.loads(path.read_text())
            return {d: scores.get(d, 0) for d in default}
        except:
            return default

    def _get_current_high_score(self):
        diff = getattr(self.game, 'current_difficulty', 'normal')
        return self.high_scores.get(diff, 0)

    def save_high_scores(self):
        try:
            Path('high_scores.json').write_text(json.dumps(self.high_scores))
        except:
            pass

    def check_high_score(self):
        current = self._get_current_high_score()
        if self.score > current:
            diff = getattr(self.game, 'current_difficulty', 'normal')
            self.high_scores[diff] = self.score
            self.high_score = self.score
            self.save_high_scores()
            return True
        return False