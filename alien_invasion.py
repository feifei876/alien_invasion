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

        # 初始化声音系统
        pygame.mixer.init()

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption('Alien Invasion')

        # 加载所有音效（紧跟在settings之后）
        self._load_sounds()

        # 创建一个用于存储游戏统计信息的实例，并创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 游戏启动后处于非活动状态
        self.game_active = False

        # 设置当前难度（默认普通）
        self.current_difficulty = 'normal'

        # 创建Play按钮和难度按钮
        self.play_button = Button(self, 'Play')
        self._create_difficulty_buttons()

        #  新增：创建玩法说明按钮
        self.help_button = Button(self, 'How to Play')
        self._position_help_button()

        # 说明界面是否显示
        self.show_help = False

    def _position_help_button(self):
        '''设置玩法说明按钮的位置'''
        screen_center_x = self.screen.get_rect().centerx
        screen_center_y = self.screen.get_rect().centery

        # 将说明按钮放在Play按钮下方
        self.help_button.rect.centerx = screen_center_x
        self.help_button.rect.centery = screen_center_y + 120  # Play按钮下方70像素
        self.help_button.msg_image_rect.center = self.help_button.rect.center

    def _load_sounds(self):
        '''加载所有声音文件'''
        try:
            # 射击声
            self.shoot_sound = pygame.mixer.Sound('sounds/shoot.wav')
            self.shoot_sound.set_volume(self.settings.shoot_volume)
            print("✓ 射击声加载成功")

            # 爆炸声
            self.explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')
            self.explosion_sound.set_volume(self.settings.explosion_volume)
            print("✓ 爆炸声加载成功")

            # 背景音乐
            pygame.mixer.music.load('sounds/background.mp3')
            pygame.mixer.music.set_volume(self.settings.background_volume)
            print("✓ 背景音乐加载成功")

        except FileNotFoundError as e:
            print(f"⚠️ 警告：找不到音效文件 - {e}")
            print("游戏将继续运行，但没有声音效果")
            self.shoot_sound = None
            self.explosion_sound = None
        except Exception as e:
            print(f"⚠️ 警告：加载音效时出错 - {e}")
            self.shoot_sound = None
            self.explosion_sound = None

    def _play_sound(self, sound):
        '''播放声音（如果声音存在且开启）'''
        if self.settings.sound_enabled and sound is not None:
            sound.play()

    def _fire_bullet(self):
        '''创建一颗子弹，并将其加入编组bullets'''
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            # ✨ 播放射击声
            self._play_sound(self.shoot_sound)

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
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_difficulty_buttons(mouse_pos)  #  检查难度按钮
                self._check_help_button(mouse_pos)  # 新增：检查说明按钮

    def _check_help_button(self, mouse_pos):
        '''检查玩家是否点击了玩法说明按钮'''
        if not self.game_active and self.help_button.rect.collidepoint(mouse_pos):
            # 点击说明按钮，显示说明界面
            self.show_help = True

    def _close_help(self):
        '''关闭玩法说明界面'''
        self.show_help = False

    def _check_difficulty_buttons(self, mouse_pos):
        '''检查玩家点击了哪个难度按钮'''
        if not self.game_active:  # 只在游戏未开始时可以选难度
            if self.easy_button.rect.collidepoint(mouse_pos):
                self._set_difficulty('easy')
            elif self.normal_button.rect.collidepoint(mouse_pos):
                self._set_difficulty('normal')
            elif self.hard_button.rect.collidepoint(mouse_pos):
                self._set_difficulty('hard')

    def _check_play_button(self, mouse_pos):
        '''在玩家单击Play按钮时开始新游戏'''
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self._start_game()

    def _create_difficulty_buttons(self):
        '''创建难度选择按钮'''
        # 创建三个难度按钮
        self.easy_button = Button(self, 'Easy')
        self.normal_button = Button(self, 'Normal')
        self.hard_button = Button(self, 'Hard')

        # 计算屏幕中心
        screen_center_x = self.screen.get_rect().centerx
        screen_center_y = self.screen.get_rect().centery

        # 设置难度按钮的位置（在屏幕上半部分）
        button_y = screen_center_y - 80  # 难度按钮在中心上方80像素
        button_spacing = 220  # 按钮间距

        # Easy按钮（左侧）
        self.easy_button.rect.centerx = screen_center_x - button_spacing
        self.easy_button.rect.centery = button_y
        self.easy_button.msg_image_rect.center = self.easy_button.rect.center

        # Normal按钮（中间）
        self.normal_button.rect.centerx = screen_center_x
        self.normal_button.rect.centery = button_y
        self.normal_button.msg_image_rect.center = self.normal_button.rect.center

        # Hard按钮（右侧）
        self.hard_button.rect.centerx = screen_center_x + button_spacing
        self.hard_button.rect.centery = button_y
        self.hard_button.msg_image_rect.center = self.hard_button.rect.center

        # 设置Play按钮的位置（在难度按钮下方）
        self.play_button.rect.centerx = screen_center_x
        self.play_button.rect.centery = screen_center_y + 50  # Play按钮在中心下方50像素
        self.play_button.msg_image_rect.center = self.play_button.rect.center

    def _set_difficulty(self, difficulty):
        '''设置游戏难度'''
        self.current_difficulty = difficulty
        self.settings.set_difficulty(difficulty)

        # 更新当前显示的最高分
        self.stats.high_score = self.stats.high_scores[difficulty]
        self.sb.prep_high_score()  # 更新记分牌显示

        # 更新按钮颜色
        self._update_button_colors(difficulty)

    def _update_button_colors(self, selected_difficulty):
        '''更新按钮颜色以显示当前选择的难度'''
        # 重置所有按钮颜色
        default_color = (0, 135, 0)  # 深绿色
        selected_color = (0, 200, 0)  # 亮绿色

        self.easy_button.button_color = default_color
        self.normal_button.button_color = default_color
        self.hard_button.button_color = default_color

        # 高亮选中的按钮
        if selected_difficulty == 'easy':
            self.easy_button.button_color = selected_color
        elif selected_difficulty == 'normal':
            self.normal_button.button_color = selected_color
        elif selected_difficulty == 'hard':
            self.hard_button.button_color = selected_color

        # 重新渲染按钮文本
        self.easy_button._prep_msg('Easy')
        self.normal_button._prep_msg('Normal')
        self.hard_button._prep_msg('Hard')

    def _start_game(self):
        '''开始新游戏'''
        # 还原游戏设置（但保持已选择的难度）
        self.settings.initialize_dynamic_settings()
        # 重新应用当前难度（确保速度等设置正确）
        self.settings.set_difficulty(self.current_difficulty)

        # 重置游戏的统计信息
        self.stats.reset_stats()
        # 重置后保持当前难度的最高分显示
        self.stats.high_score = self.stats.high_scores[self.current_difficulty]

        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.sb.prep_high_score()  # 刷新最高分显示
        self.game_active = True

        # 清空外星人列表和子弹列表
        self.bullets.empty()
        self.aliens.empty()

        # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
        self._create_fleet()
        self.ship.center_ship()

        # 播放背景音乐（循环播放）
        if self.settings.sound_enabled:
            try:
                pygame.mixer.music.play(-1)  # -1 表示循环播放
            except:
                pass

        # 隐藏光标
        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        '''响应按下'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            # 停止背景音乐
            pygame.mixer.music.stop()
            # 退出前保存所有最高分
            self.stats.save_high_scores()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p and not self.game_active:
            self._start_game()
        elif event.key == pygame.K_ESCAPE and self.show_help:  # 按ESC关闭说明
            self._close_help()

    def _check_keyup_events(self, event):
        '''响应释放'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        '''创建一颗子弹，并将其加入编组bullets'''
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        '''更新子弹的位置并删除已消失的子弹'''
        # 更新子弹的位置
        self.bullets.update()

        # 删除已消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        '''响应子弹和外星人的碰撞'''
        # 删除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )

        if collisions:
            # ✨ 播放爆炸声（每颗子弹击中播放一次）
            self._play_sound(self.explosion_sound)

            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()

            # 检查是否打破当前难度的最高分
            if self.stats.check_high_score():
                self.sb.prep_high_score()  # 更新显示

        if not self.aliens:
            # 删除现有的子弹并创建一个新的外星舰队
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        '''检查是否有外星人位于屏幕边缘，并更新整个外星舰队的位置'''
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检查是否有外星人到达屏幕的下边缘
        self._check_alien_bottom()

    def _create_fleet(self):
        '''创建一个外形舰队'''
        # 创建一个外星人，再不断添加，直到没有空间添加外星人为止
        # 外星人的间距为外星人的宽度和外星人的高度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # 添加一行外星人后，重置x值并递增y值
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        '''创建一个外星人，并将其加入外形舰队'''
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        '''在有外星人到达边缘是采取相应的措施'''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        '''将整个外星舰队向下移动，并改变它们的方向'''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        '''更新屏幕上的图像，并切换到新屏幕'''
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态，就绘制按钮
        if not self.game_active:
            # 如果没有显示说明，就绘制所有按钮
            if not self.show_help:
                self.play_button.draw_button()
                self.easy_button.draw_button()
                self.normal_button.draw_button()
                self.hard_button.draw_button()
                self.help_button.draw_button()  # ✨ 绘制说明按钮
            else:
                # 显示玩法说明界面
                self._draw_help_screen()

        pygame.display.flip()

    def _draw_help_screen(self):
        '''绘制玩法说明界面'''
        # 创建一个半透明遮罩
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # ✨ 使用更小的字体
        try:
            # Windows 系统字体
            title_font = pygame.font.Font('C:/Windows/Fonts/msyh.ttf', 48)  # 标题 48px
            heading_font = pygame.font.Font('C:/Windows/Fonts/msyh.ttf', 36)  # 小标题 36px
            text_font = pygame.font.Font('C:/Windows/Fonts/msyh.ttf', 24)  # 正文 24px
            small_font = pygame.font.Font('C:/Windows/Fonts/msyh.ttf', 20)  # 提示 20px
        except:
            # 如果找不到，使用默认字体
            title_font = pygame.font.SysFont('simhei', 48)
            heading_font = pygame.font.SysFont('simhei', 36)
            text_font = pygame.font.SysFont('simhei', 24)
            small_font = pygame.font.SysFont('simhei', 20)

        # 标题
        title = title_font.render("游戏说明", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, 50))
        self.screen.blit(title, title_rect)

        # 当前Y位置
        y_pos = 100
        line_spacing = 30  # ✨ 行间距

        # 游戏目标
        goal_title = heading_font.render("游戏目标：", True, (255, 255, 0))
        goal_rect = goal_title.get_rect(left=150, top=y_pos)
        self.screen.blit(goal_title, goal_rect)
        y_pos += 35

        goal_items = [
            "• 消灭所有外星人",
            "• 每关速度会越来越快",
            "• 获得尽可能高的分数"
        ]
        for item in goal_items:
            text = text_font.render(item, True, (255, 255, 255))
            text_rect = text.get_rect(left=180, top=y_pos)
            self.screen.blit(text, text_rect)
            y_pos += line_spacing
        y_pos += 10

        # 操作说明
        control_title = heading_font.render("操作说明：", True, (255, 255, 0))
        control_rect = control_title.get_rect(left=150, top=y_pos)
        self.screen.blit(control_title, control_rect)
        y_pos += 35

        control_items = [
            "← → : 移动飞船",
            "空格键 : 发射子弹",
            "P 键 : 开始游戏",
            "Q 键 : 退出游戏",
            "ESC : 返回主菜单"
        ]
        for item in control_items:
            text = text_font.render(item, True, (255, 255, 255))
            text_rect = text.get_rect(left=180, top=y_pos)
            self.screen.blit(text, text_rect)
            y_pos += line_spacing
        y_pos += 10

        # 难度说明
        difficulty_title = heading_font.render("难度等级：", True, (255, 255, 0))
        difficulty_rect = difficulty_title.get_rect(left=150, top=y_pos)
        self.screen.blit(difficulty_title, difficulty_rect)
        y_pos += 35

        difficulty_items = [
            "简单 : 飞船更快，外星人更慢，5条命",
            "普通 : 平衡设置，3条命",
            "困难 : 飞船更慢，外星人更快，2条命"
        ]
        for item in difficulty_items:
            text = small_font.render(item, True, (255, 255, 255))
            text_rect = text.get_rect(left=180, top=y_pos)
            self.screen.blit(text, text_rect)
            y_pos += 25  # 难度说明用更小的行距

        # 返回提示
        back_text = small_font.render("按 ESC 键返回", True, (200, 200, 200))
        back_rect = back_text.get_rect(center=(self.settings.screen_width // 2, 750))
        self.screen.blit(back_text, back_rect)

    def _ship_hit(self):
        '''响应飞船和外星人的碰撞'''
        if self.stats.ships_left > 0:
            # 播放爆炸声（飞船被撞）
            self._play_sound(self.explosion_sound)

            # 将ship_left减1并更新记分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()

            # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(0.5)
        else:
            # 停止背景音乐
            pygame.mixer.music.stop()

            # 游戏结束前保存所有最高分
            self.stats.save_high_scores()
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_alien_bottom(self):
        '''检查是否有外星人到达了屏幕的下边缘'''
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # 想飞船被撞到一样进行处理
                self._ship_hit()
                break

if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()