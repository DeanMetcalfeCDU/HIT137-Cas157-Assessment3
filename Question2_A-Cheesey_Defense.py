# https://github.com/DeanMetcalfeCDU/HIT137-Cas157-Assessment3

'''
A Cheesey Defense
Cats are invading the Cheese Factory to get their paws on the Milk
Our hero Ratson and his cheese blaster must save the factory and of course the cheese

Instructions:
Move to the right to continue to the next Level
Shoot enemies in your way
Collect milk potions to restore your health
Defeat the boss cat invading the Cheese factory

Controls:
Use arrow keys to move
Press 'space' to jump
Press 'z' to shoot
Press 'shift' to use potion
'''

import pygame
import sys

# Initialise Pygame
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

# Load health bar images
health_bar_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/HEALTH BAR/"
health_full = pygame.image.load(health_bar_path + "health_full.png").convert_alpha()
health_medium = pygame.image.load(health_bar_path + "health_medium.png").convert_alpha()
health_low = pygame.image.load(health_bar_path + "health_low.png").convert_alpha()

# Initialise Pygame's sound system
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
game_over_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/gameover.mp3"
)
milk_use_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/milk_use.mp3"
)
boss_damage_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/boss_damage.mp3"
)
victory_sound = pygame.mixer.Sound(
    "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/victory.mp3"
)
boss_theme = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SOUNDS/boss_theme.mp3"



# Initialise the score
score = 0

# Font for displaying score
font = pygame.font.Font("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/FONTS/Spongeboy_Me_Bob.ttf", 30)  # Default Pygame font, size 36


def draw_score(surface):
    """Display the score in the top-right corner."""
    font_colour = (245,157,38)
    outline_colour = (0,0,0)

    outline_text = font.render(f"Score: {score}", True, outline_colour)
    outline_rect = outline_text.get_rect()
    outline_rect.topleft = (SCREEN_WIDTH - 150, 50)
    offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for offset in offsets:
        surface.blit(outline_text, outline_rect.move(*offset))

    score_text = font.render(f"Score: {score}", True, font_colour)  # White text
    surface.blit(score_text, (SCREEN_WIDTH - 150, 50))  # Position in the top right


# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

def trigger_game_over():
    """Display the Game Over screen and wait for player input to restart or quit."""
    pygame.mixer.music.stop()
    game_over_sound.play()
    game_over_screen = pygame.image.load(
        "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/SCREENS/GAME OVER.png"
    ).convert()
    screen.blit(game_over_screen, (0, 0))
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    reset_game()  # Function to reset game state
                    waiting_for_input = False  # Exit the loop
                elif event.key == pygame.K_ESCAPE:  # Quit the game
                    pygame.quit()
                    sys.exit()

def trigger_victory():
    """Display the Victory screen and wait for player input to restart or quit."""
    victory_image = pygame.image.load(
        "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/SCREENS/VICTORY.png"
    ).convert()
    screen.blit(victory_image, (0, 0))
    pygame.display.flip()

    # Optional: Play victory sound
    victory_sound.play()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    reset_game()
                    waiting_for_input = False
                elif event.key == pygame.K_ESCAPE:  # Quit the game
                    pygame.quit()
                    sys.exit()


def reset_game():
    """Reset the game state and load the first level."""
    global current_level, score

    # Reset game variables
    current_level = 1  # Start from level 1
    score = 0  # Reset score
    player.potion_pouch = 0  # Reset potion pouch
    player.current_health_index = 0  # Restore health

    # Stop any playing music
    pygame.mixer.music.stop()

    # Clear all sprites and reload the correct ones for level 1
    enemies.empty()  # Remove all enemies from previous levels
    all_sprites.empty()  # Clear all sprites

    # Add the player back to the all_sprites group
    all_sprites.add(player)

    # Reset player position and load the first level
    player.rect.center = (100, SCREEN_HEIGHT - 100)
    load_level(current_level)  # Reload level 1



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

        # Initialise the starting image and rect
        self.image = self.idle_frame_right
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)

        # Health attributes
        self.health_states = [health_full, health_medium, health_low]
        self.current_health_index = 0

        # Potion pouch (inventory) initialised to 0
        self.potion_pouch = 0
        # Add a cooldown timer for potion use
        self.potion_cooldown = 1000  # 1 second cooldown
        self.last_potion_use = 0  # Track the last time a potion was use

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
        font_colour = (245, 157, 38)
        outline_colour = (0, 0, 0)
        outline_text = font.render(f"Potions: {self.potion_pouch}", True, outline_colour)
        outline_rect = outline_text.get_rect()
        outline_rect.topleft = (10, 50)
        offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        for offset in offsets:
            surface.blit(outline_text, outline_rect.move(*offset))

        potion_text = font.render(f"Potions: {self.potion_pouch}", True, font_colour)  # White text
        surface.blit(potion_text, (10, 50))  # Position it above the health bar

    def use_potion(self):
        """Restore health to full if a potion is available."""
        if self.potion_pouch > 0:  # Check if there is milk in the pouch
            milk_use_sound.play()
            self.current_health_index = 0  # Reset health to full
            self.potion_pouch -= 1  # Remove one potion

    def handle_input(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
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

        if keys[pygame.K_LSHIFT] and self.potion_pouch > 0:
            if now - self.last_potion_use >= self.potion_cooldown:
                self.use_potion()  # Call use_potion if cooldown allows
                self.last_potion_use = now  # Update the last use time

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
    def __init__(self, x, y, left_limit, right_limit, enemy_type="walker"):
        super().__init__()
        self.enemy_type = enemy_type
        self.direction = 1  # Patrol direction

        if enemy_type == "crawler":
            # Load crawler sprites
            self.climb_up_frames = [
                pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/crawler_climb_down1_L.png").convert_alpha(),
                pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/crawler_climb_down2_L.png").convert_alpha()
            ]
            self.climb_down_frames = [
                pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/crawler_climb1_L.png").convert_alpha(),
                pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/crawler_climb2_L.png").convert_alpha()
            ]
            self.image = self.climb_up_frames[0]  # Start with the first frame
        else:
            # Load walker sprites (default enemy)
            enemy_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/"
            self.walk_frames_left = [pygame.image.load(enemy_path + f"badcat_walk{i}_L.png").convert_alpha() for i in range(1, 3)]
            self.walk_frames_right = [pygame.image.load(enemy_path + f"badcat_walk{i}_R.png").convert_alpha() for i in range(1, 3)]
            self.image = self.walk_frames_left[0]

        self.rect = self.image.get_rect(topleft=(x, y))
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.speed = 2
        self.animation_timer = 0
        self.current_frame = 0
        self.hits = 0  # Track enemy health

    def patrol(self):
        if self.enemy_type == "crawler":
            # Patrol vertically
            self.rect.y += self.speed * self.direction
            if self.rect.top <= self.left_limit or self.rect.bottom >= self.right_limit:
                self.direction *= -1  # Change direction

            # Animate based on direction
            if self.direction == 1:
                self.animate(self.climb_up_frames)
            else:
                self.animate(self.climb_down_frames)
        else:
            # Default horizontal patrol
            self.rect.x += self.speed * self.direction
            if self.rect.right >= self.right_limit or self.rect.left <= self.left_limit:
                self.direction *= -1  # Change direction

            # Animate based on direction
            if self.direction == 1:
                self.animate(self.walk_frames_right)
            else:
                self.animate(self.walk_frames_left)

    def animate(self, frames):
        """Switch between animation frames."""
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
        cat_screech_sound.play()  # Play sound
        if self.hits >= 3:  # Remove enemy if hit 3 times
            global score
            score += 1
            self.kill()


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


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        boss_path = "C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/ENEMIES/"

        # Load the boss sprites
        self.sprites = {
            "down_right": pygame.image.load(boss_path + "catboss_ball_downards_R.png").convert_alpha(),
            "down_left": pygame.image.load(boss_path + "catboss_ball_downwards_L.png").convert_alpha(),
            "left": pygame.image.load(boss_path + "catboss_ball_L.png").convert_alpha(),
            "right": pygame.image.load(boss_path + "catboss_ball_R.png").convert_alpha(),
            "up_left": pygame.image.load(boss_path + "catboss_ball_upwards_L.png").convert_alpha(),
            "up_right": pygame.image.load(boss_path + "catboss_ball_upwards_R.png").convert_alpha(),
        }

        self.image = self.sprites["down_right"]  # Default sprite
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Set speed and direction
        self.speed_x = 4
        self.speed_y = 4
        self.hits = 0  # Boss health (6 hits)

        # Collision cooldown to avoid repeated hits
        self.last_damage_time = pygame.time.get_ticks()
        self.damage_cooldown = 1000  # 1 second cooldown

    def update(self):
        """Update the boss's movement and handle collisions."""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off the edges of the screen
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed_x *= -1  # Reverse horizontal direction

        if self.rect.bottom >= SCREEN_HEIGHT or self.rect.top <= 0:
            self.speed_y *= -1  # Reverse vertical direction

        # Change the sprite based on movement direction
        self.update_sprite()

        # Check for collisions with the player
        now = pygame.time.get_ticks()
        if self.rect.colliderect(player.rect) and now - self.last_damage_time >= self.damage_cooldown:
            player.take_damage()  # Damage the player
            self.last_damage_time = now  # Reset the cooldown

    def update_sprite(self):
        """Update the boss's sprite based on its direction."""
        if self.speed_x > 0 and self.speed_y > 0:
            self.image = self.sprites["down_right"]
        elif self.speed_x < 0 and self.speed_y > 0:
            self.image = self.sprites["down_left"]
        elif self.speed_x > 0 and self.speed_y < 0:
            self.image = self.sprites["up_right"]
        elif self.speed_x < 0 and self.speed_y < 0:
            self.image = self.sprites["up_left"]

    def take_damage(self):
        """Handle boss damage and check for defeat."""
        self.hits += 1
        boss_damage_sound.play()  # Play hit sound

        if self.hits >= 6:  # Boss defeated
            self.kill()  # Remove boss from the game
            pygame.mixer.music.stop()  # Stop the boss music
            trigger_victory()  # trigger victory screen



def load_level(level):
    global background

    if level == 1:
        background = pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/LEVELS/level.png").convert()
        enemy1 = Enemy(200, 450, 150, 400)
        enemy2 = Enemy(400, 450, 350, 600)
        milk = Milk(650, 550)
        enemies.add(enemy1, enemy2)
        all_sprites.add(enemy1, enemy2, milk)

    elif level == 2:
        background = pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/LEVELS/level2.png").convert()
        crawler1 = Enemy(200, 50, 0, SCREEN_HEIGHT, enemy_type="crawler")
        crawler2 = Enemy(550, 50, 0, SCREEN_HEIGHT, enemy_type="crawler")
        milk = Milk(570, 530)
        enemies.add(crawler1, crawler2)
        all_sprites.add(crawler1, crawler2, milk)

    elif level == 3:
        background = pygame.image.load("C:/Users/deanm/OneDrive/CDU/Sem2-24/HIT137/Assessments/Assessment 3/SPRITES/LEVELS/level3.png").convert()
        boss = Boss()  # Add the boss to level 3
        enemies.add(boss)
        all_sprites.add(boss)

        # Play boss theme when entering Level 3
        pygame.mixer.music.stop()  # Stop any currently playing music
        pygame.mixer.music.load(boss_theme)  # Load the boss theme
        pygame.mixer.music.play(-1)  # Loop the music indefinitely

    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))


def check_level_transition(player):
    """Check if the player reaches the right edge to transition to the next level."""
    global current_level

    if player.rect.right >= SCREEN_WIDTH:  # Player reaches the right edge
        if current_level < 3:  # Adjust to allow transition up to level 3
            current_level += 1
            load_level(current_level)  # Load the next level
            player.rect.left = 0  # Reset the player's position to the left side

current_level = 1  # Start at level 1
load_level(current_level)  # Load the first level

player = Player()
enemy1 = Enemy(200, 450, 150, 400)


all_sprites.add(player)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    # Check for level transition
    check_level_transition(player)
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    player.draw_health_bar(screen)
    draw_score(screen)  # Draw the score in the top right
    pygame.display.flip()

pygame.quit()
sys.exit()
