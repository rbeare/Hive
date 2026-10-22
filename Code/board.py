from copy import deepcopy

class HiveBoard:
    def __init__(self, model):
        '''
        The board is a dictionary with each tile in the format {(x, y): stack} where stack is a list of the pieces in that stack.
        Initially there is only one empty tile in the centre of the screen, and the board grows as pieces are placed
        '''
        self.model = model
        self.board = {(0, 0): ['-']}
        self.white_turns = 0
        self.black_turns = 0

    def check_neighbours(self, coord):
        '''
        Makes sure that all pieces have neighbours in the data structure
        '''
        for neighbour in neighbours(coord):
            found = False
            for coord in self.board:
                if neighbour == coord:
                    found = True
                    break
            if not found:
                self.board.update({neighbour: ['-']})

    def remove_extras(self):
        '''
        Removes redundant tiles in the data structure
        '''
        occupied_spaces = [coord for coord in self.board if self.board.get(coord) not in [['-'], None]]
        if occupied_spaces:
            if len(occupied_spaces) > 1:
                for key in self.board.copy():
                    self.isolated = True
                    for neighbour in neighbours(key):
                        if neighbour in occupied_spaces:
                            self.isolated = False
                    if self.isolated:
                        del self.board[key]
            else:
                allowed = occupied_spaces + neighbours(occupied_spaces[0])
                for key in self.board.copy():
                    if key not in allowed:
                        del self.board[key]

    def update_value(self, coord, piece):
        '''
        Adds a piece to the stack at coord
        '''
        if self.board.get(coord) == None:
            self.board.update({coord: ['-', piece]})
        else:
            self.board.get(coord).append(piece)
    
    def pop_value(self, coord):
        '''
        Removes a piece from the stack at coord
        '''
        self.board.get(coord).pop()
    
    def one_hive_rule(self, moves, coord, piece):
        '''
        Ensures the hive remains connected
        '''
        def is_connected(hive_layout):
            visited = set()
            pieces = [pos for pos, content in hive_layout.items() if content and content != ['-']]
            if not pieces:
                return True
            # Depth-first search
            stack = [pieces[0]]
            while stack:
                pos = stack.pop()
                if pos not in visited:
                    visited.add(pos)
                    for neighbor in neighbours(pos):
                        if neighbor in hive_layout and hive_layout[neighbor] and hive_layout[neighbor] != ['-']:
                            stack.append(neighbor)
            return len(visited) == len(pieces)
        valid_moves = set()
        for move in moves:
            hive_copy = deepcopy(self.board)
            hive_copy[coord].pop() # Temporarily remove the piece from its current position
            if is_connected(hive_copy): # Check if the hive remains connected after removing the piece
                hive_copy[move].append(piece) # Temporarily place the piece in the new position
                if is_connected(hive_copy): # Check if the hive remains connected after the piece is moved
                    valid_moves.add(move)
                hive_copy[move].pop() # Revert the temporary placement
            hive_copy[coord].append(piece) # Restore the original position
        return valid_moves
        
    def freedom_to_move(self, coord):
        '''
        Generates the set of every move for a particular piece that obeys the freedom to move rule
        '''
        valid_moves = set()
        visited = set()
        def search(path):
            unoccupied_neighbours = [n for n in neighbours(path[-1]) if self.board.get(n) in [['-'], None]] # every unoccupied neighbour of the last hex in the path
            occupied_neighbours = [n for n in neighbours(path[-1]) if self.board.get(n) not in [['-'], None]] # change this and line above for one if statement
            for unoccupied_neighbour in unoccupied_neighbours: # check all unoccupied neighbours of the last hex in the path
                if unoccupied_neighbour != path[-2] and unoccupied_neighbour not in visited: # no backtracking or revisiting the same hex
                    for neighbour_of_neighbour in neighbours(unoccupied_neighbour): # check if two are adjacent so that there is a large enough gap for piece to slide through
                        if neighbour_of_neighbour in unoccupied_neighbours: # check if unnoccupied_neighbour and path[-1] have an UNoccupied neighbour in common #for some reason still works if occupied_neighbours used instead
                            shared_neighbour = False
                            for n in neighbours(unoccupied_neighbour):
                                if n in occupied_neighbours:
                                    shared_neighbour = True
                            if shared_neighbour:
                                valid_moves.add(unoccupied_neighbour)
                                visited.add(unoccupied_neighbour)
                                search(path + [unoccupied_neighbour])
        search([coord, coord])
        return valid_moves
            
    def spider(self, moves, coord):
        '''
        Generates the set of valid moves for a spider
        '''
        valid_moves = set()
        def dfs(current_path, remaining_steps): # recursive depth-first search of all paths of exactly 3 steps.
            if remaining_steps == 0:
                if current_path[-1] in moves: # Add the position to valid moves if in original moves list
                    valid_moves.add(current_path[-1])
                return
            for neighbor in neighbours(current_path[-1]):
                if neighbor not in current_path and neighbor in moves: # Check if neighbor is a valid move and not already in path
                    for neighbour_of_neighbour in neighbours(neighbor): # Check for shared neighbours
                        occupied_neighbours =  [n for n in neighbours(current_path[-1]) if self.board.get(n) not in [['-'], None]]
                        if neighbour_of_neighbour in occupied_neighbours:
                            dfs(current_path + [neighbor], remaining_steps - 1)
                            break
        dfs([coord], 3)
        return valid_moves

    def grasshopper(self, coord, piece):
        '''
        Generates the set of valid moves for a grasshopper
        '''
        valid_moves = set()
        for dir in range(6):
            def inc(dir):
                if dir == 2 or dir == 4:
                    return 0
                elif dir == 0 or dir == 5:
                    return 1
                return 2
            def dec(dir):
                if dir == 3 or dir == 5:
                    return 0
                elif dir == 1 or dir == 4:
                    return 1
                return 2
            current_coord = [coord[0], coord[1], coord[0] + coord[1]] # need to sum the x and y coords to get the z coord
            current_piece = piece # piece that grasshopper is trying to move to
            steps = 0
            while current_piece != ['-']:
                current_coord[inc(dir)] += 1 # direction = 0: 1(y), 1: 2(z), 2: 0(x), 3: 2(z), 4: 0(x), 5: 1(y)
                current_coord[dec(dir)] -= 1 # direction = 0: 2(z), 1: 1(y), 2: 2(z), 3: 0(x), 4: 1(y), 5: 0(x)
                current_piece = self.board.get((current_coord[0], current_coord[1]))
                steps += 1
            if steps > 1: # has to have jumped over at least one piece
                valid_moves.add((current_coord[0], current_coord[1]))
        return valid_moves

    def possible_moves(self, coord, piece, whitePool, blackPool): # the turns should be fine as they are part of HiveBoard
        '''
        The rules that define how pieces can be moved
        '''
        if piece[:1] == '0' and self.white_turns <= 3 and whitePool.pool.get("0Q") != ["-"]: #need to change the pools here so minimax uses the right ones
            return set()
        if piece[:1] == '1' and self.black_turns <= 3 and blackPool.pool.get("1Q") != ["-"]:
            return set()
        if piece[1:] == 'Q':
            moves = set([move for move in neighbours(coord) if self.board.get(move) == ['-']])
            moves = self.one_hive_rule(moves, coord, piece)
        elif piece[1:] == 'A':
            moves = set([move for move in self.board if self.board.get(move) == ['-']])
            moves = self.one_hive_rule(moves, coord, piece)
        elif piece[1:] == 'B':
            moves = set([move for move in neighbours(coord)])
            moves = self.one_hive_rule(moves, coord, piece)
        elif piece[1:] == 'G':
            moves = self.grasshopper(coord, piece)
            moves = self.one_hive_rule(moves, coord, piece)
        if piece[1:] == 'S':
            moves = set([move for move in self.board if self.board.get(move) == ['-']])
            moves = self.one_hive_rule(moves, coord, piece)
            moves = self.spider(moves, coord)
        if piece[1:] not in ['B', 'G']:
            moves = moves.intersection(self.freedom_to_move(coord))
        return moves
    
    def possible_placements(self, piece, whitePool, blackPool):
        '''
        The rules that define how pieces can be placed
        '''
        if piece[1:] != 'Q': # The queen must be placed within the first 4 turns
            if piece[:1] == '0' and self.white_turns == 3 and whitePool.pool.get("0Q") != ["-"]:
                return set()
            elif piece[:1] == '1' and self.black_turns == 3 and blackPool.pool.get("1Q") != ["-"]: #CHANGE THESE POOLS FOR MINIMAX
                return set()
        placements = set()
        if len(self.board) > 7: # first two pieces follow different placement rules - could replace w/ something like: if len(coord for coord in self.board if self.board.get(coord) != ['-']) > 2
            for hex in self.board:
                if self.board.get(hex) == ['-']:
                    valid = False
                    for neighbour in neighbours(hex):
                        if self.board.get(neighbour) != None:
                            if self.board.get(neighbour)[-1][:1] == piece[:1]:
                                valid = True
                            elif self.board.get(neighbour)[-1][:1] == str((int(piece[:1])+1)%2): # sometimes piece is empty, probably minimax not tracking empty pools properly or something
                                valid = False
                                break
                    if valid:
                        placements.add(hex)
            return placements
        return [hex for hex in self.board if self.board.get(hex) == ['-']]

    def is_over(self):
        '''
        Checks to see if the game is in a terminal state, and returns the winner
        '''
        over = False
        winner = []
        for coord in self.board:
            piece = self.board.get(coord)
            if piece != ['-']:
                if piece[1] == '0Q':
                    over = True
                    for neighbour in neighbours(coord):
                        if self.board.get(neighbour) in [['-'], None]:
                            over = False
                            break
                    if over == True:
                        winner.append('black')
                elif piece[1] == '1Q':
                    over = True
                    for neighbour in neighbours(coord):
                        if self.board.get(neighbour) in [['-'], None]:
                            over = False
                            break
                    if over == True:
                        winner.append('white')
        return winner

class HivePool:
    def __init__(self, colour):
        self.pool = {colour + 'Q': ['-', colour + 'Q'],
                    colour + 'B': ['-', colour + 'B', colour + 'B'],
                    colour + 'S': ['-', colour + 'S', colour + 'S'],
                    colour + 'G': ['-', colour + 'G', colour + 'G', colour + 'G'],
                    colour + 'A': ['-', colour + 'A', colour + 'A', colour + 'A'],}

    def pop_value(self, piece):
        self.pool.get(piece).pop()
    
    def update_value(self, piece):
        self.pool.get(piece).append(piece)

directions = [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]

def hex_add(hex_a, hex_b):
    return (hex_a[0] + hex_b[0], hex_a[1] + hex_b[1])

# returns a list of pieces adjacent to a given coordinate
def neighbours(hex):
    return [hex_add(hex, direction) for direction in directions]

if __name__ == '__main__':
    whitePool = HivePool('0')
    blackPool = HivePool('1')
    print(whitePool.pool)
    print(blackPool.pool)