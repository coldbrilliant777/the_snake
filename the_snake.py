import random
import sys
from random import randint

import pygame

INSTRUCTION_TEXT = [
    '+-----------------+',
    '    Score: {}',
    '+-----------------+',
    '> Движение - клавиши стрелок',
    '> Выход из игры - клавиша Esc',
    '> Яблоки - красные',
    '> Отрава - синяя',
    '> За каждые 5 съеденных яблок:',
    '  + 2 к скорости движения',
    '  + 1 отрава на экране',
    '',
]

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
INFO_AREA_WIDTH = 400

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь управления движениями
MOVEMENT_KEYS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}

# Цветовая палитра
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
LIGHT_GRAY = (200, 200, 200)
LIGHT_GREEN = (155, 188, 15)
DARK_GREEN = (15, 56, 15)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = BLACK

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = RED

# Цвет змейки
SNAKE_COLOR = GREEN

# Скорость движения змейки:
SPEED = 20

pygame.init()
FONT = pygame.font.Font(None, 24)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """
    Базовый класс, от которого наследуются все объекты.
    Содержит общие атрибуты: позиция и цвет.
    """

    def __init__(self, position=None, body_color=None):
        """
        Конструктор базового игрового объекта.
        Аргументы: position (координаты), body_color (цвет).
        """
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """
        Абстрактный метод для отрисовки объекта на экране.
        Аргумент: surface (поверхность, на которой рисуем).
        """
        pass


class Snake(GameObject):
    """Наследуемый класс змейки."""

    def __init__(self):
        super().__init__(body_color=DARK_GREEN)
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False

    def move(self):
        """Инициализация движения."""
        head = self.positions[0]
        new_head = ((head[0] + self.direction[0]) % GRID_WIDTH,
                    (head[1] + self.direction[1]) % GRID_HEIGHT)

        if new_head in self.positions[4:]:
            game_over('self')
            return False

        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        return True

    def draw_cell(self, position):
        """Отрисовка одной ячейки змейки."""
        rect = pygame.Rect(position[0] * GRID_SIZE,
                           position[1] * GRID_SIZE,
                           GRID_SIZE,
                           GRID_SIZE)
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовка на игровом поле."""
        for segment in self.positions:
            self.draw_cell(segment)

    def update_direction(self, new_direction):
        """Смена направления движения змейки."""
        if (-new_direction[0], -new_direction[1]) != self.direction:
            self.direction = new_direction

    def reset(self):
        """Сброс параметров змейки."""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False

    def get_head_position(self):
        """Получить позицию головы змейки."""
        return self.positions[0]

    def length(self):
        """Получить длину змейки."""
        return len(self.positions)


class Apple(GameObject):
    """
    Класс Apple. Наследуется от GameObject.
    Появляется в случайном месте поля.
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color=body_color)
        self.randomize_position()

    def randomize_position(self, occupied_cells=None):
        """Устанавливает случайные координаты для яблока."""
        if occupied_cells is None:
            occupied_cells = []

        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            self.position = (x, y)
            if self.position not in occupied_cells:
                break

    def draw(self, surface):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position[0] * GRID_SIZE,
                           self.position[1] * GRID_SIZE,
                           GRID_SIZE,
                           GRID_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def draw_game_area(snake, apple, bombs):
    """Игровое поле."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    for bomb in bombs:
        bomb.draw(screen)
    if apple.position is not None:
        apple.draw(screen)


def draw_info_area(score):
    """Информационное поле."""
    info_area = pygame.Rect(SCREEN_WIDTH - INFO_AREA_WIDTH, 0,
                            INFO_AREA_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, LIGHT_GRAY, info_area)
    y = 10
    for text in INSTRUCTION_TEXT:
        if '{}' in text:
            text = text.format(score)
        line = FONT.render(text, True, BLACK)
        screen.blit(line, (SCREEN_WIDTH - 390, y))
        y += 30


def reset_game(snake, apple, bombs):
    """Сброс параметров игры."""
    global score, frame_delay, apples_eaten
    score = 0
    frame_delay = 100
    apples_eaten = 0
    snake.reset()
    bombs.clear()
    occupied_cells = [*snake.positions, *(bomb.position for bomb in bombs)]
    apple.randomize_position(occupied_cells)


def game_over(collision_type):
    """Сценарий завершения игры."""
    font = pygame.font.Font(None, 36)
    text = font.render('Game over. Try again', True, RED)

    text_x = (SCREEN_WIDTH - INFO_AREA_WIDTH) // 2 - text.get_width() // 2
    text_y = SCREEN_HEIGHT // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))
    pygame.display.flip()
    pygame.time.delay(2000)


def handle_keys(snake):
    """Обработка пользовательского ввода."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key in MOVEMENT_KEYS:
                snake.update_direction(MOVEMENT_KEYS[event.key])


def main():
    """Главная функция."""
    global score, frame_delay, apples_eaten
    global snake, apple, bombs

    snake = Snake()
    apple = Apple()
    bombs = []

    reset_game(snake, apple, bombs)

    while True:
        handle_keys(snake)

        if not snake.move():
            game_over('self')
            reset_game(snake, apple, bombs)
            continue

        # Проверка на столкновение с самим собой
        if snake.get_head_position() in snake.positions[1:]:
            game_over('self')
            reset_game(snake, apple, bombs)
            continue

        # Проверка на столкновение с бомбой
        if snake.get_head_position() in [bomb.position for bomb in bombs]:
            game_over('bomb')
            reset_game(snake, apple, bombs)
            continue

        # Проверка на съедение яблока
        if snake.get_head_position() == apple.position:
            occupied_cells = [*snake.positions,
                              *(bomb.position for bomb in bombs)]
            apple.randomize_position(occupied_cells)
            snake.grow = True
            score += 1
            apples_eaten += 1

            if apples_eaten % 5 == 0:
                frame_delay -= 10
                if frame_delay < 30:
                    frame_delay = 30
                occupied_cells = [*snake.positions, apple.position,
                                  *(bomb.position for bomb in bombs)]
                bomb = Apple(body_color=BLUE)
                bomb.randomize_position(occupied_cells)
                bombs.append(bomb)

        draw_game_area(snake, apple, bombs)
        draw_info_area(score)

        pygame.display.flip()
        clock.tick(1000 // frame_delay)


if __name__ == "__main__":
    main()
    