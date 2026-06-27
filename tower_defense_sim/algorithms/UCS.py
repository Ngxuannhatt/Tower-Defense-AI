import heapq
import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy Uniform Cost Search (UCS) từ {start} đến {goal}")
    
    # Priority Queue stores: (g_cost, counter, position, path)
    # Using a counter to avoid comparing lists/tuples when g is equal
    counter = 0
    frontier = [(0.0, counter, start, [start])]
    reached = {start: 0.0}
    
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    while frontier:
        g, _, curr, path = heapq.heappop(frontier)
        
        # If we reached this with a higher cost than already known, skip
        if g > reached.get(curr, float('inf')):
            continue
            
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        path_step_monitor.log_step(f"Mở node: {curr}, cost g={g}")
        
        if delay > 0:
            time.sleep(delay)
            
        if curr == goal:
            path_step_monitor.log_step(f"🎉 Đã tìm thấy đích {goal} với chi phí {g}!")
            # Mark final path in GUI
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        neighbors = grid.get_neighbors(curr[0], curr[1])
        for neighbor in neighbors:
            g_new = g + 1.0 # step cost is uniform 1.0
            if neighbor not in reached or g_new < reached[neighbor]:
                reached[neighbor] = g_new
                counter += 1
                heapq.heappush(frontier, (g_new, counter, neighbor, path + [neighbor]))
                path_step_monitor.log_node_state(neighbor[0], neighbor[1], "open")
                path_step_monitor.log_step(f"Cập nhật node lân cận: {neighbor}, g={g_new}")
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None