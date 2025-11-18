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
        # x = pixel horizontal (col * width), y = pixel vertical (row * width)
        self.x = col * width
        self.y = row * width
        # state: 'empty','obstacle','start','end','open','closed','path'
        self.state = 'empty'
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.parent = None

    def get_pos(self):
        return self.row, self.col

    def is_obstacle(self):
        return self.state == 'obstacle'

    def is_start(self):
        return self.state == 'start'

    def is_end(self):
        return self.state == 'end'

    def is_path(self):
        return self.state == 'path'

    def is_open(self):
        return self.state == 'open'

    def is_closed(self):
        return self.state == 'closed'

    def reset(self):
        self.state = 'empty'
        self.parent = None

    def make_start(self):
        self.state = 'start'

    def make_closed(self):
        self.state = 'closed'

    def make_open(self):
        self.state = 'open'

    def make_obstacle(self):
        self.state = 'obstacle'

    def make_end(self):
        self.state = 'end'

    def make_path(self):
        self.state = 'path'

    def draw(self, win):
        # Recalcula posição/size baseado no tamanho atual da janela
        surf = pygame.display.get_surface()
        if surf is not None:
            actual_width = surf.get_width()
        else:
            actual_width = WIDTH
        gap = actual_width // self.total_rows
        x = self.col * gap
        y = self.row * gap
        size = gap

        # Seleciona cores segundo o tema atual
        theme = THEMES.get(CURRENT_THEME, THEMES['default'])
        color_map = {
            'empty': WHITE,
            'obstacle': theme['obstacle'],
            'start': theme['start'],
            'end': theme['end'],
            'open': theme['open'],
            'closed': theme['closed'],
            'path': theme['path'],
        }
        color = color_map.get(self.state, WHITE)
        pygame.draw.rect(win, color, (x, y, size, size))

        # Desenha letra para início/fim (I = Início, F = Fim)
        if self.state in ('start', 'end'):
            try:
                font_size = max(12, size // 2)
                font = pygame.font.SysFont(None, font_size)
                letter = 'I' if self.state == 'start' else 'F'
                txt = font.render(letter, True, BLACK)
                txt_rect = txt.get_rect(center=(x + size//2, y + size//2))
                win.blit(txt, txt_rect)
            except Exception:
                pass

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


# Temas de cor por algoritmo
THEMES = {
    'default': {
        'start': PURPLE,
        'end': ORANGE,
        'obstacle': BLACK,
        'open': GREEN,
        'closed': RED,
        'path': BLUE,
    },
    'astar': {
        'start': PURPLE,
        'end': ORANGE,
        'obstacle': BLACK,
        'open': (0, 200, 200),
        'closed': (150, 0, 200),
        'path': (0, 120, 255),
    },
    'dijkstra': {
        'start': PURPLE,
        'end': ORANGE,
        'obstacle': BLACK,
        'open': (0, 180, 0),
        'closed': (200, 80, 80),
        'path': (255, 140, 0),
    }
}

# Tema corrente (default)
CURRENT_THEME = 'default'


def set_theme(name: str):
    global CURRENT_THEME
    if name in THEMES:
        CURRENT_THEME = name
    else:
        CURRENT_THEME = 'default'


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
    surf = pygame.display.get_surface()
    if surf is not None:
        actual_width = surf.get_width()
    else:
        actual_width = width
    gap = actual_width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (actual_width, i * gap))
    for j in range(rows):
        pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, actual_width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    # redesenha os nós (Node.draw fará o cálculo baseado no tamanho atual)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid_lines(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    # Usa o tamanho atual da janela para calcular gap (corrige problemas de DPI/rescale)
    surf = pygame.display.get_surface()
    if surf is not None:
        actual_width = surf.get_width()
    else:
        actual_width = width
    gap = actual_width // rows
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

    # Modos de pincel (largura em células, sempre ímpar para centralizar)
    BRUSH_SIZES = [1, 3, 5]
    brush_index = 0

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)

        # Desenha destaque da célula sob o cursor (retângulo translúcido)
        try:
            surf = pygame.display.get_surface()
            if surf is not None:
                actual_width = surf.get_width()
            else:
                actual_width = width
            gap = actual_width // ROWS
            mx, my = pygame.mouse.get_pos()
            hover_row = my // gap
            hover_col = mx // gap
            if 0 <= hover_row < ROWS and 0 <= hover_col < ROWS:
                theme = THEMES.get(CURRENT_THEME, THEMES['default'])
                hcolor = theme.get('open', (200, 200, 0))

                # pinta destaque central
                highlight = pygame.Surface((gap, gap), pygame.SRCALPHA)
                highlight.fill((hcolor[0], hcolor[1], hcolor[2], 90))
                win.blit(highlight, (hover_col * gap, hover_row * gap))

                # desenha contorno do pincel (quadrado de brush_size)
                brush = BRUSH_SIZES[brush_index]
                radius = brush // 2
                left = max(0, hover_col - radius)
                top = max(0, hover_row - radius)
                right = min(ROWS - 1, hover_col + radius)
                bottom = min(ROWS - 1, hover_row + radius)
                outline_rect = pygame.Rect(left * gap, top * gap, (right - left + 1) * gap, (bottom - top + 1) * gap)
                pygame.draw.rect(win, (0, 0, 0), outline_rect, 2)
                pygame.display.update(outline_rect)
        except Exception:
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            # Permite pintar/arrastar mantendo o botão pressionado
            if event.type == pygame.MOUSEMOTION:
                buttons = event.buttons if hasattr(event, 'buttons') else pygame.mouse.get_pressed()
                if buttons[0]:
                    pos = event.pos
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        apply_brush(grid, ROWS, row, col, BRUSH_SIZES[brush_index], make_obstacle=True)
                if buttons[2]:
                    pos = event.pos
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        apply_brush(grid, ROWS, row, col, BRUSH_SIZES[brush_index], make_obstacle=False)

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
                    # aplica pincel ao clicar
                    apply_brush(grid, ROWS, row, col, BRUSH_SIZES[brush_index], make_obstacle=True)

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row >= ROWS or col >= ROWS:
                    continue
                apply_brush(grid, ROWS, row, col, BRUSH_SIZES[brush_index], make_obstacle=False)
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
                    # limpa as marcações de outro algoritmo e define tema para A*
                    clear_algorithm_marks(grid)
                    set_theme('astar')
                    play_click_sound()
                    _draw_status(win, "Executando A* (placeholder)...")
                    dumb_search(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    _draw_status(win, "Execução finalizada.")

                if event.key == pygame.K_d and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    # limpa as marcações de outro algoritmo e define tema para Dijkstra
                    clear_algorithm_marks(grid)
                    set_theme('dijkstra')
                    play_click_sound()
                    _draw_status(win, "Executando Dijkstra (placeholder)...")
                    dumb_search(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    _draw_status(win, "Execução finalizada.")

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                # Alterna modos de pincel
                if event.key == pygame.K_b:
                    brush_index = (brush_index + 1) % len(BRUSH_SIZES)
                    _draw_status(win, f"Tamanho do pincel: {BRUSH_SIZES[brush_index]}x{BRUSH_SIZES[brush_index]}")

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
                # Gerar labirinto automático
                if event.key == pygame.K_m:
                    play_click_sound()
                    _draw_status(win, "Gerando labirinto...")
                    generate_maze(grid, ROWS)
                    _draw_status(win, "Labirinto gerado. Defina início e fim.")


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
                # alterna modo de pincel se clicar com Ctrl + botão esquerdo no menu (opcional)
                elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # não faz nada específico aqui — comportamento mantido no grid
                    pass
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


def generate_maze(grid, rows):
    """Gera um labirinto simples usando algoritmo de backtracker (depth-first).

    A função assume que `rows` é ímpar para um melhor resultado; caso não
    seja, o algoritmo ainda funciona, mas o labirinto pode ficar diferente.
    """
    # Marca todas as células como obstáculos
    for r in range(rows):
        for c in range(rows):
            grid[r][c].make_obstacle()

    # Coordenadas dos caminhos serão as células com índices ímpares
    start_r, start_c = 1, 1
    if start_r >= rows or start_c >= rows:
        return

    stack = [(start_r, start_c)]
    grid[start_r][start_c].reset()

    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
    import random as _rand

    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows and 0 < nc < rows and grid[nr][nc].is_obstacle():
                neighbors.append((nr, nc))

        if neighbors:
            nr, nc = _rand.choice(neighbors)
            # Remove parede entre (r,c) e (nr,nc)
            wall_r = (r + nr) // 2
            wall_c = (c + nc) // 2
            grid[wall_r][wall_c].reset()
            grid[nr][nc].reset()
            stack.append((nr, nc))
        else:
            stack.pop()


def apply_brush(grid, rows, center_row, center_col, brush, make_obstacle=True):
    """Aplica o pincel (quadrado de tamanho `brush`) centrado em (center_row, center_col).

    Se `make_obstacle` for True, desenha obstáculos; caso contrário, reseta as células.
    Não sobrescreve os nós start/end.
    """
    radius = brush // 2
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            r = center_row + dr
            c = center_col + dc
            if 0 <= r < rows and 0 <= c < rows:
                node = grid[r][c]
                if node.is_start() or node.is_end():
                    continue
                if make_obstacle:
                    node.make_obstacle()
                else:
                    node.reset()


def clear_algorithm_marks(grid):
    """Limpa as marcações temporárias de algoritmo (open/closed/path).

    Mantém obstáculos, start e end.
    """
    for row in grid:
        for node in row:
            if node.state in ('open', 'closed', 'path'):
                node.reset()



if __name__ == "__main__":
    # Inicializa pygame e exibe menu
    pygame.init()
    try:
        main_menu(WINDOW, WIDTH)
    finally:
        pygame.quit()