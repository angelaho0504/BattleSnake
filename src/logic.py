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
        "author": "elephantwaffle",  # TODO: Your Battlesnake Username
        "color": "#145369",  # TODO: Personalize
        "head": "smart-caterpillar",  # TODO: Personalize
        "tail": "weight",  # TODO: Personalize
    }


def build_board(data: dict):
  board = data["board"]
  snakes = board["snakes"]
  # empty grid
  occ_grid = np.zeros((board["height"], board["width"]))
  for snake in snakes:
    for loc in snake['body']:
      occ_grid[loc["x"], loc["y"]] = 1
  return occ_grid


def food_direction(data: dict) -> set:
  head = data["you"]["head"]
  food = get_nearest_food(data)
  
  head_x, head_y = head["x"], head["y"]
  food_x, food_y = food["x"], food["y"]
  
  x_dir = food_x - head_x
  y_dir = food_y - head_y
  
  dirs = set()
  
  if x_dir > 0:
    dirs.add("right")
  if x_dir < 0:
    dirs.add("left")
  if y_dir > 0: 
   dirs.add("up")
  if y_dir < 0:
    dirs.add("down")
    
  return dirs

  
def get_nearest_food(data: dict) -> dict:
  all_foods = data["board"]["food"]
  closest_food = None
  closest_dist = 100000
  curr_x, curr_y = data["you"]["head"]["x"], data["you"]["head"]["y"]
  for food in all_foods:
    dist = abs(curr_x - food["x"]) + abs(curr_y - food["y"])
    if dist < closest_dist:
      closest_dist = dist
      closest_food = food

  return closest_food

  
# Sample Move Request: https://docs.battlesnake.com/references/api/sample-move-request
def get_direction(data, possible_moves) -> []:
  suggested_moves = []
  hash_scores = {}
  max_score = 0
  arbitrary_heuristic = 10
  if data['you']['length'] >= 10: 
    arbitrary_heuristic = 5
  elif data['you']['length'] >= 15: 
    arbitrary_heuristic = 0
    
  for move in possible_moves:
    score = flood_fill(move, data)
    if score > max_score: max_score = score
    hash_scores[move] = score

  for key, score in hash_scores.items():
    if score == max_score: suggested_moves.append(key)

  for key, score in hash_scores.items():
    if score > max_score - arbitrary_heuristic and score != max_score: suggested_moves.append(key)

  food_moves = food_direction(data)
  if food_moves:
    if sorted(set(suggested_moves).intersection(food_moves) ,key=lambda x:suggested_moves.index(x)):
      return sorted(set(suggested_moves).intersection(food_moves) ,key=lambda x:suggested_moves.index(x))
    else:
      return suggested_moves
  else:
    return suggested_moves


def flood_fill(move: str, data: dict) -> dict:
  board = build_board(data)
  visited = np.array(board)
  head = data["you"]["head"]
  y_max = data['board']['height']
  x_max = data['board']['width']

  for snake in data['board']['snakes']:
    if snake['length'] > data['you']['length']:
      x, y = snake['head']['x'], snake['head']['y']    
      if x+1 < x_max: visited[x+1][y] = 1
      if y+1 < y_max: visited[x][y + 1] = 1
      if 0 <= x-1: visited[x-1][y] = 1
      if 0 <= y-1: visited[x][y-1] = 1

  dir = {"up": (0,1),
         "down": (0,-1),
         "left": (-1,0),
         "right": (1,0)}

  def r_visit(x: int, y: int, acc: int) -> int:
    if visited[x, y] != 1:
      acc += 1
      visited[x, y] = 1
    if x+1 < x_max and not visited[x + 1, y]: acc += r_visit(x + 1, y, 0) 
    if y+1 < y_max and not visited[x, y + 1]: acc += r_visit(x, y + 1, 0)
    if 0 <= x-1 and not visited[x - 1, y]: acc += r_visit(x - 1, y, 0)
    if 0 <= y-1 and not visited[x, y - 1]: acc += r_visit(x, y - 1, 0)
    
    return acc
  
  score = r_visit(head["x"] + dir[move][0], head["y"] + dir[move][1], 0)
  return score

def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request
    return: A String, the single move to make. One of "up", "down", "left" or "right".
    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.
    """
    my_snake = data["you"]      # A dictionary describing your snake's position on the board
    my_head = my_snake["head"]  # A dictionary of coordinates like {"x": 0, "y": 0}
    my_body = my_snake["body"]  # A list of coordinate dictionaries like [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]

    possible_moves = { "up", "down", "left", "right" } 
  
    possible_moves = _avoid_my_neck(my_body, possible_moves)
    possible_moves = avoid_walls(data, possible_moves)
    possible_moves = avoid_myself(my_body, possible_moves)
    possible_moves = avoid_others(my_head, data, possible_moves)
    backup_moves = possible_moves.copy()
    possible_final_moves = avoid_if_small(data, possible_moves)

    possible_final_moves = get_direction(data, possible_final_moves)

    # Choose a random direction from the remaining possible_moves to move in, and then return that move
    move = ""
    if possible_final_moves:
      move = possible_final_moves[0]
    else:
      move = random.choice(list(backup_moves))

    return move

def safe_possible_head_moves(head: dict) -> []:
  x, y = head['x'], head['y']

  return [{"x": x+1, "y": y}, {"x": x-1, "y": y}, {"x": x, "y": y+1}, {"x": x, "y": y-1}]

def avoid_if_small(data: dict, possible_moves: set) -> set:
  other_snakes = data['board']['snakes']
  head = data['you']['head']
  
  for snake in other_snakes:
    if snake['name'] == data['you']['name']: continue
    if snake['length'] < data['you']['length']: continue
    flat_list = safe_possible_head_moves(snake['head'])

      
    for direction in list(possible_moves):
      if direction == 'up':
        if {'x': head['x'], 'y': head['y'] + 1} in flat_list:
          possible_moves.discard('up')
      elif direction == 'down':
        if {'x': head['x'], 'y': head['y'] - 1} in flat_list:
          possible_moves.discard('down')
      elif direction == 'left':
        if {'x': head['x'] - 1, 'y': head['y']} in flat_list:
          possible_moves.discard('left')
      elif direction == 'right':
        if {'x': head['x'] + 1, 'y': head['y']} in flat_list:
          possible_moves.discard('right')

  return possible_moves

def _avoid_my_neck(my_body: dict, possible_moves: set) -> set:
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
        possible_moves.discard("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.discard("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.discard("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.discard("up")

    return possible_moves


def avoid_walls(data: dict, possible_moves: set) -> set:
  y_max = data['board']['height']
  x_max = data['board']['width']
        
  my_head = data['you']['head']

  # Bottom left is 0,0
  # Top right is x_max, y_max
  if my_head['x'] == 0:
    possible_moves.discard('left')
  if my_head['y'] == 0:
    possible_moves.discard('down')
  if my_head['x'] == x_max - 1:  
    possible_moves.discard('right')
  if my_head['y'] == y_max - 1:      
    possible_moves.discard('up')

  return possible_moves

def avoid_myself(my_body: dict, possible_moves: set) -> set:
  head = my_body[0]

  for direction in list(possible_moves):
    if direction == 'up':
      if {'x': head['x'], 'y': head['y'] + 1} in my_body:
        possible_moves.discard('up')
    elif direction == 'down':
      if {'x': head['x'], 'y': head['y'] - 1} in my_body:
        possible_moves.discard('down')
    elif direction == 'left':
      if {'x': head['x'] - 1, 'y': head['y']} in my_body:
        possible_moves.discard('left')
    elif direction == 'right':
      if {'x': head['x'] + 1, 'y': head['y']} in my_body:
        possible_moves.discard('right')
  return possible_moves

def avoid_others(head: dict, others: dict, possible_moves:set) -> set:
  bodies = []
  for snakes in others['board']['snakes']:
    bodies.append(snakes['body'][:-1])

  flat_list = [item for sublist in bodies for item in sublist]

  for direction in list(possible_moves):
    if direction == 'up':
      if {'x': head['x'], 'y': head['y'] + 1} in flat_list:
        possible_moves.discard('up')
    elif direction == 'down':
      if {'x': head['x'], 'y': head['y'] - 1} in flat_list:
        possible_moves.discard('down')
    elif direction == 'left':
      if {'x': head['x'] - 1, 'y': head['y']} in flat_list:
        possible_moves.discard('left')
    elif direction == 'right':
      if {'x': head['x'] + 1, 'y': head['y']} in flat_list:
        possible_moves.discard('right')
  return possible_moves
