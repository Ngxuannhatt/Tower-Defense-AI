import path_step_monitor
from algorithms import astar

def evaluate_creep_survival(creep_type: str, map_manager, path: list) -> float:
    """
    Evaluates the remaining HP of a creep type after traveling the path.
    Remaining HP = Max HP - Path Damage.
    Creep Types:
    - Fast: HP = 60, takes reduced damage from Fire towers, extra from Basic towers.
    - Tanky: HP = 200, takes reduced damage from Basic towers, extra from Fire towers.
    - Normal: HP = 100, standard damage.
    """
    if not path:
        return 0.0
        
    damage = 0.0
    for x, y in path:
        for (tx, ty), t_type in map_manager.towers.items():
            dist = ((tx - x)**2 + (ty - y)**2)**0.5
            if t_type == "Basic" and dist <= 3.0:
                if creep_type == "Fast":
                    damage += 12.0
                elif creep_type == "Tanky":
                    damage += 8.0
                else:
                    damage += 10.0
            elif t_type == "Fire" and dist <= 4.0:
                if creep_type == "Fast":
                    damage += 7.2
                elif creep_type == "Tanky":
                    damage += 27.0
                else:
                    damage += 18.0
            elif t_type == "Ice" and dist <= 2.0:
                if creep_type == "Fast":
                    damage += 12.0
                elif creep_type == "Tanky":
                    damage += 7.6
                else:
                    damage += 9.5
                    
    if creep_type == "Fast":
        return max(0.0, 60.0 - damage)
    elif creep_type == "Tanky":
        return max(0.0, 200.0 - damage)
    else:
        return max(0.0, 100.0 - damage)

def minimax(map_manager, path: list, depth: int, is_maximizing: bool, creep_type: str = None, log_steps: list = None):
    """
    Minimax search with depth limiting.
    MAX = Player building towers (tries to minimize creep remaining HP).
    MIN = AI spawning creeps (tries to maximize creep remaining HP).
    """
    if log_steps is None:
        log_steps = []
        
    if depth == 0 or not path:
        val = evaluate_creep_survival(creep_type, map_manager, path)
        return val, None

    if is_maximizing:
        # Player (MAX) wants to MINIMIZE creep survival HP (maximize damage)
        best_val = float('inf')
        best_move = None
        
        # Identify candidate positions near current path to test building
        path_set = set(path)
        candidates = []
        for px, py in path:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                cx, cy = px + dx, py + dy
                if map_manager.is_valid_coord(cx, cy) and not map_manager.is_obstacle(cx, cy) and (cx, cy) not in path_set:
                    if (cx, cy) not in candidates and (cx, cy) != map_manager.start and (cx, cy) != map_manager.goal:
                        candidates.append((cx, cy))
                        
        # Sort and pick top 2 candidates close to start for speed
        candidates = sorted(candidates, key=lambda c: abs(c[0]-map_manager.start[0]) + abs(c[1]-map_manager.start[1]))[:2]
        
        if not candidates:
            val = evaluate_creep_survival(creep_type, map_manager, path)
            return val, None
            
        for pos in candidates:
            for t_type in ["Basic", "Fire", "Ice"]:
                # Try placing tower
                map_manager.add_tower(pos[0], pos[1], t_type)
                
                # Recalculate path
                was_silenced = path_step_monitor.is_silenced()
                path_step_monitor.set_silenced(True)
                new_path = astar.solve(map_manager.start, map_manager.goal, map_manager, delay=0.0)
                path_step_monitor.set_silenced(was_silenced)
                
                val, _ = minimax(map_manager, new_path, depth - 1, False, creep_type, log_steps)
                
                # Revert
                map_manager.remove_tower(pos[0], pos[1])
                
                log_steps.append(f"   ├─ Player phản công: Xây {t_type} tại {pos} -> HP quái còn: {val:.1f}")
                
                if val < best_val:
                    best_val = val
                    best_move = (pos, t_type)
                    
        return best_val, best_move
    else:
        # AI (MIN) wants to MAXIMIZE creep survival HP (minimize damage)
        best_val = float('-inf')
        best_creep = None
        
        for c_type in ["Normal", "Fast", "Tanky"]:
            log_steps.append(f"AI (MIN) giả lập sinh quái: {c_type}")
            val, _ = minimax(map_manager, path, depth - 1, True, c_type, log_steps)
            log_steps.append(f" └─ HP dự báo tốt nhất cho quái {c_type}: {val:.1f}")
            
            if val > best_val:
                best_val = val
                best_creep = c_type
                
        return best_val, best_creep

def decide_optimal_creep(map_manager, path: list):
    """
    Decides the optimal creep type using minimax tree evaluation.
    Returns: (optimal_creep_name, expected_hp, log_steps)
    """
    log_steps = []
    # Depth = 2 (MIN selects creep, MAX responds with tower, evaluate)
    best_val, best_creep = minimax(map_manager, path, depth=2, is_maximizing=False, log_steps=log_steps)
    return best_creep, best_val, log_steps
