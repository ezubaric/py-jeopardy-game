

class Pane(object):
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont('Arial', 18)
        pygame.display.set_caption('Box Test')
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT), 0, 32)
        self.screen.fill((white))
        self.draw_grid_flag=True
        pygame.display.update()


    def read_questions(self, file):
        self.questions = pd.read_csv('%s.csv' % file,header=0)

        with open(file, 'r') as infile_handle:
            infile = 
        
    def draw_grid(self):
        if self.draw_grid_flag:
            self.screen.fill((white))    
            self.rect = pygame.draw.rect(self.screen, (blue), (0, 0, WIDTH, 100))
            self.draw_grid_flag=False
            self.show_score()
            self.show_selected_box()
        # pygame.display.update()

        cell_pos=WIDTH/6


        for row in range(6):
            cell_pos=WIDTH/6
            for x,header in enumerate(range(6)):
                self.rect = pygame.draw.rect(self.screen, (black), (0, row*100, cell_pos, 100),2)
                cell_pos+=WIDTH/6
                # pygame.display.update()
        pygame.display.update()

    def clear_already_selected(self,col,row):
        pygame.draw.rect(self.screen, (black), (row*(WIDTH/6), col*100, WIDTH/6, 100))
        
    def show_score(self):
        curser=10
        self.rect = pygame.draw.rect(self.screen, (grey), (0,600 , WIDTH, 100))
        for team in team_names:
            self.screen.blit(self.font.render(team, True, (255,0,0)), (curser, 610))
            curser+=WIDTH/6
        curser=10
        for score in team_scores:
            self.screen.blit(self.font.render(str(score), True, (255,0,0)), (curser, 640))
            curser+=WIDTH/6
    def show_selected_box(self):
        self.show_score()
        self.rect = pygame.draw.rect(self.screen, (red), (selected_team_index*(WIDTH/6),600 , WIDTH/6, 100),3)
        self.rect = pygame.draw.rect(self.screen, (red), (selected_team_index*(WIDTH/6),700 , WIDTH/6, 100))
        
    def addText(self,pos,text):
        # print(pos,text)
        x = pos[0]*WIDTH/6+10
        y= 100*pos[1]+35
        color = red
        # print('Y',y)
        if y<100:
            color=yellow
        self.screen.blit(self.font.render(str(text), True, color), (x, y))


if __name__ == "__main__":
    pane1= Pane()
