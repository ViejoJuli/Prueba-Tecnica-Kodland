import pygame
import os
import random
import csv

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Prueba Tecnica")

# Setting frame rate
clock = pygame.time.Clock()
FPS = 60

# Define game variables
GRAVITY = 0.75
SCROLL_TRESH = 200  # Limit scroll
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level = 1

# Define player action variables (from the beggining)
moving_left = False
moving_right = False
shoot = False

# Load images
# Background images
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()


# Tiles images
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# Other images
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
}

# Define used colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Define font
font = pygame.font.SysFont('Helvetica', 30)

# Function to draw text


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Function to draw the background
def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        # Paint the tiles
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT -
                    mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT -
                    pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT -
                    pine2_img.get_height()))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.jump = False
        self.health = 100
        self.max_health = self.health
        self.shoot_cooldown = 0  # How quickly I could fire
        self.vel_y = 0  # Velocity for jump
        self.in_air = True  # Is always in the air until hits something
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # AI specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Load all types of images
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            # Count images in folder
            num_of_frames = len(os.listdir(
                f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(
                    img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0
        screen_scroll = 0
        # update movement variables
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:  # avoid double jump
            self.vel_y = -14
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # Check collision
        for tile in world.obstacle_list:
            # Check collision in x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if enemy hit the wall turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # Check collision in y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if jumping
                if self.vel_y < 0:  # I'm going up
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        # Check if going of the limits
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Update rectangle
        self.rect.x += dx
        self.rect.y += dy

        # Update scroll
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_TRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                    or (self.rect.left < SCROLL_TRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx  # Reverse the player
                screen_scroll = -dx
        return screen_scroll

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20  # Reload time
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # Reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            # Idle check
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            # Check if AI is in front of the player
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            # Continue patrolling
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    # Update AI vision
                    self.vision.center = (
                        self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        # Scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # update image to current frame
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Reset image index if needed
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:  # Is dead?
                self.frame_index = len(self.animation_list[self.action])-1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # Iterate through the data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:  # Water
                        water = Water(img, x * TILE_SIZE,
                                      y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:  # Decoration
                        decoration = Decoration(img, x * TILE_SIZE,
                                                y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # Create player
                        player = Soldier('player', x * TILE_SIZE,
                                         y * TILE_SIZE, 1.7, 5, 20)
                        health_bar = HealthBar(
                            10, 10, player.health, player.health)
                    elif tile == 16:  # Create enemies
                        enemy = Soldier('enemy', x * TILE_SIZE,
                                        y * TILE_SIZE, 1.7, 2, 20)
                        enemy_group.add(enemy)
                    elif tile == 17 or tile == 18:  # Create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE,
                                           y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Health', x * TILE_SIZE,
                                           y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE,
                                    y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])  # (image, rect)


class Decoration (pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit (pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water (pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox (pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Scroll
        self.rect.x += screen_scroll
        # Pick the box
        if pygame.sprite.collide_rect(self, player):
            # Check the kind of box
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            else:
                player.ammo += 15
            # Delete box
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # Update with new health
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # Move bullet on the screen
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # Check that bullet gone off the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Check collision with obstacles
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # Check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


# Create sprite groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


# Create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# Load lavel data
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

    clock.tick(FPS)
    # Update background
    draw_bg()
    # Draw level map
    world.draw()
    # Show player health
    health_bar.draw(player.health)

    # Show ammo
    draw_text('AMMO: ', font, WHITE, 10, 35)
    for x in range(player.ammo):
        screen.blit(bullet_img, (90 + (x * 10), 40))

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    # Update a draw groups
    bullet_group.update()
    item_box_group.update()
    decoration_group.update()
    water_group.update()
    exit_group.update()

    bullet_group.draw(screen)
    item_box_group.draw(screen)
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)

    # Update player actions (when alive)
    if player.alive:
        # Shoot bullets
        if shoot:
            player.shoot()
        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)

        screen_scroll = player.move(moving_left, moving_right)
        bg_scroll -= screen_scroll

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keybord pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:  # I need to check if is alive
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
        # keyboard released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
