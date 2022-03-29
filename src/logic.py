import random
from typing import List, Dict
import numpy as np
"""
This file can be a nice home for your Battlesnake's logic and helper functions.
  
We have started this for you, and included some logic to remove your Battlesnake's 'neck'
from the list of possible moves!
"""
    
def get_info() -> dict:
    """
    This controls your Battlesnake appearance and author permissions.
    For customization options, see https://docs.battlesnake.com/references/personalization
     
    TIP: If you open your Battlesnake URL in browser you should see this data.
    """
    return {
        "apiversion": "1",
        "author": "aclalick2",
        "color": "#CCCCFF",
        "head": "earmuffs",
        "tail": "ice-skate",
    }

## A* implementation from https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def findFood(maze, start, tail):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    # Create start and end node
    
    start_node = Node(None, (start['x'], start['y']))
    start_node.g = start_node.h = start_node.f = 0
    tailNode = None

    # Initialize both open and closed list
    open_list = []
    closed_list = []
    mazeSize = (len(maze), len(maze[0]))

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found a goal
        if (current_node.position[0], current_node.position[1]) == (tail['x'], tail['y']):
            tailNode = current_node
        
        if maze[current_node.position[0]][current_node.position[1]] == -1:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Check Neighbors
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (mazeSize[0] - 1) or node_position[0] < 0 or node_position[1] > (mazeSize[1] - 1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] - current_node.g > 0:
                continue

            # Create new node
            child = Node(current_node, node_position)

            if child in closed_list or child in open_list:
                continue
            
            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = 0
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)   
    #None Found Go towards tail
    path = []
    current = tailNode
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1] # Return reversed path
    
def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request
    
    return: A String, the single move to make. One of "up", "down", "left" or "right".
    
    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.
    
    """
    board = data['board']
    my_head = data["you"]["head"]
    
    # Uncomment the lines below to see what this data looks like in your output!
    print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    #print(f"All board data this turn: {data}")
    print(f"My Battlesnakes head this turn is: {my_head}")

    grid = np.zeros((board['width'], board['height']))
    
    for f in board['food']:
        grid[f['x']][f['y']] = -1
    for s in board['snakes']:
        s_body = s['body']
                
        bodyLoc = len(s_body) + 1

        s_head = s_body[0]
        if s_head != my_head and s['length'] >= data['you']['length']:
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
                # Get node position
                node_position = (s_head["x"] + new_position[0], s_head["y"] + new_position[1])
                # Make sure within range
                if node_position[0] > (board['width'] - 1) or node_position[0] < 0 or node_position[1] > (board['height'] - 1) or node_position[1] < 0:
                    continue
                grid[node_position[0]][node_position[1]] = bodyLoc
        
        for b in s_body:
            grid[b['x']][b['y']] = bodyLoc
            bodyLoc -= 1
        
    #print(grid)
    path = findFood(grid, my_head, data['you']['body'][-1])
    print(path)
    firstNode = path[1]
    print(firstNode)

    if firstNode[0] < my_head["x"]:
        move = "left"
    elif firstNode[0] > my_head["x"]:
        move = "right"
    elif firstNode[1] < my_head["y"]:
        move = "down"
    elif firstNode[1] > my_head["y"]:
        move = "up"
    else:
        move = None
    
    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked")

    return move