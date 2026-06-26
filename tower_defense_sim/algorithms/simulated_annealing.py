import math
import random
import time
from algorithms import astar

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
