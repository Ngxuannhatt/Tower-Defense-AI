import heapq
import time
import path_step_monitor

class AStarNode:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g_cost = 0.0
        self.h_cost = 0.0
        self.f_cost = 0.0

    def __lt__(self, other):
        # tie-breaker: prefer higher g_cost (deeper exploration) or lower f_cost
        if self.f_cost == other.f_cost:
            return self.g_cost > other.g_cost
        return self.f_cost < other.f_cost

def solve(start, goal, grid, delay=0.0):
    """
    Solves pathfinding from start to goal using A*.
    grid: an object implementing get_neighbors(x, y)
    delay: sleep duration between steps in seconds
    """
    path_step_monitor.log_step(f"Bắt đầu thuật toán A* từ {start} đến {goal}")
    
    start_node = AStarNode(start)
    goal_node = AStarNode(goal)
    
    open_list = []
    # Use a dictionary to track node objects in open_list by position
    open_dict = {start: start_node}
    # Closed set tracks visited positions
    closed_set = set()
    
    heapq.heappush(open_list, start_node)
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    while open_list:
        current_node = heapq.heappop(open_list)
        pos = current_node.position
        
        # Remove from open_dict if it's the current one
        if pos in open_dict and open_dict[pos] == current_node:
            del open_dict[pos]
            
        if pos in closed_set:
            continue
            
        closed_set.add(pos)
        path_step_monitor.log_node_state(pos[0], pos[1], "closed")
        
        # LOG STEP REQUIREMENT:
        path_step_monitor.log_step(f"Mở node: {current_node.position}, cost: {current_node.g_cost}, total_cost: {current_node.f_cost}")
        
        # Slow down for visualization
        if delay > 0:
            time.sleep(delay)
            
        # Check if we reached the goal
        if pos == goal:
            path_step_monitor.log_step(f"Đã tìm thấy đường đi tới đích {goal}!")
            # Reconstruct path
            path = []
            curr = current_node
            while curr:
                path.append(curr.position)
                curr = curr.parent
            path.reverse()
            
            # Log final path nodes
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            
            return path
            
        # Get walkable neighbors
        neighbors = grid.get_neighbors(pos[0], pos[1])
        for n_pos in neighbors:
            if n_pos in closed_set:
                continue
                
            # Manhattan distance heuristic
            h = abs(n_pos[0] - goal[0]) + abs(n_pos[1] - goal[1])
            g = current_node.g_cost + 1.0  # cost between adjacent nodes is 1
            f = g + h
            
            # Check if this neighbor is already in open list with a better or equal cost
            if n_pos in open_dict:
                existing_node = open_dict[n_pos]
                if g >= existing_node.g_cost:
                    continue
            
            # Update or create node
            neighbor_node = AStarNode(n_pos, current_node)
            neighbor_node.g_cost = g
            neighbor_node.h_cost = h
            neighbor_node.f_cost = f
            
            open_dict[n_pos] = neighbor_node
            heapq.heappush(open_list, neighbor_node)
            
            path_step_monitor.log_node_state(n_pos[0], n_pos[1], "open")
            path_step_monitor.log_step(f"Cập nhật Heuristic cho {n_pos}: g={g}, h={h}, f={f}")
            
            if delay > 0:
                time.sleep(delay * 0.5)  # slight delay for neighbor updates
                
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None
