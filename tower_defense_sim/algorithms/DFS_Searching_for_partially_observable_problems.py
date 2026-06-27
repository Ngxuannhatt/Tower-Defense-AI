import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy DFS Partially Observable (Belief State DFS) từ {start} đến {goal}")
    
    # Initial belief state: only the start position is known
    initial_belief = frozenset([start])
    
    # DFS stack holds tuples of (belief_state, action_path)
    frontier = [(initial_belief, [])]
    visited = {initial_belief}
    
    actions = {
        'U': (0, -1),
        'D': (0, 1),
        'L': (-1, 0),
        'R': (1, 0)
    }
    
    max_states = 5000
    state_count = 0
    
    while frontier and state_count < max_states:
        state_count += 1
        curr_belief, path_actions = frontier.pop()
        
        path_step_monitor.log_step(f"Mở trạng thái niềm tin: {list(curr_belief)}")
        for px, py in curr_belief:
            path_step_monitor.log_node_state(px, py, "closed")
            
        if delay > 0:
            time.sleep(delay)
            
        if curr_belief == frozenset([goal]):
            path_step_monitor.log_step(f"🎉 Đã tìm thấy chuỗi hành động đưa mọi khả năng về đích: {path_actions}")
            
            # Trace the coordinates from start
            path = [start]
            curr = start
            for act in path_actions:
                dx, dy = actions[act]
                nx, ny = curr[0] + dx, curr[1] + dy
                if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                    curr = (nx, ny)
                path.append(curr)
                
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        # Try actions
        for act, (dx, dy) in actions.items():
            new_coords = []
            for px, py in curr_belief:
                if (px, py) == goal:
                    # Once reached goal, remains at goal
                    new_coords.append(goal)
                else:
                    nx, ny = px + dx, py + dy
                    if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                        new_coords.append((nx, ny))
                    else:
                        new_coords.append((px, py))
            next_belief = frozenset(new_coords)
            
            if next_belief not in visited:
                visited.add(next_belief)
                frontier.append((next_belief, path_actions + [act]))
                path_step_monitor.log_step(f"  Hành động '{act}' -> Trạng thái niềm tin mới: {list(next_belief)}")
                for px, py in next_belief:
                    path_step_monitor.log_node_state(px, py, "open")
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
    path_step_monitor.log_step("Không tìm thấy chuỗi hành động khả thi trong môi trường quan sát một phần!")
    return None