class Settings:
    '''存储游戏《外星人入侵》中所有设置的类'''
    def __init__(self):
        '''初始化游戏的静态设置'''
        # 屏幕设置
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230 ,230)

        # 飞船的设置
        self.ship_limit = 3

        # 子弹设置
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullet_allowed = 3

        # 外星人设置
        self.fleet_drop_speed = 5

        # 音量设置 (0.0 - 1.0)
        self.shoot_volume = 0.3      # 射击声音量 30%
        self.explosion_volume = 0.5   # 爆炸声音量 50%
        self.background_volume = 0.2  # 背景音乐音量 20%
        self.sound_enabled = True     # 音效开关

        # 以什么速度加快游戏的节奏
        self.speedup_scale = 1.2
        # 外星人分数的提高速度
        self.score_scale = 1.5

        # 初始化难度设置
        self.initialize_dynamic_settings()
        self.set_difficulty('normal')  # 默认普通难度

    def initialize_dynamic_settings(self):
        '''初始化随游戏进行而变化的设置'''
        self.ship_speed = 1.5
        self.bullet_speed = 2.5
        self.alien_speed = 1.0
        self.fleet_direction = 1
        self.alien_points = 50

    def set_difficulty(self, difficulty):
        '''根据选择的难度设置初始值'''
        if difficulty == 'easy':
            self.ship_speed = 2.0  # 飞船更快
            self.bullet_speed = 3.0  # 子弹更快
            self.alien_speed = 0.8  # 外星人更慢
            self.fleet_drop_speed = 3  # 下移更慢
            self.ship_limit = 5  # 更多生命
            self.alien_points = 30  # 分数更低
        elif difficulty == 'hard':
            self.ship_speed = 1.0  # 飞船更慢
            self.bullet_speed = 2.0  # 子弹更慢
            self.alien_speed = 1.5  # 外星人更快
            self.fleet_drop_speed = 8  # 下移更快
            self.ship_limit = 2  # 更少生命
            self.alien_points = 100  # 分数更高
        else:  # normal
            self.ship_speed = 1.5
            self.bullet_speed = 2.5
            self.alien_speed = 1.0
            self.fleet_drop_speed = 5
            self.ship_limit = 3
            self.alien_points = 50

    def increase_speed(self):
        '''提高速度设置的值和外星人分数'''
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
