import time
from PIL import Image
import math
import pygame

import tkinter as tk
from tkinter import ttk, filedialog


class ObjectLocator:
    def __init__(self, color_key, meaning_key, board=None, scale_down=3):
        self.board = board
        self.color_key = color_key
        self.meaning_key = meaning_key
        self.scale_down = scale_down
        self.current_objects_coordinates = []
        self.current_number = 0
        self.width, self.height = (len(self.board), len(self.board[0])) if board else 0, 0
        # for tank distance it's from red tank / left tank (x distance from centers), (y (+/- up/down) from blue tank)
        # otherwise it is usually this "red_tank": {"center":["x","y"], "top_left":["x","y"], "bottom_right":["x","y"]}
        self.object_data = {}

    # GENERAL FUNCTIONS
    def print_data(self):
        print(self.object_data)
        for number, data in self.object_data.items():
            print(f"Data Object {number}: {data}")

    def retrieve_object_data(self):
        return self.object_data

    # clears all data
    def clear_object_locator(self):
        self.board = []
        self.current_objects_coordinates = []
        self.current_number = []
        self.object_data = {}

    # allows you to set or get the board
    def use_board(self, board=None):
        if board:
            self.board = board
            self.width, self.height = (len(self.board), len(self.board[0]))
        else:
            return self.board if self.board else False

    # uses functions to add the objects locations to the object_data, gets the numbers from the meaning key
    def compute_objects_locations(self):
        self.get_tank_values((self.meaning_key["red_tank"], self.meaning_key["blue_tank"]))
        self.get_wind_speed(self.meaning_key["wind_bar"])
        self.get_tower_top(self.meaning_key["castle"])

    # IMAGE SCRAPING FUNCTIONS------------------------------------
    # finds the center by using the average of all the current_objects_coordinates/cords and then gets the "topleft" and
    # "bottomright" by retrieving the minimum cords and the maximum cords
    def find_object_coordinates(self):
        if not self.current_objects_coordinates:
            return {"center": (0, 0), "top_left": (0, 0), "bottom_right": (0, 0)}

        all_x_values = [cords[0] for cords in self.current_objects_coordinates]
        all_y_values = [cords[1] for cords in self.current_objects_coordinates]

        # Top left is the point with the smallest x and y value
        top_left = [min(all_x_values), min(all_y_values)]

        # Bottom right is the point with the largest x and y value
        bottom_right = [max(all_x_values), max(all_y_values)]

        # Center is the average of the x values and the average of the y values
        center_x = sum(point[0] for point in self.current_objects_coordinates) / len(self.current_objects_coordinates)
        center_y = sum(point[1] for point in self.current_objects_coordinates) / len(self.current_objects_coordinates)
        center = (round(center_x), round(center_y))

        return {"center": center, "top_left": top_left, "bottom_right": bottom_right}

    # Searches the whole grid for the number and then returns all the concordats that they were located at
    def get_data_points(self, clear_points=True):
        self.current_objects_coordinates = [] if clear_points else self.current_objects_coordinates

        y_start, y_end, x_start, x_end = 0, self.height, 0, self.width

        for x in range(x_start, x_end):
            # This "if" is for improved performance
            if self.current_number in self.board[x]:
                for y in range(y_start, y_end):
                    coordinate = x, y
                    if self.board[x][y] == self.current_number:
                        self.current_objects_coordinates.append(coordinate)

        # self.object_data[self.current_number] = self.current_objects_coordinates
        return self.current_objects_coordinates

    def up_scale_cords(self):
        for object, data in self.object_data[self.current_number].items():
            self.object_data[self.current_number][object] = data[0] * self.scale_down, data[1] * self.scale_down

    def get_tank_values(self, numbers):
        for self.current_number in numbers:
            self.get_data_points()
            self.object_data[self.current_number] = self.find_object_coordinates()
            # self.up_scale_cords()

        def calculate_distance(coord1, coord2):
            # Calculate the distance between two points in 2D space.
            return ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5

        y1, x1 = self.object_data[numbers[0]]["center"]
        y2, x2 = self.object_data[numbers[1]]["center"]
        self.object_data["tank_distance"] = [y1 - y2, x2 - x1, calculate_distance((x1, y1), (x2, y2))]

    def wind_speed_coordinates(self):

        # calculates the longest length of 0's in a list or sequence to find the length of the arrows
        def length_of_zeros(sequence):
            if not sequence:
                return 0, 0
            try:
                # Split the sequence by current_number to find all sequences of '0's
                zero_sequences = sequence.split(f'{self.current_number}')
                # Remove empty strings from the list
                zero_sequences = [seq for seq in zero_sequences if seq]
                # Find the longest sequence of '0's
                longest_zero_sequence = max(zero_sequences, key=len)
                return len(longest_zero_sequence)
            except Exception as ex:
                return 0, 0

        # finds the lengths of the sides or everything but the wind arrows to see which side is longer... the side that
        # is longer is the side wth out the arrows so the wind is ongoing he opposite direction of that side
        def count_side_numbers(sequence):
            # Find the first and last index of the longest sequence of zeros
            zero_sequences = sequence.split(str(self.current_number))
            longest_zero_sequence = max(zero_sequences, key=len)
            first_zero_index = sequence.find(longest_zero_sequence)
            last_zero_index = first_zero_index + len(longest_zero_sequence) - 1

            # Count occurrences of 'number' on the left and right side of the sequence of zeros
            left_count = sequence[:first_zero_index].count(str(self.current_number))
            right_count = sequence[last_zero_index + 1:].count(str(self.current_number))

            # Compare and return based on which side has more occurrences
            if left_count > right_count:
                return 1, left_count
            elif right_count > left_count:
                return -1, right_count

            return 0, 0

        y1, x1 = self.object_data[self.current_number]["top_left"]
        y2, x2 = self.object_data[self.current_number]["bottom_right"]
        middle, middle_x = self.object_data[self.current_number]["center"]
        total_length = x2 - x1

        # Get the sequence in the middle row from x1 to x2
        middle_sequence = ''.join(str(self.board[middle][x]) for x in range(x1, x2))
        # Use the function to get the length of zeros
        length_of_zeros_in_middle = length_of_zeros(middle_sequence)
        # used to get the direction of the wind -1-left or 1-right
        sign, count = count_side_numbers(middle_sequence)

        # gets the ratio of 0's/wind arrows to the length of one side of the bar and puts that ration on a scale from
        # 1-10 and then multiplies that by -1 or 1 for direction
        self.object_data["wind_speed"] = round((length_of_zeros_in_middle / (total_length / 2) * 10)-.6, 1) * sign

    # combines all funcs to add wind speed to object_data as a int
    def get_wind_speed(self, number):
        self.current_number = number
        self.get_data_points()
        self.object_data[self.current_number] = self.find_object_coordinates()
        self.wind_speed_coordinates()

    def get_tower_top(self, number, clear_points=True):
        self.current_number = number
        self.current_objects_coordinates = [] if clear_points else self.current_objects_coordinates

        y_start, y_end, x_start, x_end = 0, self.height, 0, self.width

        for x in range(x_start, x_end):
            # This "if" is for improved performance
            if self.current_number in self.board[x]:
                for y in range(y_start, y_end):
                    coordinate = x, y
                    if self.board[x][y] == self.current_number:
                        self.current_objects_coordinates.append(coordinate)
                break
        print("castle coords", self.current_objects_coordinates)
        #print(self.board)
        self.object_data[self.current_number] = {"center": (self.current_objects_coordinates[0][0], (self.current_objects_coordinates[0][1] + self.current_objects_coordinates[-1][1])/2), "top_left": self.current_objects_coordinates[0], "bottom_right": self.current_objects_coordinates[-1]}
        

    def find_below_tower(self):
        # if true need to add height distance to tower
        pass


class ImageDecoder(ObjectLocator):
    def __init__(self, image_path=None, scale_down=4, color_key=None, meaning_key=None, background_color=0):
        super().__init__(color_key, meaning_key, scale_down=scale_down)

        self.current_board = []  # current board your working on
        self.board_dictionary = {}  # list/dict of the boards that you have played/used

        # opens the image if you initially give it one
        self.image = Image.open(image_path) if image_path else None
        self.width, self.height = self.image.size if image_path else 0, 0

        # \/ used to scale down, say image is 128 by 64 scale_down=4 work have a list output of 32 by 16
        self.scale_down = scale_down

        self.color_key = color_key  # Stores all the objects that are to be located
        self.background_color = background_color  # background should be 0, everything we don't want is 0

    def complete_board(self, image_path):
        self.clear_all()
        self.use_image(image_path)
        self.fill_board()
        #self.print_board()
        self.use_board(self.current_board)
        self.compute_objects_locations()
        self.commit_board()

    # clears all data, when completing a new game
    def clear_all(self):
        self.current_board = []  # current board your working on
        # self.board_dictionary = {}  # list/dict of the boards that you have played/used
        self.clear_object_locator()

    # used mainly setting the image but also can be used to retrieve data
    def use_image(self, image_path=None):
        if image_path:
            self.image = Image.open(image_path)
            self.width, self.height = self.image.size
        else:
            return [image_path, self.image, (self.width, self.height)]

    # Once your finished with a board save it to "storage" in case you need it later
    def commit_board(self, name=None):
        name = len(self.board_dictionary) if name is None else name
        if name not in self.board_dictionary:
            self.board_dictionary[name] = {"board": self.current_board, "object_data": self.retrieve_object_data()}
            # Makes a copy of the last board to return bc python's a bitch with mutations
            prev_board = self.current_board.copy()
            self.current_board = []
            return prev_board, self.retrieve_object_data()
        return False

    # Retries board from board_dictionary with specified name and set it to current_board
    def retrieve_board(self, name=None):
        if name is None:
            return self.current_board
        if name in self.board_dictionary:
            self.current_board = self.board_dictionary[name]
            return self.current_board
        return False

    # rarely used but allows you to set the keyt and retrieve the color_key
    def use_color_key(self, color_key=None):
        if color_key is None:
            return color_key
        elif isinstance(color_key, dict):
            self.color_key = color_key
            return True
        else:
            return False

    # prints board... old function, but VERY GOOD FOR VISUALIZING HOW THE CODE WORKS
    def print_board(self):
        print("-" * 25)
        for i in range(len(self.current_board)):
            new_line = "| "
            for x in range(len(self.current_board[i])):
                new_line += f"{self.current_board[i][x]} "
            print(f"{new_line[:-1]} |")
        print("-" * 25)

    # fills the board using the color_key
    def fill_board(self):
        for number, options in self.color_key.items():
            self.color_filter(round(number), options["color"], options["+-"], options["section_data"])

    # fills the board following the set parameters. Adds the corresponding number from the color_key to the
    # current_board to map the collocation of the objects form the image
    def color_filter(self, number, search_color, plus_minus, section_data):

        # Determine if we are mutating an existing board or creating a new one
        mutate = self.current_board != []
        inner_list = []

        y_start, y_end, x_start, x_end = 0, self.height, 0, self.width

        if section_data:
            divide_y, divide_x = section_data["divide"]
            section_y, section_x = section_data["section"]
            y_start = (section_y - 1) * self.height // divide_y
            y_end = section_y * self.height // divide_y
            x_start = (section_x - 1) * self.width // divide_x
            x_end = section_x * self.width // divide_x

        for y in range(y_start, y_end, self.scale_down):
            # If not mutating, start a new inner list for each row
            if not mutate:
                inner_list = []

            for x in range(x_start, x_end, self.scale_down):
                if not mutate and number == self.background_color:
                    inner_list.append(self.background_color)
                    continue
                coordinate = x, y
                current_color = self.image.getpixel(coordinate)

                # Used to check each value of the color and see if it's with-in the +- range
                sum_list = [1 if (abs(current_color[idx] - search_color[idx]) <= plus_minus) else 0 for idx in range(3)]

                # If color matches, set to `number`, otherwise keep old value if mutating, or set to bg color if not
                if sum(sum_list) == 3 and number != self.background_color:
                    if mutate:
                        self.current_board[y // self.scale_down][x // self.scale_down] = number
                    else:
                        inner_list.append(number)
                elif not mutate:
                    inner_list.append(self.background_color)

            # If not mutating, append the new row to the big list
            if not mutate:
                self.current_board.append(inner_list)


# used for all physics calculations
class ImageCalculator:
    def __init__(self, scale_down, game_key, meaning_key):
        self.scale_down = scale_down # multiply cords by this if you want to get the original pixel value

        # calculated_values is where the calculated variables should be put
        self.calculated_values = {"power": 0, "angle": 0}
        self.object_data = {}
        self.game_key = game_key
        self.meaning_key = meaning_key

        # CONSTANTS
        # tower_height = 0.03
        # tower_width = 0.0125
        # acceleration = 0.037
        # #power = 75

    # General functions
    # object data is set from PigeonTanks holds object cords and wind speed
    def set_object_data(self, object_data):
        self.object_data = object_data

    def calculate_values(self, object_data=None):
        # sets object_data to new value if it was initialised
        self.object_data = object_data if object_data else self.object_data
        # use other functions do further calculations here

        # example of how to get values
        print("calculate_values", self.object_data)
        print("red_tank", self.object_data[self.meaning_key["red_tank"]])
        print("blue_tank", self.object_data[self.meaning_key["blue_tank"]])
        print("wind_bar", self.object_data[self.meaning_key["wind_bar"]])
        print("tank distance", self.object_data["tank_distance"])
        print("wind speed", self.object_data["wind_speed"])


    # Calculation functions

    def pixels_to_meters(self):
        pass

    def radians_to_degrees(self, x):
        return x * (180 / math.pi)

    def distance(self, xo, vo, t, a):
        x = xo + vo * t + .5 * a * (t ** 2)
        return x

    def range_function(self, x, g, vo):
        theta = .5 * math.asin((x * g) / (vo ** 2))
        return theta


class PigeonTanks(ImageDecoder, ImageCalculator):
    def __init__(self, master, scale_down=4, game_key=None, meaning_key=None, background_color=0):
        ImageDecoder.__init__(self, scale_down=scale_down, color_key=game_key, meaning_key=meaning_key,
                              background_color=background_color)
        ImageCalculator.__init__(self, scale_down, game_key, meaning_key)
        self.scale_down = scale_down
        self.game_key = game_key
        self.master = master
        self.image_data = []
        self.outcome_options = []
        self.current_image_number = 0
        self.uploaded = False
        self.option_var = None

        # Center the window
        self.center_window()  # Width and height can be adjusted as needed
        # Initialize the first screen
        self.home_screen()

    def center_window(self, width=300, height=200):
        # Get screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate position x, y
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.master.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    def home_screen(self):
        self.clear_screen()
        tk.Button(self.master, text="Quit", command=self.master.quit).pack(side='top', pady=10)
        tk.Button(self.master, text="New Match", command=self.upload_screen).pack(side='top', pady=10)

    def upload_screen(self):
        self.clear_screen()
        tk.Button(self.master, text="Cancel", command=self.home_screen).pack(side='top', pady=10)
        self.upload_btn = tk.Button(self.master, text="Upload", command=self.upload_image)
        self.upload_btn.pack(side='top', pady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if not self.uploaded:
                self.current_image_number += 1
                self.image_data.append(file_path)
                self.upload_btn.config(text="Re-upload")
                tk.Button(self.master, text="Next", command=self.info_screen).pack(side='top', pady=10)
            else:
                self.image_data[-1] = file_path
            self.uploaded = True

    def info_screen(self):
        self.complete_round()
        self.clear_screen()
        self.uploaded = False
        tk.Label(self.master,
                 text=f"Power {self.calculated_values['power']} Angle {self.calculated_values['angle']}°").pack(
            side='top', pady=10)
        self.option_var = tk.StringVar()
        combobox = ttk.Combobox(self.master, textvariable=self.option_var, values=["Left", "Right", "Hit"])
        combobox.pack(side='top', pady=10)
        combobox.current(0)  # Default selection
        tk.Button(self.master, text="Next", command=self.summary_screen).pack(side='top', pady=10)

        # Modify this line to pass the current image number and its path
        tk.Button(self.master, text="View Board", command=lambda: self.view_board(
            (self.current_image_number - 1, self.image_data[self.current_image_number - 1]))).pack(side='top', pady=10)

    def summary_screen(self):
        self.clear_screen()
        self.outcome_options.append(self.option_var.get())
        tk.Button(self.master, text="New Image", command=self.upload_screen).pack(side='top', pady=10)
        tk.Button(self.master, text="Finish", command=self.final_screen).pack(side='top', pady=10)

    def final_screen(self):
        self.clear_screen()
        for i, (outcome, data) in enumerate(zip(self.outcome_options, self.image_data)):
            row_frame = tk.Frame(self.master)
            row_frame.pack(side='top', pady=5)
            tk.Label(row_frame, text=f"{i + 1} - {outcome}").pack(side='left', padx=5)
            tk.Button(row_frame, text="View Board", command=lambda d=(i, data): self.view_board(d)).pack(side='left',
                                                                                                         padx=5)
        tk.Button(self.master, text="Continue", command=self.reset_to_home).pack(side='top', pady=10)

    def reset_to_home(self):
        self.clear_all()
        self.image_data = []
        self.outcome_options = []
        self.current_image_number = 0
        self.board_dictionary = {}  # should probably make a function for this but...
        self.home_screen()

    # returns the board(0's, 1's 2's...) and the object_data (the cords of the objects)
    def retrieve_reverent_data(self, board_number):
        board_info = self.retrieve_board(board_number)
        if isinstance(board_info, dict):
            return board_info["board"],  board_info["object_data"]
        return False

    def view_board(self, data):
        board_number, image_path = data
        print(f"View Board {board_number}")
        board, object_data = self.retrieve_reverent_data(board_number)
        display_pg_window(board, self.game_key, image_path, horizontal_sections=4, vertical_sections=3,
                          object_data=object_data, circle_size=3)

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def complete_round(self):
        board_number = self.current_image_number - 1
        self.complete_board(self.image_data[board_number])
        board, object_data = self.retrieve_reverent_data(board_number)
        self.calculate_values(object_data)
        self.print_data()
        

# mainly from GPT but its can be used for testing stuff and what not
def display_pg_window(board, key, image_path, object_data=None, circle_size=5, horizontal_sections=None,
                      vertical_sections=None, section_to_fill=None):
    pygame.init()  # Initialize all imported pygame modules

    background_colour = (234, 212, 252)
    block_size = 1  # Set the size of the grid block

    # Load the image
    image = pygame.image.load(image_path)

    # The display window size should be proportional to the board size
    screen_width, screen_height = len(board[0]) * block_size, len(board) * block_size
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Presses Viewer')

    def fill_section(section_coords, fill_color):
        section_width = screen_width // vertical_sections
        section_height = screen_height // horizontal_sections
        top_left_x = (section_coords[1] - 1) * section_width
        top_left_y = (section_coords[0] - 1) * section_height
        pygame.draw.rect(screen, fill_color, (top_left_x, top_left_y, section_width, section_height))

    def draw_circles():
        if object_data:
            for key, value in object_data.items():
                try:
                    y, x = value['center']
                    pygame.draw.circle(screen, (255, 255, 255), (x, y), circle_size)
                except:
                    pass

    def draw_board():
        screen.fill(background_colour)
        for y in range(len(board)):
            for x in range(len(board[y])):
                pixel_color = key[board[y][x]]["color"]
                pygame.draw.rect(screen, pixel_color, (x * block_size, y * block_size, block_size, block_size))

        # Fill a specific section if provided
        if section_to_fill is not None:
            fill_section(section_to_fill, (100, 100, 255))  # Fill color is light blue for demonstration

        if horizontal_sections is not None and vertical_sections is not None:
            # Drawing horizontal lines
            for h in range(1, horizontal_sections):
                start_pos = (0, h * (screen_height // horizontal_sections))
                end_pos = (screen_width, h * (screen_height // horizontal_sections))
                pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos)

            # Drawing vertical lines
            for v in range(1, vertical_sections):
                start_pos = (v * (screen_width // vertical_sections), 0)
                end_pos = (v * (screen_width // vertical_sections), screen_height)
                pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos)

        # Draw circles if object_data is provided
        draw_circles()

        pygame.display.flip()

    def display_image():
        # Scale the image to fit the screen if necessary
        scaled_image = pygame.transform.scale(image, (screen_width, screen_height))
        screen.blit(scaled_image, (0, 0))
        pygame.display.flip()
        

    running = True
    show_image = False  # Variable to toggle between the image and the board
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse button is pressed, show the image
                show_image = True
            elif event.type == pygame.MOUSEBUTTONUP:
                # Mouse button is released, show the board
                show_image = False
            elif event.type == pygame.KEYDOWN:
                # space bar toggles the image display
                if event.key == pygame.K_SPACE:
                    show_image = not show_image
                # ESC to Quit
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if show_image:
            display_image()
        else:
            draw_board()

    pygame.quit()


# func to help see how different code affects the load time... Testing
def time_function(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    time_taken = end_time - start_time
    return time_taken, result


if __name__ == '__main__':
        # this helps scale down the org image, larger num = smaller image... multiply it back to get true pixel positions
    SCALE_DOWN = 4

    # The colors that were searching for
    BLACK_GROUND = (0, 0, 0)  # (255, 255, 255)  #   # this will be where the colors you have chosen to search are not
    RED_TANK = (227, 114, 91)  # (89, 37, 24)
    BLUE_TANK = (54, 118, 188)  # (65, 116, 163)
    GRAY_CASTLE = (85, 94, 102)
    WIND_SPEED = (63, 77, 115)

    # "divide" = how to divide the screen & the section from the now divided screen to search for the colors in
    # "section": "divide": [8, 5], "section": [1, 1]
    # game key has been optimised to be most efficient and accurate -- still subjected to change
    GAME_KEY = {0: {"color": BLACK_GROUND, "+-": 0, "section_data": None},
                1: {"color": GRAY_CASTLE, "+-": 5, "section_data": {"divide": [2, 5], "section": [2, 3]}},
                2: {"color": RED_TANK, "+-": 40, "section_data": {"divide": [7, 2], "section": [5, 1]}},
                2.1: {"color": RED_TANK, "+-": 40, "section_data": {"divide": [7, 2], "section": [6, 1]}},
                3: {"color": BLUE_TANK, "+-": 40, "section_data": {"divide": [7, 2], "section": [5, 2]}},
                3.1: {"color": BLUE_TANK, "+-": 40, "section_data": {"divide": [7, 2], "section": [6, 2]}},
                4: {"color": WIND_SPEED, "+-": 40, "section_data": {"divide": [10, 3], "section": [2, 2]}}}

    MEANING_KEY = {"castle": 1, "red_tank": 2, "blue_tank": 3, "wind_bar": 4}

    root = tk.Tk()
    app = PigeonTanks(root, game_key=GAME_KEY, meaning_key=MEANING_KEY, scale_down=SCALE_DOWN)
    
    root.mainloop()
