import random
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0, return_all=False):
    path_step_monitor.log_step(f"Khởi chạy AND_OR_GRAPH_SEARCH từ {start}")
    
    MAX_DEPTH = 100
    MAX_PATHS = 50
    
    def goal_test(state):
        return state == goal

    def get_actions(state):
        return map_manager.get_neighbors(state[0], state[1])

    def get_results(state, action):
        prob = map_manager.get_freeze_probability(action[0], action[1])
        if prob > 0:
            return [("slowed", action), ("normal", action)]
        else:
            return [("normal", action)]

    strategy_map = {}
    failed_states = set()
    memo_or = {}

    def or_search(state, path, depth):
        if goal_test(state):
            return []
            
        if depth >= MAX_DEPTH:
            h_dist = abs(state[0] - goal[0]) + abs(state[1] - goal[1])
            if h_dist < 5:
                return []
            return None

        if state in path or state in failed_states:
            return None

        if state in memo_or:
            return memo_or[state]
            
        actions = get_actions(state)
        # Sort actions by Manhattan distance to goal to explore optimal branches first
        actions.sort(key=lambda a: abs(a[0] - goal[0]) + abs(a[1] - goal[1]))
        
        found_any = False
        first_plan = None
        
        for action in actions:
            result_states = get_results(state, action)
            plan = and_search(result_states, path + [state], depth + 1)
            if plan is not None:
                found_any = True
                if first_plan is None:
                    first_plan = [action, plan]
                    
        if found_any:
            memo_or[state] = first_plan
            return first_plan
        else:
            failed_states.add(state)
            memo_or[state] = None
            return None

    def and_search(states, path, depth):
        plans = {}
        
        for env_status, next_node in states:
            path_step_monitor.log_node_state(next_node[0], next_node[1], "open")
            
            plan_s = or_search(next_node, path, depth)
            
            if plan_s is None and next_node != goal:
                return None
                
            plans[(env_status, next_node)] = plan_s
            
            if path:
                parent = path[-1]
                key = (parent[0], parent[1], env_status)
                if key not in strategy_map:
                    strategy_map[key] = []
                if next_node not in strategy_map[key]:
                    strategy_map[key].append(next_node)
                
        return plans

    or_search(start, [], 0)

    # Standalone path extraction helper traversing strategy_map along normal transitions
    all_extracted_paths = []

    def extract_all_paths_from_strategy(current_node, current_path):
        if len(all_extracted_paths) >= MAX_PATHS:
            return
        if current_node == goal:
            full_p = current_path + [current_node]
            if full_p not in all_extracted_paths:
                all_extracted_paths.append(full_p)
            return

        key = (current_node[0], current_node[1], "normal")
        next_nodes = strategy_map.get(key, [])
        if not isinstance(next_nodes, list):
            next_nodes = [next_nodes]

        for next_node in next_nodes:
            if len(all_extracted_paths) >= MAX_PATHS:
                break
            if next_node not in current_path:
                extract_all_paths_from_strategy(next_node, current_path + [current_node])

    extract_all_paths_from_strategy(start, [])
    
    if all_extracted_paths:
        path_step_monitor.log_step(f"AND-OR Search: Tìm thấy chiến lược với {len(all_extracted_paths)} đường đi khả thi!")
        
        # Format strategy_map for single-step simulation lookup
        sim_strategy = {}
        for k, v in strategy_map.items():
            if isinstance(v, list) and len(v) > 0:
                sim_strategy[k] = v[0]
            else:
                sim_strategy[k] = v
        map_manager.last_and_or_strategy = sim_strategy
        
        if return_all:
            return all_extracted_paths

        # Highlight nodes of selected path
        selected_path = all_extracted_paths[0]
        for px, py in selected_path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
                
        return selected_path

    path_step_monitor.log_step("AND-OR Search: Không tìm thấy chiến lược khả thi trong giới hạn độ sâu!")
    return None if not return_all else []

