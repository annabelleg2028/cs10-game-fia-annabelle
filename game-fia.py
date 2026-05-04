import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse Follower")

# Load your image — put it in the same folder as this script
sprite_image = pygame.image.load("whale.png").convert_alpha()

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((30, 30, 30))  # Background color

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Center the sprite on the cursor
    rect = sprite_image.get_rect(center=(mouse_x, mouse_y))
    screen.blit(sprite_image, rect)

    pygame.display.flip()
    clock.tick(60)
