import numpy as np
import os
import pygame as pg


class CartesianPlane:
    def __init__(self, x_max, y_max, screen_width, screen_height, bg_image_file,
                 grid_color=None):
        self.screen = pg.display.set_mode((screen_width, screen_height))
        self.grid_color = grid_color
        self.screen_width, self.screen_height = self.screen.get_size()
        self.x_max = x_max
        self.y_max = y_max
        self.x_pixel_increment = self.screen_width // self.x_max
        self.y_pixel_increment = self.screen_height // self.y_max
        self.bg_image = pg.image.load(bg_image_file)
        self.sprite_list = []
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)
        self.widgets = []

    def clear(self):
        self.sprite_list = []
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)
        self.widgets = []

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)

    def add_widget(self, widget):
        self.widgets.append(widget)

    def refresh(self):
        self.screen.blit(self.bg_image, (0, 0))
        if self.grid_color is not None:
            for y in range(self.screen_height - self.y_pixel_increment, 0, -self.y_pixel_increment):
                pg.draw.aaline(self.bg_image, self.grid_color, (0, y), (self.screen_width, y))
            for x in range(self.x_pixel_increment, self.screen_width, self.x_pixel_increment):
                pg.draw.aaline(self.bg_image, self.grid_color, (x, 0), (x, self.screen_height))
        self.sprites.update()
        for sprite in self.sprites:
            sprite.redraw()
            x, y = sprite.current_position()
            coords = self.translate_coordinates(x, y)
            if coords is not None:
                width, height = sprite.size()
                sprite.rect = coords[0] - width//2, coords[1] - height//2
        self.sprites.draw(self.screen)
        for widget in self.widgets:
            widget.redraw(self)
        pg.display.flip()

    def notify(self, event):
        try:
            x, y = event.pos
            x /= self.x_pixel_increment
            y = (self.screen_height - y) / self.y_pixel_increment
            position = (x, y)
        except AttributeError:
            position = None
        for sprite in self.sprites:
            sprite.notify(event, position)
        for widget in self.widgets:
            widget.notify(event, position)

    def in_bounds(self, x, y):
        return 0 <= x <= self.x_max, 0 <= y <= self.y_max

    def translate_coordinates(self, x, y):
        return (x * self.x_pixel_increment,
                self.screen_height - (y * self.y_pixel_increment))

    def draw_rect(self, color, x, y, width, height):
        x, y = self.translate_coordinates(x, y)
        width = width * self.x_pixel_increment
        height = height * self.y_pixel_increment
        pg.draw.rect(self.screen, color, (x - width // 2, y - height // 2, width, height))

    def draw_circle(self, color, x, y, diameter):
        x, y = self.translate_coordinates(x, y)
        diameter = diameter * self.x_pixel_increment
        pg.draw.circle(self.screen, color, (x, y), diameter/2)


class AnimatedSprite(pg.sprite.Sprite):

    def __init__(self, initial_xy, animation_cells, scale=1.0):
        pg.sprite.Sprite.__init__(self)
        self.x, self.y = initial_xy
        self.animation_cells = animation_cells
        self.current_cell = 0
        self.scale = scale
        image = pg.image.load(self.animation_cells[self.current_cell])
        size = (image.get_size()[0] * self.scale, image.get_size()[1] * self.scale)
        self.image = pg.transform.scale(image, size)
        self.move_divisor = 10
        self.move_queue = []

    def size(self):
        return self.image.get_rect().width, self.image.get_rect().height

    def current_position(self):
        return self.x, self.y

    def move(self, delta_x, delta_y):
        step_size = (delta_x / self.move_divisor, delta_y / self.move_divisor)
        self.move_queue += [step_size] * self.move_divisor

    def is_stationary(self):
        return len(self.move_queue) == 0

    def notify(self, event, position):
        pass

    def flip(self):
        self.current_cell = (self.current_cell + 1) % len(self.animation_cells)

    def redraw(self):
        image = pg.image.load(self.animation_cells[self.current_cell])
        size = (image.get_size()[0] * self.scale, image.get_size()[1] * self.scale)
        self.image = pg.transform.scale(image, size)

    def update(self):
        if len(self.move_queue) > 0:
            (delta_x, delta_y), self.move_queue = self.move_queue[0], self.move_queue[1:]
            self.current_cell = (self.current_cell + 1) % len(self.animation_cells)
            self.x, self.y = self.x + delta_x, self.y + delta_y


class RainbowOverlay(AnimatedSprite):

    def __init__(self, x, y, mult=2):
        super().__init__((x, y),
                         [f"images/rainbow0.png"] +
                         [f"images/rainbow1.png"] * mult +
                         [f"images/rainbow2.png"] * mult +
                         [f"images/rainbow3.png"] * mult +
                         [f"images/rainbow4.png"] * mult +
                         [f"images/rainbow5.png"] * mult +
                         [f"images/rainbow6.png"] * mult +
                         [f"images/rainbow7.png"] * mult +
                         [f"images/rainbow8.png"] * mult +
                         [f"images/rainbow9.png"] * mult +
                         [f"images/rainbow8.png"] * mult +
                         [f"images/rainbow7.png"] * mult +
                         [f"images/rainbow6.png"] * mult +
                         [f"images/rainbow5.png"] * mult +
                         [f"images/rainbow4.png"] * mult +
                         [f"images/rainbow3.png"] * mult +
                         [f"images/rainbow2.png"] * mult +
                         [f"images/rainbow1.png"] * mult)


class PlayButton(pg.sprite.Sprite):

    def __init__(self, x, y, scale=1.0):
        pg.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.scale = scale
        self.image_file = f"images/play.png"
        self.image = pg.image.load(self.image_file)
        self.down = False

    def size(self):
        return self.image.get_rect().width, self.image.get_rect().height

    def current_position(self):
        return self.x, self.y

    def in_bounds(self, position):
        pos_x, pos_y = position
        return abs(pos_x - self.x) < 1.2 and abs(pos_y - self.y) < 1.2

    def notify(self, event, position):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.in_bounds(position):
                self.image_file = f"images/play_pushed.png"
                self.down = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.image_file = f"images/play.png"
            self.down = False

    def redraw(self):
        image = pg.image.load(self.image_file)
        size = (image.get_size()[0] * self.scale, image.get_size()[1] * self.scale)
        self.image = pg.transform.scale(image, size)

    def update(self):
        self.redraw()


class FamilyMemberWidget:

    def __init__(self, x, y, member):
        self.x, self.y = x, y
        self.member = member
        self.width = 0.42 if self.member.get_sex() == "male" else 0.5
        self.colors = [(255, 255, 255), (255, 0, 0)]
        self.current_color_index = 0
        self.current_color = self.colors[self.current_color_index]

    def get_color(self):
        return self.current_color

    def get_sex(self):
        return self.member.get_sex()

    def get_name(self):
        return self.member.get_name()

    def size(self):
        return self.rect.width, self.rect.height

    def current_position(self):
        return self.x, self.y

    def notify(self, event, position):
        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = position
            if (self.x - self.width / 2 <= x <= self.x + self.width / 2 and
                self.y - self.width / 2 <= y <= self.y + self.width / 2):
                self.current_color_index = (self.current_color_index + 1) % len(self.colors)
                self.current_color = self.colors[self.current_color_index]

    def redraw(self, plane):
        if self.member.get_sex() == "male":
            plane.draw_rect(self.current_color,
                            self.x - self.width // 2, self.y - self.width // 2,
                            self.width, self.width)
        else:
            plane.draw_circle(self.current_color,
                              self.x, self.y,
                              self.width)

    def update(self):
        pass

