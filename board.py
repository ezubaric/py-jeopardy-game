import pygame
import textwrap
import os
import time
from random import random
from collections import defaultdict

kCOLORS = {}
kCOLORS["white"] = (255,255,255)
kCOLORS["grey"] = (160, 160, 160)
kCOLORS["blue"] = (0,0,255)
kCOLORS["yellow"] = (255,255,0)
kCOLORS["red"] = (255, 0, 0)
kCOLORS["black"] = (0, 0, 0)

kTIMER_EVENT = pygame.USEREVENT + 1
kKEYBOARD_NUMBERS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]
kKEYBOARD_LETTERS = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g]
kKEYBOARD_CORRECT = [pygame.K_n, 269, pygame.K_y, 270]
kCORRECT_MAP = [-1, -1, 1, 1]
kCOLUMN_LETTERS = "ABCDEF"

kMONEY = {1: [200, 400, 600, 800, 1000],
          2: [400, 800, 1200, 1600, 2000]}
kNUM_ROWS = len(kMONEY[1])

def keypress(valid = []):
    input_needed = True
    while input_needed:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                print("Got keypress %i, %s" % (event.key, str(list(int(x) for x in valid))))
                if event.key in valid:
                    input_needed = False
                else:
                    pygame.mixer.music.load('invalid.wav')
                    pygame.mixer.music.play(0)
    try:
        return valid.index(event.key)
    except ValueError:
        return keypress(valid)



def game_loop(scores):
    # initialize the board
    pane = Pane()
    pane.draw_grid(scores, 1)
    pane.load_questions("study.csv")
    player = 1
    for round in [1, 2]:
        pane.start_round(round)
        doubles = pane.pick_dd(round)
        pane.display_text()
        while pane.clues_left() > 0:
            question = pane.get_clue()
            if question[0] == 6:
                break
            print("Selection", question)
            print("Category", pane.categories[question[0]])
            if question in doubles:
                scores = pane.daily_double(question, player, scores)
            else:
                player = pane.buzz(question)
                total_scores_old = sum(scores.values())
                scores = pane.result(scores, player,
                                     pane.board_values[question[1]], question)
                total_scores_new = sum(scores.values())
                if total_scores_new < total_scores_old:
                    player = pane.buzz(question)
                    scores = pane.result(scores, player,
                                         pane.board_values[question[1]],
                                         question)

            pane.draw_grid(scores, player)
            pane.display_text()
            print("Clues left: %i" % pane.clues_left())
            print(doubles)

    pane.start_final(scores)


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

    def daily_double(self, question, player, scores):
        self.audio("dd")
        x, y = question

        wager = -1
        while wager < 0:
            wager = input("Wager: ")
            try:
                wager = int(wager)
            except ValueError:
                wager = -1

        self.screen_fill(self.board[x][y]["clue"])
        pygame.event.clear()
        val = self.result(scores, player, wager, question)
        self.board[x][y] = None
        return val

    def audio(self, filename):
        pygame.mixer.music.load('%s.wav' % filename)
        pygame.mixer.music.play(0)

    def pick_dd(self, needed):
        from random import choice
        doubles = []
        while needed > 0:
            x = choice(list(range(1, self.num_columns)))
            y = choice(list(range(3, kNUM_ROWS)))
            if x in self.board and y in self.board[x] and self.board[x][y] is not None:
                doubles.append((x, y))
                needed -= 1
        return doubles

    def result(self, score, player, value, question):
        x, y = question
        pygame.time.wait(2500)
        print("Answer: %s" % self.board[x][y]["answer"])
        if player > 0:
            correct = keypress(kKEYBOARD_CORRECT)
            score[player] += kCORRECT_MAP[correct] * value
            if kCORRECT_MAP[correct] > 0:
                self.board[x][y] = None
        else:
            self.audio("time")
            os.system('say "%s"' % self.board[x][y]["answer"].replace('"', ''))
            self.board[x][y] = None


        return score

    def start_final(self, scores):
        from random import choice
        category = choice(list(self.questions[3].keys()))
        question = choice(list(self.questions[3][category]))
        question = self.questions[3][category][question]

        self.screen_fill("Final Jeopardy")
        for ii in scores:
            if scores[ii] > 0:
                self.screen_fill("Player %i has %i dollars" %
                                 (ii, scores[ii]))
        self.screen_fill("Decide your wagers for this final Jeopardy! category.")


        self.screen_fill(category)
        pygame.time.wait(20000)
        self.screen_fill(question["clue"])
        self.audio('Jeopardy_Music')
        pygame.time.wait(30000)
        self.screen_fill(question["answer"])
        print(scores)

    def screen_fill(self, text):
        self.screen.fill((kCOLORS["blue"]))
        pygame.display.update()

        font = pygame.font.SysFont("times", 50)
        row = 0
        for ii in textwrap.wrap(text, 40):
            row += 1
            line = font.render(ii, True, kCOLORS["white"])
            self.screen.blit(line, (.5 * self.width // self.num_columns, self.row_height * row))
        pygame.display.update()

        os.system('say "%s"' % text.replace('"', ''))

    def buzz(self, question):
        x, y = question
        self.screen_fill(self.board[x][y]["clue"])

        # time_delta = int(random() * 1000)
        time_delta = 500
        pygame.time.set_timer(kTIMER_EVENT, time_delta)

        too_early = True
        locked_out = set()
        while True:
            for event in pygame.event.get():
                print("Got event!: " + str(event.type))
                if event.type == pygame.KEYDOWN:
                    if event.key in kKEYBOARD_NUMBERS:
                        if too_early:
                            locked_out.add(kKEYBOARD_NUMBERS.index(event.key) + 1)
                            print("Locked out: ", locked_out)
                        else:
                            player = kKEYBOARD_NUMBERS.index(event.key) + 1
                            if player in locked_out:
                                continue
                            else:
                                pygame.time.set_timer(kTIMER_EVENT, 0)
                                now = time.time()
                                elapsed = int((now - go_time) * 1000)
                                print(go_time, elapsed, now)
                                self.audio("ring")
                                self.screen.fill((kCOLORS["black"]))
                                pygame.display.update()
                                os.system('say "Player %i, %i ms"' % (player, elapsed))
                                return player
                if event.type == kTIMER_EVENT:
                    if too_early:
                        print("Go time!")
                        too_early = False
                        go_time = time.time()
                        self.screen.fill((kCOLORS["yellow"]))
                        pygame.display.update()
                        pygame.time.set_timer(kTIMER_EVENT, 3000)
                    else:
                        print("No buzz")
                        pygame.time.set_timer(kTIMER_EVENT, 0)

                        return -1
        print("Exiting buzz")


    def clues_left(self):
        val = 0
        for ii in self.board:
            for jj in self.board[ii]:
                if self.board[ii][jj] is not None:
                    val += 1
        return val

    def get_clue(self):
        print("Select column")
        x = keypress(kKEYBOARD_LETTERS)
        print("Select row")
        y = keypress(kKEYBOARD_NUMBERS)

        if x == 6:
            return x, y

        if x not in self.board or y not in self.board[x] or self.board[x][y] is None:
            return self.get_clue()
        else:
            return x, y

    def start_round(self, round):
        self.audio("board")
        self.screen.fill((kCOLORS["blue"]))
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
                    try:
                        self.add_text(ii, jj, "%i\n(%s%i)" % (self.board_values[jj], kCOLUMN_LETTERS[ii], jj + 1))
                    except IndexError:
                        print("IndexError on %i %i" % (ii, jj))
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
