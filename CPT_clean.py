#import statements for modules needed
import pygame
import random
import time
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pygame.init()

# setup the display to fit full screen 
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Continuous Performance Test")

font = pygame.font.Font(None, 90)
instruction_font  = pygame.font.Font(None, 50)
button_font = pygame.font.Font(None, 40)  # Normal font for buttons

# the colours for my test
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (151, 121, 255)
MINT = (193, 255, 204)
PEACH = (193, 158, 148)
ORANGE = (214, 176, 103)
RED = (214, 93, 73)
GRAY = (104, 108, 107)

# set the letters that will be scrolled through
ALL_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                          

# test parameters
INTERVAL = random.uniform(0.5, 1.2)

# set up the csv
LOG_FILE = "test_data_3.csv" #change this line everytime a test is ran so new csv created
with open(LOG_FILE, "w", newline="") as file:
    writer = csv.writer(file) 
    writer.writerow(["Trial", "Letter", "Response", "Reaction Time (s)", "Correct"])


# buttons for the opening screen
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.hover_color if self.rect.collidepoint(mouse_pos) else self.color, self.rect)

        text_surface = button_font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()

#3 second countdown function to be called before test starts
#gives participant time to ease into the CPT
def countdown():
    for i in range(3, 0, -1):
        screen.fill(WHITE)
        count_text = font.render(str(i), True, BLACK)
        screen.blit(count_text, (WIDTH // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(1000)  

#create a test instruction function to tell user what to do
def instructions_and_start(test_type, instruction_message):
    screen.fill(WHITE)
    instruction_text = instruction_font.render(instruction_message, True, BLACK)
    start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 75, "Start", PURPLE, (100, 100, 255),
                          lambda: continuous_performance_test_AX(test_type))
    
    running = True
    while running:
        screen.fill(WHITE)
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 3))
        start_button.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            start_button.check_click(event)

#function to set test duration
def get_test_duration(test_type):
    #practice for 1 minute
    if test_type == 1: 
        return 60  
    #remaining tests which run for 10 minutes
    elif test_type in [2, 3]:
        return 600 
    else:
        return 300  

#create a standard deviation function
#used to calculate the reaction time variability
def compute_moving_std(data, window_size=10):
    return [np.std(data[max(0, i-window_size+1):i+1]) for i in range(len(data))]

#Continuous performance test function
def continuous_performance_test_AX(test_type):
    countdown()
    running = True
    previous_letter = None
    correct_reaction_times = []
    false_alarms = 0
    total_correct = 0
    omission_errors = 0
    commission_errors = 0

    # get the correct test duration
    DURATION = get_test_duration(test_type)

    # set test start time
    start_time = time.time()

    # create a "Back" button in the top-right corner
    back_button = Button(WIDTH - 100, 10, 80, 40, "Back", RED, (200, 50, 50), welcome_screen)

    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= DURATION:
            break  

        # blank screen between trials so you can tell letter has switched
        screen.fill(WHITE)
        pygame.display.flip()
        time.sleep(0.05)

        TARGET_PROBABILITY = 0.35 

        if test_type == 1:
            # Practice Test: target is 'S'
            if random.random() < TARGET_PROBABILITY:
                letter = "S"
            else:
                letter = random.choice([l for l in ALL_LETTERS if l != "S"])

        elif test_type == 2:
            # Test 1: target is 'X'
            if random.random() < TARGET_PROBABILITY:
                letter = "X"
            else:
                letter = random.choice([l for l in ALL_LETTERS if l != "X"])

        elif test_type == 3:
            # Test 2: target is any letter following a 'V'
            if previous_letter == "V" and random.random() < TARGET_PROBABILITY:
                # Pick a target letter (can be anything except V for this logic)
                letter = random.choice([l for l in ALL_LETTERS if l != "V"])
            else:
                letter = random.choice(ALL_LETTERS)


        screen.fill(WHITE)
        text = font.render(letter, True, BLACK)
        screen.blit(text, (WIDTH // 2, HEIGHT // 2))
        back_button.draw(screen)

        pygame.display.flip()

        start_trial_time = time.time()
        response = None
        reaction_time = None
        correct = False

        INTERVAL = random.uniform(0.5, 1.2) 

        while time.time() - start_trial_time < INTERVAL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    response = pygame.key.name(event.key).upper()
                    reaction_time = time.time() - start_trial_time
                    break  
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.check_click(event):
                        return  

        # check test type
        if test_type == 1:
            correct = (letter != "S" and response == "SPACE") or (letter == "S" and response == "S")
        elif test_type == 2:
            correct = (letter != "X" and response == "SPACE") or (letter == "X" and response == "X")
        elif test_type == 3:
             # don't press space if current letter comes immediately after a 'V'
            if previous_letter == "V":
                correct = response == "C"
            else:
                correct = response == "SPACE"

        if response is not None and not correct:
            commission_errors += 1
        elif response is None and not correct:
            omission_errors += 1
        if correct:
            total_correct += 1

        # log results for analysis later
        with open(LOG_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([elapsed_time, letter, response, reaction_time, correct])

        print(f"Time: {elapsed_time:.2f}s - Letter: {letter}, Response: {response}, Reaction Time: {reaction_time}, Correct: {correct}")

        if correct and reaction_time is not None:
            correct_reaction_times.append(reaction_time)

        previous_letter = letter
        time.sleep(INTERVAL)
 
    print("Test complete!")
    plot_reaction_times(list(range(len(correct_reaction_times))), correct_reaction_times)
    plot_variability(list(range(len(correct_reaction_times))), correct_reaction_times)
    plot_false_alarms_and_accuracy(false_alarms, total_correct, total_correct + omission_errors + commission_errors, omission_errors, commission_errors)
    welcome_screen()
    

# Define each test function
def test_1():
    instructions_and_start(1, "Press SPACE for all letters except 'S'. Press 'S' when 'S' is displayed.")
    continuous_performance_test_AX(test_type=1)


def test_2():
    instructions_and_start(2, "Press SPACE for all letters except 'X'. Press 'X' when 'X' is displayed.")
    continuous_performance_test_AX(test_type=2)


def test_3():
    instructions_and_start(3, "Press SPACE except for the letter that follows 'V'. Press 'C' for the letter following 'V'.")
    continuous_performance_test_AX(test_type=3)

#plots
def plot_reaction_times(trials, reaction_times):
    if not trials:
        print("No correct responses to display reaction times.")
        return

    trials_array = np.array(trials)
    reaction_times_array = np.array(reaction_times)

    # linear regression (for comparison)
    slope, intercept = np.polyfit(trials_array, reaction_times_array, 1)
    best_fit_line = slope * trials_array + intercept

    # plotting
    plt.figure(figsize=(16, 10))
    plt.scatter(trials_array, reaction_times_array, label="Reaction Times", alpha=0.5)
    plt.plot(trials_array, best_fit_line, color="red", linestyle="--", label="Best Fit Line")
    plt.xlabel("Trial")
    plt.ylabel("Reaction Time (s)")
    plt.title("Reaction Times Across Trials")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_false_alarms_and_accuracy(false_alarms, total_correct, total_trials, omission_errors, commission_errors):
    accuracy = (total_correct / total_trials) * 100
    omission_error_rate = (omission_errors / total_trials) * 100
    commission_error_rate = (commission_errors / total_trials) * 100
    
    labels = ["Accuracy", "Omission Errors", "Commission Errors"]
    values = [accuracy, omission_error_rate, commission_error_rate]
    colors = ["green", "blue", "red"]
    
    plt.figure(figsize=(6, 6))
    plt.bar(labels, values, color=colors)
    plt.ylabel("Percentage")
    plt.title("Performance Metrics: Accuracy vs Errors", pad=20)
    plt.ylim(0, 100)
    
    for i, v in enumerate(values):
        plt.text(i, v + 2, f"{v:.2f}%", ha='center', fontsize=12)
    
    plt.show()

def plot_variability(trials, reaction_times, window_size=10):
    if not trials:
        print("No correct responses to display variability.")
        return

    moving_std = compute_moving_std(reaction_times, window_size)

    plt.figure(figsize=(14, 6))
    plt.plot(trials, moving_std, label=f"Moving Std Dev (window={window_size})", color="orange")
    plt.xlabel("Trial Number")
    plt.ylabel("Standard Deviation of Reaction Time")
    plt.title("Reaction Time Variability Over Trials")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# welcome screen
def welcome_screen():
    running = True
    title_font = pygame.font.Font(None, 70) 
    
    
    # button dimensions
    button_width, button_height = 200, 75
    button_x = WIDTH // 2 - button_width // 2
    
    # define test buttons
    test_1_button = Button(button_x, HEIGHT // 3, button_width, button_height, "Practice", MINT, (100, 100, 255), test_1)
    test_2_button = Button(button_x, HEIGHT // 2, button_width, button_height, "Test 1", PEACH, (100, 100, 255), test_2)
    test_3_button = Button(button_x, HEIGHT // 1.5, button_width, button_height, "Test 2", ORANGE, (100, 100, 255), test_3)
    
    # small buttons for minimize & exit
    button_small_w, button_small_h = 150, 50 

    
    exit_x, exit_y = WIDTH - button_small_w - 10, 20  # top right corner

   
    exit_button = Button(exit_x, exit_y, button_small_w, button_small_h, "Exit", RED, (200, 50, 50), pygame.quit)

    while running:
        screen.fill(WHITE)

        title_text = title_font.render("Continuous Performance Test", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 220))  # Centered at the top
        screen.blit(title_text, title_rect)

        test_1_button.draw(screen)
        test_2_button.draw(screen)
        test_3_button.draw(screen)
        exit_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            test_1_button.check_click(event)
            test_2_button.check_click(event)
            test_3_button.check_click(event)
            exit_button.check_click(event)

# run the opening screen
welcome_screen()

