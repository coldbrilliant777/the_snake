from random import choice, randint
import sys
import pygame

INSTRUCTION_TEXT = [
    "+-----------------+",
    "    Score: {}",
    "+-----------------+",
    "> Движение - клавиши стрелок",
    "> Выход из игры - клавиша Esc",
    "> Яблоки - красные",
    "> Отрава - синяя",

    "> За каждые 5 съеденных яблок:",
    "  + 2 к скорости дижения",
    "  + 1 отрава на экране",
    "",
]

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
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
            self.position = (320, 240)
        else:
            self.position = position

    def draw(self, surface):
        """
        Абстрактный метод для отрисовки объекта на экране.
        Аргумент: surface (поверхность, на которой рисуем).
        """
        pass

class Snake(GameObject):
    """Наследуемый класс змейки."""

    def __init__(self):
        super().__init__(DARK_GREEN)
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False

    def move(self):
        """Инициализация движения."""
        head = self.positions[0]
        new_head = ((head[0] + self.direction[0]) % GRID_WIDTH,
                    (head[1] + self.direction[1]) % GRID_HEIGHT)

        if new_head in self.positions[4:]:
            game_over("self")
            return False

        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False

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

    def get_head_position(self):
        """Получить позицию головы змейки."""
        return self.positions[0]

    def length(self):
        """Получить длину змейки."""
        return len(self.positions)


class Apple(GameObject):
    """
    Класс Apple. Наследуются от GameObject.
    Появляется в случайном месте поля.
    """

    super().__init__(position=None, body_color=APPLE_COLOR)

    self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайные координаты для яблока.
        """
        max_x = 640 - 20
        max_y = 480 - 20

        x.random.randrange(0, max_x + 1, 20)
        y.random.randrange(0, max_y + 1, 20)

        self.position = (x, y)

    def draw(self, surface):
        """
        Отрисовывает яблоко на игровом поле.
        """

        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            20,
            20    
        )

        pygame.draw.rect(surface, self.body_color, rect)

def draw_info_area(score):
    """Информационное поле."""
    info_area = pygame.Rect(SCREEN_WIDTH - 400, 0, 400, SCREEN_HEIGHT)
    pygame.draw.rect(screen, LIGHT_GRAY, info_area)
    y = 10
    for text in INSTRUCTION_TEXT:
        if "{}" in text:
            text = text.format(score)
        line = FONT.render(text, True, BLACK)
        screen.blit(line, (SCREEN_WIDTH - 390, y))
        y += 30

def draw_game_area(snake, apple, bombs):
    """Игровое поле."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    for segment in snake.positions:
        snake.draw_cell(segment)
    for bomb in bombs:
        bomb.draw()

    if apple.position is not None:
        apple.draw()

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
    global score, screen, clock, frame_delay, snake, apple, bombs, apples_eaten
    pygame.init()
    pygame.display.set_caption('Змейка')

    snake = Snake()
    apple = Apple()
    bombs = []

    reset_game(snake, apple, bombs)
    frame_count = 0
    apples_eaten = 0

    while True:
        handle_keys(snake)

        if snake.move():
            game_over("self")
            continue

        collision = snake.positions[0] in snake.positions[1:]
        if collision:
            game_over("self")
            continue

        collision = snake.positions[0] in [bomb.position for
                                           bomb in bombs]
        if collision:
            game_over("bomb")
            continue

        if snake.get_head_position() == apple.position:
            occupied_cells = [*snake.positions, *(bomb.position
                                                  for bomb in bombs)]
            apple.randomize_position(occupied_cells)
            snake.grow = True
            score += 1
            apples_eaten += 1
            frame_count += 1

            if apples_eaten % 5 == 0:
                frame_delay -= 10
                occupied_cells = [*snake.positions, apple.position,
                                  *(bomb.position for bomb in bombs)]
                bomb = Apple(body_color=BLUE)
                if bomb is not None:
                    bomb.randomize_position(occupied_cells)
                bombs.append(bomb)

        draw_game_area(snake, apple, bombs)
        draw_info_area(score)

        pygame.display.flip()
        clock.tick(1000 // frame_delay)


if __name__ == "__main__":
    main()