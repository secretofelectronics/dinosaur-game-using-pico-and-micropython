from machine import I2C, Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import time
import urandom

# I2C parameters
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# Initialize the I2C bus
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Define custom dinosaur character (5x8 pixels)
dino_char = [
    0b00100,
    0b01110,
    0b11111,
    0b10100,
    0b10111,
    0b01100,
    0b00100,
    0b00000
]

# Load custom character into LCD
lcd.custom_char(0, bytearray(dino_char))

# Pin definitions
button_pin = Pin(2, Pin.IN, Pin.PULL_UP)

# Game variables
is_jumping = False
jump_timer = 0
jump_duration = 400  # Jump duration in milliseconds
obstacle_x1 = 15  # Initial obstacle positions
obstacle_x2 = 20
speed = 200  # Initial speed (lower is faster)
score = 0
game_over = False
last_update = time.ticks_ms()
last_speed_increase = time.ticks_ms()
speed_increase_interval = 5000  # Interval to increase speed (in milliseconds)
min_speed = 50  # Minimum speed
dino_y = 1  # Dino Y position on LCD (second row)

def update_game():
    global obstacle_x1, obstacle_x2, score, game_over, is_jumping, jump_timer
    
    # Clear previous obstacles
    lcd.move_to(obstacle_x1, dino_y)
    lcd.putstr(" ")
    lcd.move_to(obstacle_x2, dino_y)
    lcd.putstr(" ")
    
    # Move the obstacles
    obstacle_x1 -= 1
    obstacle_x2 -= 1
    if obstacle_x1 < 0:
        obstacle_x1 = 15
        if urandom.getrandbits(2) == 0:
            obstacle_x1 += urandom.randint(5, 10)  # Add some randomness to the obstacle position
        score += 1  # Increase the score when a new obstacle appears
    if obstacle_x2 < 0:
        obstacle_x2 = 15
        if urandom.getrandbits(2) == 0:
            obstacle_x2 += urandom.randint(5, 10)  # Add some randomness to the obstacle position
        score += 1  # Increase the score when a new obstacle appears

    # Draw the obstacles
    lcd.move_to(obstacle_x1, dino_y)
    lcd.putstr("#")
    lcd.move_to(obstacle_x2, dino_y)
    lcd.putstr("#")

    # Draw the dinosaur
    if is_jumping:
        lcd.move_to(0, dino_y)
        lcd.putstr(" ")
        lcd.move_to(0, dino_y - 1)
        lcd.putchar(chr(0))  # Custom dinosaur character
        
        # Check if the jump duration has passed
        if time.ticks_diff(time.ticks_ms(), jump_timer) >= jump_duration:
            is_jumping = False  # End the jump
    else:
        lcd.move_to(0, dino_y - 1)
        lcd.putstr(" ")
        lcd.move_to(0, dino_y)
        lcd.putchar(chr(0))  # Custom dinosaur character

    # Display the score
    lcd.move_to(6, 0)
    lcd.putstr("Score:")
    lcd.putstr(str(score))

    # Check for collision
    if (obstacle_x1 == 0 or obstacle_x2 == 0) and not is_jumping:
        game_over = True
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Game Over!         ")
        lcd.move_to(0, 1)
        lcd.putstr("Press button")

def restart_game():
    global game_over, score, speed, obstacle_x1, obstacle_x2, last_update, last_speed_increase
    # Reset game variables
    game_over = False
    score = 0
    speed = 200
    obstacle_x1 = 15
    obstacle_x2 = 20
    last_update = time.ticks_ms()
    last_speed_increase = time.ticks_ms()
    lcd.clear()

# Welcome message
lcd.move_to(0, 0)
lcd.putstr("Dino Run Game")
time.sleep(2)
lcd.clear()

while True:
    button_state = not button_pin.value()
    
    # Restart the game if it's over and the button is pressed
    if game_over and button_state:
        restart_game()
    
    # Check if the button is pressed to initiate a jump
    if button_state and not is_jumping:
        is_jumping = True
        jump_timer = time.ticks_ms()  # Start the jump timer

    # Update the game state at regular intervals
    if not game_over and time.ticks_diff(time.ticks_ms(), last_update) > speed:
        last_update = time.ticks_ms()
        update_game()

    # Increase the speed at regular intervals
    if not game_over and time.ticks_diff(time.ticks_ms(), last_speed_increase) > speed_increase_interval:
        last_speed_increase = time.ticks_ms()
        if speed > min_speed:
            speed -= 10  # Increase the speed

