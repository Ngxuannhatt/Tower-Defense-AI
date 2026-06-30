import heapq
import time
import path_step_monitor

def heuristic(a, b):
    # Sử dụng khoảng cách Manhattan làm hàm Heuristic ước lượng khoảng cách tới đích
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật Tìm kiếm Tham lam theo Lựa chọn Tốt nhất (Greedy Best-First Search).
    - Đánh giá các nút chỉ dựa trên ước lượng khoảng cách tới đích h(n) chứ không cộng thêm g(n).
    - Thuật toán mang tính "tham lam" vì tại mỗi bước, nó luôn chọn đi vào ô có vẻ gần đích nhất.
    - Nhược điểm: Không đảm bảo tìm thấy đường đi ngắn nhất, dễ bị đánh lừa đi vào ngõ cụt
      hoặc đi vòng vèo nếu gặp chướng ngại vật lớn chắn trước đích.
    """
    path_step_monitor.log_step(f"Khởi chạy Greedy_Search từ {start} đến {goal}")
    
    # Hàng đợi ưu tiên lưu các phần tử dạng: (heuristic_cost, entry_id, position)
    frontier = []
    
    # Bộ đếm tăng dần làm tie-breaker để giải quyết xung đột khi đẩy vào heapq của Python
    entry_id = 0
    heapq.heappush(frontier, (heuristic(start, goal), entry_id, start))
    
    # Tập hợp các nút đang nằm trong hàng đợi biên (tránh xét trùng lặp)
    frontier_states = {start}
    
    # Tập hợp các nút đã duyệt qua hoàn tất (Closed list)
    reached = set()
    
    # Từ điển lưu quan hệ cha-con để truy vết ngược đường đi
    parent = {start: None}
    
    while frontier:
        # Lấy nút có giá trị Heuristic h(n) nhỏ nhất (có vẻ gần đích nhất) ra khỏi Heap
        _, _, n = heapq.heappop(frontier)
        if n in frontier_states:
            frontier_states.remove(n)
            
        path_step_monitor.log_node_state(n[0], n[1], "closed")
        path_step_monitor.log_step(f"Mở node (Greedy): {n}, h={heuristic(n, goal)}")
        
        if delay > 0:
            time.sleep(delay)
            
        # Khi chạm đích, truy vết ngược lại để hoàn tất đường đi
        if n == goal:
            path = []
            curr = goal
            while curr is not None:
                path.append(curr)
                curr = parent[curr]
            path.reverse()
            
            # Cập nhật đường đi lên giao diện
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        reached.add(n)
        
        # Duyệt qua các hàng xóm
        neighbors = grid.get_neighbors(n[0], n[1])
        for m in neighbors:
            # Chỉ duyệt nếu ô hàng xóm này chưa nằm trong frontier và chưa được closed
            if m not in frontier_states and m not in reached:
                parent[m] = n
                h_m = heuristic(m, goal)
                entry_id += 1
                # Đẩy ô hàng xóm cùng chi phí h_m vào hàng đợi ưu tiên
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
