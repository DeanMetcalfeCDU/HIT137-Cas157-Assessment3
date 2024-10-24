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

# Load the background image
background_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/LEVELS/"
background = pygame.image.load(background_path + "level.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load health bar images
health_bar_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/HEALTH BAR/"
health_full = pygame.image.load(health_bar_path + "health_full.png").convert_alpha()
health_medium = pygame.image.load(health_bar_path + "health_medium.png").convert_alpha()
health_low = pygame.image.load(health_bar_path + "health_low.png").convert_alpha()

# Initialize Pygame's sound system
pygame.mixer.init()

# Load sound effects
cheese_blaster_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/cheese_blaster.mp3"
)
cat_screech_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/cat_screech.mp3"
)
player_damage_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/takedamage_squeak.mp3"
)
milk_collect_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/milk_get.mp3"
)



# Initialize the score
score = 0

# Font for displaying score
font = pygame.font.Font(None, 36)  # Default Pygame font, size 36

def draw_score(surface):
    """Display the score in the top-right corner."""
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # White text
    surface.blit(score_text, (SCREEN_WIDTH - 150, 10))  # Position in the top right


# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

def trigger_game_over():
    """Switch to the Game Over screen."""
    game_over_screen = pygame.image.load(
        "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/SCREENS/GAME OVER.png"
    ).convert()
    screen.blit(game_over_screen, (0, 0))
    pygame.display.flip()
    pygame.time.wait(3000)  # Wait for 3 seconds before closing the game
    pygame.quit()
    sys.exit()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        character_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/CHARACTERS/"

        # Load player animations
        self.idle_frame_right = pygame.image.load(character_path + "ratson_idle_R.png").convert_alpha()
        self.idle_frame_left = pygame.image.load(character_path + "ratson_idle_L.png").convert_alpha()
        self.run_frames_left = [pygame.image.load(character_path + f"ratson_run{i}_L.png").convert_alpha() for i in
                                range(1, 3)]
        self.run_frames_right = [pygame.image.load(character_path + f"ratson_run{i}_R.png").convert_alpha() for i in
                                 range(1, 3)]
        self.jump_frame_left = pygame.image.load(character_path + "ratson_jump_L.png").convert_alpha()
        self.jump_frame_right = pygame.image.load(character_path + "ratson_jump_R.png").convert_alpha()

        # Add shooting sprites (if different than idle or running)
        self.shoot_frame_right = pygame.image.load(character_path + "ratson_gun_R.png").convert_alpha()
        self.shoot_frame_left = pygame.image.load(character_path + "ratson_gun_L.png").convert_alpha()

        # Initialize the starting image and rect
        self.image = self.idle_frame_right
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)

        # Health attributes
        self.health_states = [health_full, health_medium, health_low]
        self.current_health_index = 0

        # Potion pouch (inventory) initialized to 0
        self.potion_pouch = 0

        # Movement and animation attributes
        self.speed_x = 5
        self.speed_y = 0
        self.is_jumping = False
        self.facing_right = True
        self.animation_timer = 0
        self.current_frame = 0

        # Shooting state and timers
        self.shooting = False
        self.shoot_cooldown = 500
        self.last_shot = pygame.time.get_ticks()

        # Damage cooldown
        self.last_damage_time = pygame.time.get_ticks()
        self.damage_cooldown = 1000

    def take_damage(self):
        """Handles health reduction and triggers Game Over if hit below the lowest health state."""
        now = pygame.time.get_ticks()
        if now - self.last_damage_time >= self.damage_cooldown:
            player_damage_sound.play()  # Play player damage sound
            if self.current_health_index < len(self.health_states) - 1:
                self.current_health_index += 1  # Reduce health
            else:
                # If already at the lowest health state and hit again, trigger Game Over
                trigger_game_over()

            self.last_damage_time = now  # Reset the damage cooldown
            self.set_idle_sprite()

    def set_idle_sprite(self):
        if self.facing_right:
            if self.image != self.idle_frame_right:  # Reset frame only if necessary
                self.image = self.idle_frame_right
                self.current_frame = 0
        else:
            if self.image != self.idle_frame_left:
                self.image = self.idle_frame_left
                self.current_frame = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_cooldown:
            self.last_shot = now
            projectile_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/PROJECTILES/"
            direction = 1 if self.facing_right else -1
            projectile = Projectile(self.rect.right, self.rect.centery, direction,
                                    projectile_path + f"cheese_{'R' if direction == 1 else 'L'}.png")
            all_sprites.add(projectile)

            # Play the cheese blaster sound
            cheese_blaster_sound.play()

            # Change the sprite to the shooting sprite
            if self.facing_right:
                self.image = self.shoot_frame_right
            else:
                self.image = self.shoot_frame_left

            self.shooting = True  # Set shooting state

    def reset_after_shooting(self):
        """Reset sprite after shooting back to idle or running."""
        if not self.shooting:
            return
        now = pygame.time.get_ticks()
        if now - self.last_shot >= 200:  # A short delay for shooting animation
            self.shooting = False  # Shooting is done
            # Reset sprite to idle
            self.set_idle_sprite()

    def draw_health_bar(self, surface):
        health_image = self.health_states[self.current_health_index]
        surface.blit(health_image, (10, 10))

        # Display potion pouch count above the health bar
        potion_text = font.render(f"Potions: {self.potion_pouch}", True, (255, 255, 255))  # White text
        surface.blit(potion_text, (10, 50))  # Position it above the health bar

    def use_potion(self):
        """Restore health to full if a potion is available."""
        if self.potion_pouch > 0:  # Check if there is milk in the pouch
            self.current_health_index = 0  # Reset health to full
            self.potion_pouch -= 1  # Remove one potion

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed_x
            self.facing_right = False
            if not self.is_jumping and not self.shooting:
                self.animate(self.run_frames_left)
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed_x
            self.facing_right = True
            if not self.is_jumping and not self.shooting:
                self.animate(self.run_frames_right)
        else:
            if not self.is_jumping and not self.shooting:
                self.set_idle_sprite()

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.is_jumping = True
            self.image = self.jump_frame_right if self.facing_right else self.jump_frame_left
            self.speed_y = -15

        if keys[pygame.K_z] and not self.shooting:
            self.shoot()

        if keys[pygame.K_LSHIFT] and self.potion_pouch > 0:  # Use milk with shift key
            self.use_potion()

    def apply_gravity(self):
        self.rect.y += self.speed_y
        self.speed_y += GRAVITY
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.is_jumping = False

    def animate(self, frames):
        self.animation_timer = (self.animation_timer + 1) % 10
        if self.animation_timer == 0:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.reset_after_shooting()  # Check if we need to reset the sprite after shooting


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.direction = direction

        # Explosion frames
        self.explosion_frames = [
            pygame.image.load(
                "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/PROJECTILES/cheeseboom1.png").convert_alpha(),
            pygame.image.load(
                "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/PROJECTILES/cheeseboom2.png").convert_alpha()
        ]
        self.explosion_index = 0
        self.exploding = False
        self.explosion_start_time = 0

    def update(self):
        """Update the projectile movement or handle explosion."""
        if not self.exploding:
            self.rect.x += self.speed * self.direction

            # Remove projectile if off-screen
            if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
                self.kill()

            # Check for collisions with enemies
            hit_enemies = pygame.sprite.spritecollide(self, enemies, False)
            for enemy in hit_enemies:
                enemy.take_damage()  # Damage the enemy
                self.start_explosion()  # Trigger explosion animation
        else:
            self.handle_explosion()

    def start_explosion(self):
        """Start the explosion animation."""
        self.exploding = True
        self.explosion_start_time = pygame.time.get_ticks()
        self.image = self.explosion_frames[self.explosion_index]  # Start with the first frame

    def handle_explosion(self):
        """Switch between explosion frames and remove projectile after animation."""
        now = pygame.time.get_ticks()
        if now - self.explosion_start_time > 100:  # 100ms between frames
            self.explosion_index += 1
            if self.explosion_index < len(self.explosion_frames):
                self.image = self.explosion_frames[self.explosion_index]
                self.explosion_start_time = now  # Reset the timer for the next frame
            else:
                self.kill()  # Remove the projectile after the animation completes

class Milk(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/COLLECTIBLES/milk.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        if self.rect.colliderect(player.rect):  # Check collision with the player
            milk_collect_sound.play()  # Play milk collection sound
            player.potion_pouch += 1  # Add milk to the potion pouch
            self.kill()  # Remove the milk from the screen


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, left_limit, right_limit):
        super().__init__()
        enemy_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/"
        self.hits = 0
        self.walk_frames_left = [pygame.image.load(enemy_path + f"badcat_walk{i}_L.png").convert_alpha() for i in
                                 range(1, 3)]
        self.walk_frames_right = [pygame.image.load(enemy_path + f"badcat_walk{i}_R.png").convert_alpha() for i in
                                  range(1, 3)]

        self.image = self.walk_frames_left[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect = self.rect.inflate(-30, -10)
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.speed = 2
        self.direction = 1
        self.animation_timer = 0
        self.current_frame = 0

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
        self.animation_timer = (self.animation_timer + 1) % 10
        if self.animation_timer == 0:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]

    def update(self):
        self.patrol()
        if self.rect.colliderect(player.rect):
            player.take_damage()

    def take_damage(self):
        """Handles enemy damage and removal if hit 3 times."""
        self.hits += 1
        cat_screech_sound.play()  # Play cat screech sound when damaged
        if self.hits >= 3:  # If hit 3 times, remove the enemy and increase score
            global score
            score += 1  # Increase score
            self.kill()  # Remove enemy from the screen


player = Player()
enemy1 = Enemy(200, 450, 150, 400)
enemy2 = Enemy(400, 450, 350, 600)
milk = Milk(650, 500)

enemies.add(enemy1, enemy2)
all_sprites.add(player, enemy1, enemy2, milk)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    player.draw_health_bar(screen)
    draw_score(screen)  # Draw the score in the top right
    pygame.display.flip()

pygame.quit()
sys.exit()
