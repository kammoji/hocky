# FILE: main.py
# AUTHOR: Juhana Kammonen (kammoji) assisted by CurreChat (https://curre.helsinki.fi/chat)
# PURPOSE: Hocky - The Immersive Ice Hockey Game main program logic

import math
import pygame
import sys
import asyncio  # for WebAssembly with pygbag
from time import time

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
RINK_WIDTH, RINK_HEIGHT = 600, 300
WIDTH_MARGIN = SCREEN_WIDTH - RINK_WIDTH
HEIGHT_MARGIN = SCREEN_HEIGHT - RINK_HEIGHT
PLAYER_RADIUS = 5
PUCK_RADIUS = 4

# Goal Dimensions (Add these!)
GOAL_HEIGHT = 50 
GOAL_TOP = (SCREEN_HEIGHT - GOAL_HEIGHT) // 2
GOAL_BOTTOM = (SCREEN_HEIGHT + GOAL_HEIGHT) // 2

# Rink Edges (Makes your bounce/goal code much cleaner)
RINK_LEFT = WIDTH_MARGIN // 2
RINK_RIGHT = SCREEN_WIDTH - WIDTH_MARGIN // 2
RINK_TOP = HEIGHT_MARGIN // 2
RINK_BOTTOM = SCREEN_HEIGHT - HEIGHT_MARGIN // 2

def goal(puck_pos):
    global goals_blue, goals_red
    
    # Goal Team Blue (Right side)
    # Using the RINK_RIGHT and GOAL_TOP/BOTTOM constants you defined at the top
    if puck_pos[0] >= RINK_RIGHT and GOAL_TOP <= puck_pos[1] <= GOAL_BOTTOM:
        pygame.mixer.Channel(1).play(pygame.mixer.Sound("sfx/goal_horn.mp3"))
        goals_blue += 1
        return True

    # Goal Team Red (Left side)
    if puck_pos[0] <= RINK_LEFT and GOAL_TOP <= puck_pos[1] <= GOAL_BOTTOM:
        pygame.mixer.Channel(1).play(pygame.mixer.Sound("sfx/goal_horn.mp3"))
        goals_red += 1
        return True
        
    return False


#async def move_puck(puck_pos, speed, heading, slide):
#    if heading == 0:  # heading is UP (0/360 degrees)
#        # for step in range(puck_speed):
#        puck_pos[1] -= speed 
#    if heading == 45:
#        # for step in range(puck_speed):
#        puck_pos[0] += speed // 2
#        puck_pos[1] -= speed  // 2
#    if heading == 90:
#        # for step in range(puck_speed):
#        puck_pos[0] += speed 
#    if heading == 135:
#        # for step in range(puck_speed):
#        puck_pos[0] += speed // 2
#        puck_pos[1] += speed // 2
#    if heading == 180:
#        # for step in range(puck_speed):
#        puck_pos[1] += speed 
#    if heading == 225:
#        # for step in range(puck_speed):
#        puck_pos[0] -= speed // 2
#        puck_pos[1] += speed // 2
#    if heading == 270:
#        # for step in range(puck_speed):
#        puck_pos[0] -= speed
#    if heading == 315:
#        # for step in range(puck_speed):
#        puck_pos[0] -= speed // 2
#        puck_pos[1] -= speed // 2
#    speed -= 2
#    if slide and speed > 0:
#        await move_puck(puck_pos, speed, heading, slide)
#    await asyncio.sleep(0)


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

    # START DEMO STUFF:
    DONE = False

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
    puck_speed = 10
    puck_vel = [0, 0] # New: [velocity_x, velocity_y]
    puck_pickup_cooldown = 0  # Frames until you can grab the puck again
    puck_slide_speed = 0
    puck_slide_heading = 0

    # Goals:
    global goals_blue
    global goals_red
    goals_blue = 0
    goals_red = 0

    # Create a big bold goal text font
    goal_font = pygame.font.Font("freesansbold.ttf", 100)
    show_goal_text = False
    goal_text_timer = 0

    # Game loop
    running = True
    while running:
        # Inside your loop:
        if puck_pickup_cooldown > 0:
            puck_pickup_cooldown -= 1
    
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
            # Transfer the current player heading and a set speed to the puck
            puck_slide_speed = 15 
            puck_slide_heading = player_heading

            PLAYER_HAS_PUCK = False
            PUCK_SLIDE = True
            puck_pickup_cooldown = 30  # Wait half a second (at 60fps) before grabbing it again

        # Handle puck movement
        if puck_pickup_cooldown == 0:  # <--- THIS IS THE KEY FIX
            # Player pickup
            if player_pos[0] in range(int(puck_pos[0]) - 15, int(puck_pos[0]) + 15) and \
            player_pos[1] in range(int(puck_pos[1]) - 15, int(puck_pos[1]) + 15):
                puck_pos[0], puck_pos[1] = player_pos[0], player_pos[1]
                PLAYER_HAS_PUCK = True
                OPPONENT_HAS_PUCK = False
                PUCK_SLIDE = False

            # Opponent pickup
            elif opponent_pos[0] in range(int(puck_pos[0]) - 15, int(puck_pos[0]) + 15) and \
                opponent_pos[1] in range(int(puck_pos[1]) - 15, int(puck_pos[1]) + 15):
                puck_pos[0], puck_pos[1] = opponent_pos[0], opponent_pos[1]
                OPPONENT_HAS_PUCK = True
                PLAYER_HAS_PUCK = False
                PUCK_SLIDE = False

        if PUCK_SLIDE:
             # 1. NEW MOVEMENT (Replacing await move_puck)
            rad = math.radians(puck_slide_heading)
            puck_pos[0] += math.sin(rad) * puck_slide_speed
            puck_pos[1] -= math.cos(rad) * puck_slide_speed

            # 2. BOUNCE (Keep ONLY this version)
            # Check for Left/Right hits
            if puck_pos[0] <= RINK_LEFT or puck_pos[0] >= RINK_RIGHT:
                # ONLY bounce if NOT in the goal range
                if not (GOAL_TOP <= puck_pos[1] <= GOAL_BOTTOM):
                    puck_slide_heading = 360 - puck_slide_heading
                    
            # Check for Top/Bottom hits
            if puck_pos[1] <= RINK_TOP or puck_pos[1] >= RINK_BOTTOM:
                puck_slide_heading = (180 - puck_slide_heading) % 360  

            # 3. FRICTION
            puck_slide_speed *= 0.98
            if puck_slide_speed < 0.5:
                PUCK_SLIDE = False
            if goal(puck_pos):
                # Instead of 'while time()', just reset immediately 
                # or use an async sleep if you want a pause
                puck_pos[0] = SCREEN_WIDTH // 2 + 1
                puck_pos[1] = SCREEN_HEIGHT // 2
                player_pos[0], player_pos[1] = SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2
                opponent_pos[0], opponent_pos[1] = SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2
                PUCK_SLIDE = False
                puck_slide_speed = 0
                
                puck_pickup_cooldown = 60  # 1 second of "hands off" after the goal

                # NEW: Trigger the goal text
                show_goal_text = True
                # Show for roughly 1.5 seconds (90 frames at 60fps)
                goal_text_timer = 90 
        
                # Give the user a brief pause without freezing the browser
                await asyncio.sleep(1) 

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
            # 1. Opponent movement logic
            opponent_pos[0] -= opponent_speed
            opponent_heading = 270
    
            # 2. Keep puck attached to opponent while carrying
            puck_pos[0] = opponent_pos[0]
            puck_pos[1] = opponent_pos[1]
    
            # 3. Slapshot Logic
            if opponent_pos[0] < 140:
                pygame.mixer.Channel(0).play(pygame.mixer.Sound("sfx/slapshot.mp3"))
                
                # Transfer the values to the sliding variables
                puck_slide_speed = 12  # Give the opponent a specific power
                puck_slide_heading = opponent_heading
                
                OPPONENT_HAS_PUCK = False
                PUCK_SLIDE = True
                puck_pickup_cooldown = 30  # Prevent opponent from instantly re-grabbing

        # Ensure player and opponent stay within rink boundaries
        # --- 1. CLAMP PLAYER ---
        player_pos[0] = max(RINK_LEFT + PLAYER_RADIUS, min(RINK_RIGHT - PLAYER_RADIUS - 10, player_pos[0]))
        player_pos[1] = max(RINK_TOP + PLAYER_RADIUS, min(RINK_BOTTOM - PLAYER_RADIUS - 20, player_pos[1]))

        # --- 2. CLAMP OPPONENT ---
        opponent_pos[0] = max(RINK_LEFT + PLAYER_RADIUS, min(RINK_RIGHT - PLAYER_RADIUS - 10, opponent_pos[0]))
        opponent_pos[1] = max(RINK_TOP + PLAYER_RADIUS, min(RINK_BOTTOM - PLAYER_RADIUS - 20, opponent_pos[1]))

        # --- 3. CLAMP PUCK (With Goal Opening) ---
        # We ONLY clamp the Puck's X-position if it's NOT in front of the goal
        if not (GOAL_TOP <= puck_pos[1] <= GOAL_BOTTOM):
            puck_pos[0] = max(RINK_LEFT + PUCK_RADIUS, min(RINK_RIGHT - PUCK_RADIUS, puck_pos[0]))

        # Always clamp Y (Top/Bottom boards)
        puck_pos[1] = max(RINK_TOP + PUCK_RADIUS, min(RINK_BOTTOM - PUCK_RADIUS, puck_pos[1]))

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
        font2 = pygame.font.Font("freesansbold.ttf", 62)
        text = font.render(str(goals_blue) + " - " + str(goals_red), True, BLACK)
        score_rect = text.get_rect(center=(SCREEN_WIDTH / 2, 25))
        screen.blit(text, score_rect)

        # Draw the rink
        pygame.draw.rect(
            screen, BLUE, [(SCREEN_WIDTH - RINK_WIDTH) // 2, (SCREEN_HEIGHT - RINK_HEIGHT) // 2, RINK_WIDTH, RINK_HEIGHT], 5
        )

        # Draw the goals
        pygame.draw.rect(screen, RED, [(SCREEN_WIDTH - RINK_WIDTH) // 2 - 5, (SCREEN_HEIGHT - GOAL_HEIGHT) // 2, 5, GOAL_HEIGHT])
        pygame.draw.rect(screen, RED, [(SCREEN_WIDTH + RINK_WIDTH) // 2, (SCREEN_HEIGHT - GOAL_HEIGHT) // 2, 5, GOAL_HEIGHT])

        pygame.draw.circle(screen, BLACK, (int(puck_pos[0]), int(puck_pos[1])), PUCK_RADIUS)

        # --- Was it a goal? If so, show the text for a brief moment:
        if show_goal_text and goal_text_timer > 0:
            # Flash every 15 frames
            if (goal_text_timer // 15) % 2 == 0:
                # Render the text
                text_surf = goal_font.render("GOAL!", True, RED)
                # Center it perfectly on the screen
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text_surf, text_rect)
            
            # Countdown the timer
            goal_text_timer -= 1
            if goal_text_timer <= 0:
                show_goal_text = False

        # Start demo (bouncing Hocky text):
        # Loop until the user clicks the start button.

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        # Starting position of the rectangle
        rect_x = 50
        rect_y = 50

        # Speed and direction of rectangle
        rect_change_x = 2
        rect_change_y = 2

        # -------- Demo Loop -----------
        while not DONE:
            # --- Event Processing
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pygame.mixer.Channel(2).play(pygame.mixer.Sound("sfx/chime.mp3"))
                    start = time()
                    while time() - start <= GOAL_WAIT_INTERVAL:
                        pass  # time
                    DONE = True

            # --- Logic
            # Move the rectangle starting point
            rect_x += rect_change_x
            rect_y += rect_change_y

            # Bounce the ball if needed
            if rect_y > SCREEN_HEIGHT - 50 or rect_y < 0:
                rect_change_y = rect_change_y * -1
            if rect_x > SCREEN_WIDTH - 220 or rect_x < 0:
                rect_change_x = rect_change_x * -1
            # Clear the screen
            screen.fill(WHITE)
            # Draw the rectangle
            text2 = font2.render("HOCKY", True, BLACK)
            text3 = font.render("Hit SPACE bar to start!", True, BLACK)
            rect = pygame.Rect(rect_x, rect_y, 50, 50)
            prompt_rect = text3.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
            screen.blit(text2, rect)
            screen.blit(text3, prompt_rect)

            # --- Wrap-up
            clock.tick(60)

            # Roll text!:
            pygame.display.flip()
            await asyncio.sleep(0)

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
