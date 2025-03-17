import pygame
import random

# Ініціалізація Pygame
pygame.init()

# Параметри вікна
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Платформер")

# Кольори
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Шрифт
font = pygame.font.Font(None, 36)

# Завантаження іконок
door_icon = pygame.image.load("door.png")
door_icon = pygame.transform.scale(door_icon, (50, 70))

coin_icon = pygame.image.load("coin.png")
coin_icon = pygame.transform.scale(coin_icon, (30, 30))

# Завантаження фону
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Завантаження зображень для гравця
player_idle = pygame.image.load("player_idle.png")
player_walk1 = pygame.image.load("player_walk1.png")
player_walk2 = pygame.image.load("player_walk2.png")
player_walk1_left = pygame.transform.flip(player_walk1, True, False)  # Дзеркальне зображення для ліворуч
player_walk2_left = pygame.transform.flip(player_walk2, True, False)  # Дзеркальне зображення для ліворуч
player_jump = pygame.image.load("player_jump.png")

player_idle = pygame.transform.scale(player_idle, (40, 50))
player_walk1 = pygame.transform.scale(player_walk1, (40, 50))
player_walk2 = pygame.transform.scale(player_walk2, (40, 50))
player_walk1_left = pygame.transform.scale(player_walk1_left, (40, 50))  # Масштабуємо walk1 для ліворуч
player_walk2_left = pygame.transform.scale(player_walk2_left, (40, 50))  # Масштабуємо walk2 для ліворуч
player_jump = pygame.transform.scale(player_jump, (40, 50))

# Завантаження зображення для платформи
platform_img = pygame.image.load("platform.png")
platform_img = pygame.transform.scale(platform_img, (120, 20))

# Клас гравця
class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 700, 40, 50)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.health = 3
        self.score = 0
        self.animation_counter = 0  # Лічильник анімації
        self.facing_left = False  # Прапор, що вказує, куди дивиться гравець (ліворуч або праворуч)
        self.invincible = False  # Невразливість
        self.invincibility_timer = 0  # Таймер невразливості

    def move(self, platforms):
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.x += self.vel_x

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -18  # Стрибок

    def check_collision(self, coins):
        # Перевірка зіткнень із монетами
        for coin in coins:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.score += 10  # Додавання очок за монету

        if self.rect.bottom > HEIGHT:
            self.health -= 1
            if self.health <= 0:
                return True  # Гравець загинув
        return False

    def draw(self, screen):
        if self.vel_y != 0:  # Якщо гравець у стрибку
            screen.blit(player_jump, (self.rect.x, self.rect.y))
        elif self.vel_x != 0:  # Якщо гравець рухається
            # Використовуємо два спрайти для анімації ходьби, залежно від напрямку
            self.animation_counter += 1
            if self.animation_counter % 20 == 0:
                self.animation_counter = 0
            if self.animation_counter < 10:
                if self.facing_left:  # Якщо гравець дивиться вліво
                    screen.blit(player_walk1_left, (self.rect.x, self.rect.y))
                else:  # Якщо гравець дивиться праворуч
                    screen.blit(player_walk1, (self.rect.x, self.rect.y))
            else:
                if self.facing_left:  # Якщо гравець дивиться вліво
                    screen.blit(player_walk2_left, (self.rect.x, self.rect.y))
                else:  # Якщо гравець дивиться праворуч
                    screen.blit(player_walk2, (self.rect.x, self.rect.y))
        else:  # Якщо гравець стоїть
            screen.blit(player_idle, (self.rect.x, self.rect.y))

    def draw_health(self, screen):
        health_text = font.render(f"Здоров'я: {self.health}", True, BLACK)
        screen.blit(health_text, (10, 10))

    def draw_score(self, screen):
        score_text = font.render(f"Бали: {self.score}", True, BLACK)
        screen.blit(score_text, (WIDTH - 150, 10))

    def update_invincibility(self):
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

# Клас для платформ
class Platform:
    def __init__(self, x, y, width, height, moving=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.moving = moving
        self.vel_x = random.choice([-2, -1, 1, 2]) if moving else 0  # Рухаюча платформа

    def move(self):
        if self.moving:
            self.rect.x += self.vel_x
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.vel_x = -self.vel_x  # Змінюємо напрямок руху

    def draw(self, screen):
        screen.blit(platform_img, (self.rect.x, self.rect.y))  # Відображаємо платформу із зображенням
# Клас для монет
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)

    def draw(self, screen):
        screen.blit(coin_icon, (self.rect.x, self.rect.y))

# Функція створення рівнів
def create_platforms(level):
    platforms = [
        Platform(100, 750, 120, 20),
        Platform(300, 700, 120, 20),
        Platform(500, 650, 120, 20),
        Platform(700, 600, 120, 20),
        Platform(900, 550, 120, 20),
        Platform(200, 500, 120, 20),
        Platform(400, 450, 120, 20),
        Platform(600, 400, 120, 20),
        Platform(800, 350, 120, 20),
        Platform(1000, 300, 120, 20),
        Platform(150, 250, 120, 20),
        Platform(350, 200, 120, 20),
        Platform(550, 150, 120, 20)
    ]
    
    random.shuffle(platforms)

    min_distance = 80
    for i in range(1, len(platforms)):
        if platforms[i].rect.top - platforms[i-1].rect.top < min_distance:
            platforms[i].rect.top = platforms[i-1].rect.top - min_distance

    return platforms

def create_coins(required_score, platforms):
    num_coins = required_score // 10
    coins = []

    for _ in range(num_coins):
        coin_placed = False

        while not coin_placed:
            platform = random.choice(platforms)
            x = random.randint(platform.rect.left + 10, platform.rect.right - 40)
            y = random.randint(platform.rect.top - 40, platform.rect.top - 10)

            coin_rect = pygame.Rect(x, y, 30, 30)
            coin_placed = True
            for plat in platforms:
                if coin_rect.colliderect(plat.rect):
                    coin_placed = False
                    break

        coin = Coin(x, y)
        coins.append(coin)

    return coins

def create_door(platforms):
    last_platform = platforms[-1]
    door_rect = pygame.Rect(last_platform.rect.centerx - 25, last_platform.rect.top - 70, 50, 70)
    return door_rect

def game_over_screen():
    screen.fill(WHITE)
    game_over_text = font.render("Ви померли", True, RED)
    restart_text = font.render("Натисніть R для перезапуску або ESC для виходу", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()

# Ініціалізація гри
current_level = 1
required_score = 100
platforms = create_platforms(current_level)
coins = create_coins(required_score, platforms)
door_rect = create_door(platforms)
player = Player()

running = True
clock = pygame.time.Clock()

while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                player.jump()
            elif event.key == pygame.K_r:
                player = Player()
                platforms = create_platforms(current_level)
                coins = create_coins(required_score, platforms)
                door_rect = create_door(platforms)

    player.update_invincibility()  # Оновлюємо стан невразливості гравця

    if player.check_collision(coins):
        if player.health <= 0:
            game_over_screen()
            pygame.display.flip()

            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_input = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            waiting_for_input = False
                        elif event.key == pygame.K_r:
                            player = Player()
                            platforms = create_platforms(current_level)
                            coins = create_coins(required_score, platforms)
                            door_rect = create_door(platforms)
                            waiting_for_input = False

    keys = pygame.key.get_pressed()
    player.vel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5

    if keys[pygame.K_LEFT]:
        player.facing_left = True
    elif keys[pygame.K_RIGHT]:
        player.facing_left = False

    player.move(platforms)
    player.draw(screen)
    player.draw_health(screen)
    player.draw_score(screen)

    for platform in platforms:
        platform.move()
        platform.draw(screen)

    for coin in coins:
        coin.draw(screen)

    if player.score >= required_score and player.rect.colliderect(door_rect):
        current_level += 1
        required_score += 20
        platforms = create_platforms(current_level)
        coins = create_coins(required_score, platforms)
        door_rect = create_door(platforms)
        player.score = 0
        player.health = 3
        player.rect.topleft = (100, 700)

    screen.blit(door_icon, (door_rect.x, door_rect.y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
