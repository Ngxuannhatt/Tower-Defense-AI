import math
import random
import time
import path_step_monitor
from algorithms import astar

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Solves pathfinding using Simulated Annealing with step logging for GUI visualization.
    """
    path_step_monitor.log_step(f"Khởi chạy Simulated Annealing từ {start} đến {goal}")
    
    visited_cells = {start}
    path = [start]
    current = start
    
    max_steps = 2000
    steps = 0
    T = 100.0
    T_min = 0.1
    alpha = 0.95
    
    while current != goal and steps < max_steps:
        steps += 1
        x, y = current
        
        path_step_monitor.log_node_state(x, y, "closed")
        if delay > 0:
            time.sleep(delay)
            
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny) and (nx, ny) not in visited_cells:
                neighbors.append((nx, ny))
                
        if not neighbors:
            path_step_monitor.log_step(f"Gặp ngõ cụt tại {current}! Quay lùi (Backtracking)...")
            path.pop()
            if not path:
                break
            current = path[-1]
            continue
            
        neighbors.sort(key=lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1]))
        curr_dist = abs(current[0] - goal[0]) + abs(current[1] - goal[1])
        
        if len(neighbors) == 1:
            best_neighbor = neighbors[0]
            best_dist = abs(best_neighbor[0] - goal[0]) + abs(best_neighbor[1] - goal[1])
            path_step_monitor.log_step(f"🌡️ T={T:.1f} | Ô duy nhất khả thi: {best_neighbor} (d={best_dist})")
        else:
            cand = random.choice(neighbors)
            cand_dist = abs(cand[0] - goal[0]) + abs(cand[1] - goal[1])
            delta = cand_dist - curr_dist
            
            if delta < 0:
                best_neighbor = cand
                path_step_monitor.log_step(f"🌡️ T={T:.1f} | Chấp nhận ô tốt hơn: {cand} (d={cand_dist} < {curr_dist})")
            else:
                p = math.exp(-delta / max(T, 0.01))
                if random.random() < p:
                    best_neighbor = cand
                    path_step_monitor.log_step(f"🎲 T={T:.1f} | Chấp nhận ô tệ hơn {cand} (d={cand_dist} >= {curr_dist}) với xác suất p={p:.2f}")
                else:
                    path_step_monitor.log_step(f"❌ T={T:.1f} | Từ chối ô tệ hơn {cand} (d={cand_dist} >= {curr_dist}) với xác suất p={p:.2f}. Giữ nguyên vị trí.")
                    T = max(T_min, T * alpha)
                    continue
                
        current = best_neighbor
        visited_cells.add(current)
        path.append(current)
        path_step_monitor.log_node_state(current[0], current[1], "open")
        
        T = max(T_min, T * alpha)
        
    if path and path[-1] == goal:
        path_step_monitor.log_step(f"Simulated Annealing đã tìm thấy đường đi! Độ dài: {len(path)}")
        for px, py in path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return path
        
    path_step_monitor.log_step("Không tìm thấy đường đi tới đích!")
    return None

def get_map_energy(map_manager):
    path = astar.solve(map_manager.start, map_manager.goal, map_manager, delay=0.0)
    if not path:
        return 999.0
    return -float(len(path))

def get_random_neighbor_layout(map_manager, num_towers):
    current_towers = list(map_manager.towers.items())
    if not current_towers:
        return
        
    old_pos, t_type = random.choice(current_towers)
    map_manager.remove_tower(old_pos[0], old_pos[1])
    
    placed = False
    while not placed:
        rx = random.randint(0, map_manager.width - 1)
        ry = random.randint(0, map_manager.height - 1)
        if (rx, ry) != map_manager.start and (rx, ry) != map_manager.goal and (rx, ry) not in map_manager.towers:
            map_manager.add_tower(rx, ry, t_type)
            placed = True

def run_annealing(map_manager, num_towers=18, steps=80, update_ui_callback=None, log_callback=None):
    if log_callback:
        log_callback("Khởi tạo cấu hình tháp ngẫu nhiên ban đầu...")
        
    map_manager.reset()
    types = ["Basic", "Ice", "Fire"]
    while len(map_manager.towers) < num_towers:
        rx = random.randint(0, map_manager.width - 1)
        ry = random.randint(0, map_manager.height - 1)
        if (rx, ry) != map_manager.start and (rx, ry) != map_manager.goal:
            map_manager.add_tower(rx, ry, random.choice(types))
            
    if update_ui_callback: update_ui_callback()

    T = 100.0
    Tmin = 10.0
    alpha = 0.92

    current_energy = get_map_energy(map_manager)

    while T > Tmin:
        backup_towers = dict(map_manager.towers)
        
        get_random_neighbor_layout(map_manager, num_towers)
        next_energy = get_map_energy(map_manager)
        
        delta = next_energy - current_energy
        
        if delta < 0:
            current_energy = next_energy
            if log_callback:
                log_callback(f"🌡️ T={T:.1f} | Chấp nhận cấu hình tốt hơn. Đường đi: {-current_energy:.0f} ô.")
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                current_energy = next_energy
                if log_callback:
                    log_callback(f"🎲 T={T:.1f} | Chấp nhận cấu hình tệ hơn bằng xác suất p={p:.2f}.")
            else:
                map_manager.towers = dict(backup_towers)
                
        T = alpha * T
        
        if update_ui_callback: 
            update_ui_callback()
        time.sleep(0.05)    
        
    return map_manager.towers
