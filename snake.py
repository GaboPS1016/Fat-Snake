import cell
class snake:
    def __init__(self, m0, n0, game):
        self.lenght = 1
        self.body = [(m0, n0)]
        game.board[m0][n0].type_cell = cell.Type.snake
        
    def step(self, newm, newn, game):
        ate = False
        if game.board[newm][newn].type_cell == cell.Type.apple: ate = True
        game.board[newm][newn].type_cell = cell.Type.snake
        self.body.append((newm, newn))
        game.free_cells.remove((newm, newn)) 
        if not ate: 
            popy = self.body.pop(0)
            game.board[popy[0]][popy[1]].type_cell = cell.Type.empty
            game.free_cells.append(popy)
        else: game.apples_count -= 1
