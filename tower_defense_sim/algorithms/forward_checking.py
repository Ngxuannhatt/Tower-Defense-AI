import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy Backtracking với Forward Checking từ {start}")
    
    assignment = []
    step_count = 0
    max_steps = 2000
    
    def is_connected_to_goal(node, visited_set):
        # Quick BFS to check if goal is reachable from node using only unvisited cells
        if node == goal:
            return True
        queue = [node]
        seen = {node}
        while queue:
            curr = queue.pop(0)
            if curr == goal:
                return True
            neighbors = grid.get_neighbors(curr[0], curr[1])
            for nxt in neighbors:
                if nxt not in visited_set and nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return False

    def backtrack(curr):
        nonlocal step_count
        step_count += 1
        if step_count > max_steps:
            return False
            
        if curr == goal:
            assignment.append(curr)
            path_step_monitor.log_step(f"🎉 Đã tìm thấy đích tại {curr}!")
            return True
            
        assignment.append(curr)
        path_step_monitor.log_node_state(curr[0], curr[1], "open")
        path_step_monitor.log_step(f"Gán giá trị: {curr}")
        if delay > 0:
            time.sleep(delay)
            
        neighbors = grid.get_neighbors(curr[0], curr[1])
        # Sort neighbors by heuristic distance to goal to prioritize better directions
        neighbors.sort(key=lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1]))
        
        visited_set = set(assignment)
        
        for neighbor in neighbors:
            if neighbor not in visited_set:
                # --- FORWARD CHECKING STEP ---
                # Check if neighbor has a valid connection to goal without using currently assigned nodes
                path_step_monitor.log_step(f"  🔍 Forward Checking: Kiểm tra xem từ {neighbor} có tới được {goal} không...")
                if is_connected_to_goal(neighbor, visited_set):
                    path_step_monitor.log_step(f"  ✅ FC Thành công: Từ {neighbor} vẫn còn đường đi tới đích.")
                    # Recurse
                    if backtrack(neighbor):
                        return True
                else:
                    path_step_monitor.log_step(f"  ❌ FC Thất bại: Cắt tỉa (Prune) {neighbor} vì không thể đi tới đích từ đây.")
                    path_step_monitor.log_node_state(neighbor[0], neighbor[1], "closed")
                    if delay > 0:
                        time.sleep(delay * 0.5)
                    path_step_monitor.log_node_state(neighbor[0], neighbor[1], "reset")
                    
        assignment.pop()
        path_step_monitor.log_node_state(curr[0], curr[1], "reset")
        path_step_monitor.log_step(f"↩️ Quay lui từ: {curr}")
        if delay > 0:
            time.sleep(delay)
        return False

    if backtrack(start):
        for px, py in assignment:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return assignment
        
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None