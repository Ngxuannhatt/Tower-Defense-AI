import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy IDA* từ {start} đến {goal}")
    
    def h(pos):
        # Manhattan distance to goal
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
    def search(path, g, threshold, visited):
        curr = path[-1]
        f = g + h(curr)
        
        # Log node expansion
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        path_step_monitor.log_step(f"Xét node: {curr}, g={g}, h={h(curr)}, f={f} (Ngưỡng: {threshold})")
        if delay > 0:
            time.sleep(delay)
            
        if f > threshold:
            return f, None
            
        if curr == goal:
            return f, list(path)
            
        min_val = float('inf')
        neighbors = grid.get_neighbors(curr[0], curr[1])
        # Sort neighbors by heuristic distance to search promising nodes first
        neighbors.sort(key=lambda p: h(p))
        
        for neighbor in neighbors:
            if neighbor not in path:
                # Prune if we reached this neighbor with a worse or equal cost in this iteration
                if neighbor in visited and g + 1.0 >= visited[neighbor]:
                    continue
                visited[neighbor] = g + 1.0
                
                path.append(neighbor)
                path_step_monitor.log_node_state(neighbor[0], neighbor[1], "open")
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
                t, found_path = search(path, g + 1.0, threshold, visited)
                if found_path is not None:
                    return t, found_path
                if t < min_val:
                    min_val = t
                path.pop()
                path_step_monitor.log_node_state(neighbor[0], neighbor[1], "reset")
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
        return min_val, None

    threshold = h(start)
    path = [start]
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    max_iterations = 200 # safety limit to prevent freezing
    for iteration in range(max_iterations):
        path_step_monitor.log_step(f"--- Lượt lặp mới với ngưỡng f-limit = {threshold} ---")
        visited = {start: 0.0}
        t, found_path = search(path, 0.0, threshold, visited)
        if found_path is not None:
            path_step_monitor.log_step(f"IDA* tìm thấy đường đi: {found_path}")
            # Mark final path nodes in GUI
            for px, py in found_path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return found_path
        if t == float('inf'):
            path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
            return None
        threshold = t
        
    path_step_monitor.log_step("Đạt giới hạn số lượt lặp tối đa của IDA*!")
    return None