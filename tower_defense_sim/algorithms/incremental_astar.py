import heapq
import time
import path_step_monitor

class LPAStar:
    def __init__(self, grid_width=20, grid_height=20):
        self.width = grid_width
        self.height = grid_height
        self.start = None
        self.goal = None
        self.grid = None  # Reference to MapManager
        
        # State tables
        self.g = {}
        self.rhs = {}
        self.queue = []  # Priority queue of (key, node_position)
        
        # Keep track of active nodes in the queue for fast lookup/removal
        self.queue_set = set()

    def reset(self):
        self.g.clear()
        self.rhs.clear()
        self.queue.clear()
        self.queue_set.clear()

    def h(self, u):
        """Manhattan distance heuristic."""
        if not self.goal:
            return 0.0
        return float(abs(u[0] - self.goal[0]) + abs(u[1] - self.goal[1]))

    def calculate_key(self, u):
        g_val = self.g.get(u, float('inf'))
        rhs_val = self.rhs.get(u, float('inf'))
        min_val = min(g_val, rhs_val)
        return (min_val + self.h(u), min_val)

    def get_predecessors(self, u):
        # In a standard grid, predecessors are the same as walkable neighbors
        return self.grid.get_neighbors(u[0], u[1])

    def get_successors(self, u):
        # In a standard grid, successors are the same as walkable neighbors
        return self.grid.get_neighbors(u[0], u[1])

    def update_vertex(self, u):
        if u != self.start:
            # rhs(u) = min_{s' in pred(u)} (g(s') + c(s', u))
            preds = self.get_predecessors(u)
            min_rhs = float('inf')
            for p in preds:
                g_p = self.g.get(p, float('inf'))
                cost = 1.0  # constant cost of 1 between adjacent grid cells
                if g_p + cost < min_rhs:
                    min_rhs = g_p + cost
            self.rhs[u] = min_rhs

        # Remove from queue if it is in it
        self.remove_from_queue(u)

        # If inconsistent, insert into queue
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
        self.goal = goal
        self.grid = grid
        
        self.reset()
        
        # Initialize start node
        self.rhs[start] = 0.0
        self.g[start] = float('inf')
        
        key = self.calculate_key(start)
        heapq.heappush(self.queue, (key, start))
        self.queue_set.add(start)
        path_step_monitor.log_node_state(start[0], start[1], "open")

    def compute_shortest_path(self, delay=0.0):
        while self.queue and (self.top_key() < self.calculate_key(self.goal) or 
                              self.g.get(self.goal, float('inf')) != self.rhs.get(self.goal, float('inf'))):
            
            # Pop node
            _, u = heapq.heappop(self.queue)
            if u in self.queue_set:
                self.queue_set.remove(u)

            g_u = self.g.get(u, float('inf'))
            rhs_u = self.rhs.get(u, float('inf'))
            
            # Visualization state
            path_step_monitor.log_node_state(u[0], u[1], "closed")
            h_u = self.h(u)
            path_step_monitor.log_step(f"Mở node: {u}, cost: {g_u}, total_cost: {min(g_u, rhs_u) + h_u}")
            
            if delay > 0:
                time.sleep(delay)

            if g_u > rhs_u:
                # Locally overconsistent: set g = rhs and update successors
                self.g[u] = rhs_u
                successors = self.get_successors(u)
                for s in successors:
                    self.update_vertex(s)
                    path_step_monitor.log_node_state(s[0], s[1], "open")
                    path_step_monitor.log_step(f"Cập nhật Heuristic cho {s}: g={self.g.get(s, float('inf'))}, rhs={self.rhs.get(s, float('inf'))}")
            else:
                # Locally underconsistent: set g = infinity and update self + successors
                self.g[u] = float('inf')
                self.update_vertex(u)
                successors = self.get_successors(u)
                for s in successors:
                    self.update_vertex(s)
                    
            if delay > 0:
                time.sleep(delay * 0.5)

    def top_key(self):
        if not self.queue:
            return (float('inf'), float('inf'))
        return self.queue[0][0]

    def reconstruct_path(self):
        """Reconstructs the shortest path from start to goal based on g-values."""
        g_goal = self.g.get(self.goal, float('inf'))
        if g_goal == float('inf'):
            return None
            
        path = [self.goal]
        curr = self.goal
        
        # Trace backward from goal to start
        while curr != self.start:
            preds = self.get_predecessors(curr)
            if not preds:
                return None
                
            # Find predecessor with minimum g(p)
            best_p = None
            min_g = float('inf')
            for p in preds:
                gp = self.g.get(p, float('inf'))
                if gp < min_g:
                    min_g = gp
                    best_p = p
                    
            if best_p is None or min_g == float('inf'):
                return None  # Path blocked
                
            curr = best_p
            path.append(curr)
            
        path.reverse()
        
        # Color path nodes
        for px, py in path:
            if (px, py) != self.start and (px, py) != self.goal:
                path_step_monitor.log_node_state(px, py, "path")
                
        return path

# Persistent solver instance to run incrementally
_solver_instance = None

def solve(start, goal, grid, delay=0.0, force_init=False):
    """
    Interface function to run LPA* solver.
    If the grid has changed, we should trigger updates.
    """
    global _solver_instance
    
    # Initialize solver if not yet created or grid size changed
    if _solver_instance is None or _solver_instance.width != grid.width or _solver_instance.height != grid.height:
        _solver_instance = LPAStar(grid.width, grid.height)
        force_init = True

    if force_init or _solver_instance.start != start or _solver_instance.goal != goal:
        path_step_monitor.log_step("Khởi tạo lại trạng thái LPA*")
        _solver_instance.initialize(start, goal, grid)
    else:
        # Incremental update: detect changes in towers and update affected vertices
        # In a real game, we identify which cells changed. Since we have a small grid,
        # we can just scan the grid, find discrepancies between our cached grid status and MapManager,
        # and run update_vertex on those cells and their neighbors.
        path_step_monitor.log_step("Cập nhật đồ thị thay đổi (Incremental Re-planning)")
        
        # Update vertex states for all changed coordinates
        # (This handles any towers added/removed since last call)
        # Note: MapManager provides the source of truth. We recalculate rhs for nodes.
        # To be robust, let's update vertices that have changed.
        # Since LPA* is run within pathfinder, we check all coordinates.
        for x in range(grid.width):
            for y in range(grid.height):
                coord = (x, y)
                # If coordinate is obstacle, its g and rhs should be inf
                # and its neighbors' rhs values might need update
                # Let's run update_vertex on everything to synchronize,
                # or just run it on nodes whose walkability status changed.
                # A full scan and update of modified cells is very fast.
                is_obs = grid.is_obstacle(x, y)
                if is_obs:
                    _solver_instance.g[coord] = float('inf')
                    _solver_instance.rhs[coord] = float('inf')
                    _solver_instance.remove_from_queue(coord)
                
        # Update walkable nodes to make sure their rhs matches current grid
        for x in range(grid.width):
            for y in range(grid.height):
                if not grid.is_obstacle(x, y):
                    _solver_instance.update_vertex((x, y))

    # Compute shortest path
    _solver_instance.compute_shortest_path(delay)
    
    # Reconstruct path
    path = _solver_instance.reconstruct_path()
    if path:
        path_step_monitor.log_step(f"LPA* tìm thấy đường đi độ dài: {len(path)}")
    else:
        path_step_monitor.log_step("LPA* không tìm thấy đường đi!")
    return path
