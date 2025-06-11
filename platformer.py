import pygame
import math
import random

pygame.init()

coin_sound = pygame.mixer.Sound("coin.wav")
jump_sound = pygame.mixer.Sound("jump.wav")
run_sound = pygame.mixer.Sound("run.wav")
level_up_sound = pygame.mixer.Sound("level_up.wav")
damage_sound = pygame.mixer.Sound("damage.wav")

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Креативний Платформер")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

door_icon = pygame.image.load("door.png")
door_icon = pygame.transform.scale(door_icon, (50, 70))

coin_icon = pygame.image.load("coin.png")
coin_icon = pygame.transform.scale(coin_icon, (30, 30))

player_idle = pygame.image.load("player_idle.png")
player_walk1 = pygame.image.load("player_walk1.png")
player_walk2 = pygame.image.load("player_walk2.png")
player_jump = pygame.image.load("player_jump.png")

player_idle = pygame.transform.scale(player_idle, (40, 50))
player_walk1 = pygame.transform.scale(player_walk1, (40, 50))
player_walk2 = pygame.transform.scale(player_walk2, (40, 50))
player_walk1_left = pygame.transform.flip(player_walk1, True, False)
player_walk2_left = pygame.transform.flip(player_walk2, True, False)
player_walk1_left = pygame.transform.scale(player_walk1_left, (40, 50))
player_walk2_left = pygame.transform.scale(player_walk2_left, (40, 50))
player_jump = pygame.transform.scale(player_jump, (40, 50))

platform_img = pygame.image.load("platform.png")
platform_img = pygame.transform.scale(platform_img, (120, 20))

spike_img = pygame.image.load("spike.png")
spike_img = pygame.transform.scale(spike_img, (40, 40))


class Platform:
    def __init__(self, x, y, w=120, h=20, moving=False, move_range=0, move_speed=0,
                 vertical=False, temporary=False, pulsate=False, disappear_cycle=None, diagonal=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.moving = moving
        self.move_range = move_range
        self.move_speed = move_speed
        self.vertical = vertical
        self.temporary = temporary
        self.pulsate = pulsate
        self.disappear_cycle = disappear_cycle  # (time_visible, time_invisible) in ms
        self.active = True
        self.start_pos = (x, y)
        self.direction = 1
        self.step_counter = 0
        self.timer = 0
        self.diagonal = diagonal

    def update(self):
        if self.pulsate:
            # Зміна розміру платформи по синусоїді
            scale_factor = 1 + 0.3 * math.sin(pygame.time.get_ticks() / 300)
            new_width = int(120 * scale_factor)
            new_height = int(20 * scale_factor)
            self.rect.width = new_width
            self.rect.height = new_height

        if self.moving and self.active:
            if self.diagonal:
                # Діагональне рухання
                self.rect.x += self.move_speed * self.direction
                self.rect.y += self.move_speed * self.direction
                self.step_counter += abs(self.move_speed)
                if self.step_counter >= self.move_range:
                    self.direction *= -1
                    self.step_counter = 0
            elif self.vertical:
                self.rect.y += self.move_speed * self.direction
                self.step_counter += abs(self.move_speed)
                if self.step_counter >= self.move_range:
                    self.direction *= -1
                    self.step_counter = 0
            else:
                self.rect.x += self.move_speed * self.direction
                self.step_counter += abs(self.move_speed)
                if self.step_counter >= self.move_range:
                    self.direction *= -1
                    self.step_counter = 0

        if self.disappear_cycle:
            self.timer += pygame.time.get_ticks() % 1000  # крутить таймер
            total_cycle = sum(self.disappear_cycle)
            current_time = pygame.time.get_ticks() % total_cycle
            if current_time > self.disappear_cycle[0]:
                self.active = False
            else:
                self.active = True

    def draw(self, screen):
        if self.active:
            screen.blit(platform_img, (self.rect.x, self.rect.y))


class Spike:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self, screen):
        screen.blit(spike_img, (self.rect.x, self.rect.y))


class Coin:
    def __init__(self, x, y, floating=False):
        self.base_x = x
        self.base_y = y
        self.floating = floating
        self.rect = pygame.Rect(x, y, 30, 30)
        self.float_offset = 0

    def update(self):
        if self.floating:
            self.float_offset = 5 * math.sin(pygame.time.get_ticks() / 500)
            self.rect.y = self.base_y + self.float_offset

    def draw(self, screen):
        screen.blit(coin_icon, (self.rect.x, self.rect.y))


class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 700, 40, 50)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.health = 3
        self.score = 0
        self.animation_counter = 0
        self.facing_left = False
        self.invincible = False
        self.invincibility_timer = 0
        self.is_running_sound_playing = False

    def move(self, platforms):
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.x += self.vel_x

        for platform in platforms:
            if platform.active and self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if platform.active and self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -23
            jump_sound.play()

    def check_collision(self, coins, spikes):
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.score += 10
                coin_sound.play()

        for spike in spikes:
            if self.rect.colliderect(spike.rect):
                if not self.invincible:
                    self.health -= 1
                    damage_sound.play()
                    self.invincible = True
                    self.invincibility_timer = 60 * 2  # 2 секунди

        if self.rect.bottom > HEIGHT:
            self.health -= 1
            if self.health <= 0:
                return True
            else:
                self.rect.x = 100
                self.rect.y = 700
                self.vel_y = 0
        return False

    def draw(self, screen):
        if self.vel_y != 0:
            if self.is_running_sound_playing:
                run_sound.stop()
                self.is_running_sound_playing = False
            screen.blit(player_jump, (self.rect.x, self.rect.y))
        elif self.vel_x != 0:
            self.animation_counter += 1
            if self.animation_counter % 20 == 0:
                self.animation_counter = 0

            if not self.is_running_sound_playing:
                run_sound.play(-1)
                self.is_running_sound_playing = True

            if self.animation_counter < 10:
                if self.facing_left:
                    screen.blit(player_walk1_left, (self.rect.x, self.rect.y))
                else:
                    screen.blit(player_walk1, (self.rect.x, self.rect.y))
            else:
                if self.facing_left:
                    screen.blit(player_walk2_left, (self.rect.x, self.rect.y))
                else:
                    screen.blit(player_walk2, (self.rect.x, self.rect.y))
        else:
            if self.is_running_sound_playing:
                run_sound.stop()
                self.is_running_sound_playing = False
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


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def show_menu():
    start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, "Розпочати гру")
    quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Вихід")

    while True:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        title = large_font.render("Креативний Платформер", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        start_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(event.pos):
                    return
                elif quit_button.is_clicked(event.pos):
                    pygame.quit()
                    exit()


def show_game_over_menu():
    retry_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Спробувати знову")
    quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50, "Вихід")

    while True:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        game_over_text = large_font.render("Ви програли", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

        retry_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.is_clicked(event.pos):
                    return True
                elif quit_button.is_clicked(event.pos):
                    return False


def show_level_up_menu(level_number):
    next_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Далі")
    quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50, "Вийти")

    while True:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        level_text = large_font.render(f"Рівень {level_number} пройдено!", True, BLACK)
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 100))

        next_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.is_clicked(event.pos):
                    return True
                elif quit_button.is_clicked(event.pos):
                    return False


def show_victory_screen():
    quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50, "Вийти")

    while True:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        victory_text = large_font.render("Ви пройшли всі рівні!", True, BLACK)
        screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 100))

        quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button.is_clicked(event.pos):
                    pygame.quit()
                    exit()


levels = [
    # Новий рівень 1 — рухомі платформи горизонтально і пульсуючі, багато монет
    {
        "platforms": [
            Platform(0, 770, 1200, 30),
            Platform(150, 650, moving=True, move_range=250, move_speed=4),
            Platform(500, 600, pulsate=True),
            Platform(800, 550, moving=True, move_range=150, move_speed=3, vertical=True),
            Platform(1050, 500),
        ],
        "coins": [
            Coin(170, 610, floating=True),
            Coin(520, 560),
            Coin(810, 510, floating=True),
            Coin(1070, 460),
            Coin(300, 700),
        ],
        "door": pygame.Rect(1150, 430, 50, 70),
        "spikes": [
            Spike(400, 750),
            Spike(750, 730),
            Spike(1000, 480),
        ],
    },

    # Новий рівень 2 — тимчасові платформи і діагональні рухомі платформи
    {
        "platforms": [
            Platform(0, 770, 1200, 30),
            Platform(100, 650, temporary=True),
            Platform(350, 600, moving=True, move_range=100, move_speed=3, diagonal=True),
            Platform(600, 550, temporary=True, pulsate=True),
            Platform(900, 500),
            Platform(1100, 450),
        ],
        "coins": [
            Coin(120, 610),
            Coin(370, 560, floating=True),
            Coin(620, 510),
            Coin(920, 460, floating=True),
            Coin(1120, 410),
        ],
        "door": pygame.Rect(1150, 400, 50, 70),
        "spikes": [
            Spike(550, 740),
            Spike(850, 740),
        ],
    },

    # Новий рівень 3 — складні платформи з циклічним зникненням і вертикальним рухом
    {
        "platforms": [
            Platform(0, 770, 1200, 30),
            Platform(200, 650, disappear_cycle=(1500, 1500)),
            Platform(450, 600, moving=True, move_range=200, move_speed=4, vertical=True),
            Platform(750, 550, pulsate=True),
            Platform(1000, 500),
        ],
        "coins": [
            Coin(220, 610),
            Coin(470, 560, floating=True),
            Coin(770, 510),
            Coin(1020, 460, floating=True),
        ],
        "door": pygame.Rect(1150, 430, 50, 70),
        "spikes": [
            Spike(600, 740),
            Spike(800, 740),
        ],
    },

    # Новий рівень 4 — комбінація рухомих і пульсуючих платформ, багато шипів
    {
        "platforms": [
            Platform(0, 770, 1200, 30),
            Platform(150, 650, moving=True, move_range=150, move_speed=3),
            Platform(400, 600, pulsate=True),
            Platform(700, 550, moving=True, move_range=100, move_speed=2, vertical=True),
            Platform(950, 500),
            Platform(1150, 450),
        ],
        "coins": [
            Coin(170, 610),
            Coin(420, 560, floating=True),
            Coin(720, 510),
            Coin(970, 460, floating=True),
            Coin(1170, 410),
        ],
        "door": pygame.Rect(1150, 400, 50, 70),
        "spikes": [
            Spike(300, 750),
            Spike(550, 740),
            Spike(850, 730),
            Spike(1100, 720),
        ],
    },
]


def main():
    show_menu()

    current_level = 0
    level_data = levels[current_level]
    platforms = level_data["platforms"]
    coins = level_data["coins"]
    door = level_data["door"]
    spikes = level_data.get("spikes", [])

    player = Player()
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        screen.fill(WHITE)
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.vel_x = -10
                    player.facing_left = True
                elif event.key == pygame.K_RIGHT:
                    player.vel_x = 10
                    player.facing_left = False
                elif event.key == pygame.K_UP:
                    player.jump()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.vel_x < 0:
                    player.vel_x = 0
                elif event.key == pygame.K_RIGHT and player.vel_x > 0:
                    player.vel_x = 0

        for platform in platforms:
            platform.update()
            platform.draw(screen)

        for spike in spikes:
            spike.draw(screen)

        for coin in coins:
            coin.update()
            coin.draw(screen)

        player.move(platforms)
        game_over = player.check_collision(coins, spikes)
        player.update_invincibility()
        player.draw(screen)
        player.draw_health(screen)
        player.draw_score(screen)

        screen.blit(door_icon, (door.x, door.y))

        if game_over:
            if show_game_over_menu():
                current_level = 0
                level_data = levels[current_level]
                platforms = level_data["platforms"]
                coins = level_data["coins"]
                door = level_data["door"]
                spikes = level_data.get("spikes", [])
                player = Player()
            else:
                running = False

        if player.rect.colliderect(door):
            level_up_sound.play()
            if not show_level_up_menu(current_level + 1):
                running = False
            else:
                current_level += 1
                if current_level >= len(levels):
                    show_victory_screen()
                    running = False
                else:
                    level_data = levels[current_level]
                    platforms = level_data["platforms"]
                    coins = level_data["coins"]
                    door = level_data["door"]
                    spikes = level_data.get("spikes", [])
                    player = Player()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
