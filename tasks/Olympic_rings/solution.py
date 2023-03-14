import numpy as np
from PIL import Image

# Define Olympic colors
olympic_colors = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'black': (0, 0, 0)
}

def count_pixels(image_path):
    # Open image
    with Image.open(image_path) as image:
        # Convert image to numpy array
        image_array = np.array(image)
        # Initialize counts for each color
        color_counts = {color: 0 for color in olympic_colors}
        # Iterate over each pixel
        for pixel in np.nditer(image_array, flags=['multi_index']):
            # Check if pixel is one of the Olympic colors
            if tuple(pixel) in olympic_colors.values():
                # Increment count for corresponding color
                color = list(olympic_colors.keys())[list(olympic_colors.values()).index(tuple(pixel))]
                color_counts[color] += 1
        return color_counts

if __name__ == '__main__':
    # Read image path from standard input
    image_path = input().strip()
    # Count pixels for each color
    color_counts = count_pixels(image_path)
    # Print color counts
    for color, count in color_counts.items():
        print(f'{color}: {count}')