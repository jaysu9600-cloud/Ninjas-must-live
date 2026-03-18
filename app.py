import pygame
import random
import os

FPS = 30
WIDTH = 800
HEIGHT = 500
GROUND_Y = 450

# 障礙物設定
obstacles = []
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

    def update(self):
        if self.is_jumping:
            self.rect.y -= self.jump_vel
            self.jump_vel -= self.gravity
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.is_jumping = False
                self.jump_vel = 0

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_vel = 18 # 稍微增加跳躍力

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# 計分系統變數
score = 0
score_rate = 10  # 初始每秒得分
last_score_tick = pygame.time.get_ticks()
last_rate_increase_tick = last_score_tick

running = True
while running:
    clock.tick(FPS)
    
    # --- 事件處理 (修正重點 1) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 偵測跳躍 (新增)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        
        # 障礙物生成 (必須放在 event loop 內)
        if event.type == SPAWN_EVENT:
            new_tree = pygame.Rect(WIDTH, GROUND_Y - 50, 30, 50)
            obstacles.append(new_tree)
            # 重新設定隨機間隔
            pygame.time.set_timer(SPAWN_EVENT, random.randint(1000, 2500))

    # --- 邏輯更新 ---
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

    for obstacle in obstacles[:]:
        obstacle.x -= obstacles_speed
        if obstacle.right < 0:
            obstacles.remove(obstacle)

    # --- 碰撞檢測 ---
    for obstacle in obstacles:
        # 使用 pygame.Rect.colliderect 檢測玩家與障礙物的碰撞
        if player.rect.colliderect(obstacle):
            print("遊戲結束！")
            running = False

    # --- 畫面繪製 ---
    screen.fill((255, 255, 255))
    
    # 畫地板 (輔助視覺)
    pygame.draw.line(screen, (0, 0, 0), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
    
    all_sprites.draw(screen)
    for obstacle in obstacles:
        pygame.draw.rect(screen, (255, 0, 0), obstacle)
    
    # 繪製計分資訊 (顯示在左上角)
    score_surface = font.render(f"分數: {score} (+{score_rate}/s)", True, (0, 0, 0))
    screen.blit(score_surface, (10, 10))
        
    pygame.display.update()

pygame.display.quit()
pygame.quit()
