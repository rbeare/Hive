import pygame
from eventmanager import *

class HiveController(object):

    def __init__(self, event_manager, model):
        '''
        Initialises global variables and registers as a listener to the event manager
        '''
        self.event_manager = event_manager
        self.model = model
        event_manager.register_listener(self)

    def process_event(self, event):
        '''
        Process an event posted by the event manager
        '''
        if isinstance(event, TickEvent):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.event_manager.post(QuitEvent())
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.event_manager.post(InputEvent(None, pygame.mouse.get_pos(), event.button))
                if event.type == pygame.VIDEORESIZE:
                    self.event_manager.post(WindowResizeEvent())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_HASH:
                        self.event_manager.post(InputEvent('#', None, None))