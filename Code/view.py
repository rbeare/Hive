import sys, pygame
from button import *
from eventmanager import *
from copy import deepcopy
from itertools import cycle
import random

class HiveView(object):
    def __init__(self, event_manager, model):
        '''
        Initialises global variables and registers as a listener to the event manager
        '''
        self.event_manager = event_manager
        event_manager.register_listener(self)
        self.model = model
        self.is_init = False
        self.screen_width = 1067
        self.screen_height = 800
        self.scale = min(self.screen_width/1172, self.screen_height/600)
        self.board_origin = (self.screen_width*0.5, self.screen_height*0.5)
        self.radius = 30
        self.render_stack = None
        self.selected_piece = None

    def initialise(self):
        '''
        Initialises global variables and pygame
        '''
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.is_init = True
        self.main_font = pygame.font.Font('assets/Exan-Regular.ttf', 32)
        self.BACKGROUND_COLOUR = '#191919'
        self.TEXT_COLOUR = '#F5F5F5'
        NUM_HEXAGONS = 30
        self.MAX_HEX_SIZE = 100
        self.MIN_HEX_SIZE = 30
        self.hexagons = []
        for _ in range(NUM_HEXAGONS):
            hex_x = random.randint(0, self.screen_width)
            hex_y = random.randint(0, self.screen_height)
            hex_size = random.randint(self.MIN_HEX_SIZE, self.MAX_HEX_SIZE)
            hex_piece = random.choice(['0', '1']) + random.choice(['Q', 'A', 'B', 'G', 'S'])
            self.hexagons.append([hex_x, hex_y, hex_size, hex_piece])
        self.clock = pygame.time.Clock()

    def process_event(self, event):
        '''
        Process an event posted by the event manager
        '''
        if isinstance(event, TickEvent):
            axial = self.get_axial_coords(pygame.mouse.get_pos())
            mouse_coord = (int(axial[0]), int(axial[1]))
            target_piece_stack = None
            for key in self.model.game.board:
                if mouse_coord == key:
                    target_piece_stack = self.model.game.board.get(key)
                    break
            if target_piece_stack is not None and len(target_piece_stack) > 2:
                from copy import deepcopy
                _, *self.render_stack = deepcopy(target_piece_stack)
            else:
                self.render_stack = None
            self.render()
            self.clock.tick(60)
        elif isinstance(event, InitEvent):
            self.initialise()
        elif isinstance(event, QuitEvent):
            self.is_init = False
            pygame.quit()
            sys.exit()
        elif isinstance(event, StateEvent):
            if event.state == 'play':
                self.selected_piece = None
                self.BACK_BUTTON = HiveButton(30, 30, '', self.main_font, 'white', 'green', pygame.transform.scale(pygame.image.load('assets/back_arrow.png'), (50, 50)))
                print(self.model.minimax_player, not self.model.minimax_player[0], not self.model.minimax_player[1])
                self.RESIGN_BUTTON_0 = HiveButton(40, self.screen_height//2 + 250, '', self.main_font, 'white', 'green', pygame.transform.scale(pygame.image.load('assets/resign.png'), (70, 70)))
                self.RESIGN_BUTTON_1 = HiveButton(self.screen_width - 40, self.screen_height//2 + 250, '', self.main_font, 'white', 'green', pygame.transform.scale(pygame.image.load('assets/resign.png'), (70, 70)))
                self.buttons = [self.BACK_BUTTON, self.RESIGN_BUTTON_0, self.RESIGN_BUTTON_1]
            elif event.state == 'options':
                self.BACK_BUTTON = HiveButton(30, 30, '', self.main_font, 'white', 'green', pygame.transform.scale(pygame.image.load('assets/back_arrow.png'), (50, 50)))
                self.buttons = [self.BACK_BUTTON]
                size = (60, 60)
                self.PLAYER_0 = RadioButton(100, 100, pygame.transform.scale(pygame.image.load('assets/radio_0.png'), size), pygame.transform.scale(pygame.image.load('assets/radio_1.png'), size), '  Player 1 minimax', self.main_font, self.model.minimax_player[0])
                self.PLAYER_1 = RadioButton(100, 150, pygame.transform.scale(pygame.image.load('assets/radio_0.png'), size), pygame.transform.scale(pygame.image.load('assets/radio_1.png'), size), '  Player 2 minimax', self.main_font, self.model.minimax_player[1])
                self.radio_buttons = [self.PLAYER_0, self.PLAYER_1]
            elif event.state == 'main_menu':
                size = (300, 65)
                self.NEW_GAME_BUTTON = HiveButton(self.screen_width*0.5, self.screen_height*0.5-40, 'PLAY', self.main_font, 'black', 'green', pygame.transform.scale(pygame.image.load('assets/buton.png'), size))
                self.OPTIONS_BUTTON = HiveButton(self.screen_width*0.5, self.screen_height*0.5+50, 'OPTIONS', self.main_font, 'black', 'green', pygame.transform.scale(pygame.image.load('assets/buton.png'), size))
                self.RULES_BUTTON = HiveButton(self.screen_width*0.5, self.screen_height*0.5+140, 'RULES', self.main_font, 'black', 'green', pygame.transform.scale(pygame.image.load('assets/buton.png'), size))
                self.QUIT_BUTTON = HiveButton(self.screen_width*0.5, self.screen_height*0.5+230, 'QUIT', self.main_font, 'black', 'green', pygame.transform.scale(pygame.image.load('assets/buton.png'), size))
                self.buttons = [self.NEW_GAME_BUTTON, self.OPTIONS_BUTTON, self.RULES_BUTTON, self.QUIT_BUTTON]
            elif event.state == 'rules':
                self.BACK_BUTTON = HiveButton(30, 30, '', self.main_font, 'white', 'green', pygame.transform.scale(pygame.image.load('assets/back_arrow.png'), (50, 50)))
                self.buttons = [self.BACK_BUTTON]
        elif isinstance(event, WindowResizeEvent):
            self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
            self.board_origin = (self.screen_width*0.5, self.screen_height*0.5)
            self.scale = min(self.screen_width/600, self.screen_height/1172)
        elif isinstance(event, InputEvent):
            if self.model.state == 'main_menu':
                if event.mouse_pos is not None:
                    for button in self.buttons:
                        if button.check_for_input(event.mouse_pos):
                            if button == self.NEW_GAME_BUTTON:
                                self.event_manager.post(StateEvent('play'))
                            if button == self.OPTIONS_BUTTON:
                                self.event_manager.post(StateEvent('options'))
                            if button == self.RULES_BUTTON:
                                self.event_manager.post(StateEvent('rules'))
                            if button == self.QUIT_BUTTON:
                                self.event_manager.post(QuitEvent())
            elif self.model.state == 'play':
                if event.mouse_pos is not None:
                    for button in self.buttons:
                        if button.check_for_input(event.mouse_pos):
                            if button == self.BACK_BUTTON:
                                self.event_manager.post(StateEvent('main_menu'))
                            if not self.model.game_over:
                                if button == self.RESIGN_BUTTON_0:
                                    self.model.game_over = ['black']
                                elif button == self.RESIGN_BUTTON_1:
                                    self.model.game_over = ['white']
                    if not self.model.game_over and not self.model.minimax_player[self.model.player]:
                        x = event.mouse_pos[0]
                        y = event.mouse_pos[1]
                        if (x < 100 or x > self.screen_width - 100) and self.screen_height*0.5 + 2.5*self.POOL_SIZE > y > self.screen_height*0.5 - 2.5*self.POOL_SIZE:
                            if event.button == 1: #left click
                                if x < 100 and self.model.player == 0:
                                    if self.screen_height*0.5 + 2.5*self.POOL_SIZE > y > self.screen_height*0.5 + 1.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '0G':
                                            self.selected_piece = ('0G', self.model.whitePool.pool.get('0G'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 + 1.5*self.POOL_SIZE > y > self.screen_height*0.5 + 0.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '0A':
                                            self.selected_piece = ('0A', self.model.whitePool.pool.get('0A'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 + 0.5*self.POOL_SIZE > y > self.screen_height*0.5 - 0.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '0S':
                                            self.selected_piece = ('0S', self.model.whitePool.pool.get('0S'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 - 0.5*self.POOL_SIZE > y > self.screen_height*0.5 - 1.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '0B':
                                            self.selected_piece = ('0B', self.model.whitePool.pool.get('0B'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 - 1.5*self.POOL_SIZE > y > self.screen_height*0.5 - 2.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '0Q':
                                            self.selected_piece = ('0Q', self.model.whitePool.pool.get('0Q'))
                                        else:
                                            self.selected_piece = None
                                    elif self.selected_piece[-1] == ['-']:
                                        self.selected_piece = None
                                elif x > self.screen_width - 100 and self.model.player == 1:
                                    if self.screen_height*0.5 + 2.5*self.POOL_SIZE > y > self.screen_height*0.5 + 1.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '1G':
                                            self.selected_piece = ('1G', self.model.blackPool.pool.get('1G'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 + 1.5*self.POOL_SIZE > y > self.screen_height*0.5 + 0.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '1A':
                                            self.selected_piece = ('1A', self.model.blackPool.pool.get('1A'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 + 0.5*self.POOL_SIZE > y > self.screen_height*0.5 - 0.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '1S':
                                            self.selected_piece = ('1S', self.model.blackPool.pool.get('1S'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 - 0.5*self.POOL_SIZE > y > self.screen_height*0.5 - 1.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '1B':
                                            self.selected_piece = ('1B', self.model.blackPool.pool.get('1B'))
                                        else:
                                            self.selected_piece = None
                                    elif self.screen_height*0.5 - 1.5*self.POOL_SIZE > y > self.screen_height*0.5 - 2.5*self.POOL_SIZE:
                                        if self.selected_piece is None or self.selected_piece[0] != '1Q':
                                            self.selected_piece = ('1Q', self.model.blackPool.pool.get('1Q'))
                                        else:
                                            self.selected_piece = None
                                    elif self.selected_piece[-1] == ['-']:
                                        self.selected_piece = None
                                else:
                                    self.selected_piece = None
                        else:
                            axial = self.get_axial_coords(event.mouse_pos)
                            mouse_coord = (int(axial[0]), int(axial[1]))
                            target_piece_stack = None
                            for key in self.model.game.board:
                                if mouse_coord == key:
                                    target_piece_stack = self.model.game.board.get(key)
                                    break
                            if event.button == 1: #left click
                                if self.selected_piece is not None:
                                    if isinstance(self.selected_piece[0], str): #piece from pool selected
                                        if mouse_coord in self.model.game.possible_placements(self.selected_piece[0], self.model.whitePool, self.model.blackPool): #if can be placed
                                            self.event_manager.post(TurnEvent('placement', None, mouse_coord, self.selected_piece[1][-1]))
                                            self.selected_piece = None
                                        elif target_piece_stack not in [['-'], None] and target_piece_stack[-1][:1] == str(self.model.player): #select a piece
                                            self.selected_piece = (mouse_coord, target_piece_stack)
                                        else:
                                            self.selected_piece = None
                                    else: #piece from the board selected
                                        if mouse_coord in self.model.game.possible_moves(self.selected_piece[0], self.model.game.board.get(self.selected_piece[0])[-1], self.model.whitePool, self.model.blackPool): #if can be moved
                                            self.event_manager.post(TurnEvent('move', self.selected_piece[0], mouse_coord, self.selected_piece[1][-1]))
                                            self.selected_piece = None
                                        elif target_piece_stack not in [['-'], None] and target_piece_stack[-1][:1] == str(self.model.player) and self.selected_piece[0] != mouse_coord: #select a piece
                                            self.selected_piece = (mouse_coord, target_piece_stack)
                                        else:
                                            self.selected_piece = None
                                elif target_piece_stack not in [['-'], None] and target_piece_stack[-1][:1] == str(self.model.player): # select a piece
                                    self.selected_piece = (mouse_coord, target_piece_stack)

            elif self.model.state == 'options':
                if event.mouse_pos is not None:
                    for button in self.buttons:
                        if button.check_for_input(event.mouse_pos):
                            if button == self.BACK_BUTTON:
                                self.event_manager.post(StateEvent('main_menu'))
                    for button in self.radio_buttons:
                        if button.check_for_input(event.mouse_pos):
                            if button == self.PLAYER_0:
                                self.model.minimax_player[0] = button.selected
                            elif button == self.PLAYER_1:
                                self.model.minimax_player[1] = button.selected

            elif self.model.state == 'rules':
                if event.mouse_pos is not None:
                    for button in self.buttons:
                        if button.check_for_input(event.mouse_pos):
                            if button == self.BACK_BUTTON:
                                self.event_manager.post(StateEvent('main_menu'))


    def get_axial_coords(self, click_pos):
        '''
        Convert the cartesian coordinates of a mouse click into axial coordinates
        '''
        x, y = click_pos
        axial_x = 2*(x-self.board_origin[0])/(3*self.radius)
        axial_y = (self.board_origin[0]-x)/(3*self.radius) + (y-self.board_origin[1])/(self.radius*3**0.5)
        return round(axial_x), round(axial_y)

    def render(self):
        '''
        Called every tick
        '''
        if not self.is_init:
            return
        if self.model.state == 'main_menu':
            self.main_menu()
        elif self.model.state == 'play':
            self.play()
        elif self.model.state == 'options':
            self.options()
        elif self.model.state == 'rules':
            self.rules()
        self.clock.tick(30)

    def main_menu(self):
        '''
        Renders the main menu
        '''
        pygame.display.set_caption('HIVE')
        self.screen.fill(self.BACKGROUND_COLOUR)
        height = self.screen_height*0.5-150
        height = int(150*self.scale)
        centre = self.screen_width*0.5
        rad = 73
        cos = 0.5*3**0.5

        for hexagon in self.hexagons:
            hex_x, hex_y, hex_size, hex_piece = hexagon
            self.render_hex(None, (hex_x, hex_y), [hex_piece], hex_size*0.6)
            self.draw_hex(None, (hex_x, hex_y), hex_size*0.6)
            self.draw_hex(None, (hex_x, hex_y), hex_size, colour = (50, 150, 255))

        H = pygame.font.Font('assets/Exan-Regular.ttf', int(100*self.scale)).render('H', True, '#000000')
        I = pygame.font.Font('assets/Exan-Regular.ttf', int(100*self.scale)).render('I', True, '#000000')
        V = pygame.font.Font('assets/Exan-Regular.ttf', int(100*self.scale)).render('V', True, '#000000')
        E = pygame.font.Font('assets/Exan-Regular.ttf', int(100*self.scale)).render('E', True, '#000000')
        text = cycle([H, I, V, E])
        for i in range(-3, 4, 2):
            self.render_hex(None, (int(centre+i*cos*rad*self.scale), height), ['menuhex'], int(rad*self.scale), flat_top=False, tint=(68, 103, 196))
            self.draw_hex(None, (int(centre+i*cos*rad*self.scale), height), int(rad*self.scale), flat_top=False, thickness=int(5*self.scale), colour=(0, 0, 0))
            char = next(text)
            rect = char.get_rect(center=(int(centre+i*cos*rad*self.scale), height))
            self.screen.blit(char, rect)
        for button in self.buttons:
            button.change_colour(pygame.mouse.get_pos())
            button.update(self.screen)
        pygame.display.update()

    def get_hex_centre(self, coord):
        '''
        Converts axial coordinates into cartesian.
        '''
        x = self.board_origin[0] + coord[0]*self.radius*1.5
        y = self.board_origin[1] + coord[0]*self.radius*0.5*(3**0.5) + coord[1]*self.radius*(3**0.5)
        return x, y

    def draw_hex(self, hex_coord, coord, radius, colour=(100, 100, 100), flat_top=True, thickness = 3):
        '''
        Draws the outline of a hexagon
        '''
        if coord == None:
            x, y = self.get_hex_centre(hex_coord)
        else:
            x, y = coord[0], coord[1]
        RsinA = radius*0.5 # A = 30
        RcosA = radius*0.5*(3**0.5)
        if flat_top:
            pygame.draw.polygon(self.screen, colour, [[x+RsinA, y+RcosA], [x+radius, y], [x+RsinA, y-RcosA], [x-RsinA, y-RcosA], [x-radius, y], [x-RsinA, y+RcosA]], thickness)
        else:
            pygame.draw.polygon(self.screen, colour, [[x+RcosA, y+RsinA], [x, y+radius], [x-RcosA, y+RsinA], [x-RcosA, y-RsinA], [x, y-radius], [x+RcosA, y-RsinA]], thickness)

    def render_hex(self, hex_coord, coord, piece_stack, radius, opacity=255, flat_top=True, tint=(255, 255, 255)):
        '''
        Renders an image a hexagon
        '''
        if coord == None:
            x, y = self.get_hex_centre(hex_coord)
        else:
            x, y = coord[0], coord[1]
        hex_img = pygame.transform.scale(pygame.image.load(f'assets/{piece_stack[-1]}.png'), (radius*2, radius*2))
        if not flat_top:
            hex_img = pygame.transform.rotate(hex_img, 90)
        hex_img.fill((tint[0], tint[1], tint[2], opacity), None, pygame.BLEND_RGBA_MULT)
        self.screen.blit(hex_img, (x-radius, y-radius))

    def render_moves(self, coord, piece_stack):
        '''
        Renders all possible moves for a selected piece
        '''
        for move in self.model.game.possible_moves(coord, piece_stack[-1], self.model.whitePool, self.model.blackPool):
            if piece_stack[-1][1:] == 'B': # hides the piece below a translucent beetle
                self.render_hex(move, None, ['whitehex'], self.radius)
            self.render_hex(move, None, piece_stack, self.radius, 130)
            self.draw_hex(move, None, self.radius)
    
    def render_placements(self, piece):
        '''
        Renders all possible placements for a selected piece
        '''
        for placement in self.model.game.possible_placements(piece, self.model.whitePool, self.model.blackPool):
            self.render_hex(placement, None, [piece], self.radius, 130)
            self.draw_hex(placement, None, self.radius)
    
    def render_pool(self, coord, key):
        '''
        Draws a piece from a pool
        '''
        self.render_hex(None, coord, [key], self.radius)
        self.draw_hex(None, coord, self.radius)
        if key[:1] == '0':
            NUM_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 15).render(str(len(self.model.whitePool.pool.get(key))-1), True, self.TEXT_COLOUR)
            NUM_RECT = NUM_TEXT.get_rect(center=(coord[0] + 35, coord[1] + 20))
        else:
            NUM_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 15).render(str(len(self.model.blackPool.pool.get(key))-1), True, self.TEXT_COLOUR)
            NUM_RECT = NUM_TEXT.get_rect(center=(coord[0] - 35, coord[1] + 20))
        self.screen.blit(NUM_TEXT, NUM_RECT)

    def play(self):
        '''
        Renders the play screen, including the pools and pieces on the board
        '''
        pygame.display.set_caption('HIVE')
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.RESIGN_BUTTON_0 = HiveButton(40, self.screen_height//2 + 250, '', self.main_font, 'white', 'green', pygame.transform.scale(pygame.image.load('assets/resign.png'), (70, 70)))
        self.RESIGN_BUTTON_1 = HiveButton(self.screen_width - 40, self.screen_height//2 + 250, '', self.main_font, 'white', 'green', pygame.transform.scale(pygame.image.load('assets/resign.png'), (70, 70)))
        self.buttons = [self.buttons[0], self.RESIGN_BUTTON_0, self.RESIGN_BUTTON_1]
        for button in self.buttons:
            button.change_colour(pygame.mouse.get_pos())
            button.update(self.screen)
        board_copy = deepcopy(self.model.game.board)
        for key in board_copy:
            if board_copy.get(key) != ['-']: # debug: remove the if statement and the empty hexes will render
                self.render_hex(key, None, board_copy.get(key), self.radius)
                self.draw_hex(key, None, self.radius)
        if self.selected_piece is not None:
            if isinstance(self.selected_piece[0], str): #if a piece from the pool is selected
                self.render_placements(self.selected_piece[0])
            else: #a piece on the board is selected
                self.render_moves(self.selected_piece[0], self.selected_piece[1])
                self.render_hex(self.selected_piece[0], None, self.selected_piece[1], self.radius)
                self.draw_hex(self.selected_piece[0], None, self.radius, (0, 255, 0))
        self.POOL_SIZE = 80
        x = 50
        for key in self.model.whitePool.pool:
            if key[1:] == 'Q':
                y = self.screen_height*0.5 - 2*self.POOL_SIZE
            if key[1:] == 'B':
                y = self.screen_height*0.5 - self.POOL_SIZE
            if key[1:] == 'S':
                y = self.screen_height*0.5
            if key[1:] == 'A':
                y = self.screen_height*0.5 + self.POOL_SIZE
            if key[1:] == 'G':
                y = self.screen_height*0.5 + 2*self.POOL_SIZE
            if self.model.whitePool.pool.get(key) != ['-']:
                self.render_pool((x, y), key)
                if self.selected_piece is not None:
                    if self.selected_piece[0] == '0' + key[1:]:
                        self.draw_hex(None, (x, y), self.radius, (0, 255, 0))
        for key in self.model.blackPool.pool:
            if key[1:] == 'Q':
                y = self.screen_height*0.5 - 160
            if key[1:] == 'B':
                y = self.screen_height*0.5 - 80
            if key[1:] == 'S':
                y = self.screen_height*0.5
            if key[1:] == 'A':
                y = self.screen_height*0.5 + 80
            if key[1:] == 'G':
                y = self.screen_height*0.5 + 160
            if self.model.blackPool.pool.get(key) != ['-']:
                self.render_pool((self.screen_width - x, y), key)
                if self.selected_piece is not None:
                    if self.selected_piece[0] == '1' + key[1:]:
                        self.draw_hex(None, (self.screen_width - x, y), self.radius, (0, 255, 0))
        if not self.model.game_over:
            if self.model.player == 0:
                PLAYER_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 30).render('White Turn', True, self.TEXT_COLOUR)
            else:
                PLAYER_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 30).render('Black Turn', True, self.TEXT_COLOUR)
            PLAYER_RECT = PLAYER_TEXT.get_rect(center=(self.screen_width - 100, 20))
            self.screen.blit(PLAYER_TEXT, PLAYER_RECT)
            if self.model.thinking:
                THINKING_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 30).render('Computer is thinking', True, self.TEXT_COLOUR)
                THINKING_RECT = THINKING_TEXT.get_rect(center=(self.screen_width - 180, 50))
                self.screen.blit(THINKING_TEXT, THINKING_RECT)
        if self.render_stack: #renders the pieces in a beetle stack
            x, y = 50, self.screen_height - 50
            for bug in self.render_stack:
                self.render_hex(None, (x, y), [bug], self.radius)
                self.draw_hex(None, (x, y), self.radius)
                x += 50
        if self.model.game_over:
            if len(self.model.game_over) == 2:
                GAME_OVER_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 50).render('Tie', True, self.TEXT_COLOUR)
                GAME_OVER_RECT = GAME_OVER_TEXT.get_rect(center=(self.screen_width*0.5, 50))
                self.screen.blit(GAME_OVER_TEXT, GAME_OVER_RECT)
            elif self.model.game_over == ['white']:
                GAME_OVER_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 50).render('White wins', True, self.TEXT_COLOUR)
                GAME_OVER_RECT = GAME_OVER_TEXT.get_rect(center=(self.screen_width*0.5, 50))
                self.screen.blit(GAME_OVER_TEXT, GAME_OVER_RECT)
            else:
                GAME_OVER_TEXT = pygame.font.Font('assets/Exan-Regular.ttf', 50).render('Black wins', True, self.TEXT_COLOUR)
                GAME_OVER_RECT = GAME_OVER_TEXT.get_rect(center=(self.screen_width*0.5, 50))
                self.screen.blit(GAME_OVER_TEXT, GAME_OVER_RECT)
        pygame.display.update()

    def options(self):
        '''
        Renders the options screen
        '''
        pygame.display.set_caption('HIVE')
        self.screen.fill(self.BACKGROUND_COLOUR)
        for button in self.buttons:
            button.change_colour(pygame.mouse.get_pos())
            button.update(self.screen)
        for button in self.radio_buttons:
            button.update(self.screen)
        pygame.display.update()

    def rules(self):
        '''
        Renders the rules screen
        '''
        pygame.display.set_caption('HIVE')
        self.screen.fill(self.BACKGROUND_COLOUR)
        FONT_SIZE = 20
        TEXT_A = '''Objective:\nSurround the opponent's Queen Bee while trying to stop your oppenent from doing\nthe same to you.\nPlaying the game:\nOn your turn you can either place a piece on the board or move an existing piece\naccording to the rules below.\nRules for placing:\nExcept for the first piece placed by each player, pieces cannot be placed adjacent to\nthe opponent's pieces. The Queen Bee must be placed in the first four turns.\nRules for movement:\nYour pieces cannot be moved until your queen bee has been placed. When moving, all\npieces must follow the One Hive Rule and the Freedom to Move Rule.\n\n          Queen Bee - can move one space.\n\n\n          Ant - can move any number of spaces.'''
        TEXT_B = '''          Beetle - can move one space, and can move on top of the Hive. A piece beneath\n          a Beetle cannot move.\n\n          Grasshopper - can jump in a straight line over at least one piece to the next\n          empty tile.\n\n          Spider - moves exactly 3 spaces. Cannot backtrack. Must stay in contact with\n          hive as it slides.'''
        TEXT_C = '''One Hive Rule:\nThe pieces in play must be connected at all times\nFreedom to Move Rule:\nExcept for the Beetle and Grasshopper, creature can only move in a sliding fashion.\nIf a gap is too small, they cannot pass through it.\nEnd of the game:\nThe first player to surround their opponent's queen bee wins'''
        self.render_multi_line(TEXT_A, 40, 75, FONT_SIZE)
        self.render_multi_line(TEXT_B, 40, 75+18.5*FONT_SIZE, FONT_SIZE)
        self.render_multi_line(TEXT_C, 40, 75+27*FONT_SIZE, FONT_SIZE)
        for i, piece in enumerate(['0Q', '0A', '0B', '0G', '0S']):
            self.render_hex(None, (70, 348+FONT_SIZE*i*3), [piece], 30)
            self.draw_hex(None, (70, 348+FONT_SIZE*i*3), 30)
        for button in self.buttons:
            button.change_colour(pygame.mouse.get_pos())
            button.update(self.screen)
        pygame.display.update()

    def render_multi_line(self, text, x, y, font_size):
        '''
        Renders multiple lines of text
        '''
        lines = text.splitlines()
        for i, l in enumerate(lines):
            r_text = pygame.font.SysFont('verdana', font_size).render(l, True, self.TEXT_COLOUR)
            self.screen.blit(r_text, (x, y+font_size*i))

if __name__ == '__main__':
    print(dir(HiveView))