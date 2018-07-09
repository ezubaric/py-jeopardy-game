import pygame
import textwrap
import os
from random import random
from collections import defaultdict

kCOLORS = {}
kCOLORS["white"] = (255,255,255)
kCOLORS["grey"] = (160, 160, 160)
kCOLORS["blue"] = (0,0,255)
kCOLORS["yellow"] = (255,255,0)
kCOLORS["red"] = (255, 0, 0)
kCOLORS["black"] = (0, 0, 0)

kMONEY = {1: [200, 400, 600, 800, 1000],
          2: [400, 800, 1200, 1600, 2000]}
kNUM_ROWS = len(kMONEY[1])
kCOLUMN_LETTERS = "ABCDEF"


# Utilities for single character input
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            sys.stdin.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()


def game_loop(scores):
    # initialize the board
    pane = Pane()
    pane.draw_grid(scores, 1)
    pane.load_questions("study.csv")
    pane.start_round(1)
    pane.display_text()
    while pane.clues_left() > 0:
        question = pane.get_clue()
        print("Selection", question)
        print("Category", pane.categories[question[0]])
        player = pane.buzz(question)
        print(kMONEY, question[1], question)
        scores = pane.result(scores, player, pane.board_values[question[1]], question)

        pane.draw_grid(scores, player)
        pane.display_text()
        


class Pane(object):
    def __init__(self, width=1200, height=800, row_height=100, num_columns=6,
                     text_offset_x=10, text_offset_y=10, text_line_height=20,
                     char_width=15):
        pygame.init()
        self.text_offset_x = text_offset_x
        self.char_width = char_width
        self.text_line_height = text_line_height
        self.text_offset_y = text_offset_y
        self.width = width
        self.height = height
        self.num_columns = num_columns
        self.board = {}
        self.row_height = row_height
        self.font = pygame.font.SysFont('Arial', 18)
        pygame.display.set_caption('Jeopardy Tester')
        self.screen = pygame.display.set_mode((width, height), 0, 32)
        self.screen.fill((kCOLORS["blue"]))
        self.draw_grid_flag=True
        pygame.display.update()

    def result(self, score, player, value, question):
        x, y = question
        
        print("Answer: %s" % self.board[x][y]["answer"])
        char = " "
        while char not in "+-":
            char = getch()
        if char == "+":
            score[player] += value
        elif char == "-":
            score[player] -= value

        self.board[x][y] = None
            
        return score

    def buzz(self, question):
        self.screen.fill((kCOLORS["blue"]))
        x, y = question
        pygame.display.update()

        font = pygame.font.SysFont("times", 50)
        row = 0
        for ii in textwrap.wrap(self.board[x][y]["clue"], 40):
            row += 1
            text = font.render(ii, True, kCOLORS["white"])
            self.screen.blit(text, (.5 * self.width // self.num_columns, self.row_height * row))
        pygame.display.update()

        os.system('say "%s"' % self.board[x][y]["clue"].replace('"', ''))

        sleep(random())
        keys=pygame.key.get_pressed()
        print(keys)
        
        self.screen.fill((kCOLORS["yellow"]))
        pygame.display.update()
        
        char = "q"
        while char not in " 1234567890":
            char = getch()
            print("Keypress: %s" % char)

        if char == " ":
            return -1
        else:
            os.system("say 'Player %s'" % char)
            return int(char)


        
    def clues_left(self):
        return sum(1 for x in self.board if self.board[x] is not None)

    def get_clue(self):
        square = input("Select a square:")
        while len(square) != 2 or square[0] not in kCOLUMN_LETTERS or int(square[1]) not in range(1, 7):
            square = input("Select a square:")

        
        x = kCOLUMN_LETTERS.index(square[0])
        y = int(square[1]) - 1
        if x not in self.board or y not in self.board[x] or self.board[x][y] is None:
            return self.get_clue()
        else:
            return x, y
        
    def start_round(self, round):
        from random import sample
        self.board_values = kMONEY[round]
        print("Using board", self.board_values)
        # select five categories appropriate for the round
        self.categories = sample(list(self.questions[round].keys()), self.num_columns)
        print("Using categories", self.categories)
        self.board = defaultdict(dict)

        for column, ii in enumerate(self.categories):
            row = 0
            for jj in sorted(self.questions[round][ii]):
                self.board[column][row] = self.questions[round][ii][jj]
                row += 1
            

    def load_questions(self, file):
        from collections import defaultdict
        from csv import DictReader

        self.questions = {}
        for ii in range(1,4):
            self.questions[ii] = defaultdict(dict)

        with open(file, 'r') as infile_handle:
            infile = DictReader(infile_handle)
            for ii in infile:
                round = int(ii["round"])
                self.questions[round][ii["category"]][int(ii["value"])] = ii
                
        
    def draw_grid(self, score, team):
        self.screen.fill((kCOLORS["blue"]))    
        self.rect = pygame.draw.rect(self.screen, (kCOLORS["blue"]), 
                                         (0, 0, self.width, 100))
        self.draw_grid_flag=False
        self.show_score(score)
        self.show_selected_box(score, team)

        cell_width = self.width/self.num_columns


        for row in range(kNUM_ROWS + 2):
            for col in range(self.num_columns):
                self.rect = pygame.draw.rect(self.screen, (kCOLORS["black"]),
                                             (col*cell_width, row*self.row_height, 
                                              cell_width, self.row_height), 2)

                if col in self.board and row in self.board[col] and self.board[col][row] is None:
                    self.clear_already_selected(col, row)
                # pygame.display.update()
        self.show_score(score)
        pygame.display.update()

    def clear_already_selected(self, col, row):
        print("AS", col, row)
        # Add one to row to account for category header
        pygame.draw.rect(self.screen, (kCOLORS["black"]), (col*(self.width/self.num_columns),
                         (row + 1)*self.row_height, self.width/self.num_columns, self.row_height))
        
    def show_score(self, scores):
        curser=10
        self.rect = pygame.draw.rect(self.screen, (kCOLORS["grey"]), (0,600 , self.width, 100))
        for team in scores:
            self.screen.blit(self.font.render(str(team), True, (255,0,0)), (curser, 610))
            curser+=self.width/self.num_columns
        curser=10
        for team in scores:
            self.screen.blit(self.font.render(str(scores[team]), True, (255,0,0)), (curser, 640))
            curser+=self.width/self.num_columns

    def show_selected_box(self, score, team):
        self.show_score(score)
        self.rect = pygame.draw.rect(self.screen, (kCOLORS["red"]), ((team-1)*(self.width/6),600 , self.width/6, 100),3)
        self.rect = pygame.draw.rect(self.screen, (kCOLORS["red"]), ((team-1)*(self.width/6),700 , self.width/6, 100))

    def display_text(self):
        for ii in self.board:
            if any(self.board[ii]):
                self.add_text(ii, -1, self.categories[ii])

            for jj in self.board[ii]:
                if self.board[ii][jj] is not None:
                    # These arrays are zero indexed, so we add one to what human sees
                    self.add_text(ii, jj, "%i\n(%s%i)" % (self.board_values[jj], kCOLUMN_LETTERS[ii], jj + 1))
        pygame.display.update()

    def add_text(self, column, row, text):
        lines = textwrap.wrap(str(text), self.char_width)
        
        # print(pos,text)
        x = column * self.width/self.num_columns + self.text_offset_x
        
        # Add one to the row to account for category header
        y= self.row_height * (row + 1) + self.text_offset_y
        color = kCOLORS["white"]

        if row < 0:
            color=kCOLORS["yellow"]

        offset = 0
        for ii in lines:
            self.screen.blit(self.font.render(str(ii), True, color), (x, y + offset))
            offset += self.text_line_height



            
if __name__ == "__main__":
    from time import sleep


    game_loop({1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0})
