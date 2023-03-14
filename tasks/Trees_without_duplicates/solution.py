"""
This script is solution of the first problem in psiml homework, 2023.
(Trees without duplicates)

Author: Milica Sladakovic (github.com/coma007)
"""

import sys


##############################################################
# FILETREE

# Models all files/directories as tree nodes
class File(object):
    __slots__ = "_name", "_type", "_parent", "_children", "_depth", "_listed"

    def __init__(self, name, filetype, parent=None, children=None) -> None:
        self._name = name
        self._type = filetype
        self._parent = parent
        if children is None:
            children = []
        self._children = children
        if self._parent is None:
            self._depth = 0
        else:
            self._depth = self._parent.depth + 1
        self._listed = False

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def depth(self):
        return self._depth

    @property
    def listed(self):
        return self._listed

    @listed.setter
    def listed(self, value: bool):
        self._listed = value

    def __gt__(self, __o) -> bool:
        return self.type >= __o.type and self._name > __o.name

    def find_child(self, filename, filetype="dir"):
        for child in self.children:
            if child.name == filename and child.type == filetype:
                return child
        return self.add_child(filename, filetype)

    def add_child(self, filename, filetype="dir"):
        new_child = File(name=filename, filetype=filetype, parent=self)
        self.children.append(new_child)
        return new_child

    def remove_child(self, filename, filetype="dir"):
        for child in self.children:
            if child.name == filename and child.type == filetype:
                self.children.remove(child)
                return child


# Depth first search generator
def depth_first(node):
    yield node
    node.children.sort(key=lambda x: (x.type, x.name))
    for child in node.children:
        yield from depth_first(child)


# Path from node to root
def get_path_to_root(node):
    path = [node]
    if node != ROOT:
        path += get_path_to_root(node.parent)
    return path


# Path from root to node
def get_path_from_root(node):
    path = get_path_to_root(node)
    path.reverse()
    return path


# Lowest common ancestor of two nodes
def find_lowest_common_ancestor(first_node, second_node):
    first_path = DUPLICATES_PATHS[first_node]
    second_path = DUPLICATES_PATHS[second_node]
    lowest_common_ancestor = ROOT

    for first_ancestor, second_ancestor in zip(first_path, second_path):
        if first_ancestor != second_ancestor:
            break
        lowest_common_ancestor = first_ancestor
    return lowest_common_ancestor


##############################################################
# PARSING

# Variables that store root and current node
ROOT = File(name="root", filetype="dir")
CURRENT = ROOT


# Function parses input and based on the command,
# and with helper functions generates the tree
def generate_filetree():
    lines = sys.stdin.readlines()
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if line[0] == "$":
            words = line.split(" ")
            command = words[1].strip()
            if command == "cd":
                filename = words[2].strip()
                change_dir(filename)
            elif command == "rm":
                filename = words[2].strip()
                remove_file(filename)
            elif command == "ls":
                CURRENT.listed = True
        else:
            list_files(line.split(" "))


# Helper function is called on cd command
def change_dir(dirname):
    global CURRENT, ROOT

    if dirname == "..":
        CURRENT = CURRENT.parent
    elif dirname == "/":
        CURRENT = ROOT
    else:
        CURRENT = CURRENT.find_child(dirname)


# Helper function is called on ls command
# Checks if one of listed files is name duplicate in filetree
def list_files(files):

    for filename in files:
        filename = filename.strip()
        if filename[:3] == "(f)":
            node = CURRENT.find_child(filename[3:], filetype="file")
            # check_if_first(node)
        elif filename[:3] == "(d)":
            CURRENT.find_child(filename[3:], filetype="dir")


# Helper function is called on rm command
# Removes file from duplicates
def remove_file(filename):
    global CURRENT

    node = CURRENT.remove_child(filename=filename)
    if node and DUPLICATES[filename]:
        DUPLICATES[filename].remove(node)
    if node and DUPLICATES_PATHS[node]:
        del DUPLICATES_PATHS[node]


##############################################################
# COUNTING AND PARSING FILETREE

# Variables store number of directories and files in the filetree
TOTAL_DIRS = 0
TOTAL_FILES = 0
# Variable stores sorted filetree string representation
TREE = ""


# Function counts total number of files and directories
# and creates tree string representation
# It also checks if the visited file is duplicate
def analyze_tree(node):
    global TOTAL_DIRS, TOTAL_FILES, TREE

    if node == ROOT:
        TREE += "/"
    else:
        if node.type == "file":
            TOTAL_FILES += 1
            TREE += "\n" + "|-" * node.depth + node.name
            check_for_duplicates(node)
        elif node.type == "dir":
            TOTAL_DIRS += 1
            TREE += "\n" + "|-" * node.depth + node.name + "/"
    node.children.sort(key=lambda x: (x.type, x.name))
    for child in node.children:
        analyze_tree(child)
    if not node.listed and node.type == "dir":
        TREE += "\n" + "|-" * (node.depth+1) + "?"


##############################################################
# DUPLICATES
# Varibale that stores duplicates based on their name
# key: filename, val: list of nodes with same filename
DUPLICATES = {}
DUPLICATES_PATHS = {}
# Remove script that represents minimal number of commands
# to remove all duplicate files by filename
# (except file with filename first appereance)
REMOVE_SCRIPT = ""


# Helper function checks for duplicates of given node's filename
def check_for_duplicates(node):
    global DUPLICATES, DUPLICATES_PATHS

    if node.name in DUPLICATES and node not in DUPLICATES[node.name]:
        DUPLICATES[node.name].append(node)
        DUPLICATES_PATHS[node] = get_path_from_root(node)
    elif node.name not in DUPLICATES:
        DUPLICATES[node.name] = [node]


# Function removes duplicate files if any
# by updating REMOVE_SCRIPT with helper functions
def remove_duplicates():
    global REMOVE_SCRIPT

    targets = list(DUPLICATES_PATHS.keys())
    if not targets:
        return
    start = ROOT
    for i, j in zip(range(len(targets)-1), range(1, len(targets))):
        current_target = targets[i]
        next_target = targets[j]
        REMOVE_SCRIPT += remove_target(start, current_target)
        start = find_lowest_common_ancestor(current_target, next_target)
        if jump_to_root(start, current_target.parent):
            start = ROOT
        else:
            REMOVE_SCRIPT += jump_to_start(start, current_target.parent)
    REMOVE_SCRIPT += remove_target(start, targets[-1])


# Helper function updates REMOVE_SCRIPT for certain node (target)
# including all commands for navigation from start to target
# and target removal
def remove_target(start, target):
    remove_script = ""
    path = DUPLICATES_PATHS[target]
    start_index = path.index(start)
    path = path[start_index:]
    for node in path:
        if node == ROOT:
            if should_print_root():
                remove_script += "\n$ cd /"
        elif node != target and node != path[0]:
            remove_script += "\n$ cd " + node.name
        elif node == target:
            remove_script += "\n$ rm " + node.name
    return remove_script

# Helper function prevents change directory to root
# if current directory was just changed to root
def should_print_root():
    return not (len(REMOVE_SCRIPT) > 2 and REMOVE_SCRIPT[-2:] == "..")


# Helper functions decides if it is optimal to
# jump to root and then go to lowest common ancestor, 
# or go backwards to it
def jump_to_root(start, node):
    return start.depth < node.depth // 2

# Helper function that updates REMOVE_SCRIPT
# by going backward from node to start
def jump_to_start(start, node):
    remove_script = ""
    while node != start:
        remove_script += "\n$ cd .."
        node = node.parent
    return remove_script


# main program
if __name__ == "__main__":

    # read input and generate tree
    generate_filetree()
    # TASK 1 (count files and directories) and TASK 2 (string representation of the tree)
    analyze_tree(ROOT)
    print(TOTAL_DIRS)
    print(TOTAL_FILES)
    print(TREE)
    # TASK 3 (remove duplicates)
    remove_duplicates()
    print(REMOVE_SCRIPT[1:], end="")
