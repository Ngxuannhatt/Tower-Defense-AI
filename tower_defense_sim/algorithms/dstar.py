import heapq
import time
import path_step_monitor

class DStarLite:
    def __init__(self, grid_width=20, grid_height=20):
        self.width = grid_width
        self.height = grid_height
        
        self.start = None
        self.goal = None
        self.last_start = None
        self.grid = None
        
        self.g = {}
        self.rhs = {}
        self.queue = []  # Priority queue of (key, node)
        self.queue_set = set()
        
        self.km = 0.0  # Key modifier for agent movement

    def reset(self):
        self.g.clear()
        self.rhs.clear()
        self.queue.clear()
        self.queue_set.clear()
        self.km = 0.0

    def h(self, u):
        """Manhattan distance heuristic from u to current start."""
        if not self.start:
            return 0.0
        return float(abs(u[0] - self.start[0]) + abs(u[1] - self.start[1]))

    def calculate_key(self, u):
        g_val = self.g.get(u, float('inf'))
        rhs_val = self.rhs.get(u, float('inf'))
        min_val = min(g_val, rhs_val)
        return (min_val + self.h(u) + self.km, min_val)

    def get_successors(self, u):
        # In a grid, successors and predecessors are symmetric (walkable adjacent cells)
        return self.grid.get_neighbors(u[0], u[1])

    def get_predecessors(self, u):
        return self.grid.get_neighbors(u[0], u[1])

    def update_vertex(self, u):
        if u != self.goal:
            # rhs(u) = min_{s' in succ(u)} (c(u, s') + g(s'))
            succs = self.get_successors(u)
            min_rhs = float('inf')
            for s in succs:
                g_s = self.g.get(s, float('inf'))
                cost = 1.0
                if cost + g_s < min_rhs:
                    min_rhs = cost + g_s
            self.rhs[u] = min_rhs

        self.remove_from_queue(u)

        g_val = self.g.get(u, float('inf'))
        rhs_val = self.rhs.get(u, float('inf'))
        if g_val != rhs_val:
            key = self.calculate_key(u)
            heapq.heappush(self.queue, (key, u))
            self.queue_set.add(u)

    def remove_from_queue(self, u):
        if u in self.queue_set:
            self.queue = [item for item in self.queue if item[1] != u]
            heapq.heapify(self.queue)
            self.queue_set.remove(u)

    def initialize(self, start, goal, grid):
        self.start = start
        self.last_start = start
        self.goal = goal
        self.grid = grid
        
        self.reset()
        
        # D* Lite searches BACKWARD: goal to start
        # So, rhs(goal) = 0
        self.rhs[self.goal] = 0.0
        self.g[self.goal] = float('inf')
        
        key = self.calculate_key(self.goal)
        heapq.heappush(self.queue, (key, self.goal))
        self.queue_set.add(self.goal)
        
        path_step_monitor.log_node_state(self.goal[0], self.goal[1], "open")

    def top_key(self):
        if not self.queue:
            return (float('inf'), float('inf'))
        return self.queue[0][0]

    def compute_shortest_path(self, delay=0.0):
        while self.queue and (self.top_key() < self.calculate_key(self.start) or 
                              self.g.get(self.start, float('inf')) != self.rhs.get(self.start, float('inf'))):
            
            k_old = self.top_key()
            _, u = heapq.heappop(self.queue)
            if u in self.queue_set:
                self.queue_set.remove(u)

            k_new = self.calculate_key(u)
            g_u = self.g.get(u, float('inf'))
            rhs_u = self.rhs.get(u, float('inf'))

            # Check if key needs update due to movement (km)
            if k_old < k_new:
                heapq.heappush(self.queue, (k_new, u))
                self.queue_set.add(u)
                continue

            path_step_monitor.log_node_state(u[0], u[1], "closed")
            h_u = self.h(u)
            path_step_monitor.log_step(f"Mở node: {u}, cost: {g_u}, total_cost: {min(g_u, rhs_u) + h_u}")
            
            if delay > 0:
                time.sleep(delay)

            if g_u > rhs_u:
                # Overconsistent
                self.g[u] = rhs_u
                preds = self.get_predecessors(u)
                for p in preds:
                    self.update_vertex(p)
                    path_step_monitor.log_node_state(p[0], p[1], "open")
                    path_step_monitor.log_step(f"Cập nhật Heuristic cho {p}: g={self.g.get(p, float('inf'))}, rhs={self.rhs.get(p, float('inf'))}")
            else:
                # Underconsistent
                self.g[u] = float('inf')
                self.update_vertex(u)
                preds = self.get_predecessors(u)
                for p in preds:
                    self.update_vertex(p)

            if delay > 0:
                time.sleep(delay * 0.5)

    def handle_moved_agent(self, new_start):
        """Called when the agent has moved to a new cell along the path."""
        self.start = new_start
        self.km += self.h(self.last_start)
        self.last_start = self.start

    def reconstruct_path(self):
        """
        Reconstructs the path from start to goal by moving from start
        to adjacent nodes with minimum g values.
        """
        g_start = self.g.get(self.start, float('inf'))
        if g_start == float('inf'):
            return None
            
        path = [self.start]
        curr = self.start
        
        visited = {self.start}
        
        while curr != self.goal:
            succs = self.get_successors(curr)
            if not succs:
                return None
                
            # Find successor with min (cost + g(s))
            best_s = None
            min_cost = float('inf')
            for s in succs:
                if s in visited:
                    continue
                g_s = self.g.get(s, float('inf'))
                cost = 1.0 + g_s
                if cost < min_cost:
                    min_cost = cost
                    best_s = s
                    
            if best_s is None or min_cost == float('inf'):
                return None
                
            curr = best_s
            path.append(curr)
            visited.add(curr)
            
        # Color path nodes
        for px, py in path:
            if (px, py) != self.start and (px, py) != self.goal:
                path_step_monitor.log_node_state(px, py, "path")
                
        return path

# Persistent solver instance to run incrementally
_solver_instance = None

def solve(start, goal, grid, delay=0.0, force_init=False):
    """
    Interface function to run D* Lite solver.
    If the grid has changed, it updates the priority queue and recomputes.
    """
    global _solver_instance
    
    # Initialize solver if needed
    if _solver_instance is None or _solver_instance.width != grid.width or _solver_instance.height != grid.height:
        _solver_instance = DStarLite(grid.width, grid.height)
        force_init = True

    if force_init or _solver_instance.goal != goal:
        path_step_monitor.log_step("Khởi tạo lại D* Lite (Bắt đầu từ Goal)")
        _solver_instance.initialize(start, goal, grid)
    elif _solver_instance.start != start:
        # Agent has moved
        path_step_monitor.log_step(f"Kẻ địch đã di chuyển tới: {start}. Cập nhật vị trí D* Lite")
        _solver_instance.handle_moved_agent(start)
    else:
        # Grid changes detected
        path_step_monitor.log_step("D* Lite phát hiện thay đổi bản đồ (Obstacle changed)")
        
        # Scan for changes and trigger update_vertex
        # To be clean and robust:
        for x in range(grid.width):
            for y in range(grid.height):
                coord = (x, y)
                is_obs = grid.is_obstacle(x, y)
                if is_obs:
                    _solver_instance.g[coord] = float('inf')
                    _solver_instance.rhs[coord] = float('inf')
                    _solver_instance.remove_from_queue(coord)
                    
        for x in range(grid.width):
            for y in range(grid.height):
                if not grid.is_obstacle(x, y):
                    _solver_instance.update_vertex((x, y))

    # Compute path
    _solver_instance.compute_shortest_path(delay)
    
    # Reconstruct path
    path = _solver_instance.reconstruct_path()
    if path:
        path_step_monitor.log_step(f"D* Lite tìm thấy đường đi độ dài: {len(path)}")
    else:
        path_step_monitor.log_step("D* Lite không tìm thấy đường đi!")
    return path
