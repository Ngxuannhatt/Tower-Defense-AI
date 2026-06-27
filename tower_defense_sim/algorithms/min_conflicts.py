import random
import time
from algorithms import astar
import path_step_monitor

class CSP:
    def __init__(self, map_manager, variables, domains):
        self.map_manager = map_manager
        self.variables = variables
        self.domains = domains

def get_conflicts(var, v, current, csp):
    """
    Computes conflicts for the variable 'var' when placed at value 'v'.
    Conflicts are defined as:
    - Overlaps with other towers: +500
    - Placement on Start or Goal node: +1000
    - Hard constraint: path from Start to Goal is blocked: +100
    """
    conflicts = 0
    
    # Overlap with other variables
    for other_var, other_val in current.items():
        if other_var != var and other_val == v:
            conflicts += 500
            
    # Start or goal check
    if v == csp.map_manager.start or v == csp.map_manager.goal:
        conflicts += 1000
        
    # Hard constraint: path blockage check.
    # Temporarily reconstruct the grid with this assignment to check if path is blocked.
    csp.map_manager.reset()
    for other_var, other_val in current.items():
        if other_var != var:
            csp.map_manager.add_tower(other_val[0], other_val[1], "Basic")
    csp.map_manager.add_tower(v[0], v[1], "Basic")
    
    # Run A* silently to check path
    was_silenced = path_step_monitor.is_silenced()
    path_step_monitor.set_silenced(True)
    path = astar.solve(csp.map_manager.start, csp.map_manager.goal, csp.map_manager, delay=0.0)
    path_step_monitor.set_silenced(was_silenced)
    
    if not path:
        conflicts += 100
        
    return conflicts

def min_conflicts(csp, max_steps, update_ui_callback=None, log_callback=None):
    """
    Min-conflicts CSP solver.
    """
    # 1. Initialize random complete assignment
    current = {}
    for var in csp.variables:
        current[var] = random.choice(csp.domains[var])
        
    # Apply to map
    csp.map_manager.reset()
    for var, val in current.items():
        csp.map_manager.add_tower(val[0], val[1], "Basic")
        
    if update_ui_callback:
        update_ui_callback()
        
    for step in range(1, max_steps + 1):
        # Identify all conflicted variables
        conflicted_vars = []
        for var in csp.variables:
            val = current[var]
            if get_conflicts(var, val, current, csp) > 0:
                conflicted_vars.append(var)
                
        # If no conflicts, success!
        if not conflicted_vars:
            if log_callback:
                log_callback(f"Min-Conflicts: Đã tìm thấy cấu hình hợp lệ tại bước {step}!")
            return current
            
        # Choose a conflicted variable randomly
        var = random.choice(conflicted_vars)
        
        # Find value that minimizes conflicts
        best_val = current[var]
        min_conf = get_conflicts(var, best_val, current, csp)
        
        # Sample the domain randomly to keep computation responsive
        domain_sample = random.sample(csp.domains[var], min(50, len(csp.domains[var])))
        if current[var] not in domain_sample:
            domain_sample.append(current[var])
            
        for v in domain_sample:
            conf = get_conflicts(var, v, current, csp)
            if conf < min_conf:
                min_conf = conf
                best_val = v
                
        # Update assignment
        current[var] = best_val
        
        # Apply to map
        csp.map_manager.reset()
        for v_name, v_coord in current.items():
            csp.map_manager.add_tower(v_coord[0], v_coord[1], "Basic")
            
        if log_callback:
            log_callback(f"🔄 Bước {step}/{max_steps} | Tháp: {var} -> {best_val} | Số tháp lỗi: {len(conflicted_vars)}")
            
        if update_ui_callback:
            update_ui_callback()
            
        time.sleep(0.04)
        
    if log_callback:
        log_callback(f"Kết thúc {max_steps} bước nhưng chưa tìm được cấu hình hoàn hảo không lỗi.")
    return current

def run_min_conflicts(map_manager, num_towers=18, max_steps=100, update_ui_callback=None, log_callback=None):
    """
    Main function to run Min-Conflicts algorithm from the GUI thread.
    """
    if log_callback:
        log_callback("Khởi tạo cấu hình tháp ngẫu nhiên ban đầu cho CSP Min-Conflicts...")
        
    variables = [f"T{i}" for i in range(num_towers)]
    domain = []
    for x in range(map_manager.width):
        for y in range(map_manager.height):
            if (x, y) != map_manager.start and (x, y) != map_manager.goal:
                domain.append((x, y))
                
    domains = {var: domain for var in variables}
    csp = CSP(map_manager, variables, domains)
    
    final_assignment = min_conflicts(csp, max_steps, update_ui_callback, log_callback)
    
    # Assign diverse tower types at the end for aesthetic diversity
    types = ["Basic", "Ice", "Fire"]
    map_manager.reset()
    for var, val in final_assignment.items():
        map_manager.add_tower(val[0], val[1], random.choice(types))
        
    if update_ui_callback:
        update_ui_callback()
        
    return final_assignment
