import random
from typing import List, Dict
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
        "author": "aclalick",
        "color": "#CCCCFF",
        "head": "earmuffs",
        "tail": "ice-skate",
    }

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
    my_snake = data["you"]  # A dictionary describing your snake's position on the board
    my_head = my_snake["head"]  # A dictionary of coordinates
    
    # Uncomment the lines below to see what this data looks like in your output!
    #print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    #print(f"All board data this turn: {data}")
    #print(f"My Battlesnake this turn is: {my_snake}")
    #print(f"My Battlesnakes head this turn is: {my_head}")
    #print(f"My Battlesnakes body this turn is: {my_body}")
    
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

    if nearestFood["x"] < my_head["x"] and "left" in possible_moves:
        move = "left"
    elif nearestFood["x"] > my_head["x"] and "right" in possible_moves:
        move = "right"
    elif nearestFood["y"] < my_head["y"] and "down" in possible_moves:
        move = "down"
    elif nearestFood["y"] > my_head["y"] and "up" in possible_moves:
        move = "up"
    else:
        # Choose a random direction from the remaining possible_moves to move in, and then return that move
        move = random.choice(possible_moves)
    
    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")
        
    return move
    
    
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
