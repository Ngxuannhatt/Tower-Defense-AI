import heapq
import time
import path_step_monitor

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve(start, goal, grid, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy Greedy_Search từ {start} đến {goal}")
    
    frontier = []
    entry_id = 0
    heapq.heappush(frontier, (heuristic(start, goal), entry_id, start))
    frontier_states = {start}
    
    reached = set()
    
    parent = {start: None}
    
    while frontier:
        _, _, n = heapq.heappop(frontier)
        if n in frontier_states:
            frontier_states.remove(n)
            
        path_step_monitor.log_node_state(n[0], n[1], "closed")
        path_step_monitor.log_step(f"Mở node (Greedy): {n}, h={heuristic(n, goal)}")
        
        if delay > 0:
            time.sleep(delay)
            
        if n == goal:
            path = []
            curr = goal
            while curr is not None:
                path.append(curr)
                curr = parent[curr]
            path.reverse()
            
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        reached.add(n)
        
        neighbors = grid.get_neighbors(n[0], n[1])
        for m in neighbors:
            if m not in frontier_states and m not in reached:
                parent[m] = n
                h_m = heuristic(m, goal)
                entry_id += 1
                heapq.heappush(frontier, (h_m, entry_id, m))
                frontier_states.add(m)
                
                path_step_monitor.log_node_state(m[0], m[1], "open")
                path_step_monitor.log_step(f"Cập nhật neighbor (Greedy): {m}, h={h_m}")
            else:
                continue
                
            if delay > 0:
                time.sleep(delay * 0.5)
                
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None
