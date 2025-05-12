# FILE: main.py
# AUTHOR: Juhana Kammonen (kammoji) assisted by CurreChat (https://curre.helsinki.fi/chat)
# PURPOSE: Hocky - The Immersive Ice Hockey Game main program logic

import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Define constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
RINK_WIDTH, RINK_HEIGHT = 600, 300
WIDTH_MARGIN, HEIGHT_MARGIN = SCREEN_WIDTH - RINK_WIDTH, SCREEN_HEIGHT - RINK_HEIGHT
PLAYER_RADIUS = 5
PUCK_RADIUS = 4

# Puck status
PUCK_ACQUIRED = False
PUCK_SLIDE = False

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hocky - The Immersive Ice Hockey Game")

# Define player properties
player_pos = [SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, 10, 20]
player_speed = 5

# Define puck properties
puck_pos = [SCREEN_WIDTH // 2 + 1, SCREEN_HEIGHT // 2]
puck_speed = 10

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
        player_pos[2] = 10
        player_pos[3] = 20
    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
        player_pos[2] = 10
        player_pos[3] = 20
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
        player_pos[2] = 20
        player_pos[3] = 10
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed
        player_pos[2] = 20
        player_pos[3] = 10
    if PUCK_ACQUIRED and keys[pygame.K_SPACE]:
        # Slapshot:
        puck_pos[0] += puck_speed
        PUCK_ACQUIRED = False
        PUCK_SLIDE = True
    
    # Handle puck movement
    if player_pos[0] in range(puck_pos[0]-10,puck_pos[0]+10) and player_pos[1] in range(puck_pos[1]-10,puck_pos[1]+10):
        puck_pos[0] = player_pos[0]
        puck_pos[1] = player_pos[1]
        PUCK_ACQUIRED = True

    if PUCK_SLIDE:
        for i in range(puck_speed):
            puck_pos[0] += i
            pygame.draw.circle(screen, BLACK, puck_pos, PUCK_RADIUS)
            pygame.display.flip()
        PUCK_SLIDE = False

    # Ensure player stays within rink boundaries
    player_pos[0] = max(WIDTH_MARGIN // 2 + PLAYER_RADIUS, min(SCREEN_WIDTH - WIDTH_MARGIN // 2 - PLAYER_RADIUS - 20, player_pos[0]))
    player_pos[1] = max(HEIGHT_MARGIN // 2 + PLAYER_RADIUS, min(SCREEN_HEIGHT - HEIGHT_MARGIN // 2 - PLAYER_RADIUS - 20, player_pos[1]))

    # Ensure puck stays within rink boundaries
    puck_pos[0] = max(WIDTH_MARGIN // 2 + PUCK_RADIUS, min(SCREEN_WIDTH - WIDTH_MARGIN // 2 - PUCK_RADIUS - 20, puck_pos[0]))
    puck_pos[1] = max(HEIGHT_MARGIN // 2 + PUCK_RADIUS, min(SCREEN_HEIGHT - HEIGHT_MARGIN // 2 - PUCK_RADIUS - 20, puck_pos[1]))

    # Clear the screen
    screen.fill(WHITE)

    # Player coords on screen:
    font = pygame.font.Font('freesansbold.ttf', 14)
    text = font.render("Player:" + str(player_pos[0]) + ","
                       + str(player_pos[1]) + " | " + "Puck:" + str(puck_pos[0]) + "," + str(puck_pos[1]), True, BLACK)
    textRect = text.get_rect()
    screen.blit(text, textRect)

    # Draw the rink
    pygame.draw.rect(screen, BLUE, [(SCREEN_WIDTH - RINK_WIDTH) // 2, (SCREEN_HEIGHT - RINK_HEIGHT) // 2, RINK_WIDTH, RINK_HEIGHT], 5)

    # Draw the goals
    goal_width = 100
    goal_height = 50
    pygame.draw.rect(screen, RED, [(SCREEN_WIDTH - RINK_WIDTH) // 2 - 5, (SCREEN_HEIGHT - goal_height) // 2, 5, goal_height])
    pygame.draw.rect(screen, RED, [(SCREEN_WIDTH + RINK_WIDTH) // 2, (SCREEN_HEIGHT - goal_height) // 2, 5, goal_height])

    # Draw the player
    pygame.draw.ellipse(screen, BLUE, player_pos, PLAYER_RADIUS)

    # Draw the puck
    pygame.draw.circle(screen, BLACK, puck_pos, PUCK_RADIUS)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()