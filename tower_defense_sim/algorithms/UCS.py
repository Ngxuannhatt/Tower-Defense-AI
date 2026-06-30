import heapq
import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật tìm kiếm với chi phí đồng nhất (UCS - Uniform Cost Search hoặc thuật toán Dijkstra).
    - Mở rộng các nút có tổng chi phí tích lũy g(n) từ nút gốc thấp nhất.
    - Sử dụng cấu trúc hàng đợi ưu tiên (Priority Queue - Min-Heap) để luôn lấy ra nút rẻ nhất.
    - Đảm bảo tìm thấy đường đi tối ưu nhất (chi phí thấp nhất) ngay cả khi chi phí giữa các ô khác nhau.
    """
    path_step_monitor.log_step(f"Khởi chạy Uniform Cost Search (UCS) từ {start} đến {goal}")
    
    # Bộ đếm tăng dần (counter) để giải quyết xung đột khi so sánh tuple trong Heap của Python.
    # Nếu hai nút có g_cost bằng nhau, Python sẽ so sánh phần tử tiếp theo là counter.
    # Điều này giúp tránh lỗi TypeError khi Python cố so sánh trực tiếp tọa độ (tuples) hoặc đường đi (lists).
    counter = 0
    
    # Hàng đợi ưu tiên lưu các phần tử dạng: (g_cost, counter, position, path)
    frontier = [(0.0, counter, start, [start])]
    
    # Từ điển lưu chi phí nhỏ nhất tìm được từ điểm xuất phát đến mỗi nút (đóng vai trò REACHED)
    reached = {start: 0.0}
    
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    while frontier:
        # Lấy nút có tổng chi phí g_cost tích lũy nhỏ nhất ra khỏi Heap (Min-Heap)
        g, _, curr, path = heapq.heappop(frontier)
        
        # Nếu chi phí g hiện tại lớn hơn chi phí tốt nhất đã tìm thấy để đến ô 'curr', bỏ qua (cắt tỉa)
        if g > reached.get(curr, float('inf')):
            continue
            
        # Đánh dấu ô hiện tại là closed (đã duyệt tối ưu)
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        path_step_monitor.log_step(f"Mở node: {curr}, cost g={g}")
        
        if delay > 0:
            time.sleep(delay)
            
        # Nếu đã đạt tới đích, dừng thuật toán và vẽ đường đi
        if curr == goal:
            path_step_monitor.log_step(f"🎉 Đã tìm thấy đích {goal} với chi phí {g}!")
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        # Lấy danh sách hàng xóm lân cận
        neighbors = grid.get_neighbors(curr[0], curr[1])
        for neighbor in neighbors:
            # Ở bản đồ lưới ô vuông thông thường, chi phí di chuyển giữa 2 ô liền kề là 1.0
            g_new = g + 1.0 
            
            # Nếu phát hiện đường đi mới rẻ hơn đường đi đã lưu trước đó tới ô hàng xóm này
            if neighbor not in reached or g_new < reached[neighbor]:
                reached[neighbor] = g_new
                counter += 1
                # Đẩy nút hàng xóm mới vào hàng đợi ưu tiên
                heapq.heappush(frontier, (g_new, counter, neighbor, path + [neighbor]))
                
                # Chuyển trạng thái hiển thị của ô hàng xóm thành open (đang chờ duyệt)
                path_step_monitor.log_node_state(neighbor[0], neighbor[1], "open")
                path_step_monitor.log_step(f"Cập nhật node lân cận: {neighbor}, g={g_new}")
                
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None