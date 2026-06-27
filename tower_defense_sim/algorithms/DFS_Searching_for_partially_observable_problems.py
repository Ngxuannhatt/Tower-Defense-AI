from collections import deque
from .node import Node

# Hàm hỗ trợ kiểm tra xem state hiện tại có khớp với BẤT KỲ goal nào trong tập goals không
def is_state_goal(state, goals):
    for goal_mat in goals:
        match = True
        for r in range(len(state.matrix)):
            for c in range(len(state.matrix[0])):
                val_state = state.matrix[r][c]
                val_goal = goal_mat[r][c]
                
                # Bỏ qua nếu 1 trong 2 là None (không xác định/biết trước 1 phần)
                if val_state is not None and val_goal is not None:
                    if val_state != val_goal:
                        match = False
                        break
            if not match:
                break
        if match:
            return True # Khớp thành công với 1 goal
    return False

class Belief_Node:
    def __init__(self, state1, state2, parent=None, action="Bắt đầu"):
        self.state1 = state1
        self.state2 = state2
        self.parent = parent
        self.action = action

    # Cập nhật is_goal để nhận tập hợp các goals
    def is_goal(self, goals):
        return (
            is_state_goal(self.state1, goals)
            and
            is_state_goal(self.state2, goals)
        )

    def get_state_key(self):
        return (
            self.state1.get_state_key(),
            self.state2.get_state_key()
        )

def dfs_partially_observable(self):
    
    # Định nghĩa tập các Goal (bao nhiêu mảng cũng được)
    # Dùng None cho các vị trí không quan tâm / chưa biết
    goals = [
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ],
        [
            [0, None, 1],
            [None, 0, None],
            [None, None, 0]
        ]
    ]

    # Ma trận bắt đầu không giống nhau, có chứa phần tử không xác định (None)
    start1 = Node(
        0, 0,
        [
            [1, None, 1],
            [1, 0, 1],
            [None, 1, 1]
        ]
    )   

    start2 = Node(
        2, 2,
        [
            [None, 1, 0],
            [1, 1, None],
            [1, 1, 1]
        ]
    )

    root = Belief_Node(
        start1,
        start2,
        action="Bắt đầu"
    )

    frontier = deque([root])
    reached = set()

    steps_limit = 0

    while frontier:
        curr = frontier.pop()
        steps_limit += 1

        # ======================
        # GOAL TEST (Kiểm tra cả 2 đã đạt goal chưa)
        # ======================
        if curr.is_goal(goals):
            path = []
            temp = curr

            while temp is not None:
                path.append(temp)
                temp = temp.parent

            path.reverse()
            return path

        # ======================
        # REACHED TEST (Key gồm cả 2 state, chỉ bỏ qua nếu cả 2 giống hệt trạng thái cũ)
        # ======================
        state_key = curr.get_state_key()

        if state_key in reached:
            continue

        reached.add(state_key)

        # ======================
        # ACTION MOVE
        # ======================
        moves = [
            (-1, 0, "UP"),
            (1, 0, "DOWN"),
            (0, -1, "LEFT"),
            (0, 1, "RIGHT")
        ]

        for dr, dc, action_name in moves:
            s1 = apply_move(self,curr.state1, dr, dc, goals)
            s2 = apply_move(self,curr.state2, dr, dc, goals)

            frontier.append(
                Belief_Node(
                    s1,
                    s2,
                    parent=curr,
                    action=action_name
                )
            )

        # ======================
        # ACTION SUCK
        # ======================
        s1 = apply_suck(self,curr.state1, goals)
        s2 = apply_suck(self,curr.state2, goals)

        frontier.append(
            Belief_Node(
                s1,
                s2,
                parent=curr,
                action="SUCK"
            )
        )

        if steps_limit > 5000000:
            print("Quá thời hạn xử lý.")
            return None

    return None

def apply_move(self, state, dr, dc, goals):
    # Nếu ma trận này ĐÃ ĐẠT 1 GOAL -> Dừng lại, giữ nguyên trạng thái và đợi
    if is_state_goal(state, goals):
        return Node(
            state.x, 
            state.y, 
            state.matrix, 
            action="Đã tới đích, đang đợi"
        )

    nr = state.x + dr
    nc = state.y + dc

    # Nếu đi được thì cập nhật vị trí mới
    if 0 <= nr < self.n and 0 <= nc < self.n:
        return Node(
            nr,
            nc,
            state.matrix,
            action=f"Đi tới ({nr},{nc})"
        )

    # Nếu không đi được (đụng tường) thì giữ nguyên vị trí
    return Node(
        state.x,
        state.y,
        state.matrix,
        action="Không di chuyển được"
    )

def apply_suck(self, state, goals):
    # Nếu ma trận này ĐÃ ĐẠT 1 GOAL -> Không hút rác nữa, đứng đợi
    if is_state_goal(state, goals):
        return Node(
            state.x, 
            state.y, 
            state.matrix, 
            action="Đã tới đích, đang đợi"
        )

    new_mat = [row[:] for row in state.matrix]

    # Chỉ hút nếu có rác (1)
    if new_mat[state.x][state.y] == 1:
        new_mat[state.x][state.y] = 0

    return Node(
        state.x,
        state.y,
        new_mat,
        action=f"Hút rác tại ({state.x},{state.y})"
    )