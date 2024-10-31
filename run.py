import pygame
from Box2D import (
    b2World, b2PolygonShape, b2CircleShape,
    b2_dynamicBody, b2_staticBody, b2ContactListener, b2RevoluteJointDef
)
import imageio
import numpy as np

from classes import ContactListener, Button, Slider
from world import get_world, to_pygame, draw_world_on_screen

# Initialize Pygame
pygame.init()

# Screen dimensions and conversion factor
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PPM = 20.0  # Pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
DURATION = 15  # Duration of the simulation in seconds

# Pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Domino Simulation with Balance Beam and Cups')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 18)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# Variables to track
first_domino_tipped = False
last_domino_tipped = False
ball_moving_right = False
beam_tip = "neutral"

# Create a video writer using imageio
video_writer = imageio.get_writer('domino_simulation_balance_beam.mp4', fps=TARGET_FPS)


domino_spacing_slider = Slider('domino_spacing', 100, 150, 600, 20)
domino_width_slider = Slider('domino_width', 100, 250, 600, 20)
domino_height_slider = Slider('domino_height', 100, 350, 600, 20)
sliders = [domino_spacing_slider, domino_width_slider, domino_height_slider]
start_button = Button(350, 400, 100, 50, "Start", font, GRAY, (170, 170, 170), BLACK)

# Simulation loop
running = True
game_started = False
frame_count = 0
total_frames = DURATION * TARGET_FPS  # Total number of frames to record

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        for slider in sliders:
            slider.handle_event(event)
        
        # Handle button click to start the game
        slider_values = [max(0.1, slider.get_value()) for slider in sliders]
        
        if start_button.handle_event(event):
            game_started = True  # Set the flag to True to indicate game has started
            
        world, first_domino_body, last_domino_body, bowling_ball_body, beam_body = get_world(*slider_values)

    # Clear screen
    screen.fill(WHITE)
    
    draw_world_on_screen(world, screen)
    
    if not game_started:
        # Draw the slider and display its current value
        for idx, slider in enumerate(sliders):
            slider.draw(screen)
            font = pygame.font.Font(None, 36)
            text = font.render(f"{slider.name}: {slider.get_value():.2f}", True, BLACK)
            screen.blit(text, (100, 100*(idx + 1)))
        
        start_button.draw(screen)
    else:

        # Update variables
        # Check if the first domino has tipped (angle significantly different from initial angle)
        if not first_domino_tipped and abs(first_domino_body.angle) > 0.5:
            first_domino_tipped = True

        # Check if the last domino has tipped
        if not last_domino_tipped and abs(last_domino_body.angle) > 0.5:
            last_domino_tipped = True

        if beam_body.angle > 0.2:
            beam_tip = "positive"
        elif beam_body.angle < -0.2:
            beam_tip = "negative"
        else:
            beam_tip = "neutral"
        
        # Check if the bowling ball is moving to the right
        ball_velocity = bowling_ball_body.linearVelocity.x
        ball_moving_right = ball_velocity > 0.1  # Threshold to avoid floating-point errors

        # Display variables on the screen
        status_texts = [
            f"First Domino Tipped: {'Yes' if first_domino_tipped else 'No'}",
            f"Last Domino Tipped: {'Yes' if last_domino_tipped else 'No'}",
            f"Domino and Ball Contact: {'Yes' if world.contactListener.domino_ball_contact else 'No'}",
            f"Ball Moving Right: {'Yes' if ball_moving_right else 'No'}",
            f"Ball Contact Top Level: {'Yes' if world.contactListener.ball_contact_top else 'No'}",
            f"Ball Contact Beam: {'Yes' if world.contactListener.ball_contact_bottom else 'No'}",
            f"Beam Tip: {beam_tip}"
        ]

        for i, text in enumerate(status_texts):
            rendered_text = font.render(text, True, BLACK)
            screen.blit(rendered_text, (10, 10 + i * 20))
            
        # Update physics
        world.Step(TIME_STEP, 10, 10)
        world.ClearForces()

    # Capture the screen surface as an image
    frame = pygame.surfarray.array3d(screen)
    # Convert from (width, height, channels) to (height, width, channels)
    frame = np.transpose(frame, (1, 0, 2))
    # Write the frame to the video
    video_writer.append_data(frame)

    # Update display
    pygame.display.flip()
    clock.tick(TARGET_FPS)

    frame_count += 1
    if frame_count >= total_frames:
        running = False

# Clean up
video_writer.close()
pygame.quit()
