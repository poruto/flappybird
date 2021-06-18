import tkinter as tk
from random import randint, uniform

W_TITLE = "FlappyBird"
W_HEIGHT = 600
W_WIDTH = 1000
W_BG = "#88cffa"
fps = 60
FPS = int(1000 / fps) 

P_IMAGE = "./player.png"
P_START_COORDS = (150, W_HEIGHT / 2)
P_GRAVITY = 3
P_JUMP_POWER = 100

MAX_PILLARS = 3


def check_rect_collision(rect1, rect2):
    if rect2[0] <= rect1[0] <= rect2[2] and rect2[1] <= rect1[1] <= rect2[3]:
        return True
    else:
        return False
    

class App:
    def __init__(self):
        self.alive = True
        self.player = Player(self, P_START_COORDS, gravity=P_GRAVITY, jump_power=P_JUMP_POWER)
        self.pillar_manager = None
        self.run()

    def run(self):
        self.root = tk.Tk()
        self.root.title(W_TITLE)
        self.root.bind("<space>", self.player.jump) 
        self.root.bind("<r>", self.restart)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, bg=W_BG, width=W_WIDTH, height=W_HEIGHT)
        self.canvas.pack(fill="both")

        p_image = tk.PhotoImage(file=P_IMAGE)
        self.player.width, self.player.height = p_image.width(), p_image.height()
        self.canvas.create_image(self.player.x, self.player.y, tag="player",
                                 image=p_image)

        self.pillar_manager = PillarManager(self, self.canvas,
                                            self.player, max_pillars=MAX_PILLARS)

        self.root.after(FPS, self.update)
        self.root.mainloop()
    
    def restart(self, event):
        if self.alive is False:
            self.player.x = P_START_COORDS[0]
            self.player.y = P_START_COORDS[1]
            self.pillar_manager.restart()
            self.canvas.delete("gameover")
            self.alive = True
    
    def gameover(self):
        self.alive = False
        self.canvas.create_text(W_WIDTH/2, W_HEIGHT/2 - 15, text="GAME OVER", font="Arial 30", tag="gameover")
        self.canvas.create_text(W_WIDTH/2, W_HEIGHT/2 + 15, text="Zmáčkni R pro restart", font="Arial 15", tag="gameover")

    def update(self):
        if self.alive:
            self.player.update()
            self.pillar_manager.update()
        
        self.canvas.coords("player", self.player.x, self.player.y)
        self.root.after(FPS, self.update)


class Player:
    def __init__(self, app, start_coords, gravity=1, jump_power=25):
        self.app = app
        self.grounded = True
        self.c = 0
        self.x = start_coords[0]
        self.y = start_coords[1]
        self.gravity = gravity
        self.jump_power = jump_power

        self.width = None
        self.height = None

    def jump(self, event):
        if self.grounded or self.c > self.jump_power:
            self.grounded = False
            self.c = 0

    def update(self):
        if self.grounded is False and self.c <= self.jump_power and self.y >= 0:
            temp = self.jump_power / fps * 2
            self.c += temp
            self.y -= temp
        else:
            self.grounded = True
            if self.y + self.gravity < W_HEIGHT:
                self.y += self.gravity
            
            
class PillarManager:
    def __init__(self, app, canvas, player, max_pillars=1):
        self.app = app
        self.canvas = canvas
        self.player = player
        self.max_pillars = max_pillars
        self.pillars = []
    
    def restart(self):
        self.pillars = []
        self.canvas.delete("box")

    def update(self):
        collided = self.check_collisions()

        if collided:
            self.app.gameover()

        #  Vytváření sloupů
        if len(self.pillars) < self.max_pillars:
            create = False
            
            if len(self.pillars) == 0:
                create = True
            elif self.canvas.coords(self.pillars[len(self.pillars) - 1].pillar[0])[2] < W_WIDTH/2:
                create = True
            
            if create:
                pillar = Pillar(self.canvas, randint(25, 50), randint(50, 450))
                self.pillars.append(pillar)

        for pillar in self.pillars:
            pillar.update()

            if self.canvas.coords(pillar.pillar[0])[2] < 0:
                self.pillars.remove(pillar)

    def check_collisions(self):
        for pillar in self.pillars:
            for part in pillar.pillar:
                if check_rect_collision((self.player.x, self.player.y, self.player.x + self.player.width,
                                         self.player.y + self.player.height),
                                        self.canvas.coords(part)):
                    return True
                else:
                    pass
        return False


class Pillar:
    def __init__(self, canvas, width, height, color="green", speed=2):
        self.canvas = canvas
        self.color = color
        self.speed = speed

        self.pillar = (self.canvas.create_rectangle(W_WIDTH, 0, W_WIDTH - width, 0 + height, fill=color, tag="box"),
                       self.canvas.create_rectangle(W_WIDTH, W_HEIGHT, W_WIDTH - width,
                                                    W_HEIGHT - (W_HEIGHT - height - 200 * uniform(0.5, 1)), fill=color, tag="box"))

    def update(self):
        for part in self.pillar:
            coords = self.canvas.coords(part)
            self.canvas.coords(part, coords[0] - self.speed, coords[1], coords[2] - self.speed, coords[3])


if __name__ == "__main__":
    App()
