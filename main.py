# FILE: main.py
# AUTHOR: Juhana Kammonen (kammoji) assisted by CurreChat (https://curre.helsinki.fi/chat)
# PURPOSE: Hocky - The Immersive Ice Hockey Game main program logic

import pygame
import sys
import asyncio  # for WebAssembly with pygbag
from time import time


async def goal(puck_pos):
    # goal check logic
    global goals_blue, goals_red

    if puck_pos[0] in range(700, 715) and puck_pos[1] in range(183, 217):
        # Goal team Blue!
        pygame.mixer.Channel(1).play(pygame.mixer.Sound("sfx/goal_horn.mp3"))
        goals_blue += 1
        return True
    if puck_pos[0] in range(85, 100) and puck_pos[1] in range(183, 217):
        # Goal team Red!
        pygame.mixer.Channel(1).play(pygame.mixer.Sound("sfx/goal_horn.mp3"))
        goals_red += 1
        return True
    return False


async def move_puck(puck_pos, speed, heading):
    if heading == 0:  # heading is UP (0/360 degrees)
        # for step in range(puck_speed):
        puck_pos[1] -= speed
    if heading == 45:
        # for step in range(puck_speed):
        puck_pos[0] += speed // 2
        puck_pos[1] -= speed // 2
    if heading == 90:
        # for step in range(puck_speed):
        puck_pos[0] += speed
    if heading == 135:
        # for step in range(puck_speed):
        puck_pos[0] += speed // 2
        puck_pos[1] += speed // 2
    if heading == 180:
        # for step in range(puck_speed):
        puck_pos[1] += speed
    if heading == 225:
        # for step in range(puck_speed):
        puck_pos[0] -= speed // 2
        puck_pos[1] += speed // 2
    if heading == 270:
        # for step in range(puck_speed):
        puck_pos[0] -= speed
    if heading == 315:
        # for step in range(puck_speed):
        puck_pos[0] -= speed // 2
        puck_pos[1] -= speed // 2


# Initialize Pygame
pygame.init()


async def main():  # async for WebAssembly

    # Face the music!
    pygame.mixer.init()
    pygame.mixer.music.load("music/hocky.mp3")
    pygame.mixer.music.play()

    # Define constants
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
    RINK_WIDTH, RINK_HEIGHT = 600, 300
    WIDTH_MARGIN, HEIGHT_MARGIN = SCREEN_WIDTH - RINK_WIDTH, SCREEN_HEIGHT - RINK_HEIGHT
    PLAYER_RADIUS = 5
    PUCK_RADIUS = 4

    # Puck status
    PLAYER_HAS_PUCK = False
    OPPONENT_HAS_PUCK = False
    PUCK_SLIDE = False

    # Goal stuff
    GOAL_WAIT_INTERVAL = 1.5  # seconds
    QUIT_WAIT_INTERVAL = 1  # seconds

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
    player_heading = 90  # player heading in degrees

    # Define opponent properties
    opponent_pos = [SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2, 10, 20]
    opponent_speed = 2
    opponent_heading = 270  # opponent heading in degrees

    # Define puck properties
    puck_pos = [SCREEN_WIDTH // 2 + 1, SCREEN_HEIGHT // 2]
    puck_speed = 20

    # Goals:
    global goals_blue
    global goals_red
    goals_blue = 0
    goals_red = 0

    # Game loop
    running = True
    while running:
        event_list = pygame.event.get()
        keys = pygame.key.get_pressed()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.mixer.Channel(2).play(pygame.mixer.Sound("sfx/chime.mp3"))
                start = time()
                while time() - start <= QUIT_WAIT_INTERVAL:
                    pass  # time
                running = False

        # Handle player movement
        if keys[pygame.K_LEFT] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            player_pos[0] -= player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 270
        if keys[pygame.K_LEFT] and keys[pygame.K_UP]:
            player_pos[0] -= player_speed
            player_pos[1] -= player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 315
        if keys[pygame.K_RIGHT] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            player_pos[0] += player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 90
        if keys[pygame.K_RIGHT] and keys[pygame.K_UP]:
            player_pos[0] += player_speed
            player_pos[1] -= player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 45
        if keys[pygame.K_UP] and not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            player_pos[1] -= player_speed
            player_pos[2] = 20
            player_pos[3] = 10
            player_heading = 0
        if keys[pygame.K_RIGHT] and keys[pygame.K_DOWN]:
            player_pos[0] += player_speed
            player_pos[1] += player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 135
        if keys[pygame.K_DOWN] and not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            player_pos[1] += player_speed
            player_pos[2] = 20
            player_pos[3] = 10
            player_heading = 180
        if keys[pygame.K_LEFT] and keys[pygame.K_DOWN]:
            player_pos[0] -= player_speed
            player_pos[1] += player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 225
        if PLAYER_HAS_PUCK and keys[pygame.K_SPACE]:
            # Slapshot:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound("sfx/slapshot.mp3"))
            await move_puck(puck_pos, puck_speed, player_heading)
            PLAYER_HAS_PUCK = False
            PUCK_SLIDE = True

        # Handle puck movement
        if player_pos[0] in range(puck_pos[0] - 10, puck_pos[0] + 10) and player_pos[1] in range(
            puck_pos[1] - 10, puck_pos[1] + 10
        ):
            puck_pos[0] = player_pos[0]
            puck_pos[1] = player_pos[1]
            PLAYER_HAS_PUCK = True
            OPPONENT_HAS_PUCK = False
        if opponent_pos[0] in range(puck_pos[0] - 10, puck_pos[0] + 10) and opponent_pos[1] in range(
            puck_pos[1] - 10, puck_pos[1] + 10
        ):
            puck_pos[0] = opponent_pos[0]
            puck_pos[1] = opponent_pos[1]
            OPPONENT_HAS_PUCK = True
            PLAYER_HAS_PUCK = False

        if PUCK_SLIDE:
            for i in range(puck_speed, 0, -2):
                await move_puck(puck_pos, i, player_heading)
                # Puck has slid, need to check goal condition and if needed return puck to center!
                if await goal(puck_pos):
                    pygame.draw.circle(screen, BLACK, puck_pos, PUCK_RADIUS)
                    pygame.display.flip()
                    start = time()
                    while time() - start <= GOAL_WAIT_INTERVAL:
                        pass  # time
                    puck_pos = [SCREEN_WIDTH // 2 + 1, SCREEN_HEIGHT // 2]
                    player_pos = [SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, 10, 20]
                    opponent_pos = [SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2, 10, 20]
                    PUCK_SLIDE = False
                    break
                pygame.draw.circle(screen, BLACK, puck_pos, PUCK_RADIUS)
                pygame.display.flip()
            PUCK_SLIDE = False

        # Puck has moved, need to check goal condition and return puck to center!
        if await goal(puck_pos):
            start = time()
            while time() - start <= GOAL_WAIT_INTERVAL:
                pass  # time
            puck_pos = [SCREEN_WIDTH // 2 + 1, SCREEN_HEIGHT // 2]
            player_pos = [SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, 10, 20]
            opponent_pos = [SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2, 10, 20]
            PUCK_SLIDE = False

        # Opponent moves (towards puck):
        if puck_pos[0] > opponent_pos[0]:
            opponent_pos[0] += opponent_speed
            opponent_heading = 90
        elif puck_pos[0] < opponent_pos[0]:
            opponent_pos[0] -= opponent_speed
            opponent_heading = 270
        else:
            pass  # as in don't move
        if puck_pos[1] > opponent_pos[1]:
            opponent_pos[1] += opponent_speed
            opponent_heading = 180
        elif puck_pos[1] < opponent_pos[1]:
            opponent_pos[1] -= opponent_speed
            opponent_heading = 0
        else:
            pass  # as in don't move
        if OPPONENT_HAS_PUCK:  # Try towards opposite goal
            opponent_pos[0] -= opponent_speed
            opponent_heading = 270
            if opponent_pos[0] < 140:
                # slapshot:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound("sfx/slapshot.mp3"))
                await move_puck(puck_pos, puck_speed, opponent_heading)
                OPPONENT_HAS_PUCK = False
                PUCK_SLIDE = True

        # Ensure player and opponent stay within rink boundaries
        player_pos[0] = max(
            WIDTH_MARGIN // 2 + PLAYER_RADIUS, min(SCREEN_WIDTH - WIDTH_MARGIN // 2 - PLAYER_RADIUS - 20, player_pos[0])
        )
        player_pos[1] = max(
            HEIGHT_MARGIN // 2 + PLAYER_RADIUS, min(SCREEN_HEIGHT - HEIGHT_MARGIN // 2 - PLAYER_RADIUS - 20, player_pos[1])
        )
        opponent_pos[0] = max(
            WIDTH_MARGIN // 2 + PLAYER_RADIUS, min(SCREEN_WIDTH - WIDTH_MARGIN // 2 - PLAYER_RADIUS - 20, opponent_pos[0])
        )
        opponent_pos[1] = max(
            HEIGHT_MARGIN // 2 + PLAYER_RADIUS, min(SCREEN_HEIGHT - HEIGHT_MARGIN // 2 - PLAYER_RADIUS - 20, opponent_pos[1])
        )

        # Ensure puck stays within rink boundaries
        puck_pos[0] = max(WIDTH_MARGIN // 2 + PUCK_RADIUS, min(SCREEN_WIDTH - WIDTH_MARGIN // 2 - PUCK_RADIUS - 10, puck_pos[0]))
        puck_pos[1] = max(HEIGHT_MARGIN // 2 + PUCK_RADIUS, min(SCREEN_HEIGHT - HEIGHT_MARGIN // 2 - PUCK_RADIUS - 10, puck_pos[1]))

        # Clear the screen
        screen.fill(WHITE)

        # DEBUG: Player coords and heading on screen:
        # font = pygame.font.Font('freesansbold.ttf', 14)
        # text = font.render("Player:" + str(player_pos[0]) + ","
        #                    + str(player_pos[1]) + " | " + "Puck:" + str(puck_pos[0]) + "," + str(puck_pos[1]) + " | Hdg: " + str(player_heading), True, BLACK)
        # textRect = text.get_rect()
        # screen.blit(text, textRect)

        # Score on top:
        font = pygame.font.Font("freesansbold.ttf", 28)
        text = font.render(str(goals_blue) + " - " + str(goals_red), True, BLACK)
        score_rect = text.get_rect(center=(SCREEN_WIDTH / 2, 25))
        screen.blit(text, score_rect)

        # Draw the rink
        pygame.draw.rect(
            screen, BLUE, [(SCREEN_WIDTH - RINK_WIDTH) // 2, (SCREEN_HEIGHT - RINK_HEIGHT) // 2, RINK_WIDTH, RINK_HEIGHT], 5
        )

        # Draw the goals
        goal_width = 100
        goal_height = 50
        pygame.draw.rect(screen, RED, [(SCREEN_WIDTH - RINK_WIDTH) // 2 - 5, (SCREEN_HEIGHT - goal_height) // 2, 5, goal_height])
        pygame.draw.rect(screen, RED, [(SCREEN_WIDTH + RINK_WIDTH) // 2, (SCREEN_HEIGHT - goal_height) // 2, 5, goal_height])

        # Draw the player
        pygame.draw.ellipse(screen, BLUE, player_pos, PLAYER_RADIUS)

        # Draw the opponent
        pygame.draw.ellipse(screen, RED, opponent_pos, PLAYER_RADIUS)

        # Draw the puck
        pygame.draw.circle(screen, BLACK, puck_pos, PUCK_RADIUS)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        pygame.time.Clock().tick(60)
        await asyncio.sleep(0)

    # Quit Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
