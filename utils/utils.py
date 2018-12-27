import numpy as np


def choice(l):
    """
    Returns a random element from the list
    """
    item = np.random.randint(0, len(l))
    return l[item]


def possible_directions(limit_board, position):
    """
    Gives the possible moves allowed for the agent
    Args:
        limit_board: limits of the board
        position: position of the agent
    Returns: list of possible positions
    """
    lim_x, lim_y = limit_board
    x, y = position
    possible_direction = []
    if x > 0:
        possible_direction.append((x - 1, y))
        if y > 0:
            possible_direction.append((x - 1, y - 1))
        if y < lim_y - 1:
            possible_direction.append((x - 1, y + 1))
    if y > 0:
        possible_direction.append((x, y - 1))
    if x < lim_x - 1:
        possible_direction.append((x + 1, y))
        if y > 0:
            possible_direction.append((x + 1, y - 1))
        if y < lim_y - 1:
            possible_direction.append((x + 1, y + 1))
    if y < lim_y - 1:
        possible_direction.append((x, y + 1))
    return possible_direction


def get_distance_between(limit_board, position_1, position_2):
    """
    Returns the distance between the two positions
    Args:
        limit_board: limits of the board
        position_1: position 1
        position_2: position 2
    """
    if position_1 in possible_directions(limit_board, position_2):
        return 1
    x, y = position_1
    x_2, y_2 = position_2
    x_new, y_new = position_1
    if x < x_2:
        if y < y_2:
            x_new, y_new = x+1, y+1
        elif y == y_2:
            x_new = x+1
        else:
            x_new, y_new = x+1, y-1
    elif x == x_2:
        if y < y_2:
            y_new = y+1
        elif y > y_2:
            y_new = y-1
    else:
        if y < y_2:
            x_new, y_new = x-1, y+1
        elif y == y_2:
            x_new = x-1
        else:
            x_new, y_new = x-1, y-1
    return 1 + get_distance_between(limit_board, (x_new, y_new), position_2)


def distance_enemies_around(agent, agents, max_distance=None):
    """
    Returns the distance to all enemies around one agent
    Args:
        agent: reference agent
        agents: other agents
        max_distance: max distance. Default agent's field of view
    Returns: distances
    """
    max_distance = agent.view_radius if max_distance is None else max_distance
    enemies_around = []
    for other_agent in agents:
        if ((agent.type == "target" and other_agent.type == 'officer') or
                (agent.type == "officer" and other_agent.type == 'target')):
            dist_agents = get_distance_between(agent.limit_board, agent.position, other_agent.position)
            if dist_agents <= max_distance:
                enemies_around.append(dist_agents)
    return enemies_around
