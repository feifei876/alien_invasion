class Settings:
    def __init__(self):
        # 屏幕设置
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # 飞船设置
        self.ship_limit = 3

        # 子弹设置
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullet_allowed = 3

        # 外星人设置
        self.fleet_drop_speed = 5

        # 音量设置
        self.shoot_volume = 0.3
        self.explosion_volume = 0.5
        self.background_volume = 0.2
        self.sound_enabled = True

        # 速度提升系数
        self.speedup_scale = 1.2
        self.ship_speedup_scale = 1.1  # 飞船速度提升稍慢
        self.score_scale = 1.5

        self.initialize_dynamic_settings()
        self.set_difficulty('normal')

    def initialize_dynamic_settings(self):
        '''初始化动态设置'''
        self.ship_speed = 3.0      # 提高基础速度
        self.bullet_speed = 5.0
        self.alien_speed = 1.2
        self.fleet_direction = 1
        self.alien_points = 50

    def set_difficulty(self, difficulty):
        '''设置难度'''
        if difficulty == 'easy':
            self.ship_speed = 4.0
            self.bullet_speed = 6.0
            self.alien_speed = 0.9
            self.fleet_drop_speed = 3
            self.ship_limit = 5
            self.alien_points = 30
        elif difficulty == 'hard':
            self.ship_speed = 2.5
            self.bullet_speed = 4.0
            self.alien_speed = 1.8
            self.fleet_drop_speed = 8
            self.ship_limit = 2
            self.alien_points = 100
        else:  # normal
            self.ship_speed = 3.0
            self.bullet_speed = 5.0
            self.alien_speed = 1.2
            self.fleet_drop_speed = 5
            self.ship_limit = 3
            self.alien_points = 50

    def increase_speed(self):
        '''提升速度'''
        self.ship_speed *= self.ship_speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)