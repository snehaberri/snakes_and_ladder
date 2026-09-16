import pygame
import sys
import random

def tic_tac_toe():
    WIDTH, HEIGHT = 600, 600
    LINE_COLOR = "#ffb3b3"
    BG_COLOR = "#4d0000"
    X_COLOR = "#aeb9ff"
    O_COLOR = "#ffcce5"
    LINE_WIDTH = 5
    CROSS_WIDTH = 15
    CIRCLE_WIDTH = 15
    CELL_SIZE = WIDTH // 3
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini-Game: Tic Tac Toe")
    font = pygame.font.Font(None, 56)
    small_font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    
    def new_board():
        return [None] * 9
    
    def draw_grid():
        # Vertical lines
        pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE, 0), (CELL_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE * 2, 0), (CELL_SIZE * 2, HEIGHT), LINE_WIDTH)
        
        # Horizontal lines
        pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE), (WIDTH, CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE * 2), (WIDTH, CELL_SIZE * 2), LINE_WIDTH)
        
    def draw_x(cell_index):
        row = cell_index // 3
        col = cell_index % 3
        padding = CELL_SIZE // 6
        x1 = col * CELL_SIZE + padding
        y1 = row * CELL_SIZE + padding
        x2 = (col + 1) * CELL_SIZE - padding
        y2 = (row + 1) * CELL_SIZE - padding
        
        pygame.draw.line(screen, X_COLOR, (x1, y1), (x2, y2), CROSS_WIDTH)
        pygame.draw.line(screen, X_COLOR, (x1, y2), (x2, y1), CROSS_WIDTH)
    
    def draw_o(cell_index):
        row = cell_index // 3
        col = cell_index % 3
        center = (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
        radius = CELL_SIZE // 3
        pygame.draw.circle(screen, O_COLOR, center, radius, CIRCLE_WIDTH)
    
    def draw_board(board):
        screen.fill(BG_COLOR)
        draw_grid()
        for i, mark in enumerate(board):
            if mark == 'X':
                draw_x(i)
            elif mark == 'O':
                draw_o(i)
        pygame.display.update()
    
    def check_winner(board):
        # Winning combinations
        win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]               # Diagonals
        ]
        
        for combo in win_combinations:
            if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
                return board[combo[0]]
        return None
    
    def is_board_full(board):
        return None not in board
    
    def get_empty_cells(board):
        return [i for i, cell in enumerate(board) if cell is None]
    
    def bot_move(board):
        """Choose the strongest available move for O using minimax."""
        def minimax(maximizing, depth):
            winner = check_winner(board)
            if winner == 'O':
                return 10 - depth
            if winner == 'X':
                return depth - 10
            empty = get_empty_cells(board)
            if not empty:
                return 0

            scores = []
            for cell in empty:
                board[cell] = 'O' if maximizing else 'X'
                scores.append(minimax(not maximizing, depth + 1))
                board[cell] = None
            return max(scores) if maximizing else min(scores)

        empty_cells = get_empty_cells(board)
        if not empty_cells:
            return None

        best_cell = empty_cells[0]
        best_score = float('-inf')
        for cell in empty_cells:
            board[cell] = 'O'
            score = minimax(False, 1)
            board[cell] = None
            if score > best_score:
                best_score, best_cell = score, cell
        return best_cell
    
    def draw_text(text, font, color, y_offset=0):
        rendered = font.render(text, True, color)
        text_rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
        screen.blit(rendered, text_rect)
    
    # Initialize game
    board = new_board()
    current_player = 'X'  # Player is X, Bot is O
    game_over = False
    winner = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if current_player == 'X':  # Player's turn
                    mouse_pos = pygame.mouse.get_pos()
                    col = mouse_pos[0] // CELL_SIZE
                    row = mouse_pos[1] // CELL_SIZE
                    cell_index = row * 3 + col
                    
                    if cell_index in get_empty_cells(board):
                        board[cell_index] = 'X'
                        
                        # Check for winner
                        if check_winner(board):
                            winner = 'X'
                            game_over = True
                        elif is_board_full(board):
                            game_over = True
                        else:
                            current_player = 'O'
        
        # Bot's turn
        if current_player == 'O' and not game_over:
            pygame.time.wait(500)  # Small delay for realism
            bot_cell = bot_move(board)
            if bot_cell is not None:
                board[bot_cell] = 'O'
                
                if check_winner(board):
                    winner = 'O'
                    game_over = True
                elif is_board_full(board):
                    game_over = True
                else:
                    current_player = 'X'
        
        # Draw everything
        draw_board(board)
        
        if game_over:
            if winner:
                if winner == 'X':
                    result_text = "You Win!"
                    result_color = X_COLOR
                else:
                    result_text = "Bot Wins!"
                    result_color = O_COLOR
            else:
                result_text = "It's a Draw!"
                result_color = (255, 255, 255)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            draw_text(result_text, font, result_color, -30)
            draw_text("Click to play again", small_font, (200, 200, 200), 40)
            pygame.display.update()
            
            # Wait for click to restart
            waiting_for_restart = True
            while waiting_for_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Restart game
                        board = new_board()
                        current_player = 'X'
                        game_over = False
                        winner = None
                        waiting_for_restart = False
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    tic_tac_toe()