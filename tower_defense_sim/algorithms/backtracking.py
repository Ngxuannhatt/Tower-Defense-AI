import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy Backtracking CSP từ {start}")
    
    assignment = []
    step_count = 0
    max_steps = 2000
    
    def recursive_backtracking(current_node):
        nonlocal step_count
        step_count += 1
        if step_count > max_steps:
            return False
            
        if current_node == goal:
            assignment.append(current_node)
            path_step_monitor.log_step(f"🎉 Đã tìm thấy đích tại {current_node}!")
            return True
            
        assignment.append(current_node)
        path_step_monitor.log_node_state(current_node[0], current_node[1], "open")
        path_step_monitor.log_step(f"Đi tới: {current_node}")
        
        if delay > 0:
            time.sleep(delay)
            
        neighbors = grid.get_neighbors(current_node[0], current_node[1])
        neighbors.sort(key=lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1]))
        
        for next_node in neighbors:
            if next_node not in assignment:
                if recursive_backtracking(next_node):
                    return True
                    
        assignment.pop()
        path_step_monitor.log_node_state(current_node[0], current_node[1], "reset")
        path_step_monitor.log_step(f"↩️ Quay lui từ: {current_node}")
        
        if delay > 0:
            time.sleep(delay)
        return False

    if recursive_backtracking(start):
        for px, py in assignment:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return assignment
        
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None


def solve_all_paths(start, goal, grid, max_steps=50000):
    all_paths = []
    step_count = 0
    
    def dfs(curr, path_track):
        nonlocal step_count
        if len(all_paths) >= 50 or step_count > max_steps:
            return
            
        step_count += 1
        
        if curr == goal:
            all_paths.append(list(path_track))
            return
            
        neighbors = grid.get_neighbors(curr[0], curr[1])
        for nxt in neighbors:
            if nxt not in path_track:
                path_track.append(nxt)
                dfs(nxt, path_track)
                path_track.pop()
                if len(all_paths) >= 50 or step_count > max_steps:
                    break

    dfs(start, [start])
    if step_count > max_steps:
        path_step_monitor.log_step("⚠️ Quá trình quét dừng lại sớm vì vượt quá giới hạn số bước an toàn.")
    return all_paths
