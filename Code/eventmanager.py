from weakref import WeakKeyDictionary

class event(object):
    '''
    A generic event class of which there are numerous subclasses
    '''
    def __init__(self):
        self.name = 'event'
    def __str__(self):
        return self.name

class InitEvent(event):
    '''
    Initilialises the view when the model runs
    '''
    def __init__(self):
        self.name = 'InitEvent'

class TickEvent(event):
    '''
    Allows the view to render the GUI and receive inputs a fixed number of times per second
    '''
    def __init__(self, deselect = False):
        self.name = 'TickEvent'
        self.deselect = deselect
    
    def __str__(self):
        return f'{self.name}, deselect = {self.deselect}'

class QuitEvent(event):
    '''
    Terminates the program
    '''
    def __init__(self):
        self.name = 'QuitEvent'

class InputEvent(event):
    '''
    Handles mouse and key inputs
    '''
    def __init__(self, char, mouse_pos, button):
        self.name = 'InputEvent'
        self.char = char
        self.mouse_pos = mouse_pos
        self.button = button
    
    def __str__(self):
        return f'{self.name}, char = {self.char}, mouse_pos = {self.mouse_pos}, button = {self.button}'
    
class StateEvent(event):
    '''
    Informs the model and the view of changes of state
    '''
    def __init__(self, state):
        self.name = 'StateEvent'
        self.state = state

    def __str__(self):
        return f'{self.name}, state = {self.state}'

class TurnEvent(event):
    '''
    Informs the model when the user has tried to make a move
    '''
    def __init__(self, typ, from_coord, to_coord, piece):
        self.name = 'TurnEvent'
        self.type = typ
        self.from_coord = from_coord
        self.to_coord = to_coord
        self.piece = piece
    
    def __str__(self):
        return f'{self.name}, type = {self.type}, from_coord = {self.from_coord}, to_coord = {self.to_coord}, piece = {self.piece}'
    
class WindowResizeEvent(event):
    '''
    Informs the view if the dimensions of the window change
    '''
    def __init__(self):
        self.name = 'WindowResizeEvent'

class HiveEventManager(object):
    '''
    Notifies listeners when one of the files posts an event
    '''
    def __init__(self):
        self.listeners = WeakKeyDictionary()

    def register_listener(self, listener):
        self.listeners[listener] = 1
    
    def post(self, event):
        if not isinstance(event, TickEvent):
            print(str(event))
        for listener in self.listeners.keys():
            listener.process_event(event)