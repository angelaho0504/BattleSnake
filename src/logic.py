import numpy as np
import threading
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

def _score_food(board, scores):
    grid = np.zeros((board['width'], board['height']))
    
    for f in board['food']:
        grid[f['x']][f['y']] = -1

    print("Food")
    print(grid)
    scores['food'] = grid

def _score_snakes(board, my_head, scores):
    grid = np.zeros((board['width'], board['height']))

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
    
    print("Snakes")
    print(grid)
    scores['snakes'] = grid

def setupGrid(data: dict):
    board = data['board']
    
    scores = {}
    threds = []
    threds.append(threading.Thread(target=_score_food, args=(board, scores)))
    threds.append(threading.Thread(target=_score_snakes, args=(board, data["you"]["head"], scores)))
    #_score_food(board, scores)
    #_score_snakes(board, data["you"]["head"], scores)
    for t in threds:
        t.start()

    for t in threds:
        t.join()
    
    grid = sum(scores.values())
    return grid
    
def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request
    
    return: A String, the single move to make. One of "up", "down", "left" or "right".
    
    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.
    
    """
    # Uncomment the lines below to see what this data looks like in your output!
    print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    #print(f"All board data this turn: {data}")
    my_head = data["you"]["head"]
    #print(f"My Battlesnakes head this turn is: {my_head}")
    
    grid = setupGrid(data)
    print(grid)

    move = None
    curValue = None
    for new_position in [(0, -1, "down"), (0, 1, "up"), (-1, 0, "left"), (1, 0, "right")]: # Adjacent squares
        # Get node position
        pos = (my_head["x"] + new_position[0], my_head["y"] + new_position[1])
        gridValue = grid[pos[0]][pos[1]]
        if curValue == None or gridValue < curValue:
            curValue = gridValue
            move = new_position[2]
    
    print(f"MOVE {data['turn']}: {move} picked\n")

    return move