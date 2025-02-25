from tokenize import Whitespace
import pygame
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animal Senses Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load assets
player_img = pygame.image.load("output/prerequisite_graph_subtopics.png")  # Replace with a small animal icon
player_img = pygame.transform.scale(player_img, (50, 50))

# Game variables
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5
food_x, food_y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
trail = [(food_x, food_y)]

# Sounds
sound_alert = pygame.mixer.Sound("alert.wav")  # Replace with a beep sound

# Game states
current_challenge = "hearing"  # Other options: "vision", "hearing", "touch"
run = True

# Game loop
while run:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed
    
    # Smell Challenge: Follow scent trail
    if current_challenge == "smell":
        for i in range(1, 10):
            trail.append((food_x - i * 10, food_y - i * 10))
        for t in trail:
            pygame.draw.circle(screen, GREEN, t, 5)
        pygame.draw.rect(screen, BLUE, (food_x, food_y, 20, 20))
    
    # Vision Challenge: Blurred vision simulation
    elif current_challenge == "vision":
        screen.fill((200, 200, 200))  # Simulating reduced visibility
        pygame.draw.rect(screen, BLUE, (food_x, food_y, 20, 20))
        pygame.draw.rect(screen, RED, (player_x, player_y, 50, 50))
    
    # Hearing Challenge: Sound clue
    elif current_challenge == "hearing":
        distance = abs(player_x - food_x) + abs(player_y - food_y)
        if distance < 100:
            sound_alert.play()
        pygame.draw.rect(screen, BLUE, (food_x, food_y, 20, 20))
    
    # Touch Challenge: Invisible obstacles
    elif current_challenge == "touch":
        obstacles = [(random.randint(100, 700), random.randint(100, 500)) for _ in range(5)]
        for obs in obstacles:
            pygame.draw.circle(screen, BLACK, obs, 20)
            if abs(player_x - obs[0]) < 20 and abs(player_y - obs[1]) < 20:
                print("You hit an obstacle! Change direction.")
    
    # Player movement
    screen.blit(player_img, (player_x, player_y))
    pygame.display.update()
    pygame.time.delay(50)

pygame.quit()
