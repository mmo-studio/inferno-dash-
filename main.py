import pygame
import os
import math
import random
import array

# Инициализация
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# Константы
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Inferno Dash: Clean Sound")

# Цвета
LAVA_DEEP = (150, 20, 0)
LAVA_BRIGHT = (255, 100, 0)
SKY_DARK = (10, 0, 0)
SKY_RED = (50, 0, 0)
TEXT_COLOR = (255, 215, 0)
BTN_COLOR = (140, 0, 0)

SAVE_FILE = "highscore_pro.txt"

# Генерация приятного звука прыжка (короткий мягкий удар)
def generate_jump_sound():
    sample_rate = 22050
    duration = 0.15
    num_samples = int(sample_rate * duration)
    buf = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        freq = 300 - (t / duration) * 200
        wave = math.sin(2 * math.pi * freq * t)
        envelope = 1.0 - (i / num_samples)
        sample = int(wave * 12000 * envelope)
        buf.append(sample)
        
    return pygame.mixer.Sound(buffer=buf)

jump_sound = generate_jump_sound()

def load_highscore():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            try: return int(f.read())
            except: return 0
    return 0

def save_highscore(score):
    high = load_highscore()
    if score > high:
        with open(SAVE_FILE, "w") as f:
            f.write(str(score))

class AshParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(1, 2.5)
        self.size = random.randint(1, 3)
    def update(self, speed):
        self.y -= self.speed
        self.x -= speed * 0.25
        if self.y < 0: self.y = HEIGHT
        if self.x < 0: self.x = WIDTH
    def draw(self):
        pygame.draw.circle(screen, (80, 30, 20), (int(self.x), int(self.y)), self.size)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(150, 300, 40, 40)
        self.vel_y = 0
        self.jumps_left = 2
        self.gravity = 1.2
        self.jump_force = -16.5 

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = self.jump_force
            self.jumps_left -= 1
            if jump_sound:
                jump_sound.play()

    def update(self):
        self.vel_y += self.gravity
        if self.vel_y > 20: self.vel_y = 20
        self.rect.y += self.vel_y

    def draw(self):
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5
        pygame.draw.circle(screen, (255, 50, 0), self.rect.center, int(22 + pulse))
        pygame.draw.circle(screen, (255, 180, 0), self.rect.center, 16)
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.centerx + 10, self.rect.centery - 5), 5)
        pygame.draw.circle(screen, (0, 0, 0), (self.rect.centerx + 12, self.rect.centery - 5), 2)

class Platform:
    def __init__(self, x):
        self.rect = pygame.Rect(x, random.randint(420, 500), random.randint(180, 250), 30)
    def draw(self):
        pulse_color = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 150 + 100)
        pygame.draw.rect(screen, (30, 30, 30), self.rect, border_radius=4)
        pygame.draw.rect(screen, (pulse_color, 40, 0), self.rect, 3, border_radius=4)

class Dragon:
    def __init__(self, x, speed):
        self.rect = pygame.Rect(x, random.randint(150, 350), 85, 45)
        self.speed = speed + random.uniform(1.5, 3.0)
        
    def update(self):
        self.rect.x -= self.speed
        
    def draw(self):
        rx, ry, rw, rh = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        
        body_rect = pygame.Rect(rx + 20, ry + 12, rw - 30, rh - 20)
        pygame.draw.rect(screen, (110, 0, 160), body_rect, border_radius=12)
        pygame.draw.rect(screen, (180, 40, 230), body_rect, 2, border_radius=12)
        
        head_rect = pygame.Rect(rx, ry + 8, 30, 25)
        pygame.draw.ellipse(screen, (130, 10, 190), head_rect)
        pygame.draw.polygon(screen, (255, 200, 0), [(rx + 10, ry + 8), (rx + 5, ry - 4), (rx + 18, ry + 6)])
        pygame.draw.circle(screen, (255, 255, 0), (rx + 10, ry + 16), 4)
        pygame.draw.circle(screen, (0, 0, 0), (rx + 10, ry + 16), 2)
        
        wing_anim = math.sin(pygame.time.get_ticks() * 0.02) * 10
        pygame.draw.polygon(screen, (160, 50, 210), [
            (rx + 35, ry + 15), 
            (rx + 50, ry - 12 + wing_anim), 
            (rx + 65, ry + 15)
        ])
        
        tail_start = (rx + rw - 10, ry + 22)
        tail_end = (rx + rw + 15, ry + 15)
        pygame.draw.line(screen, (190, 80, 255), tail_start, tail_end, 5)
        pygame.draw.polygon(screen, (255, 100, 0), [tail_end, (tail_end[0] + 8, tail_end[1] - 5), (tail_end[0] + 4, tail_end[1] + 6)])

def game_loop():
    player = Player()
    base_speed = 7.0
    platforms = [Platform(100), Platform(500), Platform(900)]
    ash = [AshParticle() for _ in range(50)]
    dragons = []
    score = 0
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    last_dragon_spawn = 0
    
    while True:
        now = pygame.time.get_ticks()

        elapsed = (now - start_time) / 1000
        current_speed = min(base_speed + (score * 0.2) + (elapsed * 0.1), 16.0)

        for y in range(HEIGHT):
            color = (int(SKY_DARK[0] + (SKY_RED[0] - SKY_DARK[0]) * y / HEIGHT), 0, 0)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        
        for a in ash:
            a.update(current_speed)
            a.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                player.jump()

        # Лава
        for i in range(3):
            off = math.sin(pygame.time.get_ticks() * 0.003 + i) * 10
            pygame.draw.rect(screen, LAVA_DEEP if i==0 else LAVA_BRIGHT, (0, HEIGHT-25+i*8 + off, WIDTH, 40))

        # Платформы
        for p in platforms[:]:
            p.rect.x -= current_speed
            p.draw()
            
            if player.rect.colliderect(p.rect):
                if player.vel_y > 0 and player.rect.bottom <= p.rect.top + 22:
                    player.rect.bottom = p.rect.top
                    player.vel_y = 0
                    player.jumps_left = 2
            
            if p.rect.right < 0:
                platforms.remove(p)
                dist = random.randint(220, 380)
                platforms.append(Platform(platforms[-1].rect.right + dist))
                score += 1

        # Драконы
        if now - last_dragon_spawn > 1500:
            if random.random() < 0.2:
                dragons.append(Dragon(WIDTH + 100, current_speed))
                last_dragon_spawn = now

        for d in dragons[:]:
            d.update()
            d.draw()
            if d.rect.inflate(-15, -15).colliderect(player.rect): 
                return death_screen(score)
            if d.rect.right < -100: dragons.remove(d)

        player.update()
        player.draw()
        if player.rect.bottom > HEIGHT - 10: 
            return death_screen(score)

        draw_text(f"SOULS: {score}", 25, 80, 40)
        pygame.display.flip()
        clock.tick(60)

def draw_text(text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont("Verdana", size, bold=True)
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

def death_screen(score):
    save_highscore(score)
    high = load_highscore()
    while True:
        screen.fill((20, 2, 2))
        draw_text("YOU FELL", 60, WIDTH//2, HEIGHT//4, (200, 0, 0))
        draw_text(f"SCORE: {score} | BEST: {high}", 35, WIDTH//2, HEIGHT//2 - 20)
        
        # Кнопка RETRY (Заново)
        btn_retry = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 30, 220, 45)
        pygame.draw.rect(screen, BTN_COLOR, btn_retry, border_radius=8)
        draw_text("RETRY", 22, WIDTH//2, HEIGHT//2 + 52)

        # Кнопка MENU (Меню)
        btn_menu = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 85, 220, 45)
        pygame.draw.rect(screen, (100, 20, 20), btn_menu, border_radius=8)
        draw_text("MENU", 22, WIDTH//2, HEIGHT//2 + 107)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.collidepoint(event.pos): return "game"
                if btn_menu.collidepoint(event.pos): return "menu"
                
        pygame.display.flip()

def main_menu():
    while True:
        screen.fill(SKY_DARK)
        draw_text("INFERNO DASH", 70, WIDTH//2, HEIGHT//3, TEXT_COLOR)
        btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 60)
        pygame.draw.rect(screen, BTN_COLOR, btn, border_radius=12)
        draw_text("START", 35, WIDTH//2, HEIGHT//2 + 90)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(event.pos):
                    while True:
                        result = game_loop()
                        if result == "exit" or result == "menu":
                            break
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
