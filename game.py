import pygame
import sys
import math
import asyncio

async def main():
    # Initialize Pygame
    pygame.init()

    # Constants
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    PLAYER_SIZE = 30
    ENEMY_SIZE = 20
    COIN_SIZE = 15
    PLAYER_SPEED = 5
    ENEMY_SPEED = 4

    # Colors
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    LIGHT_RED = (255, 100, 100)
    BLUE = (0, 0, 255)
    LIGHT_BLUE = (100, 100, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    WALL_COLOR = (100, 100, 100)
    BACKGROUND_COLOR = (240, 240, 240)
    SAFE_ZONE_COLOR = (200, 255, 200)

    # Set up the display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("World's Hardest Game")
    clock = pygame.time.Clock()

    class Wall:
        def __init__(self, x, y, width, height):
            self.rect = pygame.Rect(x, y, width, height)

    class Player:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
            self.deaths = 0
            self.start_x = x
            self.start_y = y

        def move(self, dx, dy):
            self.x += dx
            self.y += dy
            self.rect.x = self.x
            self.rect.y = self.y

        def draw(self, screen):
            inner_rect = pygame.Rect(self.x + 3, self.y + 3, PLAYER_SIZE - 6, PLAYER_SIZE - 6)
            pygame.draw.rect(screen, RED, self.rect)
            pygame.draw.rect(screen, LIGHT_RED, inner_rect)

        def reset_position(self):
            self.x = self.start_x
            self.y = self.start_y
            self.rect.x = self.x
            self.rect.y = self.y

    class Enemy:
        def __init__(self, x, y, path):
            self.x = x
            self.y = y
            self.path = path
            self.path_index = 0
            self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
            self.speed = ENEMY_SPEED

        def move(self):
            target = self.path[self.path_index]
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.speed:
                self.path_index = (self.path_index + 1) % len(self.path)
            else:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                self.x += dx
                self.y += dy
                self.rect.x = self.x
                self.rect.y = self.y

        def draw(self, screen):
            inner_rect = pygame.Rect(self.x + 3, self.y + 3, ENEMY_SIZE - 6, ENEMY_SIZE - 6)
            pygame.draw.rect(screen, BLUE, self.rect)
            pygame.draw.rect(screen, LIGHT_BLUE, inner_rect)

    class Coin:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.rect = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)
            self.collected = False
            self.animation_offset = 0
            self.animation_speed = 0.1

        def draw(self, screen):
            if not self.collected:
                self.animation_offset += self.animation_speed
                size_offset = math.sin(self.animation_offset) * 2
                pygame.draw.circle(screen, YELLOW,
                                 (self.x + COIN_SIZE // 2, self.y + COIN_SIZE // 2),
                                 (COIN_SIZE // 2) + size_offset)
                pygame.draw.circle(screen, (200, 200, 0),
                                 (self.x + COIN_SIZE // 2, self.y + COIN_SIZE // 2),
                                 (COIN_SIZE // 4) + size_offset)

    # Create walls
    walls = [
        Wall(50, 50, 700, 20),  # Top
        Wall(50, 530, 700, 20),  # Bottom
        Wall(50, 50, 20, 500),  # Left
        Wall(730, 50, 20, 500),  # Right
    ]

    # Create safe zones
    safe_zones = [
        pygame.Rect(70, 70, 100, 100),  # Starting safe zone
        pygame.Rect(630, 430, 100, 100)  # Ending safe zone
    ]

    # Create game objects
    player = Player(100, WINDOW_HEIGHT // 2)
    enemies = [
        Enemy(300, 200, [(300, 200), (300, 400)]),
        Enemy(500, 400, [(500, 400), (500, 200)]),
        Enemy(400, 300, [(400, 300), (400, 100), (400, 500), (400, 300)])
    ]
    coins = [
        Coin(400, 300),
        Coin(600, 300),
        Coin(300, 200)
    ]

    def draw_background_grid():
        for x in range(0, WINDOW_WIDTH, 40):
            pygame.draw.line(screen, (230, 230, 230), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 40):
            pygame.draw.line(screen, (230, 230, 230), (0, y), (WINDOW_WIDTH, y))

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player movement
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * PLAYER_SPEED
        
        old_x = player.x
        old_y = player.y
        
        player.move(dx, dy)

        # Wall collision
        for wall in walls:
            if player.rect.colliderect(wall.rect):
                player.x = old_x
                player.y = old_y
                player.rect.x = player.x
                player.rect.y = player.y

        # Keep player in bounds
        player.x = max(0, min(player.x, WINDOW_WIDTH - PLAYER_SIZE))
        player.y = max(0, min(player.y, WINDOW_HEIGHT - PLAYER_SIZE))
        player.rect.x = player.x
        player.rect.y = player.y

        # Move enemies
        for enemy in enemies:
            enemy.move()
            if player.rect.colliderect(enemy.rect):
                in_safe_zone = False
                for safe_zone in safe_zones:
                    if player.rect.colliderect(safe_zone):
                        in_safe_zone = True
                        break
                if not in_safe_zone:
                    player.deaths += 1
                    player.reset_position()

        # Check coin collection
        for coin in coins:
            if not coin.collected and player.rect.colliderect(coin.rect):
                coin.collected = True

        # Drawing
        screen.fill(BACKGROUND_COLOR)
        draw_background_grid()
        
        # Draw safe zones
        for safe_zone in safe_zones:
            pygame.draw.rect(screen, SAFE_ZONE_COLOR, safe_zone)
            pygame.draw.rect(screen, (150, 200, 150), safe_zone, 2)

        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, WALL_COLOR, wall.rect)
            pygame.draw.line(screen, (120, 120, 120), 
                            wall.rect.topleft, wall.rect.topright, 3)
            pygame.draw.line(screen, (80, 80, 80), 
                            wall.rect.bottomleft, wall.rect.bottomright, 3)
        
        # Draw coins
        for coin in coins:
            coin.draw(screen)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw player
        player.draw(screen)

        # Draw death counter with shadow effect
        font = pygame.font.Font(None, 36)
        shadow_text = font.render(f"Deaths: {player.deaths}", True, (50, 50, 50))
        deaths_text = font.render(f"Deaths: {player.deaths}", True, BLACK)
        screen.blit(shadow_text, (12, 12))
        screen.blit(deaths_text, (10, 10))

        pygame.display.flip()
        await asyncio.sleep(0)  # Required for Pygbag
        clock.tick(60)

asyncio.run(main())
