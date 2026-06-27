import sys
import os

# Include directory in search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from map_manager import MapManager
from pathfinder import Pathfinder

def run_tests():
    print("========================================")
    print("RUNNING PATHFINDING ALGORITHM TESTS")
    print("========================================")
    
    # 1. Initialize Map and Pathfinder
    map_manager = MapManager(width=10, height=10)  # 10x10 grid for fast tests
    map_manager.start = (0, 0)
    map_manager.goal = (9, 9)
    
    pathfinder = Pathfinder(map_manager)
    
    algorithms = ["A*", "Dijkstra", "Incremental A*", "D*", "BFS", "DFS", "Greedy Best-First", "Backtracking (DFS)", "Belief State Search", "Steepest Ascent Hill Climbing", "Expectimax", "AND-OR Search"]
    
    for alg in algorithms:
        print(f"\n--- Testing Algorithm: {alg} ---")
        pathfinder.set_algorithm(alg)
        
        # Test Case 1: Open grid (no obstacles)
        map_manager.reset()
        path = pathfinder.find_path(force_init=True)
        assert path is not None, f"Failed: {alg} could not find a path in an open grid"
        assert path[0] == (0, 0) and path[-1] == (9, 9), f"Failed: {alg} path coordinates mismatch"
        print(f"  [PASS] Open grid search. Path length: {len(path)}")
        
        # Test Case 2: Simple obstacle avoidance
        # Place towers at (1, 0) and (1, 1) to divert the path
        # This forces the path to go around via (0, 1) -> (0, 2)...
        map_manager.reset()
        map_manager.add_tower(1, 0)
        map_manager.add_tower(1, 1)
        path = pathfinder.find_path(force_init=True)
        assert path is not None, f"Failed: {alg} could not bypass simple obstacles"
        assert (1, 0) not in path and (1, 1) not in path, f"Failed: {alg} path went through obstacles"
        print(f"  [PASS] Simple obstacle avoidance. Path length: {len(path)}")
        
        # Test Case 3: Complete blockage (No Path)
        # Block the goal node completely
        map_manager.reset()
        map_manager.add_tower(9, 8)
        map_manager.add_tower(8, 9)
        path = pathfinder.find_path(force_init=True)
        assert path is None or len(path) == 0, f"Failed: {alg} claimed to find a path through a blocked goal"
        print(f"  [PASS] Blocked goal detection (No path).")
        
    # Test Case 4: Simulated Annealing layout generation
    print("\n--- Testing Simulated Annealing Map Optimizer ---")
    from algorithms import simulated_annealing
    map_manager.reset()
    simulated_annealing.run_annealing(map_manager, num_towers=8, steps=10, update_ui_callback=None, log_callback=None)
    assert len(map_manager.towers) > 0, "Failed: Simulated Annealing did not place any towers"
    print("  [PASS] Simulated Annealing placed towers successfully.")
    
    print("\n========================================")
    print("ALL PATHFINDING ALGORITHMS PASSED TESTS!")
    print("========================================")

if __name__ == "__main__":
    run_tests()
