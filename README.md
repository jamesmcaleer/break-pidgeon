# Game Pigeon Tanks Aim Assistant

## Overview

The Tank Battle Aim Assistant is a tool designed to enhance gameplay for tank-based strategy games. By analyzing screenshots, the tool identifies key game elements such as tanks and obstacles and computes the optimal firing solution in terms of angle and power, taking into account environmental factors like wind.

## Features

- **Image Processing**: Converts screenshots into a map of relevant game objects.
- **Object Detection**: Locates and marks tanks and other important objects.
- **Trajectory Calculation**: Uses physics to determine the best shot.
- **Easy Interface**: Easily upload images to get accurate Power and Angle estimates.
- **Fine Tuning**: Uses user input to adjust the values depending on if the shot was off target.
- **Visual Testing Environment**: Provides a Pygame-based interface for visual verification.

## Installation -- Not available right now :( 

To set up the Tank Battle Aim Assistant, follow these steps:

1. Clone the repository:

git clone [https://github.com/jamesmcaleer/break-pidgeon.git](https://github.com/jamesmcaleer/break-pidgeon.git)

2. Navigate to the project directory:

cd pigeon-tanks

3. Install the required dependencies:

pip install -r requirements.txt


## Usage Instructions

1. **Capture the Screenshot**: Before taking your shot in the game, capture a screenshot on your phone. Then, transfer this screenshot to your computer using email or another preferred method.

2. **Run the Assistant**: Once the screenshot is on your computer, launch the assistant tool to start the analysis process.

3. **Uploading the Image**: Navigate by clicking [New Match] -> [Upload] -> [Re-Upload] or [Next] to upload the image.

4. **Info Page**: The estimated Power and Angle are displayed on the next page. Below, there is a dropdown menu to inform the program whether its calculation was correct ("Hit") or missed to the "left" or "right." A [View Board] button is also available to see what the program interprets from the image.

5. **Continue Page**: You will be prompted to either [New Image] to continue the game or [Finish] to end the session.

6. **Final Page**: This page displays the entire match history, including all calculation outcomes and the ability to view each uploaded photo. After hitting [Continue], you will be taken back to the home page.

## Contributing

Contributions to improve the Tank Battle Aim Assistant are welcome. To contribute:

1. Fork the project.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a new Pull Request.


## License

This project is not licensed. We understand that a license is very important, but I, in fact, have no idea why we would need one. So if you're trying to find one, please click the soon-to-be red 'X' in the top right corner.

## Acknowledgments

- The Pygame community for providing an excellent platform for testing and visualization.
- Contributors who spend time to help improve this tool. Michael, James, Andrey, Zhi

## Contact

For support or to contact the maintainers, please e-mail us at [NotAEmail.com](mailto:email@example.com).
