import time
import path_step_monitor

def steepest_ascent_hill_climbing(start: tuple, goal: tuple, grid) -> list:
    """
    Steepest Ascent Hill Climbing with memory (visited_cells) to bypass local maxima.
    Returns: a path as a list of coordinates, or None if goal is not reachable.
    """
    visited_cells = {start}
    path = [start]
    current = start
    
    max_steps = 1000
    steps = 0
    
    while current != goal and steps < max_steps:
        steps += 1
        x, y = current
        
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny) and (nx, ny) not in visited_cells:
                neighbors.append((nx, ny))
                
        if not neighbors:
            break
            
        # Find neighbor with minimal Manhattan distance to goal
        best_neighbor = min(neighbors, key=lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1]))
        
        current = best_neighbor
        visited_cells.add(current)
        path.append(current)
        
    if path[-1] == goal:
        return path
    return None

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Solves pathfinding using Steepest Ascent Hill Climbing with step logging for GUI visualization.
    """
    path_step_monitor.log_step(f"Khởi chạy Steepest Ascent Hill Climbing từ {start} đến {goal}")
    
    visited_cells = {start}
    path = [start]
    current = start
    
    max_steps = 1000
    steps = 0
    
    while current != goal and steps < max_steps:
        steps += 1
        x, y = current
        
        path_step_monitor.log_node_state(x, y, "closed")
        if delay > 0:
            time.sleep(delay)
            
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny) and (nx, ny) not in visited_cells:
                neighbors.append((nx, ny))
                
        if not neighbors:
            path_step_monitor.log_step(f"Cực đại cục bộ không còn lối đi lân cận trống tại {current}!")
            break
            
        # Sort neighbors by Manhattan distance to Goal
        neighbors.sort(key=lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1]))
        best_neighbor = neighbors[0]
        
        curr_dist = abs(current[0] - goal[0]) + abs(current[1] - goal[1])
        best_dist = abs(best_neighbor[0] - goal[0]) + abs(best_neighbor[1] - goal[1])
        
        if best_dist >= curr_dist:
            path_step_monitor.log_step(f"Rơi vào cực đại cục bộ tại {current} (d={curr_dist}). Đi tiếp ô lân cận tốt nhất tiếp theo {best_neighbor} (d={best_dist}).")
        else:
            path_step_monitor.log_step(f"Đi tới ô tốt hơn: {best_neighbor} (d={best_dist} < {curr_dist})")
            
        current = best_neighbor
        visited_cells.add(current)
        path.append(current)
        path_step_monitor.log_node_state(current[0], current[1], "open")
        
    if path[-1] == goal:
        path_step_monitor.log_step(f"Hill Climbing đã tìm thấy đích! Độ dài: {len(path)}")
        for px, py in path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return path
        
    path_step_monitor.log_step("Không tìm thấy đường đi tới đích!")
    return None
