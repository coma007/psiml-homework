"""
This script is solution of the second problem in psiml homework, 2023.
(Asteroid)

Author: Milica Sladakovic (github.com/coma007)
"""

import sys


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


def count_leveled_areas():
    positive_direction_polygons = []
    negative_direction_polygons = []
    max_area = 0
    for axis in range(3):
        ith_coordinates = [voxel.coordinates[axis] for voxel in VOXELS]
        min_coordinate = min(ith_coordinates)
        max_coordinate = max(ith_coordinates)
        for coordinate in range(min_coordinate, max_coordinate+1):
            cubes = [voxel for voxel in VOXELS if voxel.coordinates[axis] == coordinate]
            
            positive_direction_areas, positive_max_area = get_areas_for_direction(cubes, axis, positive=True)
            negative_direction_areas, negative_max_area = get_areas_for_direction(cubes, axis, positive=False)
            
            max_area = max(max_area, positive_max_area, negative_max_area)
            if positive_direction_areas:
                positive_direction_polygons += positive_direction_areas
            if negative_direction_areas:
                negative_direction_polygons += negative_direction_areas
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
    indexes = {cubes[0] : 0}
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


if __name__ == "__main__":

    read_vertices()
    print(count_total_area())
    print(count_leveled_areas())
