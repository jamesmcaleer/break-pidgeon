# test
from PIL import Image
import math
import pygame


# CONSTANTS
# tower_height = 0.03
# tower_width = 0.0125
# acceleration = 0.037
# #power = 75


class ImageDecoder:
    def __init__(self, image_path="screenshot.png", scale_down=4, color_key=None):
        self.current_board = []  # current board your working on
        self.board_dictionary = {}  # list/dict of the boards that you have played/used
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size
        self.scale_down = scale_down  # used to scale down, say image is 128 by 64 scale_down=4 work have a list output of 32 by 16
        self.color_key = color_key

    # Once your finished with a board save it to "storage" in case you need it later
    def commit_board(self, name=None):
        name = f"board_{len(self.board_dictionary)}" if name is None else name
        if name not in self.board_dictionary:
            self.board_dictionary[name] = self.current_board
            prev_board = self.current_board.copy()  # Makes a copy of the last board to return bc python's a bitch with mutations
            self.current_board = []
            return prev_board
        return False

    # Retries board from board_dictionary with specified name and set it to current_board
    def retrieve_board(self, name=None):
        if name is None:
            return self.current_board
        if name in self.board_dictionary:
            self.current_board = self.board_dictionary[name]
            return self.current_board
        return False

    def use_color_key(self, key=None):
        if key is None:
            return key
        elif isinstance(key, dict):  # Use isinstance() for checking an instance's type
            self.color_key = key
            return True
        else:
            return False

    # prints board... old function
    def print_board(self):
        print("-" * 25)
        for i in range(len(self.current_board)):
            new_line = "| "
            for x in range(len(self.current_board[i])):
                new_line += f"{self.current_board[i][x]} "
            print(f"{new_line[:-1]} |")
        print("-" * 25)

    # Used to check a single value of a color and see if it's with-in the +- range
    def check_value(self, v1, v2, plus_minus):
        if v1 == v2:
            return True
        elif v2 > v1:
            return v2 - plus_minus <= v1
        elif v2 < v1:
            return v2 + plus_minus >= v1
        else:
            return False

    # fills the board using every key
    def fill_board(self):
        for number, options in self.color_key.items():
            self.color_filter(number, options["color"], options["+-"], options["section_data"])

    # fills the board following the set parameters
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
                coordinate = x, y
                current_color = self.image.getpixel(coordinate)
                sum_list = [1 if self.check_value(color_value, search_color[idx], plus_minus) else 0 for
                            idx, color_value in enumerate(current_color)]

                # If color matches, set to `number`, otherwise keep old value if mutating, or set to 0 if not
                if sum(sum_list) == 3 and number != 0:
                    if mutate:
                        self.current_board[y // self.scale_down][x // self.scale_down] = number
                    else:
                        inner_list.append(number)
                elif not mutate:
                    inner_list.append(0)

            # If not mutating, append the new row to the big list
            if not mutate:
                self.current_board.append(inner_list)


class ImageCalculator:
    def __init__(self, board, color_key, scale_down=3):
        self.board = board
        self.color_key = color_key
        self.scale_down = scale_down
        self.data_points = []
        self.current_number = 0
        self.width, self.height = len(self.board), len(self.board[0])
        # for tank distance it's from red tank / left tank (x distance from centers), (y (+/- up/down) from blue tank)

        self.data_example = {"red_tank": {"center": ["x", "y"], "top_left": ["x", "y"], "bottom_right": ["x", "y"]},
                             "blue_tank": {"center": ["x", "y"], "top_left": ["x", "y"], "bottom_right": ["x", "y"]},
                             "tank_distance": ["x", "y", "total"],
                             "castle": {"center": ["x", "y"], "top_left": ["x", "y"], "bottom_right": ["x", "y"]},
                             "wind_speed": 0
                             }
        self.object_data = {}

    # GENERAL FUNCTIONS
    def print_data(self):
        print(self.object_data)
        for number, data in self.object_data.items():
            print(f"Data Object {number}: {data}")

    def retrieve_object_data(self):
        return self.object_data

    # IMAGE SCRAPING FUNCTIONS
    def find_coordinates(self, data_points):
        # Top left is the point with the smallest x and y value
        top_left = min(data_points, key=lambda point: (point[0], point[1]))
        # Bottom right is the point with the largest x and y value
        bottom_right = max(data_points, key=lambda point: (point[0], point[1]))

        # Center is the average of the x values and the average of the y values
        center_x = sum(point[0] for point in data_points) / len(data_points)
        center_y = sum(point[1] for point in data_points) / len(data_points)
        center = (round(center_x), round(center_y))

        return {"center": center, "top_left": top_left, "bottom_right": bottom_right}

    def get_data_points(self, clear_points=True):
        self.data_points = [] if clear_points else self.data_points

        y_start, y_end, x_start, x_end = 0, self.height, 0, self.width

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                coordinate = x, y
                if board[x][y] == self.current_number:
                    self.data_points.append(coordinate)

        return self.data_points

    def up_scale_cords(self):
        for object, data in self.object_data[self.current_number].items():
            self.object_data[self.current_number][object] = data[0]*self.scale_down,data[1]*self.scale_down

    def get_tank(self):
        points = self.get_data_points()
        self.object_data[self.current_number] = self.find_coordinates(points)

    def get_tank_values(self, numbers):
        for self.current_number in numbers:
            self.get_tank()
            # self.up_scale_cords()

        def calculate_distance(coord1, coord2):
            # Calculate the distance between two points in 2D space.
            return ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5

        y1, x1 = self.object_data[numbers[0]]["center"]
        y2, x2 = self.object_data[numbers[1]]["center"]
        self.object_data["tank_distance"] = [y1 - y2, x2 - x1, calculate_distance((x1, y1), (x2, y2))]

    def wind_speed_coordinates(self):

        def length_of_zeros(sequence):
            # Split the sequence by current_number to find all sequences of '0's
            zero_sequences = sequence.split(f'{self.current_number}')
            # Remove empty strings from the list
            zero_sequences = [seq for seq in zero_sequences if seq]
            # Find the longest sequence of '0's
            longest_zero_sequence = max(zero_sequences, key=len)
            return len(longest_zero_sequence)

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

        y1, x1 = self.object_data[self.current_number]["top_left"]
        y2, x2 = self.object_data[self.current_number]["bottom_right"]
        middle = (y1 + y2) // 2
        total_length = x2 - x1

        # Get the sequence in the middle row from x1 to x2
        middle_sequence = ''.join(str(board[middle][x]) for x in range(x1, x2))
        # Use the function to get the length of zeros
        length_of_zeros_in_middle = length_of_zeros(middle_sequence)

        sign, count = count_side_numbers(middle_sequence)

        wind_speed = round(length_of_zeros_in_middle / (total_length / 2) * 10, 1) * sign

        self.object_data["wind_speed"] = wind_speed

    def get_wind_speed(self, number):
        self.current_number = number
        points = self.get_data_points()
        self.object_data[self.current_number] = self.find_coordinates(points)
        self.wind_speed_coordinates()

    def get_height(self):
        pass

    def find_below_tower(self):
        # if true need to add height distance to tower
        pass

    # EQUATION FUNCTIONS
    def pixels_to_meters(self, ):
        pass

    def radians_to_degrees(self, x):
        return x * (180 / math.pi)

    def distance(self, xo, vo, t, a):
        x = xo + vo * t + .5 * a * (t ** 2)
        return x

    def range_function(self, x, g, vo):
        theta = .5 * math.asin((x * g) / (vo ** 2))
        return theta


# mainly from GPT but its can be used for testing stuff and what not
def display_pg_window(board, key, image_path, object_data=None, circle_size=5, horizontal_sections=None, vertical_sections=None, section_to_fill=None):
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
                if key in [2, 3, 4]:  # Assuming these are the keys for objects we want to draw
                    y, x = value['center']
                    pygame.draw.circle(screen, (255, 255, 255), (x, y), circle_size)


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


if __name__ == '__main__':
    scale_down = 2

    black_ground = (0, 0, 0)  # (255, 255, 255)  #   # this will be where the colors you have chosen to search are not
    red_tank = (89, 37, 24)
    blue_tank = (65, 116, 163)
    gray_castle = (85, 94, 102)
    # wind_speed = (157, 196, 218)
    wind_speed = (63, 77, 115)

    # "divide" = how to divide the screen & the section from the now divided screen to search for the colors in
    # "section": "divide": [8, 5], "section": [1, 1]

    key = {0: {"color": black_ground, "+-": 0, "section_data": None},
           1: {"color": gray_castle, "+-": 5, "section_data": {"divide": [2, 5], "section": [2, 3]}},
           2: {"color": red_tank, "+-": 40, "section_data": {"divide": [8, 5], "section": [7, 1]}},
           3: {"color": blue_tank, "+-": 40, "section_data": {"divide": [8, 5], "section": [7, 5]}},
           4: {"color": wind_speed, "+-": 20, "section_data": {"divide": [45, 3], "section": [9, 2]}}}

    image_decoder = ImageDecoder(image_path="screenshot.png", color_key=key, scale_down=scale_down)
    image_decoder.fill_board()
    # number = 1
    # image_decoder.color_filter(key[number]["color"], key[number]["+-"], number)

    board = image_decoder.retrieve_board()

    image_calculator = ImageCalculator(board, key, scale_down=scale_down)
    image_calculator.print_data()

    image_calculator.get_tank_values((2, 3))
    image_calculator.get_wind_speed(4)

    image_calculator.print_data()

    display_pg_window(board, key, 'screenshot.png', object_data=image_calculator.retrieve_object_data(), circle_size=4)

