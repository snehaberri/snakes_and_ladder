import pygame
import sys
import math
import time

def tic_tac_toe():

    WIDTH, HEIGHT = 600, 600
    LINE_COLOR = (23, 145, 135)
    BG_COLOR = (28, 170, 156)
    X_COLOR = (84, 84, 84)
    O_COLOR = (242, 235, 211)
    LINE_WIDTH = 10
    CROSS_WIDTH = 15
    CIRCLE_WIDTH = 15
    CELL_SIZE = WIDTH // 3
    
    pygame.init()
    screen= pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini- Game: Tic Tac Toe")
    font= pygame.font.Font(None, 56)
    small_font= pygame.font.Font(None, 36)
    clock= pygame.time.Clock()
    
    def new_board():
        return [None]*9
    
    def draw_grid():
        pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE,0),(CELL_SIZE, HEIGHT),LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE*2,0), (CELL_SIZE*2, HEIGHT), LINE_WIDTH)
        
        pygame.draw.line(screen, LINE_COLOR, (0,CELL_SIZE), (WIDTH, CELL_SIZE). LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR,(0, CELL_SIZE*2), (WIDTH, CELL_SIZE), LINE_WIDTH)
        
    def draw_x(cell_index):
        row= cell_index//3
        col= cell_index%3
        padding= CELL_SIZE//6
        x1= col*CELL_SIZE+padding
        y1= row*CELL_SIZE+padding
        x2= (col+1) * CELL_SIZE- padding
        y2= (row+1)*CELL_SIZE - padding
        
        pygame.draw.line(screen, X_COLOR(x1,y1), (x2,y2), CROSS_WIDTH)
        pygame.draw.line(screen, X_COLOR, (x1,y2), (x2,y1), CROSS_WIDTH)
    
    def draw_O(cell_index):
        row= cell_index//3
        col= cell_index%3
        center= (col * CELL_SIZE+ CELL_SIZE//2, row * CELL_SIZE+CELL_SIZE//2) 
        radius= CELL_SIZE//3
        pygame.draw.circle(screen, O_COLOR, center, radius,CIRCLE_WIDTH)  
        
    def render_board(board):
             