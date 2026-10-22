from eventmanager import *
from board import HiveBoard
from board import HivePool
from copy import deepcopy
from random import random
import threading

class HiveModel(object):
    def __init__(self, event_manager):
        '''
        Initialises global variables and registers as a listener to the event manager
        '''
        self.event_manager = event_manager
        event_manager.register_listener(self)
        self.minimax_player = [False, False]
        self.difficulty = 3
        self.state = 'not_running'
        self.player = 0 # 0 is white, 1 is black
        self.whitePool = HivePool('0')
        self.blackPool = HivePool('1')
        self.game_over = None
        self.game = HiveBoard(self)

    def initialise(self):
        '''
        Initialises the board, pools, and global variables
        '''
        self.player = 0
        self.whitePool = HivePool('0')
        self.blackPool = HivePool('1')
        self.game_over = None
        self.game = HiveBoard(self)
        self.thinking = False

    def run(self):
        '''
        Start the running of the game
        '''
        self.event_manager.post(InitEvent())
        self.event_manager.post(StateEvent('main_menu'))
        while self.state != 'not running':
            self.event_manager.post(TickEvent())
    
    def move(self, from_coord, to_coord, piece):
        '''
        Move a piece and then clean up empty tiles
        '''
        self.game.update_value(to_coord, piece)
        self.game.pop_value(from_coord)
        if self.player == 0:
            self.game.white_turns += 1
        elif self.player == 1:
            self.game.black_turns += 1
        self.player = (self.player+1)%2
        self.game_over = self.game.is_over()
        self.game.check_neighbours(to_coord)
        self.game.remove_extras()

    def place(self, to_coord, piece):
        '''
        Place a piece on the board from a pool
        '''
        self.game.update_value(to_coord, piece)
        if self.player == 0:
            self.whitePool.pop_value(piece)
            self.game.white_turns += 1
        else:
            self.blackPool.pop_value(piece)
            self.game.black_turns += 1
        self.player = (self.player+1)%2
        self.game.check_neighbours(to_coord)
        self.game_over = self.game.is_over()
    
    def check_for_passes(self):
        '''
        At the end of either players turn, check to see if the next player has any legal moves
        '''
        print(self.evaluate(self.game, self.whitePool, self.blackPool)[0])
        if self.game.is_over():
            return
        forced_pass = True
        for hex in self.game.board: # moves
            piece = self.game.board.get(hex)[-1]
            if piece[:1] == str(self.player):
                if len(self.game.possible_moves(hex, piece, self.whitePool, self.blackPool)) > 0:
                    forced_pass = False
                    break
        if forced_pass and self.player == 0: # white placements
            for hex in self.whitePool.pool:
                piece = self.whitePool.pool.get(hex)
                if piece != ['-'] and len(self.game.possible_placements(piece[-1], self.whitePool, self.blackPool)) > 0:
                    forced_pass = False
                    break
        if forced_pass and self.player == 1: # black placements
            for hex in self.blackPool.pool:
                piece = self.blackPool.pool.get(hex)
                if piece != ['-'] and len(self.game.possible_placements(piece[-1], self.whitePool, self.blackPool)) > 0:
                    forced_pass = False
                    break
        if forced_pass:
            self.event_manager.post(TurnEvent('pass', None, None, None))

    def process_event(self, event):
        '''
        Process an event posted by the event manager
        '''
        if isinstance(event, QuitEvent):
            self.state = 'not running'
        elif isinstance(event, TurnEvent):
            if event.type == 'move':
                if event.to_coord in self.game.possible_moves(event.from_coord, event.piece, self.whitePool, self.blackPool):
                    self.move(event.from_coord, event.to_coord, event.piece)
                    self.check_for_passes()
                    if self.minimax_player[self.player]:
                        t = threading.Thread(target=self.minimax_turn)
                        t.start()
                        
            elif event.type == 'placement':
                if event.to_coord in self.game.possible_placements(event.piece, self.whitePool, self.blackPool):
                    self.place(event.to_coord, event.piece)
                    self.check_for_passes()
                    if self.minimax_player[self.player]:
                        t = threading.Thread(target=self.minimax_turn)
                        t.start()
            elif event.type == 'pass':
                if self.player == 0:
                    self.game.white_turns += 1
                elif self.player == 1:
                    self.game.black_turns += 1
                self.player = (self.player+1)%2
                self.check_for_passes()
                if self.minimax_player[self.player]:
                    t = threading.Thread(target=self.minimax_turn)
                    t.start()

        elif isinstance(event, StateEvent):
            self.state = event.state
            if self.state == 'play':
                self.initialise()
                self.event_manager.post(TickEvent())
                if self.minimax_player[self.player]:
                    t = threading.Thread(target=self.minimax_turn)
                    t.start()
    
    def minimax_turn(self):
        '''
        Handles the logic for the computer player's turn
        '''
        if self.game.is_over():
            return
        self.thinking = True
        DEPTH = 3
        if self.player == 0:
            move = self.minimax(deepcopy(self.game), DEPTH, True, deepcopy(self.whitePool), deepcopy(self.blackPool)) # [static_eval, type (a move or place), from_coord, to_coord, piece]
        else:
            move = self.minimax(deepcopy(self.game), DEPTH, False, deepcopy(self.whitePool), deepcopy(self.blackPool)) # [static_eval, type (a move or place), from_coord, to_coord, piece]
        self.event_manager.post(TurnEvent(move[1], move[2], move[3], move[4]))
        self.thinking = False

    def minimax_move(self, game, piece, from_coord, to_coord):
        '''
        Makes a move on the minimax algorithm's copy of the board. Also used to undo moves made by minimax
        '''
        game.update_value(to_coord, piece)
        if game.board.get(from_coord) == ['-']:
            del game.board[from_coord]
        else:
            game.pop_value(from_coord)
        game.check_neighbours(to_coord)
        game.remove_extras()

    def minimax_place(self, game, pool, piece, to_coord):
        '''
        Places a piece on the minimax algorithm's copy of the board
        '''
        game.update_value(to_coord, piece)
        pool.pop_value(piece)
        game.check_neighbours(to_coord)
    
    def revert_place(self, game, pool, piece, to_coord):
        '''
        Undoes placements made by minimax
        '''
        if game.board.get(to_coord) == ['-']:
            del game.board[to_coord]
        else:
            game.pop_value(to_coord)
        pool.update_value(piece)
        game.check_neighbours(to_coord)
        game.remove_extras()
    
    def minimax(self, game, depth, maximising_player, whitePool, blackPool, alpha = float('-inf'), beta = float('inf')):
        '''
        Recursive function that determines the best move for the computer player
        '''
        over = game.is_over()
        if over != []:
            if over == ['white']:
                return [float('inf')]
            if over == ['black']:
                return [float('-inf')]
            return 0
        if depth == 0:
            return self.evaluate(game, whitePool, blackPool)
        
        if maximising_player:
            max_eval = float('-inf')
            max_type = None
            max_from_coord = None
            max_to_coord = None
            max_piece = None
            moves = [[game.board.get(coord)[-1], coord, game.possible_moves(coord, game.board.get(coord)[-1], whitePool, blackPool)] for coord in game.board if game.board.get(coord)[-1][:1] == '0']
            children = set()
            for piece, from_coord, to_coords in moves:
                for to_coord in to_coords:
                    children.add((piece, from_coord, to_coord, 'move'))
            queen_placements = game.possible_placements('0Q', whitePool, blackPool)
            other_placements = game.possible_placements('0A', whitePool, blackPool)
            pieces = [piece for piece in whitePool.pool if whitePool.pool.get(piece) != ['-']]
            for piece in pieces:
                if piece[1:] == 'Q':
                    for placement in queen_placements:
                        children.add((piece, None, placement, 'placement'))
                else:
                    for placement in other_placements:
                        children.add((piece, None, placement, 'placement'))
            for child in children: # each child is (piece, from_coord, to_coord, type)
                if child[3] == 'move':
                    self.minimax_move(game, child[0], child[1], child[2]) # apply the move to the position
                    game.white_turns += 1
                    eval = self.minimax(game, depth - 1, False, whitePool, blackPool, alpha, beta)[0]
                    game.white_turns -= 1
                    self.minimax_move(game, child[0], child[2], child[1]) # revert the move - might need to be a separate func to decrement the turn counter
                elif child[3] == 'placement':
                    self.minimax_place(game, whitePool, child[0], child[2]) # apply the placement to the position
                    game.white_turns += 1
                    eval = self.minimax(game, depth - 1, False, whitePool, blackPool, alpha, beta)[0]
                    game.white_turns -= 1
                    self.revert_place(game, whitePool, child[0], child[2]) # revert the placement
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                if eval > max_eval:
                    max_eval = eval
                    max_piece = child[0]
                    max_from_coord = child[1]
                    max_to_coord = child[2]
                    max_type = child[3]
            return [max_eval, max_type, max_from_coord, max_to_coord, max_piece]
        
        else:
            min_eval = float('inf')
            min_type = None
            min_from_coord = None
            min_to_coord = None
            min_piece = None
            # moves = [[piece, coord of piece, possible_moves of piece], [...]]
            moves = [[game.board.get(coord)[-1], coord, game.possible_moves(coord, game.board.get(coord)[-1], whitePool, blackPool)] for coord in game.board if game.board.get(coord)[-1][:1] == '1'] #[(from_coord, set of to_coords), ...]
            children = set()
            for piece, from_coord, to_coords in moves:
                for to_coord in to_coords:
                    children.add((piece, from_coord, to_coord, 'move'))
            queen_placements = game.possible_placements('1Q', whitePool, blackPool)
            other_placements = game.possible_placements('1A', whitePool, blackPool)
            pieces = [piece for piece in blackPool.pool if blackPool.pool.get(piece) != ['-']]
            for piece in pieces:
                if piece[1:] == 'Q':
                    for placement in queen_placements:
                        children.add((piece, None, placement, 'placement'))
                else:
                    for placement in other_placements:
                        children.add((piece, None, placement, 'placement'))
            for child in children: # each child is (piece, from_coord, to_coord, type)
                if child[3] == 'move':
                    self.minimax_move(game, child[0], child[1], child[2]) # apply the move to the position
                    game.black_turns += 1 # doesnt fix the bees moving back and forth, but might still fix something
                    eval = self.minimax(game, depth - 1, True, whitePool, blackPool, alpha, beta)[0]
                    game.black_turns -= 1
                    self.minimax_move(game, child[0], child[2], child[1]) # revert the move
                elif child[3] == 'placement':
                    self.minimax_place(game, blackPool, child[0], child[2]) # apply the placement to the position
                    game.black_turns += 1
                    eval = self.minimax(game, depth - 1, True, whitePool, blackPool, alpha, beta)[0]
                    game.black_turns -= 1
                    self.revert_place(game, blackPool, child[0], child[2]) # revert the placement
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                if eval < min_eval:
                    min_eval = eval
                    min_piece = child[0]
                    min_from_coord = child[1]
                    min_to_coord = child[2]
                    min_type = child[3]
            return [min_eval, min_type, min_from_coord, min_to_coord, min_piece]
    
    def evaluate(self, game, whitePool, blackPool):
        '''
        Uses heuristics to evaluate the board once the maximum depth for minimax has been reached
        '''
        white_queen_neighbours = 0 # -
        black_queen_neighbours = 0 # +
        white_beetle_pins = 0 # +
        black_beetle_pins = 0 # -
        free_white_pieces = [0, 0, 0, 0, 0] # QABGS
        free_black_pieces = [0, 0, 0, 0, 0] # QABGS
        for coord in game.board:
            piece_stack = game.board.get(coord)
            piece = piece_stack[-1]
            if piece_stack != ['-']:

                # Number of pieces adjacent to each queen
                if len(piece_stack) > 1:
                    if piece_stack[1] =='0Q': # of Q neighbours
                        white_queen_neighbours += sum([1 for neighbour in neighbours(coord) if game.board.get(neighbour) != ['-']])# / 6
                    if piece_stack[1] =='1Q':
                        black_queen_neighbours += sum([1 for neighbour in neighbours(coord) if game.board.get(neighbour) != ['-']])# / 6

                # Number of beetles pinning a piece
                if len(piece_stack) > 2 and piece == '0B' and '1' in list(map(lambda x: x[:1], piece_stack[1:-1])):
                    white_beetle_pins += 1 # maybe make pinned queens a separate counter to increase the weight, and not necessarily just by beetles
                elif len(piece_stack) > 2 and piece == '1B' and '0' in list(map(lambda x: x[:1], piece_stack[1:-1])):
                    black_beetle_pins += 1
                
                if len(piece_stack) > 1 and len(game.possible_moves(coord, piece, whitePool, blackPool)) != 0:
                    if piece[:1] == '0':
                        if piece[1:] == 'Q':
                            free_white_pieces[0] += 1
                        if piece[1:] == 'A':
                            free_white_pieces[1] += 1
                        if piece[1:] == 'B':
                            free_white_pieces[2] += 1
                        if piece[1:] == 'G':
                            free_white_pieces[3] += 1
                        if piece[1:] == 'S':
                            free_white_pieces[4] += 1
                    if piece[:1] == '1':
                        if piece[1:] == 'Q':
                            free_black_pieces[0] += 1
                        if piece[1:] == 'A':
                            free_black_pieces[1] += 1
                        if piece[1:] == 'B':
                            free_black_pieces[2] += 1
                        if piece[1:] == 'G':
                            free_black_pieces[3] += 1
                        if piece[1:] == 'S':
                            free_black_pieces[4] += 1

            # 5 Randomness - number between 0.75 and 1.25
        rand = 0.5 * random() + 0.75
        eval = rand * (2*(black_queen_neighbours - white_queen_neighbours) + white_beetle_pins - black_beetle_pins + sum(free_white_pieces) - sum(free_black_pieces))
        return [eval]
        
directions = [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]

def hex_add(hex_a, hex_b):
    '''
    Add two coordinates
    '''
    return (hex_a[0] + hex_b[0], hex_a[1] + hex_b[1])

def neighbours(hex):
    '''
    Returns a list of tiles neighbouring a coordinate
    '''
    return [hex_add(hex, direction) for direction in directions]

if __name__ == '__main__':
    print(dir(HiveModel))