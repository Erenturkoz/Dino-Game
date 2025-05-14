import pygame
import random
import sys
import os

pygame.init()
obstacles = []
spawn_timer = 0

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 300
FPS = 60

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")


class Dino:
    def __init__(self, x, y):
        self.images = [
            pygame.image.load(os.path.join(ASSET_DIR, "Dino", "DinoRun1.png")),
            pygame.image.load(os.path.join(ASSET_DIR, "Dino", "DinoRun2.png"))
        ]
        self.duck_images = [
            pygame.image.load(os.path.join(ASSET_DIR, "Dino", "DinoDuck1.png")),
            pygame.image.load(os.path.join(ASSET_DIR, "Dino", "DinoDuck2.png"))
        ]
        self.index = 0
        self.image_timer = 0
        self.width = 65
        self.height = 70
        self.stand_width = 65
        self.stand_height = 70
        self.duck_width = 80
        self.duck_height = 41
        self.x = x
        self.y = y - self.height
        self.vel_y = 6
        self.gravity = 0.7
        self.is_jumping = False
        self.is_ducking = False
        self.stand_height = self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, keys, ground_y):
        # Zıplama
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.vel_y = -15
            self.is_jumping = True
        if keys[pygame.K_UP] and not self.is_jumping:
            self.vel_y = -15
            self.is_jumping = True
        if keys[pygame.K_DOWN] and not self.is_jumping:
            self.is_ducking = True
            self.width = self.duck_width
            self.height = self.duck_height
        else:
            self.is_ducking = False
            self.width = self.stand_width
            self.height = self.stand_height  


        self.vel_y += self.gravity
        self.y += self.vel_y

        # Zemine düşme kontrolü
        if self.y >= ground_y - self.height:
            self.y = ground_y - self.height
            self.is_jumping = False

        # Animasyon
        self.image_timer += 1
        if self.image_timer >= 10:
            self.index = (self.index + 1) % 2
            self.image_timer = 0

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.is_ducking:
            img = pygame.transform.scale(self.duck_images[self.index], (self.width, self.height))
        else:
            img = pygame.transform.scale(self.images[self.index], (self.width, self.height))

        screen.blit(img, (self.x, self.y))

    def draw_hitbox(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height), 2)    


class Ground:
    def __init__(self, y, speed):
        self.image = pygame.image.load(os.path.join(ASSET_DIR, "Other", "Track.png"))
        self.parts = [{"x": 0}, {"x": self.image.get_width()}]
        self.y = y - 25
        self.speed = speed

    def update(self):
        for part in self.parts:
            part["x"] -= self.speed

        # Eski parça çıkarsa kaldır
        if self.parts[0]["x"] <= -self.image.get_width():
            self.parts.pop(0)

        # Yeni parça gerekirse ekle
        if self.parts[-1]["x"] <= SCREEN_WIDTH:
            new_x = self.parts[-1]["x"] + self.image.get_width()
            self.parts.append({"x": new_x})

    def draw(self, screen):
        for part in self.parts:
            screen.blit(self.image, (part["x"], self.y))

class Obstacle:
    def __init__(self, image, x, y, speed):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return self.x + self.width < 0
    def draw_hitbox(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), self.rect, 2)


class Cactus(Obstacle):
    def __init__(self, ground_y, speed, asset_dir):
        self.image_list = [
            pygame.image.load(os.path.join(asset_dir, "Cactus", "SmallCactus1.png")),
            pygame.image.load(os.path.join(asset_dir, "Cactus", "SmallCactus2.png")),
            pygame.image.load(os.path.join(asset_dir, "Cactus", "SmallCactus3.png")),
            pygame.image.load(os.path.join(asset_dir, "Cactus", "LargeCactus1.png")),
            pygame.image.load(os.path.join(asset_dir, "Cactus", "LargeCactus2.png")),
            pygame.image.load(os.path.join(asset_dir, "Cactus", "LargeCactus3.png")),
        ]
        image = random.choice(self.image_list)
        scale_factor = 0.7
        new_width = int(image.get_width() * scale_factor)
        new_height = int(image.get_height() * scale_factor)
        image = pygame.transform.scale(image, (new_width, new_height))
        y = ground_y - image.get_height()  # Zemine oturt
        super().__init__(image, x=800, y=y, speed=speed)

class Bird(Obstacle):
    def __init__(self, speed, asset_dir, ground_y):
        scale_factor = 0.7
        self.images = [
            pygame.transform.scale(
                pygame.image.load(os.path.join(asset_dir, "Bird", "Bird1.png")),
                (int(93 * scale_factor), int(62 * scale_factor))
            ),
            pygame.transform.scale(
                pygame.image.load(os.path.join(asset_dir, "Bird", "Bird2.png")),
                (int(93 * scale_factor), int(62 * scale_factor))
            )
        ]
        self.index = 0
        self.image_timer = 0

        possible_y = [ground_y - 150, ground_y - 90, ground_y - 120]
        y = random.choice(possible_y)

        self.x = 800
        self.y = y
        self.speed = speed

        image = self.images[self.index]
        super().__init__(image, self.x, self.y, speed)

    def update(self):
        super().update()
        self.image_timer += 1
        if self.image_timer >= 10:
            self.index = (self.index + 1) % 2
            self.image_timer = 0
            self.image = self.images[self.index]
            self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())                       


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dino Game")

    clock = pygame.time.Clock()
    ground_y = 250
    game_over = False

    font_path = os.path.join(ASSET_DIR, "other", "PressStart2P-Regular.ttf")
    font = pygame.font.Font(font_path, 16)
    score = 0
    speed = 5

    game_over_img = pygame.image.load(os.path.join(ASSET_DIR, "Other", "GameOver.png"))
    game_over_rect = game_over_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_img = pygame.image.load(os.path.join(ASSET_DIR, "Other", "Reset.png"))
    restart_rect = restart_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    dino = Dino(x=50, y=ground_y)
    ground = Ground(y=ground_y, speed=speed)

    obstacles = []
    spawn_timer = 0

    while True:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                if restart_rect.collidepoint(event.pos):
                    main()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        for obs in obstacles:
            obs.draw(screen)
            obs.draw_hitbox(screen)

        if not game_over:
            # Skor ve en yüksek skor güncellemesi
            score += 0.25

            ground.speed = speed

            dino.update(keys, ground_y)
            ground.update()

            for obs in obstacles[:]:
                obs.speed = speed
                obs.update()
                obs.draw(screen)

                if dino.rect.colliderect(obs.rect):
                    game_over = True
                    break

                if obs.off_screen():
                    obstacles.remove(obs)

            # Yeni engel üret
            spawn_timer -= 1
            if spawn_timer <= 0:
                if random.random() < 0.7:
                    obstacles.append(Cactus(ground_y, speed=speed, asset_dir=ASSET_DIR))
                else:
                    obstacles.append(Bird(speed=speed, asset_dir=ASSET_DIR, ground_y=ground_y))
                spawn_timer = random.randint(60, 120)

        # Arkaplan ve karakter çizimi (her durumda çizilsin)
        ground.draw(screen)
        dino.draw(screen)
        dino.draw_hitbox(screen)

        # Skor   
        score_text = font.render(f"SCORE {int(score):04}", True, (0, 0, 0))
        text_width = score_text.get_width()
        screen.blit(score_text, (SCREEN_WIDTH - text_width - 10, 10))

        if int(score) % 100 == 0:  # her 100 puanda bir hızlan
            speed += 0.5

        # Game Over ekranı
        if game_over:
            screen.blit(game_over_img, game_over_rect)
            screen.blit(game_over_img, game_over_rect)
            screen.blit(restart_img, restart_rect)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
