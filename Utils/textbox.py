import pygame
import math

class DialogueManager:
    def __init__(self, dialogue_list):
        self.dialogues = dialogue_list
        self.index = 0
        self.char_index = 0
        self.displayed = ""

    def current(self):
        if self.index >= len(self.dialogues):
            return None
        return self.dialogues[self.index]

    def advance(self, dt):
        d = self.current()
        if d is None:
            return
        text = d["text"]
        # 60 chars per second
        self.char_index = min(self.char_index + 60*dt, len(text))
        self.displayed = text[:int(self.char_index)]

    def skip_or_next(self):
        d = self.current()
        if d is None:
            return
        if int(self.char_index) < len(d["text"]):
            self.char_index = len(d["text"])
            self.displayed = d["text"]
        else:
            self.index += 1
            self.char_index = 0
            self.displayed = ""

    def finished(self):
        return self.index >= len(self.dialogues)

class Textbox:
    def __init__(self, screen, dialogue_list=None):
        self.screen = screen
        self.dialogue_manager = DialogueManager(dialogue_list or [])
        self.font = pygame.font.SysFont('segoeui', 36, bold=True)
        self.width, self.height = screen.get_size()
        # Dialogue box rectangle
        self.box_rect = pygame.Rect(50, self.height-180, self.width-100, 130)
        self.bg_color = (20,20,30,220)
        self.text_color = (255,215,0)

    def update(self, dt):
        self.dialogue_manager.advance(dt)

    def draw(self):
        if self.dialogue_manager.current() is None:
            return
        # semi-transparent box
        surf = pygame.Surface((self.box_rect.width,self.box_rect.height),pygame.SRCALPHA)
        surf.fill(self.bg_color)
        self.screen.blit(surf, self.box_rect.topleft)

        # Speaker
        speaker = self.dialogue_manager.current()["speaker"]
        text = self.dialogue_manager.displayed

        speaker_surf = self.font.render(speaker+":", True, self.text_color)
        self.screen.blit(speaker_surf, (self.box_rect.x+10, self.box_rect.y+10))

        # Text
        lines = self.wrap_text(text, self.font, self.box_rect.width-20)
        for i,line in enumerate(lines):
            line_surf = self.font.render(line, True, self.text_color)
            self.screen.blit(line_surf, (self.box_rect.x+10, self.box_rect.y+50 + i*40))

    def skip_or_next(self):
        self.dialogue_manager.skip_or_next()

    def is_finished(self):
        return self.dialogue_manager.finished()

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current = ""
        for word in words:
            test = current + (' ' if current else '') + word
            if font.size(test)[0] > max_width:
                if current:
                    lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        return lines
