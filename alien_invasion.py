import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    def __init__(self):
        '''初始化游戏并创建游戏资源'''
        pygame.init()
        pygame.mixer.init()

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption('Alien Invasion')

        self._load_sounds()

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()
        self.game_active = False
        self.current_difficulty = 'normal'
        self.show_help = False

        # 创建按钮
        self.play_button = Button(self, 'Play')
        self.help_button = Button(self, 'How to Play')
        self._create_difficulty_buttons()
        self._position_help_button()

    def _position_help_button(self):
        '''设置玩法说明按钮的位置'''
        center_x = self.screen.get_rect().centerx
        center_y = self.screen.get_rect().centery
        self.help_button.rect.center = (center_x, center_y + 120)
        self.help_button.msg_image_rect.center = self.help_button.rect.center

    def _load_sounds(self):
        '''加载所有声音文件'''
        self.shoot_sound = None
        self.explosion_sound = None
        try:
            self.shoot_sound = pygame.mixer.Sound('sounds/shoot.wav')
            self.shoot_sound.set_volume(self.settings.shoot_volume)
            self.explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')
            self.explosion_sound.set_volume(self.settings.explosion_volume)
            pygame.mixer.music.load('sounds/background.mp3')
            pygame.mixer.music.set_volume(self.settings.background_volume)
        except:
            pass  # 静默失败

    def _play_sound(self, sound):
        '''播放声音'''
        if self.settings.sound_enabled and sound:
            sound.play()

    def run_game(self):
        '''开始游戏的主循环'''
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        '''响应按键和鼠标事件'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_difficulty_buttons(mouse_pos)
                self._check_help_button(mouse_pos)

    def _quit_game(self):
        '''退出游戏'''
        pygame.mixer.music.stop()
        self.stats.save_high_scores()
        sys.exit()

    def _check_help_button(self, mouse_pos):
        '''检查是否点击说明按钮'''
        if not self.game_active and self.help_button.rect.collidepoint(mouse_pos):
            self.show_help = True

    def _check_difficulty_buttons(self, mouse_pos):
        '''检查难度按钮'''
        if self.game_active:
            return
        if self.easy_button.rect.collidepoint(mouse_pos):
            self._set_difficulty('easy')
        elif self.normal_button.rect.collidepoint(mouse_pos):
            self._set_difficulty('normal')
        elif self.hard_button.rect.collidepoint(mouse_pos):
            self._set_difficulty('hard')

    def _check_play_button(self, mouse_pos):
        '''检查Play按钮'''
        if not self.game_active and self.play_button.rect.collidepoint(mouse_pos):
            self._start_game()

    def _create_difficulty_buttons(self):
        '''创建难度按钮'''
        self.easy_button = Button(self, 'Easy')
        self.normal_button = Button(self, 'Normal')
        self.hard_button = Button(self, 'Hard')

        center_x = self.screen.get_rect().centerx
        center_y = self.screen.get_rect().centery
        button_y = center_y - 80
        spacing = 220

        # 设置按钮位置
        positions = [
            (self.easy_button, center_x - spacing, button_y),
            (self.normal_button, center_x, button_y),
            (self.hard_button, center_x + spacing, button_y)
        ]
        for btn, x, y in positions:
            btn.rect.center = (x, y)
            btn.msg_image_rect.center = btn.rect.center

        self.play_button.rect.center = (center_x, center_y + 50)
        self.play_button.msg_image_rect.center = self.play_button.rect.center

    def _set_difficulty(self, difficulty):
        '''设置难度'''
        self.current_difficulty = difficulty
        self.settings.set_difficulty(difficulty)
        self.stats.high_score = self.stats.high_scores[difficulty]
        self.sb.prep_high_score()
        self._update_button_colors(difficulty)

    def _update_button_colors(self, selected):
        '''更新按钮颜色'''
        default = (0, 135, 0)
        selected_color = (0, 200, 0)

        for btn in [self.easy_button, self.normal_button, self.hard_button]:
            btn.button_color = default

        if selected == 'easy':
            self.easy_button.button_color = selected_color
        elif selected == 'normal':
            self.normal_button.button_color = selected_color
        else:
            self.hard_button.button_color = selected_color

        self.easy_button._prep_msg('Easy')
        self.normal_button._prep_msg('Normal')
        self.hard_button._prep_msg('Hard')

    def _start_game(self):
        '''开始新游戏'''
        self.settings.initialize_dynamic_settings()
        self.settings.set_difficulty(self.current_difficulty)

        self.stats.reset_stats()
        self.stats.high_score = self.stats.high_scores[self.current_difficulty]

        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.sb.prep_high_score()

        self.game_active = True
        self.bullets.empty()
        self.aliens.empty()

        self._create_fleet()
        self.ship.center_ship()

        if self.settings.sound_enabled:
            try:
                pygame.mixer.music.play(-1)
            except:
                pass

        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        '''按键按下'''
        key = event.key
        if key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif key == pygame.K_q:
            self._quit_game()
        elif key == pygame.K_SPACE:
            self._fire_bullet()
        elif key == pygame.K_p and not self.game_active:
            self._start_game()
        elif key == pygame.K_ESCAPE and self.show_help:
            self.show_help = False

    def _check_keyup_events(self, event):
        '''按键释放'''
        key = event.key
        if key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        '''发射子弹'''
        if len(self.bullets) < self.settings.bullet_allowed:
            self.bullets.add(Bullet(self))
            self._play_sound(self.shoot_sound)

    def _update_bullets(self):
        '''更新子弹'''
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        '''检查子弹碰撞'''
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )

        if collisions:
            self._play_sound(self.explosion_sound)
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            if self.stats.check_high_score():
                self.sb.prep_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        '''更新外星人'''
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_alien_bottom()

    def _create_fleet(self):
        '''创建外星舰队'''
        alien = Alien(self)
        width, height = alien.rect.size

        x, y = width, height
        while y < self.settings.screen_height - 3 * height:
            while x < self.settings.screen_width - 2 * width:
                self._create_alien(x, y)
                x += 2 * width
            x = width
            y += 2 * height

    def _create_alien(self, x, y):
        '''创建单个外星人'''
        alien = Alien(self)
        alien.x = x
        alien.rect.x = x
        alien.rect.y = y
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        '''检查边缘'''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        '''改变方向'''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        '''更新屏幕'''
        self.screen.fill(self.settings.bg_color)

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.sb.show_score()

        if not self.game_active:
            if not self.show_help:
                self.play_button.draw_button()
                self.easy_button.draw_button()
                self.normal_button.draw_button()
                self.hard_button.draw_button()
                self.help_button.draw_button()
            else:
                self._draw_help_screen()

        pygame.display.flip()

    def _draw_help_screen(self):
        '''绘制帮助界面'''
        # 半透明遮罩
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 加载字体
        try:
            font_path = 'fonts/msyh.ttc'
            fonts = {
                'title': pygame.font.Font(font_path, 48),
                'heading': pygame.font.Font(font_path, 36),
                'text': pygame.font.Font(font_path, 24),
                'small': pygame.font.Font(font_path, 20)
            }
        except:
            try:
                fonts = {
                    'title': pygame.font.SysFont('microsoftyaheui', 48),
                    'heading': pygame.font.SysFont('microsoftyaheui', 36),
                    'text': pygame.font.SysFont('microsoftyaheui', 24),
                    'small': pygame.font.SysFont('microsoftyaheui', 20)
                }
            except:
                self._draw_english_help()
                return

        # 标题
        title = fonts['title'].render("游戏说明", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.settings.screen_width // 2, 50)))

        y, spacing = 100, 30
        left = 150

        # 内容列表
        sections = [
            ("游戏目标：", (255, 255, 0), fonts['heading'],
             ["• 消灭所有外星人", "• 每关速度会越来越快", "• 获得尽可能高的分数"]),
            ("操作说明：", (255, 255, 0), fonts['heading'],
             ["← → : 移动飞船", "空格键 : 发射子弹", "P 键 : 开始游戏", "Q 键 : 退出游戏", "ESC : 返回主菜单"]),
            ("难度等级：", (255, 255, 0), fonts['heading'],
             ["简单 : 飞船更快，外星人更慢，5条命", "普通 : 平衡设置，3条命", "困难 : 飞船更慢，外星人更快，2条命"])
        ]

        for title, color, font, items in sections:
            text = font.render(title, True, color)
            self.screen.blit(text, (left, y))
            y += 35

            for item in items:
                use_font = fonts['small'] if "难度" in title else fonts['text']
                text = use_font.render(item, True, (255, 255, 255))
                self.screen.blit(text, (left + 30, y))
                y += 25 if "难度" in title else spacing
            y += 10

        # 返回提示
        back = fonts['small'].render("按 ESC 键返回", True, (200, 200, 200))
        self.screen.blit(back, back.get_rect(center=(self.settings.screen_width // 2, 750)))

    def _draw_english_help(self):
        '''英文帮助（简化版）'''
        font = pygame.font.Font(None, 36)
        texts = ["How to Play", "ESC to return"]
        y = 200
        for text in texts:
            surface = font.render(text, True, (255, 255, 255))
            rect = surface.get_rect(center=(self.settings.screen_width // 2, y))
            self.screen.blit(surface, rect)
            y += 50

    def _ship_hit(self):
        '''飞船被撞'''
        if self.stats.ships_left > 0:
            self._play_sound(self.explosion_sound)
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            pygame.mixer.music.stop()
            self.stats.save_high_scores()
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_alien_bottom(self):
        '''检查外星人到底部'''
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()