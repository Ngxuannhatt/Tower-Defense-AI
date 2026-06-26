import heapq
import time
import path_step_monitor

class DijkstraNode:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g_cost = 0.0
        self.f_cost = 0.0  # f_cost equals g_cost for Dijkstra

    def __lt__(self, other):
        return self.f_cost < other.f_cost

def solve(start, goal, grid, delay=0.0):
    """
    Solves pathfinding from start to goal using Dijkstra's algorithm.
    grid: an object implementing get_neighbors(x, y)
    delay: sleep duration between steps in seconds
    """
    path_step_monitor.log_step(f"Bắt đầu thuật toán Dijkstra từ {start} đến {goal}")
    
    start_node = DijkstraNode(start)
    
    open_list = []
    open_dict = {start: start_node}
    closed_set = set()
    
    heapq.heappush(open_list, start_node)
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    while open_list:
        current_node = heapq.heappop(open_list)
        pos = current_node.position
        
        if pos in open_dict and open_dict[pos] == current_node:
            del open_dict[pos]
            
        if pos in closed_set:
            continue
            
        closed_set.add(pos)
        path_step_monitor.log_node_state(pos[0], pos[1], "closed")
        
        # LOG STEP REQUIREMENT:
        path_step_monitor.log_step(f"Mở node: {current_node.position}, cost: {current_node.g_cost}, total_cost: {current_node.f_cost}")
        
        if delay > 0:
            time.sleep(delay)
            
        if pos == goal:
            path_step_monitor.log_step(f"Đã tìm thấy đường đi tới đích {goal}!")
            path = []
            curr = current_node
            while curr:
                path.append(curr.position)
                curr = curr.parent
            path.reverse()
            
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        neighbors = grid.get_neighbors(pos[0], pos[1])
        for n_pos in neighbors:
            if n_pos in closed_set:
                continue
                
            g = current_node.g_cost + 1.0
            f = g  # no heuristic
            
            if n_pos in open_dict:
                existing_node = open_dict[n_pos]
                if g >= existing_node.g_cost:
                    continue
                    
            neighbor_node = DijkstraNode(n_pos, current_node)
            neighbor_node.g_cost = g
            neighbor_node.f_cost = f
            
            open_dict[n_pos] = neighbor_node
            heapq.heappush(open_list, neighbor_node)
            
            path_step_monitor.log_node_state(n_pos[0], n_pos[1], "open")
            path_step_monitor.log_step(f"Cập nhật neighbor: {n_pos}, g_cost: {g}")
            
            if delay > 0:
                time.sleep(delay * 0.5)
                
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None
