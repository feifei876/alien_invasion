import json
from pathlib import Path

class GameStats:
    '''跟踪游戏的统计信息'''

    def __init__(self, ai_game):
        '''初始化统计信息'''
        self.settings = ai_game.settings
        self.game = ai_game  #  保存游戏实例引用
        self.reset_stats()

        # 从文件加载所有难度的最高分
        self.high_scores = self._load_high_scores()
        # 设置当前难度的最高分
        self.high_score = self._get_current_high_score()

    def reset_stats(self):
        '''初始化在游戏运行期间可能变化的统计信息'''
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def _load_high_scores(self):
        '''从文件加载所有难度的最高分'''
        path = Path('high_scores.json')
        default_scores = {'easy': 0, 'normal': 0, 'hard': 0}

        if path.exists():
            try:
                contents = path.read_text()
                scores = json.loads(contents)
                # 确保所有难度都有记录
                for difficulty in default_scores:
                    if difficulty not in scores:
                        scores[difficulty] = 0
                return scores
            except (json.JSONDecodeError, FileNotFoundError):
                return default_scores
        return default_scores

    def _get_current_high_score(self):
        '''获取当前难度的最高分'''
        if hasattr(self.game, 'current_difficulty'):
            return self.high_scores.get(self.game.current_difficulty, 0)
        return self.high_scores.get('normal', 0)  # 默认普通难度

    def save_high_scores(self):
        '''将所有难度的最高分保存到文件'''
        path = Path('high_scores.json')
        try:
            contents = json.dumps(self.high_scores)
            path.write_text(contents)
        except Exception as e:
            print(f"保存最高分时出错: {e}")

    def check_high_score(self):
        '''检查是否诞生了新的最高分（当前难度）'''
        if self.score > self._get_current_high_score():
            # 更新当前难度的最高分
            current_diff = getattr(self.game, 'current_difficulty', 'normal')
            self.high_scores[current_diff] = self.score
            self.high_score = self.score
            self.save_high_scores()  # 立即保存
            return True
        return False