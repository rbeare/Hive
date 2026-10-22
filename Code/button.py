import pygame

pygame.init()
class HiveButton():
    '''
    This class is for regular buttons
    '''
    def __init__(self, x, y, text_input, font, base_colour, hovering_colour, image=None):
        self.x = x
        self.y = y
        self.font = font
        self.base_colour, self.hovering_colour = base_colour, hovering_colour
        self.text_input = text_input
        self.text = font.render(self.text_input, True, base_colour)
        self.text_rect = self.text.get_rect(center=(self.x, self.y))
        self.image = image
        if self.image == None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_for_input(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False
    
    def change_colour(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_colour)
        else:
            self.text = self.font.render(self.text_input, True, self.base_colour)


class RadioButton():
    '''
    This class is for buttons with two states. When clicked, the button state alternates
    '''
    def __init__(self, x, y, image_0, image_1, text, font, selected = True):
        self.x = x
        self.y = y
        self.selected = selected
        self.images = [image_0, image_1]
        self.rect = self.images[self.selected].get_rect(center=(self.x, self.y))
        self.font = font
        self.text = font.render(text, True, '#F5F5F5')
        self.text_rect = self.text.get_rect(center=(self.x + 150, self.y))

    def update(self, screen):
        screen.blit(self.images[self.selected], self.rect)
        screen.blit(self.text, self.text_rect)

    def check_for_input(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            if self.selected:
                self.selected = False
            else:
                self.selected = True
            self.rect = self.images[self.selected].get_rect(center=(self.x, self.y))
            return True
        return False