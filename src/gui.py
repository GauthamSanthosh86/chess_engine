import os
import sys

import pygame

pygame.init()

# constants
width, height = 800, 800
square_size = width // 8
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

# colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
brown = (139, 69, 19)

# create the screen
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess Game")

_image_cache = {}


def load_image(color, type):
    key = (color, type)
    if key not in _image_cache:
        path = os.path.join(IMAGE_DIR, f"{color}_{type}.png")
        img = pygame.image.load(path)
        _image_cache[key] = pygame.transform.scale(img, (square_size, square_size))
    return _image_cache[key]


# chess piece class
class ChessPiece:
    def __init__(self, color, type):
        self.color = color
        self.type = type
        self.image = load_image(color, type)
        self.has_moved = False


# board and game state
board = [[None for _ in range(8)] for _ in range(8)]
current_player = "white"
selected_piece = None
selected_pos = None
game_over = False


def init_board():
    back_rank = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for col in range(8):
        board[0][col] = ChessPiece("black", back_rank[col])
        board[1][col] = ChessPiece("black", "pawn")
        board[6][col] = ChessPiece("white", "pawn")
        board[7][col] = ChessPiece("white", back_rank[col])


def draw_board():
    for row in range(8):
        for col in range(8):
            color = white if (row + col) % 2 == 0 else brown
            pygame.draw.rect(screen, color,
                             (col * square_size, row * square_size, square_size, square_size))
    if selected_pos:
        pygame.draw.rect(screen, green,
                         (selected_pos[1] * square_size, selected_pos[0] * square_size,
                          square_size, square_size), 5)

def draw_move_dots(selected_piece, selected_pos):
    if selected_piece is None or selected_pos is None:
        return
    valid_moves = get_valid_moves(selected_piece, selected_pos[0], selected_pos[1])
    for (r, c) in valid_moves:
        center = (c * square_size + square_size // 2, r * square_size + square_size // 2)
        pygame.draw.circle(screen, green, center, square_size // 8)
    



def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                screen.blit(piece.image, (col * square_size, row * square_size))


def slide_moves(piece, row, col, directions):
    """Moves for rook/bishop/queen: slide along each direction until blocked."""
    moves = []
    for dr, dc in directions:
        r, c = row + dr, col + dc
        while 0 <= r < 8 and 0 <= c < 8:
            if board[r][c] is None:
                moves.append((r, c))
            else:
                if board[r][c].color != piece.color:
                    moves.append((r, c))
                break
            r += dr
            c += dc
    return moves


def get_pseudo_moves(piece, row, col):
    """Moves that follow the piece's movement rules (may leave own king in check)."""
    moves = []
    if piece.type == "pawn":
        direction = -1 if piece.color == "white" else 1
        start_row = 6 if piece.color == "white" else 1
        # forward one
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            # forward two (only if the square in front is also empty)
            if row == start_row and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))
        # captures
        for dc in [-1, 1]:
            r, c = row + direction, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is not None and board[r][c].color != piece.color:
                    moves.append((r, c))
    elif piece.type == "rook":
        moves = slide_moves(piece, row, col, [(1, 0), (-1, 0), (0, 1), (0, -1)])
    elif piece.type == "bishop":
        moves = slide_moves(piece, row, col, [(1, 1), (1, -1), (-1, 1), (-1, -1)])
    elif piece.type == "queen":
        moves = slide_moves(piece, row, col, [(1, 0), (-1, 0), (0, 1), (0, -1),
                                              (1, 1), (1, -1), (-1, 1), (-1, -1)])
    elif piece.type == "knight":
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None or board[r][c].color != piece.color:
                    moves.append((r, c))
    elif piece.type == "king":
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8 and (board[r][c] is None or board[r][c].color != piece.color):
                    moves.append((r, c))
    return moves


def is_check(color):
    king_pos = None
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p.color == color and p.type == "king":
                king_pos = (r, c)
    if king_pos is None:
        return False

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color != color:
                if king_pos in get_pseudo_moves(piece, r, c):
                    return True
    return False


def get_valid_moves(piece, row, col):
    """Legal moves: pseudo moves that don't leave your own king in check."""
    legal = []
    for (r, c) in get_pseudo_moves(piece, row, col):
        captured = board[r][c]
        board[r][c] = piece
        board[row][col] = None
        in_check = is_check(piece.color)
        board[row][col] = piece
        board[r][c] = captured
        if not in_check:
            legal.append((r, c))
    return legal


def has_any_legal_move(color):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color == color:
                if get_valid_moves(piece, r, c):
                    return True
    return False


def handle_click(pos):
    global selected_piece, selected_pos, current_player, game_over
    if game_over:
        return

    col = pos[0] // square_size
    row = pos[1] // square_size
    if not (0 <= row < 8 and 0 <= col < 8):
        return

    clicked = board[row][col]

    if selected_piece is None:
        if clicked and clicked.color == current_player:
            selected_piece = clicked
            selected_pos = (row, col)
        return

    # clicking another of your own pieces switches the selection
    if clicked and clicked.color == current_player:
        selected_piece = clicked
        selected_pos = (row, col)
        return

    if (row, col) in get_valid_moves(selected_piece, selected_pos[0], selected_pos[1]):
        board[row][col] = selected_piece
        board[selected_pos[0]][selected_pos[1]] = None
        selected_piece.has_moved = True

        # pawn promotion
        if selected_piece.type == "pawn" and (row == 0 or row == 7):
            board[row][col] = ChessPiece(selected_piece.color, "queen")

        current_player = "black" if current_player == "white" else "white"

        if not has_any_legal_move(current_player):
            game_over = True
            if is_check(current_player):
                print(f"Checkmate! {current_player.capitalize()} loses.")
            else:
                print("Stalemate!")

    selected_piece = None
    selected_pos = None


def main():
    init_board()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())
        draw_board()
        draw_move_dots(selected_piece, selected_pos)
        draw_pieces()
        pygame.display.flip()


if __name__ == "__main__":
    main()