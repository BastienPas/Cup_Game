import os
import pygame
import random
import sys

pygame.init()

# Constantes
WIDTH, HEIGHT = 1920,1080
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (80, 80, 255)
score = 0
# Fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu des gobelets")
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont("Arial", 50)  # nom police, taille


if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(__file__)
    
def scoreimg():
    if score % 2 == 0:
        background = pygame.image.load(os.path.join(BASE_DIR, "Img", "Galaxie2.jpg")).convert_alpha()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    else:
        background = pygame.image.load(os.path.join(BASE_DIR, "Img", "Galaxie.jpg")).convert_alpha()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    return background

class Soucoupe:
    def __init__(self, x, y, size=100, speed=20):
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Img", "Soucoupe.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        
        self.speed = speed
        self.target_pos = (x, y)  # première position cible
        self.last_change = pygame.time.get_ticks()  # temps depuis dernier changement
        self.delay = 10  # délai (ms) entre 2 choix de cible

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
        

    def update(self):
        # Temps écoulé
        now = pygame.time.get_ticks()
        
        # Si la soucoupe est arrivée à sa cible et que le délai est passé -> nouvelle cible
        if self.rect.topleft == self.target_pos and now - self.last_change > self.delay:
            new_x = random.randint(0, WIDTH - self.size)
            new_y = random.randint(0, HEIGHT - self.size)
            self.target_pos = (new_x, new_y)
            self.last_change = now

        # Déplacement progressif vers target_pos
        x, y = self.rect.topleft
        tx, ty = self.target_pos
        if (x, y) != (tx, ty):
            dx, dy = tx - x, ty - y
            dist = (dx**2 + dy**2) ** 0.5
            if dist < self.speed:
                self.rect.topleft = self.target_pos
            else:
                self.rect.move_ip(self.speed * dx / dist, self.speed * dy / dist)


# Classe Cup
class Cup:
    def __init__(self, x, y, size=100, velocity=10):
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.velocity = velocity
        self.ball = False
        self.target_pos = self.rect.topleft  # position cible
        self.trail = []
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Img", "Etoile2.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.ballImage = pygame.image.load(os.path.join(BASE_DIR, "Img", "Cosmonaute.png")).convert_alpha()
        self.ballImage = pygame.transform.scale(self.ballImage, (size, size))

    def draw(self):
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                # Couleur qui s’éclaircit avec le temps
                alpha = max(50, 255 - i * 30)  
                color = (0, 0, alpha)  # bleu qui s'estompe
                pygame.draw.line(
                    screen,
                    color,
                    self.trail[i-1],
                    self.trail[i],
                    max(1, 15 - i)  # épaisseur diminue
                )
        screen.blit(self.image, self.rect.topleft)
        if self.ball:
            screen.blit(self.ballImage, self.rect.topleft)

    def update(self):
        # Déplacement progressif vers la target_pos
        x, y = self.rect.topleft
        tx, ty = self.target_pos
        self.velocity = 10 + score * 10 + (WIDTH / HEIGHT) * 15
        if (x, y) != (tx, ty):
            dx = tx - x
            dy = ty - y
            dist = (dx**2 + dy**2) ** 0.5
            if dist < self.velocity:
                self.rect.topleft = self.target_pos
            else:
                self.rect.move_ip(self.velocity * dx / dist, self.velocity * dy / dist)

            self.trail.insert(0, self.rect.center)

            # Limiter la longueur du trail
            if len(self.trail) > 20:
                self.trail.pop()
        else:
            # Si le cup est immobile -> trail vide
            self.trail.clear()

# Initialisation des 4 cups
margin = 100
cups = [
    Cup(margin, margin),                                # Haut gauche (1)
    Cup(WIDTH - margin - 100, margin),                  # Haut droite (2)
    Cup(margin, HEIGHT - margin - 100),                 # Bas gauche (3)
    Cup(WIDTH - margin - 100, HEIGHT - margin - 100),   # Bas droite (4)
    #Cup(WIDTH /2, HEIGHT - margin - 100),               # Bas millieu (5)
    #Cup(WIDTH /2, margin),                              # Haut millieu (6)
    #Cup(WIDTH /2, HEIGHT /2-margin/2),                  # Centre(7)
]

soucoupes = [
    Soucoupe(WIDTH /2 - 150, HEIGHT - margin + 50, size=150)  ]

state = "WAIT"  # WAIT -> SHOW -> SHUFFLE -> GUESS -> RESULT
ball_cup = None
shuffle_moves = 10 + score * 2

# Fonctions d'échange
def prepare_swap(c1, c2):
    # échange les positions cibles uniquement
    c1.target_pos, c2.target_pos = c2.target_pos, c1.target_pos

def random_swap():
    c1, c2 = random.sample(cups, 2)
    prepare_swap(c1, c2)

# Boucle principale
running = True
show_timer = 0
shuffles_done = 0
waiting_for_move = False
background = pygame.image.load(os.path.join(BASE_DIR, "Img", "Galaxie2.jpg")).convert_alpha()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and state == "WAIT":
                background=scoreimg()
                # Choisir une cup au hasard
                ball_cup = random.choice(cups)
                ball_cup.ball = True
                state = "SHOW"
                show_timer = pygame.time.get_ticks()

        if event.type == pygame.MOUSEBUTTONDOWN and state == "GUESS":
            pos = event.pos
            for c in cups:
                if c.rect.collidepoint(pos):
                    if c == ball_cup:
                        score += 1
                        c.ball = True
                        print("Bravo ! Score:", score)
                        soucoupes.append(Soucoupe(WIDTH /2 - 150, HEIGHT - margin + 50, size=150))
                    else:
                        print("Raté ! Score:", score)
                        ball_cup.ball = True
                    state = "RESULT"
                    result_timer = pygame.time.get_ticks()
    
    screen.blit(background, (0, 0))

    

    # Logique d'état
    if state == "SHOW":
        if pygame.time.get_ticks() - show_timer > 2000:
            ball_cup.ball = False
            state = "SHUFFLE"
            shuffles_done = 0
            waiting_for_move = False

    elif state == "SHUFFLE":
        if not waiting_for_move and shuffles_done < shuffle_moves:
            random_swap()
            waiting_for_move = True
        else:
            # Vérifie si toutes les cups ont atteint leur position
            if all(c.rect.topleft == c.target_pos for c in cups):
                shuffles_done += 1
                waiting_for_move = False
                if shuffles_done >= shuffle_moves:
                    state = "GUESS"
        

    elif state == "RESULT":
        if pygame.time.get_ticks() - result_timer > 2000:
            # Reset
            for c in cups:
                c.ball = False
            state = "WAIT"

    # Mise à jour et dessin
    for cup in cups:
        cup.update()
        cup.draw()

    for s in soucoupes:
        s.update()
        s.draw()

    # Création du texte
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # blanc

    # Affichage en haut au centre
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
