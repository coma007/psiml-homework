"""
This script is solution of the third problem in psiml homework, 2023.
(Olympic rings)

Author: Milica Sladakovic (github.com/coma007)
"""

import numpy as np
from PIL import Image
from collections import defaultdict
from math import sqrt, pi, cos, sin, inf

OLYMPIC_COLORS = {
    (255, 255, 0): 'Y',    # yellow
    (0, 0, 255): 'B',      # blue
    (0, 0, 0): 'K',        # black
    (0, 255, 0): 'G',      # green
    (255, 0, 0): 'R'       # red
}


##############################################################
# COUNT OLYMPIC COLOR PIXELS ON IMAGE

def count_olympic_pixels(image):

    with Image.open(image) as image:

        pixel_count = {k: 0 for k in OLYMPIC_COLORS.values()}

        for pixel in image.getdata():
            rgb = pixel[:3]
            if rgb in OLYMPIC_COLORS:
                pixel_count[OLYMPIC_COLORS[rgb]] += 1

        return pixel_count


##############################################################
# FIND OLYMPIC LOGOS ON IMAGE

def find_olympic_logos(image, minimum_radius, maximum_radius, max_iter_steps, threshold):

    edge_coordinates = get_edge_coordinates(image)
    points = get_radius_patterns(
        minimum_radius, maximum_radius, max_iter_steps)

    accumulator = hough_transform(edge_coordinates, points)

    circles = find_olympic_circles(image, max_iter_steps, threshold, accumulator)
    logo_circles, logos_count = validate_circles(circles)
    return logo_circles, logos_count


def get_edge_coordinates(image):
    binary_image = get_binary_image(image)
    pixels = np.asarray(binary_image)
    coordinates = np.column_stack(np.where(pixels == 0))
    return coordinates.tolist()


def get_binary_image(image):
    with Image.open(image) as image:
        grayscale = image.convert('L')
        grayscale.putdata(np.where(np.array(grayscale) > 240, 255, 0).flatten())
        return grayscale


def get_radius_patterns(minimum_radius, maximum_radius, max_iter_steps):
    points = []
    for r in range(minimum_radius, maximum_radius + 1):
        for t in range(max_iter_steps):
            points.append((r, int(r * cos(2 * pi * t / max_iter_steps)),
                          int(r * sin(2 * pi * t / max_iter_steps))))
    return points


def hough_transform(edge_coordinates, points):
    accumulator = {}
    for y, x in edge_coordinates:
        for r, dx, dy in points:
            a = x - dx
            b = y - dy
            if (a, b, r) in accumulator:
                accumulator[(a, b, r)] += 1
            else:
                accumulator[(a, b, r)] = 1
    return accumulator


def find_olympic_circles(image, max_iter_steps, threshold, accumulator):
    with Image.open(image) as image:
        rgb = image.convert('RGB')
        circles = []
        for point, intersections_counter in sorted(accumulator.items(), key=lambda x: -x[1]):
            x, y, r = point
            if intersections_counter / max_iter_steps >= threshold and is_circle(circles, x, y):
                color = rgb.getpixel((x + r, y))
                if color in OLYMPIC_COLORS:
                    circles.append((OLYMPIC_COLORS[color], x, y, r))
        for i in range(len(circles)):
            circles[i] = circles[i][:3]
        return circles


def is_circle(circles, x, y):
    return all((x - xc) ** 2 + (y - yc) ** 2 > rc ** 2 for _, xc, yc, rc in circles)


def validate_circles(circles):

    valid_circles = []
    valid_count = 0
    while True:
        potential_logo = []
        valid_color_combinations = [('B', 'Y'), ('Y', 'B'), ('Y', 'K'), ('K', 'G'), ('G', 'R')]
        for first_color, second_color in valid_color_combinations:
            potential_logo.append(find_closest_intersecting_circle(circles, first_color, second_color))
        if None in potential_logo:
            break
        for circle in potential_logo:
            circles.remove(circle)
            valid_circles.append(circle)
        valid_count += 1

    return valid_circles, valid_count


def find_closest_intersecting_circle(circles, first_color, second_color):

    min_distance = inf
    closest_circle = None
    for first_circle in circles:
        for second_circle in circles:
            if first_circle[0] == first_color and second_circle[0] == second_color:
                distance = sqrt((first_circle[1]-second_circle[1])**2+(first_circle[2]-second_circle[2])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_circle = second_circle
    return closest_circle



if __name__ == '__main__':

    image_path = input().strip()

    color_counts = count_olympic_pixels(image_path)
    for color, count in color_counts.items():
        print(f'{color}: {count}')

    
    logo_circles, logos_count = find_olympic_logos(image_path, 60, 89, 17, 0.6)
    print(logos_count)
    for x, y, z in logo_circles:
        print(x, y, z)
