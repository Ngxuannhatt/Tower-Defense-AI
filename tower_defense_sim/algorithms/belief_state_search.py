from collections import deque
import time
import path_step_monitor

def belief_state_search(possible_starts: list, goal: tuple, grid) -> list:
    """
    Solves belief state search using BFS.
    possible_starts: list of tuples [(x, y), ...]
    goal: tuple (x, y)
    grid: MapManager object
    
    Returns: list of actions, e.g., ['U', 'D', 'L', 'R']
    """
    initial_state = frozenset(possible_starts)
    queue = deque([(initial_state, [])])
    visited = {initial_state}
    
    # 4 directions
    actions = {
        'U': (0, -1),
        'D': (0, 1),
        'L': (-1, 0),
        'R': (1, 0)
    }
    
    max_states = 10000
    state_count = 0
    
    while queue and state_count < max_states:
        state_count += 1
        current_state, path_actions = queue.popleft()
        
        # Win condition: all possible locations have converged to the goal
        if current_state == frozenset([goal]):
            return path_actions
            
        for act, (dx, dy) in actions.items():
            new_coords = []
            for px, py in current_state:
                if (px, py) == goal:
                    # Freeze at goal: once it reaches goal, it doesn't move
                    new_coords.append(goal)
                else:
                    nx, ny = px + dx, py + dy
                    if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                        new_coords.append((nx, ny))
                    else:
                        # Stand still on wall/tower hit
                        new_coords.append((px, py))
                        
            next_state = frozenset(new_coords)
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path_actions + [act]))
                
    return []

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Wrapper for pathfinder compatibility. Returns list of coordinate tuples.
    """
    path_step_monitor.log_step(f"Khởi chạy Belief State Search từ {start} đến {goal}")
    
    # By default, we solve for the active start node.
    possible_starts = [start]
    
    actions_list = belief_state_search(possible_starts, goal, grid)
    
    if not actions_list:
        path_step_monitor.log_step("Không tìm thấy chuỗi hành động niềm tin mù!")
        return None
        
    path_step_monitor.log_step(f"Belief State Search tìm thấy chuỗi hành động: {actions_list}")
    
    # Trace action path from start coordinate for GUI visualization
    path = [start]
    curr = start
    for act in actions_list:
        dx, dy = 0, 0
        if act == 'U': dy = -1
        elif act == 'D': dy = 1
        elif act == 'L': dx = -1
        elif act == 'R': dx = 1
        
        nx, ny = curr[0] + dx, curr[1] + dy
        if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
            curr = (nx, ny)
        # We append to path even if standing still to visualize the movements correctly
        path.append(curr)
        
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        if delay > 0:
            time.sleep(delay * 0.1)
            
    # Mark path coordinates in GUI
    for px, py in path:
        if (px, py) != start and (px, py) != goal:
            path_step_monitor.log_node_state(px, py, "path")
            
    return path
