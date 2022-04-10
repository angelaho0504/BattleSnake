import numpy as np
import threading
"""
This file can be a nice home for your Battlesnake's logic and helper functions.
  
We have started this for you, and included some logic to remove your Battlesnake's 'neck'
from the list of possible moves!
"""

""" TODO
Fix fill to account for enemy snake cutting off
Change food value when enemy snake is closer than us (to target reachable food)
"""

def get_info() -> dict:
    """
    This controls your Battlesnake appearance and author permissions.
    For customization options, see https://docs.battlesnake.com/references/personalization
     
    TIP: If you open your Battlesnake URL in browser you should see this data.
    """
    return {
        "apiversion": "1",
        "author": "aclalick3",
        "color": "#CCCCFF",
        "head": "earmuffs",
        "tail": "ice-skate",
    }

#[(0,-1,1), (0,1,1), (-1,0,1), (1,0,1), (1,1,2), (1,-1,2), (-1,1,2), (-1,-1,2),
#(0,-2,2), (0,2,2), (-2,0,2), (2,0,2), (2,2,4), (2,-2,4), (-2,2,4), (-2,-2,4),
#(1,-2,3), (1,2,3), (-1,-2,3), (-1,2,3), (-2,1,3), (2,1,3), (-2,-1,3), (2,-1,3)]

MAX_HEALTH = 100 # max health of a snake
HUNGER_COST_SMALLER = 3 # how much to increase hunger when smaller
LENGTH_DIFF = 2 # how much larger snake wants to be than other snakes to attack
HUNGER_COST_LENGTH_DIFF = HUNGER_COST_SMALLER / LENGTH_DIFF # cost of each segment larger, calculated to never give negative
SEARCH_DIST = 20 # how far to search when calculating available movement room

def _score_snakes2(board, my_snake):
    gridHead = np.zeros((board['width'], board['height']))
    gridCenter = np.zeros((board['width'], board['height']))

    my_head = my_snake['head']
    center = ((board['width'] - 1) / 2.0, (board['height'] - 1) / 2.0)
    for s in board['snakes']:
        #s_body = s['body']
        s_head = s['head']

        if s_head != my_head:
            # Avoid head to head with larger snakes, Kill smaller snakes with head to head
            lengthDiff = s['length'] - my_snake['length'] # positive when other snake larger
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
                # Get node position
                pos = (my_head['x'] + new_position[0], my_head['y'] + new_position[1])
                if pos[0] > (len(gridHead) - 1) or pos[0] < 0 or pos[1] > (len(gridHead[0]) - 1) or pos[1] < 0:
                    continue
                dist = abs(pos[0] - s_head['x']) + abs(pos[1] - s_head['y'])
                gridHead[pos[0]][pos[1]] += lengthDiff / dist # Run from bigger, go towards smaller
                
                # Prefer a central position over snakes
                myDistToCenter = abs(pos[0] - center[0]) / board['width'] + abs(pos[1] - center[1]) / board['height']
                sDistToCenter = abs(s_head['x'] - center[0]) / board['width'] + abs(s_head['y'] - center[1]) / board['height']
                if myDistToCenter >= sDistToCenter and lengthDiff < 0:
                    gridCenter[pos[0]][pos[1]] += lengthDiff / myDistToCenter
                else:
                    gridCenter[pos[0]][pos[1]] += lengthDiff * myDistToCenter
                
    return gridHead, gridCenter

# https://python.plainenglish.io/a-python-example-of-the-flood-fill-algorithm-bced7f96f569
def _flood_fill2(grid, curPos, prevPos, dist, my_body):
    # firstly, make sure the x and y are inbounds
    if curPos[0] > (len(grid) - 1) or curPos[0] < 0 or curPos[1] > (len(grid[0]) - 1) or curPos[1] < 0:
        return 0

    dist += 1
    # check if open when snake gets to it
    occupation = grid[curPos[0]][curPos[1]] - dist
    if occupation > 0:
        return 0
        
    # check if max length
    if dist >= SEARCH_DIST:
        return -SEARCH_DIST

    # append curPos and update obstacles
    if grid[curPos[0]][curPos[1]] == -1:
        for v in my_body:
            grid[v[0]][v[1]] += 1
    my_body.append(curPos)
    grid[curPos[0]][curPos[1]] = grid[prevPos[0]][prevPos[1]] + 1

    # attempt to fill the neighboring positions
    for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
        # Get node position
        pos = (curPos[0] + new_position[0], curPos[1] + new_position[1])
        childSpace = _flood_fill2(grid.copy(), pos, curPos, dist, my_body.copy())
        dist = max(dist, childSpace)
        if childSpace == -SEARCH_DIST:
            return -SEARCH_DIST
    #if occupation > 0:
    #    return dist / 2
    return dist

def longestRoom(board, my_snake):
    my_head = my_snake['head']
    obstacles = np.zeros((board['width'], board['height']))
    for s in board['snakes']:
        s_body = s['body']
        bodyLoc = s['length']
        if s['head'] != my_snake['head']:
            for f in board['food']:
                if abs(f['x'] - s['head']['x']) + abs(f['y'] - s['head']['y']) == 1:
                    bodyLoc += 1
                    continue
        for b in s_body:
            obstacles[b['x']][b['y']] += bodyLoc
            bodyLoc -= 1
            
    for f in board['food']:
        obstacles[f['x']][f['y']] = -1

    bodPos = []
    for bp in my_snake['body']:
        bodPos.append((bp['x'], bp['y']))
    
    grid = np.zeros((board['width'], board['height']))
    for new_position in [(0, -1, "down"), (0, 1, "up"), (-1, 0, "left"), (1, 0, "right")]: # Adjacent squares
        # Get node position
        pos = (my_head["x"] + new_position[0], my_head["y"] + new_position[1])
        if pos[0] > (board['width'] - 1) or pos[0] < 0 or pos[1] > (board['height'] - 1) or pos[1] < 0:
            continue
        space = _flood_fill2(obstacles.copy(), pos, (my_head['x'], my_head['y']), 0, bodPos.copy())
        print(new_position[2], "space:", space)
        grid[pos[0]][pos[1]] = SEARCH_DIST / (space + .01)
    return grid

def towards_food(board, my_snake):
    grid = np.zeros((board['width'], board['height']))
    for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
        # Get node position
        x = my_snake['head']["x"] + new_position[0]
        y = my_snake['head']["y"] + new_position[1]
        if x > (board['width'] - 1) or x < 0 or y > (board['height'] - 1) or y < 0:
            continue
        
        # Go Towards Food
        closestFoodDist = board['width'] + board['height'] + 1
        for f in board['food']:
            dist = abs(x - f['x']) + abs(y - f['y'])
            if dist < closestFoodDist:
                closestFoodDist = dist
        grid[x][y] += closestFoodDist
    return grid

def get_hunger(board, my_snake):
    # focus eating when hungry
    hunger = MAX_HEALTH / my_snake['health']
    # focus eating when smaller than other snakes
    longest = 0
    for s in board['snakes'][1:]:
        longest = max(longest, s['length'])
    if my_snake['length'] <= longest + LENGTH_DIFF:
        hunger *= HUNGER_COST_SMALLER + (HUNGER_COST_LENGTH_DIFF * (longest - my_snake['length']))

    return hunger

def print_near_snake(grid, my_head):
    for new_position in [(0, -1, "down"), (0, 1, "up"), (-1, 0, "left"), (1, 0, "right")]: # Adjacent squares
        # Get node position
        pos = (my_head["x"] + new_position[0], my_head["y"] + new_position[1])
        if pos[0] > (len(grid) - 1) or pos[0] < 0 or pos[1] > (len(grid[0]) - 1) or pos[1] < 0:
            continue
        print(new_position[2], "{:.3f}".format(grid[pos[0]][pos[1]]), end = ', ')
    print()

def setupGrid(data: dict):
    board = data['board']
    my_snake = data['you']

    towards_food_grid = towards_food(board, my_snake)
    longestRoom_grid = longestRoom(board, my_snake)
    snakes_head_grid, snakes_center_grid = _score_snakes2(board, my_snake)

    weights = {"towards_food_grid": get_hunger(board, my_snake),
              "longestRoom_grid": 10,
              "snakes_head_grid": 20,
              "snakes_center_grid": 10,}
    print("towards_food_grid:")
    print_near_snake(weights['towards_food_grid'] * towards_food_grid, my_snake['head'])
    print("longestRoom_grid:")
    print_near_snake(weights['longestRoom_grid'] * longestRoom_grid, my_snake['head'])
    print("snakes_head_grid:")
    print_near_snake(weights['snakes_head_grid'] * snakes_head_grid, my_snake['head'])
    print("snakes_center_grid:")
    print_near_snake(weights['snakes_center_grid'] * snakes_center_grid, my_snake['head'])
    
    grid = np.zeros((board['width'], board['height']))
    grid += weights['towards_food_grid'] * towards_food_grid
    grid += weights['longestRoom_grid'] * longestRoom_grid
    grid += weights['snakes_head_grid'] * snakes_head_grid
    grid += weights['snakes_center_grid'] * snakes_center_grid
    print("Final Grid:")
    print_near_snake(grid, my_snake['head'])
    #print(np.array(grid)[my_snake['head']['x']-1:my_snake['head']['x']+1+1, my_snake['head']['y']-1:my_snake['head']['y']+1+1])
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
    print(f"My Battlesnakes head this turn: {data['turn']} is: {my_head}")
    
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
    
    print(f"MOVE {data['turn']}: {move} picked\n")

    return move