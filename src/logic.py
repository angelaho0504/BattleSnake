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

def _score_center(board, health, scores):
    grid = np.zeros((board['width'], board['height']))
    center = ((board['width'] - 1) / 2.0, (board['height'] - 1) / 2.0)
    for x in range(board['width']):
        for y in range(board['height']):
            grid[x][y] = (abs(x - center[0]) / board['width'] + abs(y - center[1]) / board['height'])
    
    healthLevel = (health / 100)
    grid *= healthLevel / 4
    #print("Center")
    #print(grid)
    scores['center'] = grid

def _score_food(board, health, my_len, scores):
    grid = np.ones((board['width'], board['height'])) * (board['width'] + board['height'])
    
    for x in range(board['width']):
        for y in range(board['height']):
            for f in board['food']:
                dist = abs(x - f['x']) + abs(y - f['y'])
                grid[x][y] = min(grid[x][y], dist)

    # focus eating when hungry
    hunger = (1 / health)
    # focus eating when smaller than other snakes
    longest = 0
    for s in board['snakes'][1:]:
        longest = max(longest, s['length'])
    if my_len <= longest:
        hunger *= 3 + (1 * (longest - my_len))
    grid *= hunger
    #print("Food")
    #print(grid)
    scores['food'] = grid

#[(0,-1,1), (0,1,1), (-1,0,1), (1,0,1), (1,1,2), (1,-1,2), (-1,1,2), (-1,-1,2),
#(0,-2,2), (0,2,2), (-2,0,2), (2,0,2), (2,2,4), (2,-2,4), (-2,2,4), (-2,-2,4),
#(1,-2,3), (1,2,3), (-1,-2,3), (-1,2,3), (-2,1,3), (2,1,3), (-2,-1,3), (2,-1,3)]
def _score_snakes(board, my_head, my_len, scores):
    grid = np.zeros((board['width'], board['height']))

    for s in board['snakes']:
        s_body = s['body']

        s_head = s_body[0]
        if s_head != my_head:
            if s['length'] >= my_len: # Avoid head to head with larger snakes
                for new_position in [(0,-1,1/1), (0,1,1/1), (-1,0,1/1), (1,0,1/1), (1,1,1/2), (1,-1,1/2), (-1,1,1/2), (-1,-1,1/2),(0,-2,1/2), (0,2,1/2), 
                                     (-2,0,1/2), (2,0,1/2), (2,2,1/4), (2,-2,1/4), (-2,2,1/4), (-2,-2,1/4),(1,-2,1/3), (1,2,1/3), (-1,-2,1/3), (-1,2,1/3), 
                                     (-2,1,1/3), (2,1,1/3), (-2,-1,1/3), (2,-1,1/3)]: # Adjacent squares
                    node_position = (s_head["x"] + new_position[0], s_head["y"] + new_position[1])
                    if node_position[0] > (board['width'] - 1) or node_position[0] < 0 or node_position[1] > (board['height'] - 1) or node_position[1] < 0:
                        continue
                    grid[node_position[0]][node_position[1]] += new_position[2]
            else: # Kill smaller snakes with head to head
                for x in range(board['width'] - 1):
                    for y in range(board['height'] - 1):
                        if x > (board['width'] - 1) or y < 0 or x > (board['height'] - 1) or y < 0:
                            continue
                        dist = abs(x - s_head['x']) + abs(y - s_head['y'])
                        grid[x][y] -= 1 / dist
        
        for b in s_body:
            grid[b['x']][b['y']] = 10

        # set tail value, 1 if not next to food otherwise 2
        tailVal = 1
        for new_position in [(0,-1), (0,1), (-1,0), (1,0)]: # Adjacent squares
            node_position = (s_head["x"] + new_position[0], s_head["y"] + new_position[1])
            for f in board['food']:
                if f['x'] == node_position[0] and f['y'] == node_position[1]:
                    tailVal = 2
        s_tail = s_body[-1]
        grid[s_tail['x']][s_tail['y']] = tailVal

    #print("Snakes", my_head)
    #print(grid)
    scores['snakes'] = grid

# https://python.plainenglish.io/a-python-example-of-the-flood-fill-algorithm-bced7f96f569
def _flood_fill(grid, x, y, start_pos):
    # firstly, make sure the x and y are inbounds
    if x > (len(grid) - 1) or x < 0 or y > (len(grid[0]) - 1) or y < 0:
        return 0

    # check if already visited
    if grid[x][y] == -1:
        return 0

    # check if open when snake gets to it
    if grid[x][y] - (abs(x - start_pos[0]) + abs(y - start_pos[1])) > 0:
        return 0

    grid[x][y] = -1
    # attempt to fill the neighboring positions
    count = 1
    count += _flood_fill(grid, x+1, y, start_pos)
    count += _flood_fill(grid, x-1, y, start_pos)
    count += _flood_fill(grid, x, y+1, start_pos)
    count += _flood_fill(grid, x, y-1, start_pos)
    return count

def _score_dir_room(board, my_head, scores):
    grid = np.zeros((board['width'], board['height']))
    obstacles = np.zeros((board['width'], board['height']))
    for s in board['snakes']:
        s_body = s['body']
        bodyLoc = len(s_body)        
        for b in s_body:
            obstacles[b['x']][b['y']] = bodyLoc
            bodyLoc -= 1
    
    for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
        # Get node position
        pos = (my_head["x"] + new_position[0], my_head["y"] + new_position[1])
        if pos[0] > (board['width'] - 1) or pos[0] < 0 or pos[1] > (board['height'] - 1) or pos[1] < 0:
            continue
        space = _flood_fill(obstacles.copy(), pos[0], pos[1], pos)
        #print(space)
        grid[pos[0]][pos[1]] = 10 / (space + 1)
    #print("Room", my_head)
    #print(grid)
    scores['room'] = grid

def setupGrid(data: dict):
    board = data['board']
    my_snake = data['you']
    scores = {}
    threds = []
    threds.append(threading.Thread(target=_score_center, args=(board, my_snake['health'], scores)))
    threds.append(threading.Thread(target=_score_food, args=(board, my_snake['health'], my_snake['length'], scores)))
    threds.append(threading.Thread(target=_score_snakes, args=(board, my_snake["head"], my_snake['length'], scores)))
    threds.append(threading.Thread(target=_score_dir_room, args=(board, my_snake["head"], scores)))
    for t in threds:
        t.start()

    for t in threds:
        t.join()

    #print(scores)
    grid = sum(scores.values())
    #print("Grid", my_snake['head'])
    #print(grid)
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
    np.set_printoptions(formatter={'float': '{: 0.2f}'.format})
    # Uncomment the lines below to see what this data looks like in your output!
    #print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    #print(f"All board data this turn: {data}")
    my_head = data["you"]["head"]
    board = data['board']
    print(f"My Battlesnakes head this turn is: {my_head}")
    
    grid = setupGrid(data)

    move = None
    curValue = None
    for new_position in [(0, -1, "down"), (0, 1, "up"), (-1, 0, "left"), (1, 0, "right")]: # Adjacent squares
        # Get node position
        pos = (my_head["x"] + new_position[0], my_head["y"] + new_position[1])
        if pos[0] > (board['width'] - 1) or pos[0] < 0 or pos[1] > (board['height'] - 1) or pos[1] < 0:
            continue
        gridValue = grid[pos[0]][pos[1]]
        if curValue == None or gridValue < curValue:
            curValue = gridValue
            move = new_position[2]
    
    print(f"MOVE {data['turn']}: {move} picked")

    return move