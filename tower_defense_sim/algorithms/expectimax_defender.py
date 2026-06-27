import math

def calculate_path_expected_damage(map_manager, path: list) -> float:
    """
    Calculates total expected damage dealt to a creep along path.
    Models path steps as Chance Nodes (accounting for 30% freeze chance from Ice towers 
    and 40% critical damage chance from Fire towers).
    """
    total_damage = 0.0
    for px, py in path:
        step_base_damage = 0.0
        freeze_prob = 0.0
        for (tx, ty), t_type in map_manager.towers.items():
            dist = math.sqrt((tx - px)**2 + (ty - py)**2)
            if t_type == "Basic" and dist <= 3.0:
                step_base_damage += 10.0
            elif t_type == "Fire" and dist <= 4.0:
                # Fire tower: 18.0 expected damage (10 * 0.6 + 30 * 0.4 crit chance)
                step_base_damage += 18.0
            elif t_type == "Ice" and dist <= 2.0:
                # Ice tower: 9.5 expected damage + 30% freeze probability
                step_base_damage += 9.5
                freeze_prob = 0.3
                
        # Chance Node evaluation at step (px, py):
        # When slowed (30% chance near Ice), creep takes double damage from other towers
        step_exp_damage = step_base_damage * (1.0 + freeze_prob)
        total_damage += step_exp_damage
    return total_damage

def decide_optimal_tower_expectimax(map_manager, current_path: list):
    """
    Expectimax decision maker for AI Tower Placement.
    MAX Node scans walkable empty cells adjacent to current_path and evaluates placing 
    "Basic", "Ice", or "Fire" towers to MAXIMIZE expected damage dealt to the creep.
    Returns: (best_pos, best_tower_type, max_expected_damage, log_steps)
    """
    log_steps = []
    log_steps.append("=== EXPECTIMAX TOWER PLACEMENT (MAX NODE DEFENDER) ===")

    if not current_path:
        return None, None, 0.0, ["⚠️ Chưa có đường đi hiện tại để đặt trụ."]

    path_set = set(current_path)
    candidates = []
    for px, py in current_path:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            cx, cy = px + dx, py + dy
            if map_manager.is_valid_coord(cx, cy) and not map_manager.is_obstacle(cx, cy) and (cx, cy) not in path_set:
                if (cx, cy) != map_manager.start and (cx, cy) != map_manager.goal and (cx, cy) not in candidates:
                    candidates.append((cx, cy))

    if not candidates:
        return None, None, 0.0, ["⚠️ Không tìm thấy ô trống lân cận phù hợp để đặt trụ."]

    best_pos = None
    best_tower_type = None
    max_expected_damage = float('-inf')

    # Baseline expected damage before placing new tower
    baseline_damage = calculate_path_expected_damage(map_manager, current_path)
    log_steps.append(f"🛡️ Sát thương kỳ vọng hiện tại trên đường đi: {baseline_damage:.1f}")

    for pos in candidates:
        for t_type in ["Basic", "Fire", "Ice"]:
            map_manager.add_tower(pos[0], pos[1], t_type)
            exp_dmg = calculate_path_expected_damage(map_manager, current_path)
            map_manager.remove_tower(pos[0], pos[1])

            if exp_dmg > max_expected_damage:
                max_expected_damage = exp_dmg
                best_pos = pos
                best_tower_type = t_type

    if best_pos:
        diff = max_expected_damage - baseline_damage
        log_steps.append(f"🎯 AI MAX Node chọn vị trí tối ưu: {best_pos} với trụ [{best_tower_type}]")
        log_steps.append(f"📈 Sát thương kỳ vọng mới: {max_expected_damage:.1f} (Tăng thêm +{diff:.1f})")

    return best_pos, best_tower_type, max_expected_damage, log_steps
