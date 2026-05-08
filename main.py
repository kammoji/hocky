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
GOAL_TOP = (RINK_HEIGHT - GOAL_HEIGHT) // 2
GOAL_BOTTOM = GOAL_TOP + GOAL_HEIGHT

# Rink Edges (Makes your bounce/goal code much cleaner)
RINK_LEFT = 0
RINK_RIGHT = RINK_WIDTH
RINK_TOP = 0
RINK_BOTTOM = RINK_HEIGHT

# Virtual Controls Config
JOYSTICK_X, JOYSTICK_Y = 150, 450
JOYSTICK_RADIUS = 60

FIRE_BTN_X, FIRE_BTN_Y = 650, 450  # Adjusted for typical mobile landscape
FIRE_BTN_RADIUS = 70


def draw_fire_button(screen, text=None):
    # 1. Draw the translucent red circle
    fire_surf = pygame.Surface((FIRE_BTN_RADIUS * 2, FIRE_BTN_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(fire_surf, (255, 0, 0, 180), (FIRE_BTN_RADIUS, FIRE_BTN_RADIUS), FIRE_BTN_RADIUS)

    # 2. Add text if provided (e.g., "START" or "TULI")
    if text:
        # Use whatever font you already have loaded
        font = pygame.font.SysFont("Arial", 30, bold=True)
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(FIRE_BTN_RADIUS, FIRE_BTN_RADIUS))
        fire_surf.blit(text_surf, text_rect)

    # 3. Blit to the main screen
    screen.blit(fire_surf, (FIRE_BTN_X - FIRE_BTN_RADIUS, FIRE_BTN_Y - FIRE_BTN_RADIUS))


def goal(puck_pos, off_x, off_y):
    global goals_blue, goals_red

    # 1. Calculate the dynamic Goal Y boundaries
    # This must match your drawing logic: OFFSET_Y + (RINK_HEIGHT - GOAL_HEIGHT) // 2
    g_top = off_y + (RINK_HEIGHT - GOAL_HEIGHT) // 2
    g_bottom = g_top + GOAL_HEIGHT

    # 2. Calculate dynamic X boundaries
    g_left_x = off_x
    g_right_x = off_x + RINK_WIDTH

    # Goal Team Blue (Scores in Right Goal)
    if puck_pos[0] + off_x >= g_right_x and g_top <= puck_pos[1] + off_y <= g_bottom:
        pygame.mixer.Channel(1).play(pygame.mixer.Sound("sfx/goal_horn.mp3"))
        goals_blue += 1
        return True

    # Goal Team Red (Scores in Left Goal)
    if puck_pos[0] + off_x <= g_left_x and g_top <= puck_pos[1] + off_y <= g_bottom:
        pygame.mixer.Channel(1).play(pygame.mixer.Sound("sfx/goal_horn.mp3"))
        goals_red += 1
        return True

    return False


class VirtualJoystick:
    def __init__(self, x, y, radius=50):
        self.base_pos = (x, y)
        self.knob_pos = (x, y)
        self.radius = radius
        self.active = False
        self.vector = [0, 0]  # This will replace your arrow keys

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            pos = getattr(event, "pos", (0, 0))
            if math.hypot(pos[0] - self.base_pos[0], pos[1] - self.base_pos[1]) < self.radius * 2:
                self.active = True

        elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
            self.active = False
            self.knob_pos = self.base_pos
            self.vector = [0, 0]

        elif (event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION) and self.active:
            pos = getattr(event, "pos", (0, 0))
            dx = pos[0] - self.base_pos[0]
            dy = pos[1] - self.base_pos[1]
            dist = math.hypot(dx, dy)

            # Keep knob inside the circle
            angle = math.atan2(dy, dx)
            clamped_dist = min(dist, self.radius)
            self.knob_pos = (self.base_pos[0] + math.cos(angle) * clamped_dist, self.base_pos[1] + math.sin(angle) * clamped_dist)

            # Normalize vector for movement (-1 to 1)
            self.vector = [math.cos(angle) * (clamped_dist / self.radius), math.sin(angle) * (clamped_dist / self.radius)]

    def draw(self, screen, font, text=None):
        # 1. Draw the base circle (the grey socket)
        pygame.draw.circle(screen, (150, 150, 150), self.base_pos, self.radius, 3)

        # 2. Draw the knob (the red handle)
        pygame.draw.circle(screen, (200, 0, 0), (int(self.knob_pos[0]), int(self.knob_pos[1])), 20)

        # 3. Draw the label (MOVE)
        if text and font:
            t_surf = font.render(text, True, (0, 0, 0))  # BLACK for white background
            t_rect = t_surf.get_rect(center=(self.base_pos[0], self.base_pos[1] - (self.radius + 30)))
            screen.blit(t_surf, t_rect)


# Initialize Pygame
pygame.init()


async def main():  # async for WebAssembly

    # Face the music!
    pygame.mixer.init()
    pygame.mixer.music.load("music/hocky.mp3")
    pygame.mixer.music.play()

    # Define constants
    SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
    RINK_WIDTH, RINK_HEIGHT = 600, 300
    OFFSET_X = (SCREEN_WIDTH - RINK_WIDTH) // 2
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

    # Define player properties (Logic-based center of the ICE)
    # Start the player on the left side of the center ice
    player_pos = [RINK_WIDTH // 2 - 40, RINK_HEIGHT // 2, 10, 20]
    player_speed = 5
    player_heading = 90  # player heading in degrees

    # Define opponent properties
    # Start the opponent on the right side of the center ice
    opponent_pos = [RINK_WIDTH // 2 + 40, RINK_HEIGHT // 2, 10, 20]
    opponent_speed = 2
    opponent_heading = 270  # opponent heading in degrees

    # Define puck properties
    puck_pos = [RINK_WIDTH // 2, RINK_HEIGHT // 2]
    puck_speed = 10
    puck_vel = [0, 0]  # New: [velocity_x, velocity_y]
    puck_pickup_cooldown = 0  # Frames until you can grab the puck again
    puck_slide_speed = 0
    puck_slide_heading = 0

    # Goals:
    global goals_blue
    global goals_red
    goals_blue = 0
    goals_red = 0
    scoring_team = "NONE"

    # Create a big bold goal text font
    goal_font = pygame.font.Font("freesansbold.ttf", 100)
    show_goal_text = False
    goal_text_timer = 0

    joystick = VirtualJoystick(150, 450)

    # Position the fire button in the bottom right
    fire_button_pos = (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120)
    fire_button_radius = 60
    fire_button_color = (255, 0, 0, 100)  # Semi-transparent Red

    # Game loop
    running = True
    while running:
        # Get live screen dimensions every frame for WASM/Mobile safety
        sw, sh = screen.get_size()
        OFFSET_X = (sw - RINK_WIDTH) // 2
        OFFSET_Y = (sh - RINK_HEIGHT) // 2  # Center it vertically too

        # Calculate SAFE positions (180px up from bottom to avoid browser bars)
        JOY_POS = (100, sh - 180)
        FIRE_POS = (sw - 100, sh - 180)

        # Update your joystick's internal position to match
        joystick.base_pos = JOY_POS
        if not joystick.active:
            joystick.knob_pos = JOY_POS

        if puck_pickup_cooldown > 0:
            puck_pickup_cooldown -= 1

        event_list = pygame.event.get()
        keys = pygame.key.get_pressed()
        mobile_fire_trigger = False
        for event in event_list:
            joystick.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.mixer.Channel(2).play(pygame.mixer.Sound("sfx/chime.mp3"))
                start = time()
                while time() - start <= QUIT_WAIT_INTERVAL:
                    pass  # time
                running = False

        # Handle player movement

        # Get joystick vector
        jx, jy = joystick.vector

        # Determine movement from Keys OR Joystick
        move_left = keys[pygame.K_LEFT] or jx < -0.3
        move_right = keys[pygame.K_RIGHT] or jx > 0.3
        move_up = keys[pygame.K_UP] or jy < -0.3
        move_down = keys[pygame.K_DOWN] or jy > 0.3

        # Slapshot logic (Keys OR Joystick "Fire" button later)
        # For now, let's say a touch on the right 20% of screen = Space
        touch_fire = False
        for event in event_list:
            if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Use a distance check (like we did for the joystick)
                f_pos = getattr(event, "pos", (0, 0))
                # For pygbag/mobile, multiply normalized coords by screen size
                if hasattr(event, "x"):
                    f_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)

                dist = math.hypot(f_pos[0] - fire_button_pos[0], f_pos[1] - fire_button_pos[1])
                if dist < fire_button_radius:
                    mobile_fire_trigger = True

        if move_left and not move_up and not move_down:
            player_pos[0] -= player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 270
        if move_left and move_up:
            player_pos[0] -= player_speed
            player_pos[1] -= player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 315
        if move_right and not move_up and not move_down:
            player_pos[0] += player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 90
        if move_right and move_up:
            player_pos[0] += player_speed
            player_pos[1] -= player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 45
        if move_up and not move_left and not move_right:
            player_pos[1] -= player_speed
            player_pos[2] = 20
            player_pos[3] = 10
            player_heading = 0
        if move_right and move_down:
            player_pos[0] += player_speed
            player_pos[1] += player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 135
        if move_down and not move_left and not move_right:
            player_pos[1] += player_speed
            player_pos[2] = 20
            player_pos[3] = 10
            player_heading = 180
        if move_left and move_down:
            player_pos[0] -= player_speed
            player_pos[1] += player_speed
            player_pos[2] = 10
            player_pos[3] = 20
            player_heading = 225
        if PLAYER_HAS_PUCK and (keys[pygame.K_SPACE] or mobile_fire_trigger):
            # Slapshot:
            pygame.mixer.Channel(0).play(pygame.mixer.Sound("sfx/slapshot.mp3"))
            # Transfer the current player heading and a set speed to the puck
            puck_slide_speed = 15
            puck_slide_heading = player_heading

            PLAYER_HAS_PUCK = False
            PUCK_SLIDE = True
            puck_pickup_cooldown = 30  # Wait half a second (at 60fps) before grabbing it again

        # Corners:
        # List of positions to check (You and the AI)
        for pos in [player_pos, opponent_pos]:
            # --- 1. Basic Wall Bounds ---
            if pos[0] < RINK_LEFT + PLAYER_RADIUS:
                pos[0] = RINK_LEFT + PLAYER_RADIUS
            if pos[0] > RINK_RIGHT - PLAYER_RADIUS:
                pos[0] = RINK_RIGHT - PLAYER_RADIUS
            if pos[1] < RINK_TOP + PLAYER_RADIUS:
                pos[1] = RINK_TOP + PLAYER_RADIUS
            if pos[1] > RINK_BOTTOM - PLAYER_RADIUS:
                pos[1] = RINK_BOTTOM - PLAYER_RADIUS

            # --- 2. Angular Corner Bounds ---
            # We use the same corner_size as the rink (e.g., 30)
            c = 30 + PLAYER_RADIUS

            # Top-Left Corner
            if pos[0] + pos[1] < (RINK_LEFT + RINK_TOP + c):
                # If player tries to go into the corner, push them back
                pos[0] += 2
                pos[1] += 2

            # Top-Right Corner
            if (RINK_RIGHT - pos[0]) + pos[1] < (RINK_TOP + c):
                pos[0] -= 2
                pos[1] += 2

            # Bottom-Left Corner
            if pos[0] + (RINK_BOTTOM - pos[1]) < (RINK_LEFT + c):
                pos[0] += 2
                pos[1] -= 2

            # Bottom-Right Corner
            if (RINK_RIGHT - pos[0]) + (RINK_BOTTOM - pos[1]) < c:
                pos[0] -= 2
                pos[1] -= 2

        # Handle puck movement
        if puck_pickup_cooldown == 0:  # <--- THIS IS THE KEY FIX
            # Player pickup
            if player_pos[0] in range(int(puck_pos[0]) - 15, int(puck_pos[0]) + 15) and player_pos[1] in range(
                int(puck_pos[1]) - 15, int(puck_pos[1]) + 15
            ):
                puck_pos[0], puck_pos[1] = player_pos[0], player_pos[1]
                PLAYER_HAS_PUCK = True
                OPPONENT_HAS_PUCK = False
                PUCK_SLIDE = False

            # Opponent pickup
            elif opponent_pos[0] in range(int(puck_pos[0]) - 15, int(puck_pos[0]) + 15) and opponent_pos[1] in range(
                int(puck_pos[1]) - 15, int(puck_pos[1]) + 15
            ):
                puck_pos[0], puck_pos[1] = opponent_pos[0], opponent_pos[1]
                OPPONENT_HAS_PUCK = True
                PLAYER_HAS_PUCK = False
                PUCK_SLIDE = False

        if PUCK_SLIDE:
            # 1. MOVEMENT
            rad = math.radians(puck_slide_heading)
            puck_pos[0] += math.sin(rad) * puck_slide_speed
            puck_pos[1] -= math.cos(rad) * puck_slide_speed

            # 2. BOUNCE & SNAP
            # Side Walls (Left/Right)
            if puck_pos[0] <= RINK_LEFT or puck_pos[0] >= RINK_RIGHT:
                if not (GOAL_TOP <= puck_pos[1] <= GOAL_BOTTOM):
                    # SNAP: Force it back inside
                    if puck_pos[0] <= RINK_LEFT:
                        puck_pos[0] = RINK_LEFT + 3
                    else:
                        puck_pos[0] = RINK_RIGHT - 3
                    puck_slide_heading = 360 - puck_slide_heading

            # TOP Wall (The missing piece!)
            if puck_pos[1] <= RINK_TOP:
                puck_pos[1] = RINK_TOP + 3  # SNAP DOWN
                puck_slide_heading = (180 - puck_slide_heading) % 360
                puck_slide_speed += 0.2

            # BOTTOM Wall
            if puck_pos[1] >= RINK_BOTTOM:
                puck_pos[1] = RINK_BOTTOM - 3  # SNAP UP
                puck_slide_heading = (180 - puck_slide_heading) % 360
                puck_slide_speed += 0.5

            # --- Invisible Corner Bumpers ---
            corner_size = 30
            kick_force = 0.9

            # TOP-LEFT
            if puck_pos[0] < RINK_LEFT + corner_size and puck_pos[1] < RINK_TOP + 15:
                puck_slide_heading = 135
                puck_slide_speed *= kick_force
                puck_pos[0], puck_pos[1] = RINK_LEFT + corner_size + 1, RINK_TOP + 16

            # TOP-RIGHT
            elif puck_pos[0] > RINK_RIGHT - corner_size and puck_pos[1] < RINK_TOP + 15:
                puck_slide_heading = 225
                puck_slide_speed *= kick_force
                puck_pos[0], puck_pos[1] = RINK_RIGHT - corner_size - 1, RINK_TOP + 16

            # BOTTOM-LEFT
            elif puck_pos[0] < RINK_LEFT + corner_size and puck_pos[1] > RINK_BOTTOM - corner_size:
                puck_slide_heading = 45
                puck_slide_speed *= kick_force
                puck_pos[0], puck_pos[1] = RINK_LEFT + corner_size + 1, RINK_BOTTOM - corner_size - 1

            # BOTTOM-RIGHT
            elif puck_pos[0] > RINK_RIGHT - corner_size and puck_pos[1] > RINK_BOTTOM - corner_size:
                puck_slide_heading = 315
                puck_slide_speed *= kick_force
                puck_pos[0], puck_pos[1] = RINK_RIGHT - corner_size - 1, RINK_BOTTOM - corner_size - 1

            # 3. FRICTION
            puck_slide_speed *= 0.98
            if puck_slide_speed < 0.5:
                PUCK_SLIDE = False
            if goal(puck_pos, OFFSET_X, OFFSET_Y):

                # If the puck is on the right side of the rink, Blue scored
                if puck_pos[0] > SCREEN_WIDTH // 2:
                    scoring_team = BLUE
                else:
                    scoring_team = RED

                # 2. Reset positions to the center of the RINK (Internal logic 0-800)
                puck_pos[0] = RINK_WIDTH // 2
                puck_pos[1] = RINK_HEIGHT // 2

                # Start players on their respective sides of the CENTER ICE
                player_pos[0], player_pos[1] = RINK_WIDTH // 2 - 50, RINK_HEIGHT // 2
                opponent_pos[0], opponent_pos[1] = RINK_WIDTH // 2 + 50, RINK_HEIGHT // 2
                PUCK_SLIDE = False
                puck_slide_speed = 0

                puck_pickup_cooldown = 60  # 1 second of "hands off" after the goal

                # NEW: Trigger the goal text
                show_goal_text = True
                # Show for roughly 2 seconds (120 frames at 60fps)
                goal_text_timer = 120

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

        # The "Black Bar" size on the left
        OFFSET_X = (SCREEN_WIDTH - RINK_WIDTH) // 2

        # Clears sidebars:
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
        text = font2.render(str(goals_blue) + " - " + str(goals_red), True, BLACK)
        score_rect = text.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(text, score_rect)

        # Draw the rink

        c = 30  # = corner size

        # Apply BOTH offsets to the rink points
        rink_points = [
            (OFFSET_X + c, OFFSET_Y),
            (OFFSET_X + RINK_WIDTH - c, OFFSET_Y),
            (OFFSET_X + RINK_WIDTH, OFFSET_Y + c),
            (OFFSET_X + RINK_WIDTH, OFFSET_Y + RINK_HEIGHT - c),
            (OFFSET_X + RINK_WIDTH - c, OFFSET_Y + RINK_HEIGHT),
            (OFFSET_X + c, OFFSET_Y + RINK_HEIGHT),
            (OFFSET_X, OFFSET_Y + RINK_HEIGHT - c),
            (OFFSET_X, OFFSET_Y + c),
        ]
        pygame.draw.polygon(screen, WHITE, rink_points)

        # Draw the rink border (Black line, width 3)
        pygame.draw.polygon(screen, BLACK, rink_points, 3)

        # Draw Goals (Centered automatically by OFFSET_Y)
        pygame.draw.rect(screen, RED, [OFFSET_X - 5, OFFSET_Y + (RINK_HEIGHT - GOAL_HEIGHT) // 2, 5, GOAL_HEIGHT])
        pygame.draw.rect(screen, RED, [OFFSET_X + RINK_WIDTH, OFFSET_Y + (RINK_HEIGHT - GOAL_HEIGHT) // 2, 5, GOAL_HEIGHT])

        # --- Was it a goal? If so, show the text for a brief moment:
        if show_goal_text and goal_text_timer > 0:

            # Flash every 15 frames
            if (goal_text_timer // 15) % 2 == 0:
                # 1. Use Size 48
                goal_font = pygame.font.SysFont("Arial", 48, bold=True)

                # 2. Use scoring_team directly (it's already the color)
                text_surf = goal_font.render("GOAL!", True, scoring_team)

                # 3. Position higher (-100 from center)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) - 100))
                screen.blit(text_surf, text_rect)

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
            # Force-refresh coordinates
            sw, sh = screen.get_size()
            OFFSET_X = (SCREEN_WIDTH - RINK_WIDTH) // 2

            # Move them 250px up from the floor
            JOY_POS = (100, sh - 250)
            FIRE_POS = (sw - 100, sh - 250)

            # Re-link the joystick to the new position
            joystick.base_pos = JOY_POS
            joystick.knob_pos = JOY_POS
            # --- Event Processing
            event_list = pygame.event.get()
            for event in event_list:
                # 1. Check for Keyboard Start
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    start_trigger = True

                # 2. Check for Mobile/Mouse Start (Button Click)
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    f_pos = getattr(event, "pos", (0, 0))
                    # Pygbag/Mobile normalization
                    if hasattr(event, "x"):
                        f_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)

                    # FIX: Use FIRE_POS here so it matches the drawing!
                    dist = math.hypot(f_pos[0] - FIRE_POS[0], f_pos[1] - FIRE_POS[1])
                    if dist < 80:  # Made the hit-box slightly larger for easier tapping
                        start_trigger = True

                # Common Start Logic
                if "start_trigger" in locals() and start_trigger:
                    pygame.mixer.Channel(2).play(pygame.mixer.Sound("sfx/chime.mp3"))
                    start = time()
                    while time() - start <= GOAL_WAIT_INTERVAL:
                        pass
                    DONE = True
                    del start_trigger  # Clean up for the next run

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
            text3 = font.render("Hit SPACE bar or punch FIRE to start!", True, BLACK)
            rect = pygame.Rect(rect_x, rect_y, 50, 50)
            prompt_rect = text3.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
            screen.blit(text2, rect)
            screen.blit(text3, prompt_rect)

            # --- Wrap-up
            clock.tick(60)

            joystick.draw(screen, font, "MOVE")

            # 2. Start Button
            btn_radius = 70  # Make it a bit bigger
            fire_surf = pygame.Surface((btn_radius * 2, btn_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(fire_surf, (255, 0, 0, 180), (btn_radius, btn_radius), btn_radius)

            txt_surf = font.render("FIRE", True, (255, 255, 255))
            txt_rect = txt_surf.get_rect(center=(btn_radius, btn_radius))
            fire_surf.blit(txt_surf, txt_rect)

            # Center the blit on our FIRE_POS
            screen.blit(fire_surf, (FIRE_POS[0] - btn_radius, FIRE_POS[1] - btn_radius))

            # Roll text!:
            pygame.display.flip()
            await asyncio.sleep(0)

        # --- 4. DRAW PLAYERS & PUCK (SHIFTED VISUALLY ONLY) ---
        # Blue Player
        blue_rect = [player_pos[0] + OFFSET_X, player_pos[1] + OFFSET_Y, player_pos[2], player_pos[3]]
        pygame.draw.ellipse(screen, BLUE, blue_rect)

        # Red Player
        red_rect = [opponent_pos[0] + OFFSET_X, opponent_pos[1] + OFFSET_Y, opponent_pos[2], opponent_pos[3]]
        pygame.draw.ellipse(screen, RED, red_rect)

        # Puck
        pygame.draw.circle(screen, BLACK, (int(puck_pos[0] + OFFSET_X), int(puck_pos[1] + OFFSET_Y)), PUCK_RADIUS)

        # --- DRAW VIRTUAL CONTROLS ---
        # 1. Draw Joystick (The class now handles the circle, knob, and "MOVE" text)
        joystick.draw(screen, font, "MOVE")

        # 2. Draw Fire Button
        btn_radius = 60
        fire_surf = pygame.Surface((btn_radius * 2, btn_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(fire_surf, (255, 0, 0, 150), (btn_radius, btn_radius), btn_radius)

        btn_label = "FIRE"

        # Now render it
        txt_surf = font.render(btn_label, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=(btn_radius, btn_radius))
        fire_surf.blit(txt_surf, txt_rect)

        # Blit centered on the FIRE_POS
        screen.blit(fire_surf, (FIRE_POS[0] - btn_radius, FIRE_POS[1] - btn_radius))

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
