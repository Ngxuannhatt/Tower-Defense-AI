class Node:
    def __init__(self, x, y, matrix, parent=None, action="Bắt đầu"):
        self.x = x
        self.y = y
        # Copy ma trận độc lập (dùng list comprehension thay cho numpy để nhẹ UI)
        self.matrix = [row[:] for row in matrix]
        self.parent = parent
        self.action = action

    def is_goal(self):
        for row in self.matrix:
            if 1 in row:  # Còn số 1 nghĩa là còn dơ
                return False
        return True

    def get_state_key(self):
        return (self.x, self.y, tuple(tuple(row) for row in self.matrix))
   