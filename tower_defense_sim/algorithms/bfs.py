from collections import deque
import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật tìm kiếm theo chiều rộng (BFS - Breadth-First Search).
    - Duyệt qua các nút theo từng cấp độ sâu (từng lớp sóng loang ra).
    - Sử dụng hàng đợi FIFO (First In First Out) để quản lý biên tìm kiếm (frontier).
    - Đảm bảo tìm thấy đường đi ngắn nhất (về mặt số bước đi) nếu chi phí mỗi bước bằng nhau.
    """
    path_step_monitor.log_step(f"Bắt đầu thuật toán BFS từ {start} đến {goal}")
    
    node = start
    
    # Nếu điểm bắt đầu trùng điểm đích, trả về ngay đường đi chứa điểm xuất phát
    if node == goal:
        return [node]
        
    # Hàng đợi FIFO để lưu các nút chuẩn bị duyệt (Frontier)
    frontier = deque([node])
    
    # Tập hợp (set) để kiểm tra nhanh các nút đang nằm trong hàng đợi biên (tránh quét trùng)
    frontier_states = {node}
    
    # Tập hợp ghi nhận các nút đã khám phá hoặc đã đưa vào hàng đợi
    reached = {node}
    
    # Từ điển lưu cha-con để truy vết lại đường đi sau khi tìm thấy đích
    parent = {start: None}
    
    # Vòng lặp chính: Duyệt cho đến khi không còn nút nào trong hàng đợi
    while frontier:
        # Lấy nút đầu tiên ra khỏi hàng đợi (cơ chế FIFO)
        node = frontier.popleft()
        frontier_states.remove(node)
        
        # Đánh dấu nút này đã duyệt xong (màu closed trên GUI)
        path_step_monitor.log_node_state(node[0], node[1], "closed")
        path_step_monitor.log_step(f"Mở node (BFS): {node}")
        
        if delay > 0:
            time.sleep(delay)
            
        # Lấy các ô hàng xóm hợp lệ (4 hướng: Lên, Xuống, Trái, Phải, không phải chướng ngại vật)
        neighbors = grid.get_neighbors(node[0], node[1])
        for child in neighbors:
            # Chỉ xét những ô chưa từng được duyệt và chưa nằm trong hàng đợi biên
            if child not in reached and child not in frontier_states:
                parent[child] = node # Lưu lại nút cha của ô hiện tại
                
                # Nếu hàng xóm tiếp theo là đích, thực hiện truy vết ngược lại đường đi
                if child == goal:
                    path = []
                    curr = child
                    while curr is not None:
                        path.append(curr)
                        curr = parent[curr]
                    path.reverse() # Đảo ngược danh sách từ Start -> Goal
                    
                    # Đánh dấu các ô trên đường đi cuối cùng màu path (xanh lục/vàng trên GUI)
                    for px, py in path:
                        if (px, py) != start and (px, py) != goal:
                            path_step_monitor.log_node_state(px, py, "path")
                    return path
                    
                # Đánh dấu đã khám phá ô này
                reached.add(child)
                
                # Thêm vào hàng đợi để chuẩn bị duyệt tiếp theo cấp độ sâu của nó
                frontier.append(child)
                frontier_states.add(child)
                
                # Cập nhật hiển thị ô này là "đang chờ duyệt" (màu open trên GUI)
                path_step_monitor.log_node_state(child[0], child[1], "open")
                path_step_monitor.log_step(f"Khám phá neighbor (BFS): {child}")
                
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None
