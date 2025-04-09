import pygame
import sys
import random

pygame.init()

# Инициализация mixer для воспроизведения музыки
pygame.mixer.init()

# Получаем размеры экрана
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
FPS = 60
LIVES = 3

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (20, 50, 100)
LIGHT_BLUE = (70, 120, 255)
BUTTON_HOVER = (100, 150, 255)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Вова охота за яйцами")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

font = pygame.font.SysFont("Arial", int(HEIGHT * 0.05))

# Размеры объектов (адаптивные)
player_size = int(WIDTH * 0.035)
obstacle_size = int(WIDTH * 0.015)
coin_size = int(WIDTH * 0.02)
life_size = int(WIDTH * 0.02)

# Скорости
player_speed = int(WIDTH * 0.008)
obstacle_speed = int(HEIGHT * 0.006)

# Загрузка изображений с чётким масштабированием
player_texture = pygame.transform.smoothscale(pygame.image.load("player.png"), (player_size, int(player_size * 1.5)))
obstacle_texture = pygame.transform.smoothscale(pygame.image.load("obstacle.png"), (obstacle_size, int(obstacle_size * 1.4)))
coin_texture = pygame.transform.smoothscale(pygame.image.load("coin.png"), (coin_size, int(coin_size * 1.4)))

# Жизни
life_raw = pygame.image.load("heart.png").convert_alpha()
life_texture = pygame.transform.smoothscale(life_raw, (life_size, int(life_size * 1.2)))

# Начальные данные
player_pos = [WIDTH // 2, HEIGHT - 2 * player_size]
score = 0
lives = LIVES

obstacles = []
coins = []
life_animations = []

# Состояния кнопок
left_held = False
right_held = False

# Создание объектов
def create_obstacle():
    return [random.randint(0, WIDTH - obstacle_size), 0]

def create_coin():
    return [random.randint(0, WIDTH - coin_size), 0]

def detect_collision(player, obj, size):
    px, py = player
    ox, oy = obj
    return (px < ox + size and px + player_size > ox and py < oy + size and py + player_size > oy)

# Анимация потери жизни
def trigger_life_animation(pos):
    anim = {
        "surface": pygame.transform.smoothscale(life_raw, (life_size * 2, int(life_size * 2.4))),
        "pos": pos,
        "alpha": 255,
        "timer": 15
    }
    life_animations.append(anim)

def render_life_animations():
    for anim in life_animations[:]:
        anim["alpha"] -= 20
        anim["timer"] -= 1
        anim_surf = anim["surface"].copy()
        anim_surf.set_alpha(max(anim["alpha"], 0))
        x, y = anim["pos"]
        screen.blit(anim_surf, (x, y))
        if anim["timer"] <= 0:
            life_animations.remove(anim)

# Экран завершения игры
def game_over():
    while True:
        screen.fill(BLACK)
        over_text = font.render("Game Over! Final Score: " + str(score), True, WHITE)
        restart_text = font.render("Press F to Restart or L to Quit", True, WHITE)
        screen.blit(over_text, (WIDTH // 4, HEIGHT // 3))
        screen.blit(restart_text, (WIDTH // 4, HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    main()
                elif event.key == pygame.K_l:
                    pygame.quit()
                    sys.exit()

# Рисуем кнопки с красивым стилем
def draw_buttons():
    button_width = WIDTH // 4
    button_height = HEIGHT // 10

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Кнопка влево
    left_button = pygame.Rect(0, HEIGHT - button_height, button_width, button_height)
    if left_button.collidepoint(mouse_x, mouse_y):
        button_color = BUTTON_HOVER
    else:
        button_color = LIGHT_BLUE
    pygame.draw.rect(screen, button_color, left_button, border_radius=20)

    left_text = font.render("LEFT", True, BLACK)
    screen.blit(left_text, (button_width // 4, HEIGHT - button_height + button_height // 4))

    # Кнопка вправо
    right_button = pygame.Rect(WIDTH - button_width, HEIGHT - button_height, button_width, button_height)
    if right_button.collidepoint(mouse_x, mouse_y):
        button_color = BUTTON_HOVER
    else:
        button_color = LIGHT_BLUE
    pygame.draw.rect(screen, button_color, right_button, border_radius=20)

    right_text = font.render("RIGHT", True, BLACK)
    screen.blit(right_text, (WIDTH - button_width + button_width // 4, HEIGHT - button_height + button_height // 4))

# Обработка событий для мобильных устройств (касания и удержания)
def handle_touch_events():
    global player_pos, left_held, right_held

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Проверка нажатия на кнопку влево
            if 0 <= x <= WIDTH // 4 and HEIGHT - HEIGHT // 10 <= y <= HEIGHT:
                left_held = True

            # Проверка нажатия на кнопку вправо
            if WIDTH - WIDTH // 4 <= x <= WIDTH and HEIGHT - HEIGHT // 10 <= y <= HEIGHT:
                right_held = True

        if event.type == pygame.MOUSEBUTTONUP:
            x, y = event.pos

            # Отпускание кнопки влево
            if 0 <= x <= WIDTH // 4 and HEIGHT - HEIGHT // 10 <= y <= HEIGHT:
                left_held = False

            # Отпускание кнопки вправо
            if WIDTH - WIDTH // 4 <= x <= WIDTH and HEIGHT - HEIGHT // 10 <= y <= HEIGHT:
                right_held = False

# Основной игровой цикл
def main():
    global score, player_pos, obstacles, coins, lives, left_held, right_held
    score = 0
    lives = LIVES
    player_pos = [WIDTH // 2, HEIGHT - 2 * player_size]
    obstacles = []
    coins = []
    life_animations.clear()

    clock = pygame.time.Clock()

    # Воспроизведение фоновой музыки
    pygame.mixer.music.load("background_music.mp3")  # Замените на свой файл
    pygame.mixer.music.set_volume(0.2)  # Настройте громкость
    pygame.mixer.music.play(-1, 0.0)  # Циклическое воспроизведение музыки

    while True:
        handle_touch_events()  # Обрабатываем события с касаниями

        if random.randint(0, 20) == 0:
            obstacles.append(create_obstacle())
        if random.randint(0, 50) == 0:
            coins.append(create_coin())

        for obstacle in obstacles[:]:
            obstacle[1] += obstacle_speed
            if obstacle[1] > HEIGHT:
                obstacles.remove(obstacle)
            if detect_collision(player_pos, obstacle, obstacle_size):
                lives -= 1
                obstacles.remove(obstacle)
                if lives <= 0:
                    game_over()

        for coin in coins[:]:
            coin[1] += obstacle_speed
            if coin[1] > HEIGHT:
                coins.remove(coin)
            if detect_collision(player_pos, coin, coin_size):
                coins.remove(coin)
                score += 10

        # Обработка движения игрока при удержании кнопок
        if left_held and player_pos[0] > 0:
            player_pos[0] -= player_speed
        if right_held and player_pos[0] < WIDTH - player_size:
            player_pos[0] += player_speed

        screen.fill(BLACK)
        screen.blit(player_texture, (player_pos[0], player_pos[1]))

        for obstacle in obstacles:
            screen.blit(obstacle_texture, (obstacle[0], obstacle[1]))

        for coin in coins:
            screen.blit(coin_texture, (coin[0], coin[1]))

        # Счёт
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Жизни — ниже счёта
        for i in range(lives):
            screen.blit(life_texture, (10 + i * int(WIDTH * 0.03), int(HEIGHT * 0.07)))

        render_life_animations()

        # Рисуем кнопки управления
        draw_buttons()

        pygame.display.flip()
        clock.tick(FPS)

main()
