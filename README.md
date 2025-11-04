# MatemáticA* Dijkstra

Projeto educacional: visualizador e atividade para implementação dos algoritmos de pathfinding A* e Dijkstra.

Este repositório contém uma aplicação pedagógica em Python que permite visualizar um grid, colocar um nó inicial e final, desenhar obstáculos e executar um algoritmo placeholder. O objetivo é servir de base para uma atividade prática em que os alunos implementam as versões completas dos algoritmos em arquivos separados.

Visão geral do que está incluído

- `pathfinder.py` — aplicação principal (GUI) com menu, botões, efeitos sonoros (Windows via winsound quando disponível), animações simples e um algoritmo placeholder (busca "burra e lenta").
- `astar_impl.py` — stub para a implementação do A*. Deve conter `run_astar(draw, grid, start, end)`.
- `dijkstra_impl.py` — stub para a implementação de Dijkstra. Deve conter `run_dijkstra(draw, grid, start, end)`.

Requisitos

- Python 3.8+ (testado em Windows)
- Biblioteca: `pygame`

Instalação (passo a passo)

1. Crie e ative um ambiente virtual (opcional, recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

Se `requirements.txt` não existir, instale diretamente:

```powershell
pip install pygame
```

Execução

Para iniciar a aplicação (Windows PowerShell):

```powershell
python .\pathfinder.py
```

Uso rápido (interface)

- No menu inicial use os botões:
  - Iniciar — abre o grid e permite edição.
  - Tutorial — instruções rápidas na própria tela.
  - Sair — fecha o programa.

- No grid:
  - Clique para definir o nó INÍCIO (primeiro clique) e o nó FIM (segundo clique).
  - Clique em outras células para criar obstáculos.
  - Botões do teclado:
    - A → executa A* (atualmente um placeholder do exercício).
    - D → executa Dijkstra (placeholder).
    - C → limpa todo o grid.
    - R → limpa apenas o caminho, preservando obstáculos.

Efeitos sonoros e visuais

- Efeitos de hover e clique são reproduzidos via `winsound.Beep` no Windows quando disponível. Caso contrário, o programa prossegue sem som.
- A interface inclui animação simples do título e feedback visual nos botões (hover/flash).

Atividade (consigna para estudantes)

Objetivo: implementar corretamente os algoritmos A* e Dijkstra, cada um em seu arquivo:

- `astar_impl.py` → implementar `run_astar(draw, grid, start, end)`
- `dijkstra_impl.py` → implementar `run_dijkstra(draw, grid, start, end)`

Contrato/API esperado

- `draw`: função sem argumentos que redesenha o grid (o algoritmo deve chamar `draw()` sempre que atualizar o estado para permitir visualização).
- `grid`: lista 2D de objetos `Node` (classe definida em `pathfinder.py`).
- `start`, `end`: instâncias de `Node` que representam o início e o fim.
- Retorno: `True` se o caminho for encontrado, `False` caso contrário.

Critérios de avaliação (sugestão)

- Correção: o algoritmo encontra um caminho válido e não atravessa obstáculos.
- Eficiência: tempo de execução aceitável em grids 40x40 (comparado com o placeholder).
- Qualidade do código: clareza, comentários, uso de estruturas de dados adequadas (ex.: fila de prioridade para A* / Dijkstra).
- Experiência visual: chama `draw()` em pontos apropriados para que o usuário veja a evolução do algoritmo.

Sugestões de extensão (opcional)

- Implementar heurísticas diversas (Manhattan, Euclidiana) e permitir seleção.
- Adicionar salvamento/carregamento de mapas.
- Adicionar suporte a movimento 8-direções.

Testes rápidos

Para testar localmente após implementar um dos algoritmos, altere o `pathfinder.py` para importar e invocar a função implementada no evento de tecla 'A' ou 'D'. Exemplo:

```python
from astar_impl import run_astar
# ...
run_astar(lambda: draw(win, grid, ROWS, width), grid, start, end)
```

Troubleshooting

- Se a janela não abrir, confirme que o ambiente gráfico está disponível e que `pygame` foi instalado.
- Em alguns ambientes (WSL sem servidor X, servidores headless), a interface gráfica não funcionará.
- Se `winsound` não estiver disponível (p.ex. não-Windows), sons serão silenciosamente ignorados.

Licença

Código fornecido para fins educacionais; adapte conforme sua política institucional.

Contato

Para qualquer dúvida sobre a atividade ou para receber uma solução de referência implementada, abra uma issue ou envie uma mensagem ao instrutor.
