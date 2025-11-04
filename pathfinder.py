import pygame
import random
import time
import sys
import os

# Tentamos usar winsound para sons no Windows; se não disponível, usamos pygame.mixer como fallback
try:
    import winsound
    _HAS_WINSOUND = True
except Exception:
    _HAS_WINSOUND = False

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("MatemáticA* Dijkstra")

# --- Cores ---
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)


class Node:
    """Representa uma célula no grid."""
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.parent = None

    def get_pos(self):
        return self.row, self.col

    def is_obstacle(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == PURPLE

    def is_end(self):
        return self.color == ORANGE

    def is_path(self):
        return self.color == BLUE

    def reset(self):
        self.color = WHITE
        self.parent = None

    def make_start(self):
        self.color = PURPLE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_obstacle(self):
        self.color = BLACK

    def make_end(self):
        self.color = ORANGE

    def make_path(self):
        self.color = BLUE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        """Atualiza lista de vizinhos 4-direções (ignora obstáculos)."""
        self.neighbors = []
        # baixo
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row + 1][self.col])
        # cima
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row - 1][self.col])
        # direita
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col + 1])
        # esquerda
        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col - 1])


def play_click_sound():
    """Toca um som curto de clique. Usa winsound no Windows quando disponível."""
    try:
        if _HAS_WINSOUND:
            # frequência, duração(ms)
            winsound.Beep(800, 60)
        else:
            # fallback simples usando pygame.mixer (se inicializado)
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            # gera um pequeno tom sintetizado (curto) - se não funcionar, ignora
            arr = pygame.sndarray.make_sound(
                (pygame.surfarray.array2d(pygame.Surface((1, 1))) * 0).astype('int16')
            )
            arr.play()
    except Exception:
        # Se tudo falhar, não atrapalha a execução
        pass


def play_hover_sound():
    """Som curto ao posicionar o cursor sobre um botão."""
    try:
        if _HAS_WINSOUND:
            winsound.Beep(1000, 35)
    except Exception:
        pass


def play_error_sound():
    """Som de aviso/erro."""
    try:
        if _HAS_WINSOUND:
            winsound.Beep(480, 120)
    except Exception:
        pass


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid


def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid_lines(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = y // gap
    col = x // gap
    return row, col


def dumb_search(draw, grid, start, end):
    """
    "Burro e lento": caminhada aleatória com marcação de visitados e backtracking simples.
    Serve como placeholder enquanto os alunos implementam algoritmos reais em outros arquivos.
    """
    # iniciamos a busca
    visited = set()
    stack = [start]
    start.parent = None
    start.g_score = 0

    while stack:
        # Mantém a janela responsiva
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        # Marca nós para visual (aberto/vermelho)
        if not current.is_start() and not current.is_end():
            current.make_closed()

        draw()
        time.sleep(0.01)  # torna a busca visível (intencionalmente lenta)

        if current == end:
            # Reconstrói caminho ingênuo
            node = current
            while node and not node.is_start():
                node.make_path()
                node = node.parent
            return True

        # Atualiza vizinhos e empilha em ordem aleatória
        current.update_neighbors(grid)
        neighbors = list(current.neighbors)
        random.shuffle(neighbors)
        for n in neighbors:
            if n not in visited and not n.is_obstacle():
                n.parent = current
                n.make_open()
                stack.append(n)

    return False


class Button:
    """UI simples para menu: retângulo com texto e callback."""
    def __init__(self, rect, text, callback, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.hovered = False

    def draw(self, surface):
        # cor varia se estiver em hover
        color = (200, 200, 200) if self.hovered else GREY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        txt = self.font.render(self.text, True, BLACK)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_hover(self, pos):
        return self.rect.collidepoint(pos)


def show_tutorial_screen(win):
    """Mostra instruções simples sobre a atividade (leia o README para mais detalhes)."""
    win.fill(WHITE)
    font = pygame.font.SysFont(None, 22)
    lines = [
        "Tutorial rápido:",
        "- Clique para definir o nó INÍCIO (primeiro clique) e o nó FIM (segundo clique).",
        "- Depois, clique em outras células para desenhar OBSTÁCULOS.",
        "- Teclas na tela do grid:",
        "    • 'A' → roda A* (no momento usa um placeholder).",
        "    • 'D' → roda Dijkstra (placeholder).",
        "    • 'C' → limpa todo o grid.",
        "    • 'R' → limpa apenas o caminho, mantendo obstáculos.",
        "Atividade: implemente os algoritmos em 'astar_impl.py' e 'dijkstra_impl.py'.",
        "Consulte o README para instruções detalhadas e critérios de avaliação."
    ]
    y = 80
    for line in lines:
        surf = font.render(line, True, BLACK)
        win.blit(surf, (40, y))
        y += 28
    pygame.display.update()


def main_app(win, width):
    ROWS = 40
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row >= ROWS or col >= ROWS:
                    continue
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_obstacle()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row >= ROWS or col >= ROWS:
                    continue
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                if node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and start and end:
                    # prepara vizinhos
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    play_click_sound()
                    _draw_status(win, "Executando A* (placeholder)...")
                    dumb_search(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    _draw_status(win, "Execução finalizada.")

                if event.key == pygame.K_d and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    play_click_sound()
                    _draw_status(win, "Executando Dijkstra (placeholder)...")
                    dumb_search(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    _draw_status(win, "Execução finalizada.")

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                if event.key == pygame.K_r:
                    for row in grid:
                        for node in row:
                            if node.is_open() or node.is_closed() or node.is_path():
                                node.reset()
                            if node.is_start():
                                start = node
                                start.make_start()
                            if node.is_end():
                                end = node
                                end.make_end()


def main_menu(win, width):
    """Mostra menu inicial com botões: Iniciar, Tutorial, Sair.

    Inclui animação simples no título, efeitos de hover com som, e uma
    barra de status em pt-br.
    """
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 48)
    title_text = "MatemáticA* Dijkstra"
    title = big_font.render(title_text, True, BLACK)

    # Define botões centrais (texto em pt-br)
    btn_w, btn_h = 220, 50
    center_x = width // 2
    start_btn = Button((center_x - btn_w // 2, 220, btn_w, btn_h), "Iniciar", lambda: None, font)
    tutorial_btn = Button((center_x - btn_w // 2, 290, btn_w, btn_h), "Tutorial", lambda: None, font)
    exit_btn = Button((center_x - btn_w // 2, 360, btn_w, btn_h), "Sair", lambda: None, font)

    status = "Clique em 'Iniciar' para abrir o grid."
    last_hovered = None
    title_pulse = 0.0
    pulse_dir = 1

    while True:
        win.fill(WHITE)

        # animação simples no título (pulso)
        title_pulse += 0.025 * pulse_dir
        if title_pulse > 0.6:
            pulse_dir = -1
        if title_pulse < -0.6:
            pulse_dir = 1
        scale = 1.0 + title_pulse * 0.03
        title_surf = pygame.transform.rotozoom(title, 0, scale)
        win.blit(title_surf, (width//2 - title_surf.get_width()//2, 100))

        # detecta hover e desenha botões
        mouse_pos = pygame.mouse.get_pos()
        for btn in (start_btn, tutorial_btn, exit_btn):
            hovered_now = btn.is_hover(mouse_pos)
            if hovered_now and not btn.hovered:
                play_hover_sound()
            btn.hovered = hovered_now
            btn.draw(win)

        _draw_status(win, status)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if start_btn.is_clicked(pos):
                    play_click_sound()
                    status = "Abrindo o grid..."
                    _draw_status(win, status)
                    main_app(win, width)
                    status = "Clique em 'Iniciar' para abrir o grid."
                elif tutorial_btn.is_clicked(pos):
                    play_click_sound()
                    show_tutorial_screen(win)
                    # espera o usuário voltar com clique ou tecla
                    waiting = True
                    while waiting:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.KEYDOWN:
                                waiting = False
                elif exit_btn.is_clicked(pos):
                    play_click_sound()
                    pygame.quit()
                    return


def _draw_status(win, text):
    """Desenha uma barra de status na parte inferior com texto em pt-br."""
    font = pygame.font.SysFont(None, 20)
    rect = pygame.Rect(0, WIDTH - 28, WIDTH, 28)
    pygame.draw.rect(win, (245, 245, 245), rect)
    pygame.draw.line(win, GREY, (0, WIDTH - 28), (WIDTH, WIDTH - 28))
    txt = font.render(text, True, BLACK)
    win.blit(txt, (8, WIDTH - 22))
    pygame.display.update(rect)


if __name__ == "__main__":
    # Inicializa pygame e exibe menu
    pygame.init()
    try:
        main_menu(WINDOW, WIDTH)
    finally:
        pygame.quit()