''' '''

import pyglet

class BaseWindow(pyglet.window.Window):
    def __init__(self, application, width, height, caption):
        self.application = application
        self.batch = pyglet.graphics.Batch()
        self.controls = []
        self.focused_control = None
        pyglet.window.Window.__init__(self, width=width, height=height, caption=caption)

    def on_draw(self):
        self.clear()
        self.batch.draw()
        
    def on_mouse_motion(self, x, y, dx, dy):
        for control in self.controls:
            if control.hit_test(x, y):
                control.on_mouse_motion(x, y, dx, dy)
                self.set_mouse_cursor(control.mouse_cursor)                
                break
        else:
            self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self.controls:
            if control.hit_test(x, y):
                self.set_focus(control)
                control.on_mouse_press(x, y, button, modifiers)
                break
        else:
            self.set_focus(None)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focused_control:
            self.focused_control.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        
    def on_text(self, text):
        if self.focused_control:
            self.focused_control.on_text(text)
        
    def on_text_motion(self, motion):
        if self.focused_control:
            self.focused_control.on_text_motion(motion)
      
    def on_text_motion_select(self, motion):
        if self.focused_control:
            self.focused_control.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                dir = -1
            else:
                dir = 1

            if self.focused_control in self.controls:
                i = self.controls.index(self.focused_control)
            else:
                i = 0
                dir = 0

            self.set_focus(self.controls[(i + dir) % len(self.controls)])

        elif symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

    def set_focus(self, control):
        if self.focused_control:
            self.focused_control.on_focus(False)
        self.focused_control = control
        if self.focused_control:
            self.focused_control.on_focus(True)
            
class Control(object):
    def __init__(self, parent_window, x, y, width, height, background_color, foreground_color):
        self.parent_window = parent_window
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mouse_cursor = None

        # Rectangulo del fondo del control
        self.parent_window.batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', [self.x - 2, self.y - 2, x + self.width + 2, self.y - 2, x + self.width + 2, self.y + self.height + 2, self.x - 2, self.y + self.height + 2]),
            ('c4B', [background_color[0], background_color[1], background_color[2], background_color[3]] * 4)
        )

    def hit_test(self, x, y):
        return (0 < x - self.x < self.width and 0 < y - self.y < self.height)

    def on_resize(self): pass
    def on_draw(self): pass
    def on_mouse_motion(self, x, y, dx, dy): pass
    def on_mouse_press(self, x, y, button, modifiers): pass
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers): pass
    def on_text(self, text): pass
    def on_text_motion(self, motion): pass
    def on_text_motion_select(self, motion): pass
    def on_focus(self, value): pass
    
class TextBox(Control):
    def __init__(self, parent_window, x, y, width, height, text, background_color, foreground_color):
        Control.__init__(self, parent_window, x, y, width, height, background_color, foreground_color)

        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), dict(color=foreground_color))

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, width, height, multiline=False, batch=self.parent_window.batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        self.mouse_cursor = self.parent_window.get_system_mouse_cursor('text')

    def on_mouse_press(self, x, y, button, modifiers):
        self.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    
    def on_text(self, text):
        self.caret.on_text(text)

    def on_text_motion(self, motion):
        self.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        self.caret.on_text_motion_select(motion)

    def on_focus(self, value):
        if not value:
            self.caret.visible = False
            self.caret.mark = self.caret.position = 0
        else:
            self.caret.visible = True
            self.caret.mark = 0
            self.caret.position = len(self.document.text)

class Button(Control):
    def __init__(self, parent_window, x, y, width, height, text, background_color, foreground_color):
        Control.__init__(self, parent_window, x, y, width, height, background_color, foreground_color)
        self.label = pyglet.text.Label(text=text, x=self.x + self.width / 2, y=self.y + self.height / 2, width=width, height=height, anchor_x='center', anchor_y='center', color=foreground_color, batch=self.parent_window.batch)
        self.click = None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.click:
            self.click()
