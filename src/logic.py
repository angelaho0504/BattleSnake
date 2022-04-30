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
        "author": "angela",
        "color": "#CC0000",
        "head": "evil",
        "tail": "flake",
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

def findpath(maze, start, target):
  # Create start and end node
  start_node = Node(None, (start['x'], start['y']))
  start_node.g = start_node.h = start_node.f = 0

  # Initialize both open and closed list
  open_list = []
  closed_list = []
  mazeSize = (len(maze), len(maze[0]))

  open_list.append(start_node)
  
  while len(open_list) > 0 and len(closed_list) < 150:
    current_node = open_list[0]
    current_index = 0
    for index, item in enumerate(open_list):
      if item.f < current_node.f:
          current_node = item
          current_index = index

    # Pop current off open list, add to closed list
    open_list.pop(current_index)
    closed_list.append(current_node)

    if (current_node.position[0], current_node.position[1]) == (target['x'], target['y']):
      path = []
      current = current_node
      while current is not None:
        path.append(current.position)
        current = current.parent
      return path[::-1] # Return reversed path
    
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
          if child == open_node and child.g >= open_node.g:
              continue

      # Add the child to the open list
      open_list.append(child)

def _rem_dir(dir: str, possible_moves: List[str]) -> List[str]:
    if dir in possible_moves:
        if dir == "left":
            possible_moves.remove("left")
        elif dir == "right":
            possible_moves.remove("right")
        elif dir == "down":
            possible_moves.remove("down")
        elif dir == "up":
            possible_moves.remove("up")
            
    return possible_moves   

def _avoid_my_neck(my_body: dict, possible_moves: List[str]) -> List[str]:
    """
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]
    
    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_head = my_body[0]  # The first body coordinate is always the head
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'
    
    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")
    
    return possible_moves    

def choose_move_basic(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request
    
    return: A String, the single move to make. One of "up", "down", "left" or "right".
    
    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.
    
    """
    board = data['board']
    my_snake = data["you"]  # A dictionary describing your snake's position on the board
    my_head = my_snake["head"]  # A dictionary of coordinates
    
    possible_moves = ["up", "down", "left", "right"]
    # Step 0: Don't allow your Battlesnake to move back on it's own neck.
    possible_moves = _avoid_my_neck(my_snake["body"], possible_moves)

    # Step 1 - Don't hit walls.
    # Use information from `data` and `my_head` to not move beyond the game board.
    if my_head["y"] == 0:
        possible_moves = _rem_dir("down", possible_moves)
    elif my_head["y"] == board['height'] - 1:
        possible_moves = _rem_dir("up", possible_moves)
    if my_head["x"] == 0:
        possible_moves = _rem_dir("left", possible_moves)
    elif my_head["x"] == board['width'] - 1:
        possible_moves = _rem_dir("right", possible_moves)
    
    # Step 2 - Don't hit yourself.
    # Use information from `my_body` to avoid moves that would collide with yourself.
    # Step 3 - Don't collide with others.
    # Use information from `data` to prevent your Battlesnake from colliding with others.
    for s in board['snakes']:
        for b in s['body']:
            if abs(b["x"] - my_head["x"]) + abs(b["y"] - my_head["y"]) == 1:
                if b["x"] == my_head["x"] - 1:
                    possible_moves = _rem_dir("left", possible_moves)
                elif b["x"] == my_head["x"] + 1:
                    possible_moves = _rem_dir("right", possible_moves)
                elif b["y"] == my_head["y"] - 1:
                    possible_moves = _rem_dir("down", possible_moves)
                elif b["y"] == my_head["y"] + 1:
                    possible_moves = _rem_dir("up", possible_moves)

    # Step 4 - Find food.
    # Use information in `data` to seek out and find food.
    food = board['food']
    dist = 9999
    nearestFood = None
    for f in food:
        f_dist = abs(f["x"] - my_head["x"]) + abs(f["y"] - my_head["y"])
        if f_dist < dist:
            dist = f_dist
            nearestFood = f

    # Choose a random direction from the remaining possible_moves to move in, and then return that move
    move = random.choice(possible_moves)
    if nearestFood != None:
        if nearestFood["x"] < my_head["x"] and "left" in possible_moves:
            move = "left"
        elif nearestFood["x"] > my_head["x"] and "right" in possible_moves:
            move = "right"
        elif nearestFood["y"] < my_head["y"] and "down" in possible_moves:
            move = "down"
        elif nearestFood["y"] > my_head["y"] and "up" in possible_moves:
            move = "up"        
    
    print(f"MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")
        
    return move

def choose_move(data: dict) -> str:

  board = data['board']
  my_head = data["you"]["head"]
  snakes = data['board']['snakes'];
  my_snake = data['you'];
  
  grid = np.zeros((board['width'], board['height']))

  for f in board['food']:
    grid[f['x']][f['y']] = -1
  for s in board['snakes']:
    s_body = s['body']
                
    bodyLoc = len(s_body)

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
        
  possibleSnakes = []
  for s in snakes:
    if(s['length'] + 1 < my_snake['length']):
      possibleSnakes.append(s)
  
  dist = 9999
  nearestFood = None
  targetSnake = None
  
  for s in possibleSnakes:
    s_dist = abs(s["head"]["x"] - my_head["x"]) + abs(s["head"]["y"] - my_head["y"])
    if s_dist < dist:
      dist = s_dist
      targetSnake = s
  
  if (targetSnake == None):
    # find shortest distance to nearest food
    food = board['food']
    nearestFood = None
    for f in food:
      f_dist = abs(f["x"] - my_head["x"]) + abs(f["y"] - my_head["y"])
      if f_dist < dist:
        dist = f_dist
        nearestFood = f
    path = findpath(grid, my_head, nearestFood)
  else:
    print("Found Snake")
    path = findpath(grid, my_head, targetSnake["head"])

  if path == None or len(path) < 2:
    return choose_move_basic(data)

  firstNode = path[1]
    #print(firstNode)
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
  
  print(f"MOVE {data['turn']}: {move} picked")
  
  return move
    

# wont move away from other snake
# 
  
      