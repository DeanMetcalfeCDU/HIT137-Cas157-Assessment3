import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 1

# Create the screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("A Cheesy Defense")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)

# Load the background image
background_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/LEVELS/"
background = pygame.image.load(background_path + "level.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Sprite Groups
all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # File paths
        character_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/CHARACTERS/"

        # Load player animations
        self.idle_frame_right = pygame.image.load(character_path + "ratson_idle_R.png").convert_alpha()
        self.idle_frame_left = pygame.image.load(character_path + "ratson_idle_L.png").convert_alpha()
        self.run_frames_left = [
            pygame.image.load(character_path + "ratson_run1_L.png").convert_alpha(),
            pygame.image.load(character_path + "ratson_run2_L.png").convert_alpha()
        ]
        self.run_frames_right = [
            pygame.image.load(character_path + "ratson_run1_R.png").convert_alpha(),
            pygame.image.load(character_path + "ratson_run2_R.png").convert_alpha()
        ]
        self.jump_frame = pygame.image.load(character_path + "ratson_jump.png").convert_alpha()
        self.shoot_frame_right = pygame.image.load(character_path + "ratson_gun_R.png").convert_alpha()
        self.shoot_frame_left = pygame.image.load(character_path + "ratson_gun_L.png").convert_alpha()

        # Initialize the starting image and rect
        self.image = self.idle_frame_right
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)

        # Movement attributes
        self.speed_x = 5
        self.speed_y = 0
        self.is_jumping = False
        self.facing_right = True  # Track direction
        self.current_frame = 0
        self.animation_timer = 0

        # Shooting state and timers
        self.shooting = False
        self.shoot_cooldown = 500  # 500ms cooldown between shots
        self.last_shot = pygame.time.get_ticks()
        self.shooting_duration = 300  # Keep the gun sprite for 300ms
        self.shooting_start = 0  # Track when shooting started

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Movement left and right with animation
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed_x
            self.facing_right = False
            if not self.is_jumping:  # Only animate if not jumping
                self.animate(self.run_frames_left)
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed_x
            self.facing_right = True
            if not self.is_jumping:  # Only animate if not jumping
                self.animate(self.run_frames_right)
        else:
            if not self.shooting and not self.is_jumping:  # Only switch to idle if not shooting or jumping
                self.set_idle_sprite()

        # Jumping logic with persistent jump sprite
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.is_jumping = True
            self.image = self.jump_frame  # Switch to jump sprite
            self.speed_y = -15  # Jump power

        # Shooting logic
        if keys[pygame.K_z] and not self.shooting:
            self.shoot()

    def set_idle_sprite(self):
        """Set the correct idle sprite based on the facing direction."""
        if self.facing_right:
            self.image = self.idle_frame_right
        else:
            self.image = self.idle_frame_left

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_cooldown:  # Ensure cooldown has passed
            self.last_shot = now  # Reset the shot timer
            self.shooting = True  # Set shooting state to true
            self.shooting_start = now  # Record when shooting started

            # Use the correct gun sprite based on direction
            if self.facing_right:
                self.image = self.shoot_frame_right
            else:
                self.image = self.shoot_frame_left

            # Create the projectile based on the facing direction
            projectile_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/PROJECTILES/"
            if self.facing_right:
                projectile = Projectile(self.rect.right, self.rect.centery, 1, projectile_path + "cheese.png")
            else:
                projectile = Projectile(self.rect.left, self.rect.centery, -1, projectile_path + "cheese.png")

            projectiles.add(projectile)
            all_sprites.add(projectile)

    def update_shooting_state(self):
        """Keep the gun sprite for a short duration before switching back to idle."""
        if self.shooting:
            now = pygame.time.get_ticks()
            if now - self.shooting_start >= self.shooting_duration:
                self.shooting = False  # End shooting state
                self.set_idle_sprite()  # Switch back to the correct idle sprite

    def apply_gravity(self):
        self.rect.y += self.speed_y
        self.speed_y += GRAVITY

        if self.rect.y >= SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.is_jumping = False
            self.speed_y = 0

    def animate(self, frames):
        self.animation_timer += 1
        if self.animation_timer >= 10:  # Switch frame every 10 ticks
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]
            self.animation_timer = 0

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.update_shooting_state()  # Update shooting state


### PROJECTILE CLASS ###
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5  # Adjust projectile speed
        self.direction = direction

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

### ENEMY CLASS ###
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, left_limit, right_limit):
        super().__init__()

        # File path
        enemy_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/"

        # Load animations
        self.idle_frames_left = [pygame.image.load(enemy_path + "badcat_idle_L.png").convert_alpha()]
        self.idle_frames_right = [pygame.image.load(enemy_path + "badcat_idle_R.png").convert_alpha()]
        self.walk_frames_left = [
            pygame.image.load(enemy_path + "badcat_walk1_L.png").convert_alpha(),
            pygame.image.load(enemy_path + "badcat_walk2_L.png").convert_alpha()
        ]
        self.walk_frames_right = [
            pygame.image.load(enemy_path + "badcat_walk1_R.png").convert_alpha(),
            pygame.image.load(enemy_path + "badcat_walk2_R.png").convert_alpha()
        ]

        self.image = self.idle_frames_left[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.left_limit = left_limit
        self.right_limit = right_limit
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left
        self.walking = True
        self.current_frame = 0
        self.animation_timer = 0

    def update(self):
        if self.walking:
            self.patrol()

    def patrol(self):
        if self.direction == 1:
            self.rect.x += self.speed
            if self.rect.right >= self.right_limit:
                self.direction = -1
            self.animate(self.walk_frames_right)
        else:
            self.rect.x -= self.speed
            if self.rect.left <= self.left_limit:
                self.direction = 1
            self.animate(self.walk_frames_left)

    def animate(self, frames):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]
            self.animation_timer = 0

# Create player and enemies
player = Player()
enemy1 = Enemy(200, 450, 150, 400)
enemy2 = Enemy(400, 450, 350, 600)

# Add to sprite groups
all_sprites.add(player, enemy1, enemy2)
enemies.add(enemy1, enemy2)

### MAIN GAME LOOP ###
running = True
while running:
    clock.tick(FPS)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update all sprites
    all_sprites.update()

    # Draw everything
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
