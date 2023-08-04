"""
This script is solution of the second problem in psiml homework, 2023.
(Asteroid)

Author: Milica Sladakovic (github.com/coma007)
"""

import sys
import numpy as np
from math import sqrt, pi


##############################################################
# VOXEL GRAPH

# Models voxel and its connections to other voxels
class Voxel(object):
    __slots__ = "_x", "_y", "_z", "_neighbours"

    def __init__(self, coordinates) -> None:
        self._x = coordinates[0]
        self._y = coordinates[1]
        self._z = coordinates[2]
        self._neighbours = {}

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def neighbours(self):
        return self._neighbours

    @property
    def coordinates(self):
        return (self._x, self._y, self._z)

    def has_neighbour(self, other):
        dx = abs(self._x - other.x)
        dy = abs(self._y - other.y)
        dz = abs(self._z - other.z)
        return (dx, dy, dz) in ((1, 0, 0), (0, 1, 0), (0, 0, 1))

    def classify_neighbour(self, other):
        for i in range(3):
            if self.coordinates[i] == other.coordinates[i] + 1:
                self._neighbours[f"{i}-"] = other
                other.neighbours[f"{i}+"] = self
            elif self.coordinates[i] == other.coordinates[i] - 1:
                self._neighbours[f"{i}+"] = other
                other.neighbours[f"{i}-"] = self

    def __str__(self):
        return str(self.coordinates)

    def __repr__(self):
        return str(self.coordinates)


##############################################################
# INPUT PARSING


VOXELS = []
NUM_OF_VOXELS = 0

lines = ""


def read_vertices():
    global VOXELS, NUM_OF_VOXELS, lines

    lines = sys.stdin.readlines()
    for line in lines:
        line = line.replace("(", "").replace(")", "").replace("\\r", "")
        coordinates = line.split(", ")
        coordinates = tuple(int(x) for x in coordinates)
        VOXELS.append(Voxel(coordinates))
    NUM_OF_VOXELS = len(VOXELS)


##############################################################
# AREA OF ASTEROID SURFACE


def count_total_area():
    total_areas = NUM_OF_VOXELS * 6
    return total_areas - count_common_areas()


def count_common_areas():
    common_areas = 0
    for i in range(0, len(VOXELS)):
        a = VOXELS[i]
        for j in range(i+1, len(VOXELS)):
            b = VOXELS[j]
            if a.has_neighbour(b):
                common_areas += 2
                a.classify_neighbour(b)
    return common_areas


##############################################################
# LARGEST AREA ON THE SAME LEVEL OF ASTEROID SURFACE

polygons = {0: [], 1: [], 2: []}


def count_leveled_areas():
    global polygons

    max_area = 0
    for axis in range(3):
        ith_coordinates = [voxel.coordinates[axis] for voxel in VOXELS]
        min_coordinate = min(ith_coordinates)
        max_coordinate = max(ith_coordinates)
        for coordinate in range(min_coordinate, max_coordinate+1):
            cubes = [
                voxel for voxel in VOXELS if voxel.coordinates[axis] == coordinate]

            positive_direction_areas, positive_max_area = get_areas_for_direction(
                cubes, axis, positive=True)
            negative_direction_areas, negative_max_area = get_areas_for_direction(
                cubes, axis, positive=False)

            max_area = max(max_area, positive_max_area, negative_max_area)
            if positive_direction_areas:
                polygons[axis] += positive_direction_areas
            if negative_direction_areas:
                polygons[axis] += negative_direction_areas
    return max_area


def get_areas_for_direction(cubes, axis, positive=True):
    cubes = ignore_cubes_with_common_area(cubes, axis, positive)
    if not cubes:
        return None, 0
    connected_areas = find_connected_areas(cubes)
    if connected_areas:
        return connected_areas, max(map(len, connected_areas))
    else:
        return None, 0


def ignore_cubes_with_common_area(cubes, axis, positive=True):
    filtered_cubes = []
    sign = "+" if positive else "-"
    for cube in cubes:
        if f"{axis}{sign}" not in cube.neighbours:
            filtered_cubes.append(cube)
    return filtered_cubes


def find_connected_areas(cubes):
    areas = [[cubes[0]]]
    indexes = {cubes[0]: 0}
    for i in range(len(cubes)-1):
        for j in range(i+1, len(cubes)):
            if cubes[j] in indexes:
                continue
            if cubes[i].has_neighbour(cubes[j]):
                if cubes[i] in indexes:
                    indexes[cubes[j]] = indexes[cubes[i]]
                    areas[indexes[cubes[j]]].append(cubes[j])
                else:
                    indexes[cubes[i]] = len(areas)
                    indexes[cubes[j]] = len(areas)
                    areas.append([cubes[i], cubes[j]])
        if cubes[i] not in indexes:
            indexes[cubes[i]] = len(areas)
            areas.append([cubes[i]])

    return areas


##############################################################
# LANDING AREA OF ASTEROID


def find_landing_subarea():
    max_radius = 0
    for axis in polygons:
        subareas = polygons[axis]
        for area in subareas:
            if len(area) <= 1:
                current_radius = len(area) / 2
            else:
                area = transform_cubes_to_surface(area, axis)
                current_radius = find_largest_square_subarea(area)
            max_radius = max(current_radius, max_radius)
    return max_radius ** 2 * pi


def transform_cubes_to_surface(cubes, axis):
    surface = []
    for cube in cubes:
        coordinates = list(cube.coordinates)
        coordinates.pop(axis)
        surface.append(tuple(coordinates))
    return surface


def find_largest_square_subarea(area):
    total_max_square = 0
    area.sort()
    neighbours = find_all_succesive_neighbours(area)
    for unit_square in area:
        max_possible_square = min(
            len(neighbours[unit_square][0]), len(neighbours[unit_square][1]))
        can_form_square = False
        while not can_form_square:
            can_form_square = test_neighbours(
                neighbours, unit_square, max_possible_square)
            max_possible_square -= 1
        current_size = max_possible_square + 1
        largest_radius = find_radius_of_landing_surface(
            unit_square, current_size, area)
        total_max_square = max(total_max_square, largest_radius)
    return total_max_square


def test_neighbours(neighbours, unit_square, max_possible_square):
    for i in range(1, max_possible_square):
        top_neighbour = neighbours[unit_square][0][i]
        right_neighbour = neighbours[unit_square][1][i]
        if len(neighbours[top_neighbour][1]) == len(neighbours[right_neighbour][0]) == max_possible_square:
            continue
        else:
            return False
    return True


def find_all_succesive_neighbours(area):
    neighbours = {}
    for unit_square in area:
        index = area.index(unit_square)
        top_neighbours = find_succesive_neighbours(
            unit_square, area[index+1:], axis=0)
        right_neighbours = find_succesive_neighbours(
            unit_square, area[index+1:], axis=1)
        neighbours[unit_square] = top_neighbours, right_neighbours
    return neighbours


def find_succesive_neighbours(unit_square, area, axis):
    neighbours = [unit_square]
    for square in area:
        if unit_square[axis] == square[axis]:
            neighbours.append(square)
    return neighbours


def find_radius_of_landing_surface(unit_square, current_size, area):
    radius = current_size / 2
    horizontal_chunks, vertical_chunks = detect_chunks(
        unit_square, current_size, area)
    if all(vertical_chunks):
        if horizontal_chunks.count(True) == 1:
            radius = calculate_radius_if_three_chunks(radius)
        elif all(horizontal_chunks):
            radius = calculate_radius_if_four_chunks(radius)
    elif vertical_chunks.count(True) == 1:
        if horizontal_chunks.count(True) == 1:
            radius = calculate_radius_if_two_chunks(radius)
        elif all(horizontal_chunks):
            radius = calculate_radius_if_three_chunks(radius)
    return radius


def detect_chunks(unit_square, current_size, area):
    left_chunk = [False] * current_size
    right_chunk = [False] * current_size
    top_chunk = [False] * current_size
    bottom_chunk = [False] * current_size

    x = unit_square[0]
    y = unit_square[1]
    for i in range(current_size):
        if (x+i, y-1) in area:
            bottom_chunk[i] = True
        if (x+i, y+current_size) in area:
            top_chunk[i] = True
        if (x-1, y+i) in area:
            left_chunk[i] = True
        if (x+current_size, y+i) in area:
            right_chunk[i] = True

    return [all(left_chunk), all(right_chunk)], [all(top_chunk), all(bottom_chunk)]


def calculate_radius_if_two_chunks(radius):
    return radius * (2*sqrt(2))/(1+sqrt(2))


def calculate_radius_if_three_chunks(radius):
    return 5/4 * radius


def calculate_radius_if_four_chunks(radius):
    return sqrt(2) * radius


if __name__ == "__main__":

    read_vertices()
    print(count_total_area(), end=" ")
    print(count_leveled_areas(), end=" ")
    print(find_landing_subarea())
