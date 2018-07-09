import pygame
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

class Pane(object):
    def __init__(self, width=1200, height=800, row_height=100, num_columns=6,
                     text_offset_x=10, text_offset_y=10):
        pygame.init()
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y
        self.width = width
        self.height = height
        self.num_columns = num_columns
        self.row_height = row_height
        self.font = pygame.font.SysFont('Arial', 18)
        pygame.display.set_caption('Box Test')
        self.screen = pygame.display.set_mode((width, height), 0, 32)
        self.screen.fill((kCOLORS["white"]))
        self.draw_grid_flag=True
        pygame.display.update()

    def start_round(self, round):
        from random import sample
        self.board_values = kMONEY[round]
        print("Using board", self.board_values)
        # select five categories appropriate for the round
        self.categories = sample(list(self.questions[round].keys()), self.num_columns)
        print("Using categories", self.categories)
        self.board = defaultdict(dict)

        column = 0
        for ii in self.categories:
            column += 1
            row = 0
            for jj in sorted(self.questions[round][ii]):
                row += 1
                self.board[column][row] = self.questions[round][ii][jj]

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
        if self.draw_grid_flag:
            self.screen.fill((kCOLORS["white"]))    
            self.rect = pygame.draw.rect(self.screen, (kCOLORS["blue"]), 
                                         (0, 0, self.width, 100))
            self.draw_grid_flag=False
            self.show_score(score)
            self.show_selected_box(score, team)
        # pygame.display.update()

        cell_pos=self.width/self.num_columns


        for row in range(self.num_columns):
            cell_pos=self.width/self.num_columns
            for x,header in enumerate(range(self.num_columns)):
                self.rect = pygame.draw.rect(self.screen, (kCOLORS["black"]),
                                             (0, row*self.row_height, 
                                              cell_pos, self.row_height), 2)
                cell_pos+=self.width/self.num_columns
                # pygame.display.update()
        pygame.display.update()

    def clear_already_selected(self, col, row):
        pygame.draw.rect(self.screen, (black), (row*(self.width/self.num_columns),
                                                col*self.row_height,
                                                self.width/self.num_columns,
                                                self.row_height))
        
    def show_score(self, scores):
        curser=10
        self.rect = pygame.draw.rect(self.screen, (kCOLORS["grey"]), (0,600 , self.width, 100))
        for team in scores:
            self.screen.blit(self.font.render(team, True, (255,0,0)), (curser, 610))
            curser+=self.width/self.num_columns
        curser=10
        for team in scores:
            self.screen.blit(self.font.render(str(scores[team]), True, (255,0,0)), (curser, 640))
            curser+=self.width/self.num_columns

    def show_selected_box(self, score, team):
        self.show_score(score)
        self.rect = pygame.draw.rect(self.screen, (kCOLORS["red"]), (team*(self.width/6),600 , self.width/6, 100),3)
        self.rect = pygame.draw.rect(self.screen, (kCOLORS["red"]), (team*(self.width/6),700 , self.width/6, 100))

    def display_text(self):
        for ii in self.board:
            if any(self.board[ii]):
                self.add_text(ii, 0, self.categories[ii - 1])

            row = 0
            for jj in self.board[ii]:
                row += 1
                print(self.board[ii][jj])
                if self.board[ii][jj]:
                    print(ii, row)
                    self.add_text(ii, row, self.board_values[row - 1])
        pygame.display.update()

        
    def add_text(self, column, row, text):
        # print(pos,text)
        x = column * self.width/self.num_columns + self.text_offset_x
        y= self.row_height * row + self.text_offset_y
        color = kCOLORS["white"]

        if row == 0:
            color=kCOLORS["yellow"]
        print("RENDER", x, y, text)
        self.screen.blit(self.font.render(str(text), True, color), (x, y))


if __name__ == "__main__":
    from time import sleep

    pane = Pane()
    pane.draw_grid({"A": 0, "B": 0}, 1)
    pane.load_questions("study.csv")
    pane.start_round(1)
    pane.display_text()
    sleep(10)
