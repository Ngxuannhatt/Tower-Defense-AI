import os
import sys

# Ensure current module and parent directories are in the Python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from algorithms import astar, bfs, greedy_best_first, backtracking, expectimax, and_or, dfs, belief_state_search, hill_climbing,simulated_annealing,alpha_beta, IDAstar, Local_Beam_Search, UCS, forward_checking, DFS_Searching_for_partially_observable_problems


class Pathfinder:
    """
    Unified pathfinding controller. Acts as an interface to load, select, 
    and invoke different search algorithms under the algorithms/ package.
    """
    def __init__(self, map_manager):
        self.map_manager = map_manager
        self.current_algorithm = "alpha_beta"
        self.delay = 0.0  # delay in seconds between exploration steps

    def set_algorithm(self, algorithm_name):
        """Sets the active algorithm (A*,  BFS, Greedy, Backtracking, Expectimax, AND-OR, Simulated Annealing)."""
        self.current_algorithm = algorithm_name

    def set_delay(self, delay_seconds):
        """Sets the delay between search steps for visualization."""
        self.delay = delay_seconds

    def find_path(self, start=None, goal=None, force_init=False):
        """
        Solves the path planning problem using the selected algorithm.
        start: tuple (x, y) starting coordinate. Defaults to map start.
        goal: tuple (x, y) ending coordinate. Defaults to map goal.
        force_init: set to True to force the incremental algorithms to reset.
        
        Returns a list of tuples [(x, y), ...] representing the path, or None.
        """
        if start is None:
            start = self.map_manager.start
        if goal is None:
            goal = self.map_manager.goal

        # Dispatch search query
        if self.current_algorithm == "A*":
            return astar.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "BFS":
            return bfs.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "Greedy Best-First":
            return greedy_best_first.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "Backtracking (DFS)":
            return backtracking.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "AND-OR Search":
            return and_or.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "DFS":
            return dfs.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "Belief State Search":
            return belief_state_search.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "Steepest Ascent Hill Climbing":
            return hill_climbing.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "alpha_beta":
            return alpha_beta.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "IDAstar":
            return IDAstar.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "Local_Beam_Search":
            return Local_Beam_Search.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm in ["UCS"]:
            return UCS.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "forward_checking":
            return forward_checking.solve(start, goal, self.map_manager, delay=self.delay)
            
        elif self.current_algorithm == "DFS_Searching_for_partially_observable_problems":
            return DFS_Searching_for_partially_observable_problems.solve(start, goal, self.map_manager, delay=self.delay)

        elif self.current_algorithm == "Simulated Annealing":
            return simulated_annealing.solve(start, goal, self.map_manager, delay=self.delay)
            
        else:
            raise ValueError(f"Thuật toán không hợp lệ: {self.current_algorithm}")

    def convert_path_to_directions(self, path):
        """
        Optional helper to convert a coordinate-based path into a list of movement directions.
        Returns list of strings, e.g. ['RIGHT', 'DOWN', ...]
        """
        if not path or len(path) < 2:
            return []
            
        directions = []
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            dx, dy = x2 - x1, y2 - y1
            
            if dx == 1 and dy == 0:
                directions.append("RIGHT")
            elif dx == -1 and dy == 0:
                directions.append("LEFT")
            elif dx == 0 and dy == 1:
                directions.append("DOWN")
            elif dx == 0 and dy == -1:
                directions.append("UP")
            else:
                directions.append("DIAGONAL")
        return directions
