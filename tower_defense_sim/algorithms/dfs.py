import time
import path_step_monitor

def dfs(start: tuple, goal: tuple, grid) -> list:
    """
    Standard DFS search returning a list of coordinates or None.
    Uses a stack-based approach with a visited set.
    """
    visited = set()
    stack = [(start, [start])]
    
    while stack:
        curr, path = stack.pop()
        if curr == goal:
            return path
            
        if curr not in visited:
            visited.add(curr)
            neighbors = grid.get_neighbors(curr[0], curr[1])
            # Process neighbors in normal order (pushed to stack)
            for nxt in neighbors:
                if nxt not in visited:
                    stack.append((nxt, path + [nxt]))
    return None

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Solves pathfinding using DFS and logs step updates for visual feedback in the GUI.
    """
    path_step_monitor.log_step(f"Khởi chạy DFS từ {start} đến {goal}")
    visited = set()
    stack = [(start, [start])]
    
    while stack:
        curr, path = stack.pop()
        if curr in visited:
            continue
            
        visited.add(curr)
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        path_step_monitor.log_step(f"Duyệt DFS: {curr}")
        
        if delay > 0:
            time.sleep(delay)
            
        if curr == goal:
            path_step_monitor.log_step("🎉 DFS đã tìm thấy đích!")
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        neighbors = grid.get_neighbors(curr[0], curr[1])
        for nxt in neighbors:
            if nxt not in visited:
                path_step_monitor.log_node_state(nxt[0], nxt[1], "open")
                stack.append((nxt, path + [nxt]))
                if delay > 0:
                    time.sleep(delay * 0.2)
                    
    path_step_monitor.log_step("DFS: Không tìm thấy đường đi!")
    return None
