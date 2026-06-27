import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    k = 4 # beam size
    path_step_monitor.log_step(f"Khởi chạy Local Beam Search (k={k}) từ {start} đến {goal}")
    
    def h(pos):
        # Manhattan distance to goal
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
    # The beam stores tuples of (heuristic_value, path_list)
    beam = [(h(start), [start])]
    
    max_steps = 150
    for step in range(max_steps):
        path_step_monitor.log_step(f"--- Bước {step+1}: Kích thước chùm hạt hiện tại = {len(beam)} ---")
        
        # Check if any path in the beam has reached the goal
        for _, path in beam:
            if path[-1] == goal:
                path_step_monitor.log_step(f"🎉 Chùm hạt đã đạt tới đích: {path}")
                # Mark final path in GUI
                for px, py in path:
                    if (px, py) != start and (px, py) != goal:
                        path_step_monitor.log_node_state(px, py, "path")
                return path
                
        # Generate successors
        successors = []
        for _, path in beam:
            curr = path[-1]
            path_step_monitor.log_node_state(curr[0], curr[1], "closed")
            neighbors = grid.get_neighbors(curr[0], curr[1])
            for neighbor in neighbors:
                if neighbor not in path:
                    new_path = path + [neighbor]
                    successors.append((h(neighbor), new_path))
                    path_step_monitor.log_node_state(neighbor[0], neighbor[1], "open")
                    
        if not successors:
            path_step_monitor.log_step("Không còn node lân cận nào để mở rộng!")
            break
            
        if delay > 0:
            time.sleep(delay)
            
        # Select k best successors
        successors.sort(key=lambda item: item[0])
        # To avoid duplicate ending nodes in the beam, filter them
        seen_ends = set()
        unique_successors = []
        for heur, path in successors:
            end_node = path[-1]
            if end_node not in seen_ends:
                seen_ends.add(end_node)
                unique_successors.append((heur, path))
                
        beam = unique_successors[:k]
        
        if not beam:
            path_step_monitor.log_step("Chùm hạt bị triệt tiêu hoàn toàn!")
            break
            
        # Log the selected beam candidates
        beam_ends = [path[-1] for _, path in beam]
        path_step_monitor.log_step(f"Chọn {len(beam)} hạt tốt nhất tiếp theo: {beam_ends}")
        
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None