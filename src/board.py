# 1 -white pawn
# 2 -white knight
# 3 -white bishop
# 4 -white rook
# 5 -white queen
# 6 -white king
# -1 -black pawn
# -2 -black knight
# -3 -black bishop
# -4 -black rook
# -5 -black queen
# -6 -black king

SYMBOLS = {
    0: ".",
    1: "♙",   # white pawn
    2: "♘",   # white knight
    3: "♗",   # white bishop
    4: "♖",   # white rook
    5: "♕",   # white queen
    6: "♔",   # white king
    -1: "♟",  # black pawn
    -2: "♞",  # black knight
    -3: "♝",  # black bishop
    -4: "♜",  # black rook
    -5: "♛",  # black queen
    -6: "♚",  # black king
}
class Board:
    def __init__(self):
        self.state = [[-4,-2,-3,-5,-6,-3,-2,-4],
                      [-1,-1,-1,-1,-1,-1,-1,-1],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [1,1,1,1,1,1,1,1],
                      [4,2,3,5,6,3,2,4]]
    def __str__(self):
        line=[]
        for row in self.state:
            line.append(" ".join(str(SYMBOLS[x])for x in row))
        return "\n".join(line)

if __name__ == "__main__":
    board = Board()
    print(board)

