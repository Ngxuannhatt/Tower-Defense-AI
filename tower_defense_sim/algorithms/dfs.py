import time
import path_step_monitor

def dfs(start: tuple, goal: tuple, grid) -> list:
    """
    Hàm DFS tiêu chuẩn (không ghi log hiển thị lên GUI).
    Sử dụng ngăn xếp (stack LIFO) kết hợp tập hợp visited để tìm đường đi cơ bản.
    """
    visited = set()
    stack = [(start, [start])] # Mỗi phần tử trong stack lưu: (tọa độ_hiện_tại, đường_đi_đến_đó)
    
    while stack:
        curr, path = stack.pop() # Lấy phần tử trên cùng ra (LIFO)
        if curr == goal:
            return path
            
        if curr not in visited:
            visited.add(curr)
            neighbors = grid.get_neighbors(curr[0], curr[1])
            for nxt in neighbors:
                if nxt not in visited:
                    stack.append((nxt, path + [nxt]))
    return None

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Giải thuật tìm kiếm theo chiều sâu (DFS - Depth-First Search).
    - Đi sâu nhất có thể dọc theo mỗi nhánh trước khi quay lui (backtracking).
    - Sử dụng cấu trúc ngăn xếp (Stack LIFO). Ở đây ta dùng kiểu danh sách (list) với pop().
    - Lưu ý: DFS không đảm bảo tìm thấy đường đi ngắn nhất.
    """
    path_step_monitor.log_step(f"Khởi chạy DFS từ {start} đến {goal}")
    visited = set()
    # Khởi tạo ngăn xếp chứa tuple: (tọa độ hiện tại, đường đi từ start đến tọa độ này)
    stack = [(start, [start])]
    
    while stack:
        # Lấy phần tử được thêm vào muộn nhất ra khỏi ngăn xếp (cơ chế LIFO)
        curr, path = stack.pop()
        
        # Nếu ô này đã được duyệt từ một nhánh khác ngắn hơn/nhanh hơn, bỏ qua
        if curr in visited:
            continue
            
        # Đánh dấu ô hiện tại đã được duyệt và chuyển sang màu closed trên GUI
        visited.add(curr)
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        path_step_monitor.log_step(f"Duyệt DFS: {curr}")
        
        if delay > 0:
            time.sleep(delay)
            
        # Nếu đã đến đích, dừng giải thuật và hiển thị đường đi
        if curr == goal:
            path_step_monitor.log_step("🎉 DFS đã tìm thấy đích!")
            # Vẽ đường đi màu xanh lá/vàng trên GUI
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        # Lấy các ô hàng xóm lân cận
        neighbors = grid.get_neighbors(curr[0], curr[1])
        for nxt in neighbors:
            if nxt not in visited:
                # Cập nhật trạng thái ô lân cận thành open (đang chờ xét)
                path_step_monitor.log_node_state(nxt[0], nxt[1], "open")
                # Đưa ô hàng xóm và đường đi mới vào đỉnh ngăn xếp
                stack.append((nxt, path + [nxt]))
                if delay > 0:
                    time.sleep(delay * 0.2)
                    
    path_step_monitor.log_step("DFS: Không tìm thấy đường đi!")
    return None
