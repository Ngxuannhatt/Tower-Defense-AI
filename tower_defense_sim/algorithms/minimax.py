import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import path_step_monitor
from algorithms import astar

def evaluate_creep_survival(creep_type: str, map_manager, path: list) -> float:
    """
    Hàm lượng giá: Tính toán lượng máu (HP) còn lại của quái vật sau khi đi hết đường đi 'path'.
    Công thức: HP còn lại = HP tối đa - Tổng sát thương gánh chịu.
    Các loại quái có đặc tính kháng/yếu khác nhau đối với từng loại tháp:
    1. Quái Nhanh (Fast): HP = 60. Giảm sát thương nhận từ tháp lửa (Fire), tăng sát thương từ tháp cơ bản (Basic).
    2. Quái Trâu (Tanky): HP = 200. Giảm sát thương nhận từ tháp cơ bản (Basic), tăng sát thương từ tháp lửa (Fire).
    3. Quái Thường (Normal): HP = 100. Nhận sát thương tiêu chuẩn từ tất cả các tháp.
    """
    if not path:
        return 0.0
        
    damage = 0.0
    for x, y in path:
        # Kiểm tra tất cả các tháp hiện có trên bản đồ
        for (tx, ty), t_type in map_manager.towers.items():
            dist = ((tx - x)**2 + (ty - y)**2)**0.5 # Tính khoảng cách Euclidean từ tháp đến ô quái đang đứng
            
            # Tính toán sát thương dựa trên loại tháp và tầm bắn
            if t_type == "Basic" and dist <= 3.0:
                if creep_type == "Fast":
                    damage += 12.0 # Quái nhanh nhận nhiều sát thương hơn từ tháp Basic
                elif creep_type == "Tanky":
                    damage += 8.0  # Quái trâu kháng bớt sát thương tháp Basic
                else:
                    damage += 10.0
            elif t_type == "Fire" and dist <= 4.0:
                if creep_type == "Fast":
                    damage += 7.2  # Quái nhanh kháng bớt sát thương tháp lửa
                elif creep_type == "Tanky":
                    damage += 27.0 # Quái trâu chịu nhiều sát thương hơn từ tháp lửa
                else:
                    damage += 18.0
            elif t_type == "Ice" and dist <= 2.0:
                if creep_type == "Fast":
                    damage += 12.0
                elif creep_type == "Tanky":
                    damage += 7.6
                else:
                    damage += 9.5
                    
    # Áp dụng hệ số tỉ lệ cân bằng game (chia cho 15.0 để quái không bị chết quá sớm khi chạy thử)
    damage = damage / 15.0

    if creep_type == "Fast":
        return max(0.0, 60.0 - damage)
    elif creep_type == "Tanky":
        return max(0.0, 200.0 - damage)
    else:
        return max(0.0, 100.0 - damage)

def minimax(map_manager, path: list, depth: int, is_maximizing: bool, creep_type: str = None, log_steps: list = None):
    """
    Thuật toán Minimax giới hạn độ sâu (Depth-Limited Minimax) mô phỏng cuộc đấu trí đối kháng:
    - Người chơi MAX (Muốn tối đa hóa sát thương / Cố gắng MINIMIZE lượng máu HP còn lại của quái).
    - AI MIN (Muốn tối đa hóa khả năng sinh tồn của quái / Cố gắng MAXIMIZE lượng máu HP còn lại khi quái về đích).
    """
    if log_steps is None:
        log_steps = []
        
    # Điều kiện dừng đệ quy: Đạt độ sâu giới hạn hoặc đường đi trống
    if depth == 0 or not path:
        val = evaluate_creep_survival(creep_type, map_manager, path)
        return val, None

    if is_maximizing:
        # Nhánh của người chơi (MAX): Tìm cách XÂY THÁP để quái vật có HP thấp nhất (tối thiểu hóa HP)
        best_val = float('inf')
        best_move = None
        
        # Xác định các ô đất trống cạnh đường đi hiện tại để thử nghiệm xây tháp
        path_set = set(path)
        candidates = []
        for px, py in path:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                cx, cy = px + dx, py + dy
                if map_manager.is_valid_coord(cx, cy) and not map_manager.is_obstacle(cx, cy) and (cx, cy) not in path_set:
                    if (cx, cy) not in candidates and (cx, cy) != map_manager.start and (cx, cy) != map_manager.goal:
                        candidates.append((cx, cy))
                        
        # Sắp xếp và chọn ra 2 ô trống tốt nhất gần điểm xuất phát nhất để chạy giả định (tăng tốc độ chạy)
        candidates = sorted(candidates, key=lambda c: abs(c[0]-map_manager.start[0]) + abs(c[1]-map_manager.start[1]))[:2]
        
        if not candidates:
            val = evaluate_creep_survival(creep_type, map_manager, path)
            return val, None
            
        # Thử giả lập đặt các loại tháp (Basic, Fire, Ice) lên các ô ứng viên
        for pos in candidates:
            for t_type in ["Basic", "Fire", "Ice"]:
                # Đặt thử tháp phòng thủ
                map_manager.add_tower(pos[0], pos[1], t_type)
                
                # Tính toán lại đường đi ngắn nhất của quái sau khi bị đặt tháp mới
                was_silenced = path_step_monitor.is_silenced()
                path_step_monitor.set_silenced(True)
                new_path = astar.solve(map_manager.start, map_manager.goal, map_manager, delay=0.0)
                path_step_monitor.set_silenced(was_silenced)
                
                # Gọi đệ quy Minimax xuống tầng dưới (Lượt của AI MIN chọn loại quái)
                val, _ = minimax(map_manager, new_path, depth - 1, False, creep_type, log_steps)
                
                # Khôi phục trạng thái bản đồ (gỡ bỏ tháp vừa thử nghiệm)
                map_manager.remove_tower(pos[0], pos[1])
                
                log_steps.append(f"   ├─ Player phản công: Xây {t_type} tại {pos} -> HP quái còn: {val:.1f}")
                
                # Lựa chọn tháp nào làm lượng máu HP còn lại của quái nhỏ nhất
                if val < best_val:
                    best_val = val
                    best_move = (pos, t_type)
                    
        return best_val, best_move
    else:
        # Nhánh của AI (MIN): Tìm cách SINH QUÁI để lượng máu HP sống sót về đích là lớn nhất (tối đa hóa HP)
        best_val = float('-inf')
        best_creep = None
        
        # Thử giả lập sinh 3 loại quái vật
        for c_type in ["Normal", "Fast", "Tanky"]:
            log_steps.append(f"AI (MIN) giả lập sinh quái: {c_type}")
            # Gọi đệ quy Minimax xuống tầng dưới (Lượt của Player thử xây tháp)
            val, _ = minimax(map_manager, path, depth - 1, True, c_type, log_steps)
            log_steps.append(f" └─ HP dự báo tốt nhất cho quái {c_type}: {val:.1f}")
            
            # Chọn loại quái nào có HP còn lại cao nhất để đối đầu hệ thống
            if val > best_val:
                best_val = val
                best_creep = c_type
                
        return best_val, best_creep

def decide_optimal_creep(map_manager, path: list):
    """
    Hàm quyết định loại quái tối ưu nhất bằng cây đánh giá Minimax.
    Độ sâu duyệt depth = 2:
    - Tầng 1: AI (MIN) chọn loại quái.
    - Tầng 2: Player (MAX) phản công bằng cách xây thêm tháp.
    Trả về: (tên_loại_quái_tối_ưu, máu_dự_báo, danh_sách_log_các_bước)
    """
    log_steps = []
    best_val, best_creep = minimax(map_manager, path, depth=2, is_maximizing=False, log_steps=log_steps)
    return best_creep, best_val, log_steps
