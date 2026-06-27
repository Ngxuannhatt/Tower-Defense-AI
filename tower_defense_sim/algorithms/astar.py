import heapq
import time
import path_step_monitor

class AStarNode:
    def __init__(self, position, parent=None, g=0.0, h=0.0):
        self.position = position
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

    @property
    def g_cost(self):
        return self.g

    @g_cost.setter
    def g_cost(self, val):
        self.g = val

    @property
    def h_cost(self):
        return self.h

    @h_cost.setter
    def h_cost(self, val):
        self.h = val

    @property
    def f_cost(self):
        return self.f

    @f_cost.setter
    def f_cost(self, val):
        self.f = val

    def __lt__(self, other):
        # tie-breaker: prefer higher g (deeper exploration) if f is equal
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f

def solve(start, goal, grid, delay=0.0):
    """
    Solves pathfinding from start to goal using A*.
    grid: an object implementing get_neighbors(x, y), is_valid_coord, and is_obstacle
    delay: sleep duration between steps in seconds
    """
    path_step_monitor.log_step(f"Bắt đầu thuật toán A* từ {start} đến {goal}")
    
    # Heuristic using Manhattan distance
    start_h = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    start_node = AStarNode(start, parent=None, g=0.0, h=start_h)
    
    FRONTIER = [start_node]
    REACHED = {}
    
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    while FRONTIER:
        n_node = heapq.heappop(FRONTIER)
        n = n_node.position
        
        # If this coordinate was already reached via a better/shorter path, skip
        if n in REACHED and REACHED[n].g <= n_node.g:
            continue
            
        REACHED[n] = n_node
        path_step_monitor.log_node_state(n[0], n[1], "closed")
        path_step_monitor.log_step(f"Mở node: {n}, cost: {n_node.g}, total_cost: {n_node.f}")
        
        if delay > 0:
            time.sleep(delay)
            
        if n == goal:
            path_step_monitor.log_step(f"Đã tìm thấy đường đi tới đích {goal}!")
            path = []
            curr = n_node
            while curr:
                path.append(curr.position)
                curr = curr.parent
            path.reverse()
            
            # Log path nodes for visual tracking
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        neighbors = grid.get_neighbors(n[0], n[1])
        for m in neighbors:
            g_new = n_node.g + 1.0
            h_m = abs(m[0] - goal[0]) + abs(m[1] - goal[1])
            f_m = g_new + h_m
            
            # Case 1: m is in REACHED
            if m in REACHED:
                m_reached_node = REACHED[m]
                if g_new >= m_reached_node.g:
                    continue
                else:
                    # Remove from REACHED and update it, then push back to FRONTIER
                    del REACHED[m]
                    m_reached_node.g = g_new
                    m_reached_node.f = f_m
                    m_reached_node.parent = n_node
                    heapq.heappush(FRONTIER, m_reached_node)
                    
                    path_step_monitor.log_node_state(m[0], m[1], "open")
                    path_step_monitor.log_step(f"Cập nhật Heuristic (Reopen) cho {m}: g={g_new}, h={h_m}, f={f_m}")
                    if delay > 0:
                        time.sleep(delay * 0.5)
            
            # Case 2: m is in FRONTIER
            else:
                m_frontier_node = next((node for node in FRONTIER if node.position == m), None)
                if m_frontier_node:
                    if g_new < m_frontier_node.g:
                        m_frontier_node.g = g_new
                        m_frontier_node.f = f_m
                        m_frontier_node.parent = n_node
                        heapq.heapify(FRONTIER)
                        
                        path_step_monitor.log_step(f"Cập nhật Heuristic cho {m} trong FRONTIER: g={g_new}, h={h_m}, f={f_m}")
                        if delay > 0:
                            time.sleep(delay * 0.5)
                
                # Case 3: m is not in either
                else:
                    m_node = AStarNode(m, parent=n_node, g=g_new, h=h_m)
                    heapq.heappush(FRONTIER, m_node)
                    
                    path_step_monitor.log_node_state(m[0], m[1], "open")
                    path_step_monitor.log_step(f"Cập nhật Heuristic cho {m}: g={g_new}, h={h_m}, f={f_m}")
                    if delay > 0:
                        time.sleep(delay * 0.5)
                        
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None
