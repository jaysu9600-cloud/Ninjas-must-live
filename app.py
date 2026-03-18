import pygame
import random
import os

FPS = 30
WIDTH = 800
HEIGHT = 500
GROUND_Y = 450

# 顏色定義
WHITE = (255, 255, 255)

# 障礙物設定
SPAWN_EVENT = pygame.USEREVENT + 1
obstacles_speed = 7
acceleration = 0.002
max_speed = 15

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("忍者必須活")
clock = pygame.time.Clock()

# 初始化字型系統
pygame.font.init()
font = pygame.font.SysFont("Microsoft JhengHei", 30)

ninja_img = pygame.image.load(os.path.join("img","ninja.png")).convert_alpha()
ninja_img.set_colorkey(WHITE) # 去除忍者白底

# 載入障礙物基礎圖片 (PNG 格式支援透明度)
shuriken_img = pygame.image.load(os.path.join("img", "shuriken.png")).convert_alpha()
kunai_img = pygame.image.load(os.path.join("img", "kunai.png")).convert_alpha()

# 初始化計時器
pygame.time.set_timer(SPAWN_EVENT, random.randint(1500, 3000))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(ninja_img,(62,78))
        self.rect = self.image.get_rect()
        self.rect.midbottom = (100, GROUND_Y)
        self.is_jumping = False
        self.jump_vel = 0
        self.gravity = 1
        
        # 跳躍高度控制相關變數
        self.jump_start_time = 0
        self.is_holding_jump = False
        self.base_jump_vel = 12
        self.additional_jump_vel = 13 # 總計最大約 25
        self.max_hold_time = 350 # 毫秒 (起跳後可持續增加力道的時間)

    def update(self):
        """
        更新玩家狀態：包含空中位移與長按增益檢測
        """
        if self.is_jumping:
            # 如果還在長按中，且在上升階段，且未超過最大時限
            if self.is_holding_jump and self.jump_vel > 0:
                elapsed = pygame.time.get_ticks() - self.jump_start_time
                if elapsed < self.max_hold_time:
                    # 隨著長按時間給予額外的微小加速度抵銷重力，實現「跳更高」
                    # 這裡採用直接微調 jump_vel 的方式
                    self.jump_vel += 0.8 # 抵銷部分重力並增加上升力
                else:
                    self.is_holding_jump = False

            self.rect.y -= self.jump_vel
            self.jump_vel -= self.gravity
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.is_jumping = False
                self.jump_vel = 0
                self.is_holding_jump = False

    def start_jump(self):
        """
        按下瞬間立即起跳
        """
        if not self.is_jumping:
            self.is_jumping = True
            self.is_holding_jump = True
            self.jump_start_time = pygame.time.get_ticks()
            self.jump_vel = self.base_jump_vel

    def stop_hold(self):
        """
        玩家放開按鍵，停止蓄力增益
        """
        self.is_holding_jump = False

class Obstacle(pygame.sprite.Sprite):
    """
    障礙物類別，負責隨機選擇圖片並移動
    """
    def __init__(self, speed):
        super().__init__()
        # 隨機選擇手裏劍或苦無
        self.type = random.choice(["shuriken", "kunai"])
        if self.type == "shuriken":
            # 取得原圖尺寸並等比例縮放 (高度固定 45)
            orig_rect = shuriken_img.get_rect()
            aspect_ratio = orig_rect.width / orig_rect.height
            new_width = int(45 * aspect_ratio)
            self.original_image = pygame.transform.scale(shuriken_img, (new_width, 45))
        else:
            self.original_image = pygame.transform.scale(kunai_img, (60, 30))
        
        self.image = self.original_image
        # PNG 已具備透明通道，不再強制去色，若仍有白邊則保留此註解
        # self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        # 苦無位置稍微低一點，手裏劍稍微高一點或隨機
        if self.type == "kunai":
            self.rect.midbottom = (WIDTH, GROUND_Y)
        else:
            self.rect.midbottom = (WIDTH, GROUND_Y - random.randint(0, 30))
        
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

all_sprites = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# 計分系統變數
score = 0
score_rate = 10  # 初始每秒得分
last_score_tick = pygame.time.get_ticks()
last_rate_increase_tick = last_score_tick

# 生命值系統變數
lives = 3
invincible_duration = 1500  # 1.5 秒無敵時間
last_damage_tick = 0        # 上次受傷時間

game_over = False  # 新增遊戲狀態旗標

def reset_game():
    """
    重置遊戲狀態至初始值
    """
    global score, score_rate, lives, last_score_tick, last_rate_increase_tick, obstacles_speed, game_over
    score = 0
    score_rate = 10
    lives = 3
    last_score_tick = pygame.time.get_ticks()
    last_rate_increase_tick = last_score_tick
    for sprite in obstacle_group:
        sprite.kill()
    obstacles_speed = 7
    game_over = False
    player.rect.midbottom = (100, GROUND_Y)
    player.is_jumping = False
    player.jump_vel = 0

running = True
while running:
    clock.tick(FPS)
    
    # --- 事件處理 (修正重點 1) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 鍵盤事件處理
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                # 按下空白鍵立即起跳
                player.start_jump()
            if event.key == pygame.K_r and game_over:
                reset_game()
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # 放開空白鍵停止增益
                player.stop_hold()
        
        # 障礙物生成
        if event.type == SPAWN_EVENT and not game_over:
            new_obstacle = Obstacle(obstacles_speed)
            all_sprites.add(new_obstacle)
            obstacle_group.add(new_obstacle)
            # 重新設定隨機間隔
            pygame.time.set_timer(SPAWN_EVENT, random.randint(1000, 2500))

    # --- 邏輯更新 ---
    if not game_over:
        current_time = pygame.time.get_ticks()
        
        # 每隔 1 秒增加分數 (1000 毫秒)
        if current_time - last_score_tick >= 1000:
            score += score_rate
            last_score_tick = current_time
        
        # 每隔 10 秒增加得分率 (10000 毫秒)
        if current_time - last_rate_increase_tick >= 10000:
            score_rate += 10 # 每 10 秒增加 10 分的秒分量
            last_rate_increase_tick = current_time
            print(f"得分增量提升！目前每秒得分: {score_rate}")

        if obstacles_speed < max_speed:
            obstacles_speed += acceleration
        
        all_sprites.update()

        # --- 碰撞檢測 ---
        current_ticks = pygame.time.get_ticks()
        is_invulnerable = current_ticks - last_damage_tick < invincible_duration

        # 只有在非無敵狀態下才檢測碰撞
        if not is_invulnerable:
            # 使用 sprite group 碰撞檢測
            hit_list = pygame.sprite.spritecollide(player, obstacle_group, False)
            if hit_list:
                lives -= 1
                last_damage_tick = current_ticks
                print(f"碰撞！剩餘生命: {lives}")
                if lives <= 0:
                    game_over = True

    # --- 畫面繪製 ---
    screen.fill((255, 255, 255))
    
    # 畫地板 (輔助視覺)
    pygame.draw.line(screen, (0, 0, 0), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
    
    all_sprites.draw(screen)
    
    # 繪製計分資訊 (顯示在左上角)
    score_surface = font.render(f"分數: {score} (+{score_rate}/s)", True, (0, 0, 0))
    screen.blit(score_surface, (10, 10))
    
    # 繪製生命值 (顯示在分數下方)
    if not game_over:
        # 若目前是無敵狀態，改變顏色提示
        health_color = (255, 0, 0) if is_invulnerable else (0, 0, 0)
        health_text = "❤" * lives
        health_surface = font.render(f"生命: {health_text}", True, health_color)
        screen.blit(health_surface, (10, 50))
    
    # --- 遊戲結束畫面 ---
    if game_over:
        # 繪製半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # 顯示 GAME OVER
        game_over_font = pygame.font.SysFont("Microsoft JhengHei", 60, bold=True)
        over_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
        over_rect = over_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(over_surface, over_rect)
        
        # 顯示最終分數
        final_score_surface = font.render(f"最終得分: {score}", True, (255, 255, 255))
        final_rect = final_score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(final_score_surface, final_rect)
        
        # 顯示重新開始提示 (R 鍵圖示化文字)
        restart_surface = font.render("按 [R] 鍵重新開始", True, (0, 255, 0))
        restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        screen.blit(restart_surface, restart_rect)
        
    pygame.display.update()

pygame.display.quit()
pygame.quit()
