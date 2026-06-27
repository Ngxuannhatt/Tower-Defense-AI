import math

def get_base_damage(creep_type: str, map_manager, x: int, y: int) -> float:
    """
    Calculates base damage dealt by towers in range to a specific creep type at cell (x, y).
    """
    damage = 0.0
    for (tx, ty), t_type in map_manager.towers.items():
        dist = math.sqrt((tx - x)**2 + (ty - y)**2)
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
    return damage

def evaluate_creep_expectimax(creep_type: str, map_manager, path: list):
    """
    Evaluates expected remaining HP for a creep type traversing current_path.
    Models path steps as Chance Nodes (30% chance of being slowed near Ice towers, taking double damage).
    Returns (expected_hp, total_expected_damage).
    """
    if not path:
        return 0.0, 0.0

    max_hp = 60.0 if creep_type == "Fast" else (200.0 if creep_type == "Tanky" else 100.0)
    total_expected_damage = 0.0

    for x, y in path:
        base_dmg = get_base_damage(creep_type, map_manager, x, y)
        freeze_prob = map_manager.get_freeze_probability(x, y)
        # Chance Node evaluation at step (x, y): 30% chance slowed (2x damage), 70% normal (1x damage)
        exp_step_dmg = base_dmg * (1.0 + freeze_prob)
        total_expected_damage += exp_step_dmg

    expected_hp = max(0.0, max_hp - total_expected_damage)
    return expected_hp, total_expected_damage

def decide_optimal_creep_expectimax(map_manager, current_path: list):
    """
    Expectimax decision maker for AI Creep Spawner.
    MAX Node selects best creep type ("Fast", "Tanky", "Normal") to maximize expected survival HP.
    Chance Nodes model environmental uncertainty (freeze chance along path).
    Returns: (best_creep, expected_hp, log_steps)
    """
    log_steps = []
    log_steps.append("=== EXPECTIMAX CREEP SPAWNER (CHANCE NODES) ===")

    best_creep = None
    best_expected_hp = float('-inf')

    creep_types = ["Normal", "Fast", "Tanky"]
    for c_type in creep_types:
        max_hp = 60.0 if c_type == "Fast" else (200.0 if c_type == "Tanky" else 100.0)
        exp_hp, exp_dmg = evaluate_creep_expectimax(c_type, map_manager, current_path)
        survival_rate = (exp_hp / max_hp) * 100.0 if max_hp > 0 else 0.0
        
        log_steps.append(f"🎲 Đánh giá quái [{c_type}]: HP tối đa = {max_hp:.0f} | Sát thương kỳ vọng = {exp_dmg:.1f} | HP dự báo = {exp_hp:.1f} ({survival_rate:.1f}%)")

        if exp_hp > best_expected_hp:
            best_expected_hp = exp_hp
            best_creep = c_type

    if best_creep is None:
        best_creep = "Normal"
        best_expected_hp = 100.0

    return best_creep, best_expected_hp, log_steps
