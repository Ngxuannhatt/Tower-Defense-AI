import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as st
import threading
import queue
import time
import path_step_monitor

class TowerDefenseGUI:
    def __init__(self, root, map_manager, pathfinder):
        self.root = root
        self.map_manager = map_manager
        self.pathfinder = pathfinder
        
        # Configure root window
        self.root.title("Tower Defense Pathfinding Simulator")
        self.root.geometry("1100x650")
        self.root.configure(bg="#0f172a")  # Slate 900
        
        # UI Queue for thread-safe updates
        self.ui_queue = queue.Queue()
        
        # Grid visual state cache (tracks node state colors to keep search artifacts)
        # 0: empty, 1: open, 2: closed, 3: path
        self.search_node_states = {}
        
        # Active path lists
        self.current_path = []
        
        # Enemy simulation state
        self.enemy_id = None
        self.enemy_pos = None  # (float_x, float_y) current sub-pixel position
        self.enemy_path_index = 0
        self.is_simulating = False
        self.simulation_thread = None
        
        # Setup modern dark style
        self.setup_styles()
        
        # Setup layout
        self.create_widgets()
        
        # Register step monitor callbacks
        path_step_monitor.register_log_callback(self.queue_log)
        path_step_monitor.register_node_callback(self.queue_node_state)
        
        # Start queue processing loop
        self.root.after(30, self.process_ui_queue)
        
        # Initial map rendering
        self.redraw_grid()

    def setup_styles(self):
        """Sets up ttk fonts and styles for custom dark widgets."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Custom configurations
        self.style.configure("TFrame", background="#1e293b")  # Slate 800
        self.style.configure("TLabel", background="#1e293b", foreground="#f8fafc", font=("Segoe UI", 10))
        self.style.configure("TCombobox", fieldbackground="#0f172a", background="#334155", foreground="#f8fafc")
        
        # Style headings
        self.style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground="#60a5fa")
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#3b82f6", background="#0f172a")

    def create_widgets(self):
        """Creates and layouts the Control Panel, Grid Area, Steps Monitor, and Status Bar."""
        # Top banner
        title_lbl = ttk.Label(self.root, text="🛡️ TOWER DEFENSE PATHFINDING SIMULATOR", style="Title.TLabel")
        title_lbl.pack(pady=10, fill=tk.X, padx=15)
        
        # Main Frame to hold left, center, right panels
        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 1. Left Panel: Controls (width ~250px)
        ctrl_frame = tk.Frame(main_frame, bg="#1e293b", bd=1, relief=tk.FLAT)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        ctrl_frame.pack_propagate(False)
        ctrl_frame.config(width=260)
        
        # Control Panel title
        ctrl_lbl = tk.Label(ctrl_frame, text="BẢNG ĐIỀU KHIỂN", bg="#1e293b", fg="#60a5fa", font=("Segoe UI", 12, "bold"))
        ctrl_lbl.pack(pady=10)
        
        # Alg dropdown
        tk.Label(ctrl_frame, text="Thuật toán tìm đường:", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.alg_var = tk.StringVar(value="A*")
        self.alg_combo = ttk.Combobox(ctrl_frame, textvariable=self.alg_var, values=["A*", "Dijkstra", "Incremental A*", "D*"], state="readonly")
        self.alg_combo.pack(fill=tk.X, padx=15, pady=(2, 10))
        self.alg_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Tower type dropdown
        tk.Label(ctrl_frame, text="Loại trụ phòng thủ:", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.tower_var = tk.StringVar(value="Basic Tower")
        self.tower_combo = ttk.Combobox(ctrl_frame, textvariable=self.tower_var, values=["Basic Tower (Purple)", "Ice Tower (Cyan)", "Fire Tower (Orange)"], state="readonly")
        self.tower_combo.pack(fill=tk.X, padx=15, pady=(2, 10))
        
        # Delay slider (speed)
        tk.Label(ctrl_frame, text="Độ trễ từng bước (ms):", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.delay_scale = tk.Scale(ctrl_frame, from_=0, to=500, orient=tk.HORIZONTAL, bg="#1e293b", fg="#f8fafc", troughcolor="#0f172a", activebackground="#3b82f6", bd=0, highlightthickness=0)
        self.delay_scale.set(50)  # default 50ms delay
        self.delay_scale.pack(fill=tk.X, padx=15, pady=(2, 15))
        
        # Buttons
        self.btn_find = self.create_styled_button(ctrl_frame, "Tìm Đường Lại", self.start_pathfinding_thread, "#3b82f6", "#2563eb")
        self.btn_find.pack(fill=tk.X, padx=15, pady=5)
        
        self.btn_simulate = self.create_styled_button(ctrl_frame, "Bắt Đầu Mô Phỏng", self.start_enemy_simulation, "#10b981", "#059669")
        self.btn_simulate.pack(fill=tk.X, padx=15, pady=5)
        
        self.btn_reset = self.create_styled_button(ctrl_frame, "Reset Lưới", self.reset_grid, "#ef4444", "#dc2626")
        self.btn_reset.pack(fill=tk.X, padx=15, pady=5)
        
        self.btn_clear_path = self.create_styled_button(ctrl_frame, "Xóa Tìm Kiếm", self.clear_search_visuals, "#475569", "#334155")
        self.btn_clear_path.pack(fill=tk.X, padx=15, pady=5)
        
        # Quick guide
        guide_text = "💡 Hướng dẫn:\n• Click trái: Đặt trụ\n• Kéo trái: Vẽ nhanh trụ\n• Click/Kéo phải: Xóa trụ\n• Bắt đầu tìm đường trước khi chạy mô phỏng."
        guide_lbl = tk.Label(ctrl_frame, text=guide_text, bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 8), justify=tk.LEFT)
        guide_lbl.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)
        
        # 2. Center Panel: Canvas grid
        self.grid_frame = tk.Frame(main_frame, bg="#0f172a")
        self.grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calculate cell size based on grid 20x20 inside 500x500
        self.grid_size = 20
        self.cell_size = 25
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size
        
        self.canvas = tk.Canvas(self.grid_frame, width=self.canvas_width, height=self.canvas_height, bg="#020617", highlightthickness=1, highlightbackground="#334155")
        self.canvas.pack(anchor=tk.CENTER, expand=True)
        
        # Canvas Mouse bindings
        self.canvas.bind("<Button-1>", self.on_canvas_left_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_left_drag)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<B3-Motion>", self.on_canvas_right_drag)
        
        # 3. Right Panel: Steps Monitor (width ~320px)
        monitor_frame = tk.Frame(main_frame, bg="#1e293b", bd=1, relief=tk.FLAT)
        monitor_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        monitor_frame.pack_propagate(False)
        monitor_frame.config(width=340)
        
        monitor_lbl = tk.Label(monitor_frame, text="LOG THUẬT TOÁN (REAL-TIME)", bg="#1e293b", fg="#60a5fa", font=("Segoe UI", 12, "bold"))
        monitor_lbl.pack(pady=10)
        
        # Scrolled Text Box
        self.log_area = st.ScrolledText(monitor_frame, wrap=tk.WORD, bg="#020617", fg="#a7f3d0", insertbackground="white", font=("Consolas", 9), bd=0, highlightthickness=1, highlightbackground="#334155")
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        self.log_area.insert(tk.END, "Sẵn sàng đón nhận log thuật toán...\n")
        self.log_area.config(state=tk.DISABLED)
        
        # 4. Status Bar (bottom)
        self.status_bar = tk.Frame(self.root, bg="#0f172a", bd=1, relief=tk.FLAT)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 10))
        
        # LED indicator
        self.led = tk.Canvas(self.status_bar, width=12, height=12, bg="#0f172a", bd=0, highlightthickness=0)
        self.led.pack(side=tk.LEFT, padx=(5, 5))
        self.set_led_color("#10b981")  # Green for ready
        
        self.status_lbl = tk.Label(self.status_bar, text="Trạng thái: Sẵn sàng", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9, "bold"))
        self.status_lbl.pack(side=tk.LEFT)

    def set_led_color(self, color):
        self.led.delete("all")
        self.led.create_oval(2, 2, 10, 10, fill=color, outline="#334155")

    def create_styled_button(self, parent, text, command, normal_bg, hover_bg):
        """Creates a custom modern flat button with hover animations."""
        btn = tk.Button(parent, text=text, command=command, bg=normal_bg, fg="#ffffff", activebackground=hover_bg, activeforeground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), cursor="hand2")
        
        # Hover effect bindings
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))
        return btn

    def get_tower_color(self, tower_type):
        """Returns colors for different tower types to enhance aesthetics."""
        if "Ice" in tower_type:
            return "#06b6d4"  # Cyan
        elif "Fire" in tower_type:
            return "#f97316"  # Orange
        else:
            return "#8b5cf6"  # Purple/Indigo for Basic Tower

    def redraw_grid(self):
        """Redraws the entire grid canvas based on MapManager and search states."""
        self.canvas.delete("grid_elements")
        self.canvas.delete("path_elements")
        
        # Redraw all cells
        for x in range(self.map_manager.width):
            for y in range(self.map_manager.height):
                coord = (x, y)
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Check color mapping
                if coord == self.map_manager.start:
                    color = "#10b981"  # Emerald Green
                    text = "S"
                elif coord == self.map_manager.goal:
                    color = "#ef4444"  # Rose Red
                    text = "G"
                elif self.map_manager.is_obstacle(x, y):
                    # Find color based on custom property or draw standard
                    # In this grid, we store towers in set.
                    # We can store tower types or just map them to purple for now.
                    # Let's check if we have custom types. We will dynamically assign color based on grid state
                    color = "#8b5cf6"  # default Basic
                    text = ""
                elif coord in self.current_path:
                    color = "#f59e0b"  # Golden/Yellow for path
                    text = ""
                elif self.search_node_states.get(coord) == "closed":
                    color = "#1e3a8a"  # Dark blue for closed
                    text = ""
                elif self.search_node_states.get(coord) == "open":
                    color = "#0369a1"  # Cyan-blue for open
                    text = ""
                else:
                    color = "#0f172a"  # Slate 900
                    text = ""
                
                # Draw rect
                outline_color = "#334155" if color == "#0f172a" else "#475569"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline_color, tags="grid_elements")
                
                if text:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, text=text, fill="#ffffff", font=("Segoe UI", 10, "bold"), tags="grid_elements")

        # Redraw final path connecting line if path exists
        if len(self.current_path) > 1:
            points = []
            for px, py in self.current_path:
                cx = px * self.cell_size + self.cell_size // 2
                cy = py * self.cell_size + self.cell_size // 2
                points.append((cx, cy))
            
            # Draw line segments to make path look premium
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i+1]
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#fbbf24", width=3, capstyle=tk.ROUND, tags="path_elements")

        # Re-render enemy if simulating
        if self.is_simulating and self.enemy_pos is not None:
            ex, ey = self.enemy_pos
            ecx = ex * self.cell_size + self.cell_size // 2
            ecy = ey * self.cell_size + self.cell_size // 2
            r = 7
            self.enemy_id = self.canvas.create_oval(ecx - r, ecy - r, ecx + r, ecy + r, fill="#ef4444", outline="#ffffff", width=2)

    def on_algorithm_change(self, event):
        """Callback when pathfinding algorithm is changed from dropdown."""
        alg = self.alg_var.get()
        self.pathfinder.set_algorithm(alg)
        self.write_to_log(f"\n--- Chọn thuật toán: {alg} ---\n")
        self.status_lbl.config(text=f"Trạng thái: Thuật toán {alg} được chọn.")
        
        # Reset incremental caches on algo change to avoid conflicts
        self.clear_search_visuals()

    def get_cell_coord(self, event):
        """Converts pixel coordinate on canvas to grid coordinates."""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        return x, y

    def on_canvas_left_click(self, event):
        """Places a tower on left click."""
        x, y = self.get_cell_coord(event)
        if self.map_manager.add_tower(x, y):
            tower_type = self.tower_var.get()
            self.write_to_log(f"Đặt {tower_type} tại ô ({x}, {y})\n")
            self.redraw_grid()
            
            # Dynamic Re-planning during simulation
            if self.is_simulating:
                self.replan_during_movement()

    def on_canvas_left_drag(self, event):
        """Draws towers continuously on click & drag."""
        x, y = self.get_cell_coord(event)
        if self.map_manager.add_tower(x, y):
            self.redraw_grid()
            
            # Dynamic Re-planning during simulation
            if self.is_simulating:
                self.replan_during_movement()

    def on_canvas_right_click(self, event):
        """Removes a tower on right click."""
        x, y = self.get_cell_coord(event)
        if self.map_manager.remove_tower(x, y):
            self.write_to_log(f"Xóa trụ tại ô ({x}, {y})\n")
            self.redraw_grid()
            
            # Dynamic Re-planning during simulation
            if self.is_simulating:
                self.replan_during_movement()

    def on_canvas_right_drag(self, event):
        """Erases towers continuously on right click & drag."""
        x, y = self.get_cell_coord(event)
        if self.map_manager.remove_tower(x, y):
            self.redraw_grid()
            
            # Dynamic Re-planning during simulation
            if self.is_simulating:
                self.replan_during_movement()

    def start_pathfinding_thread(self):
        """Spawns background thread to run pathfinder solve method without locking GUI."""
        if self.is_simulating:
            self.write_to_log("⚠️ Vui lòng chờ mô phỏng kẻ địch chạy xong!\n")
            return
            
        # Get UI config
        delay_val = self.delay_scale.get() / 1000.0  # convert ms to seconds
        self.pathfinder.set_delay(delay_val)
        
        # Prepare visuals
        self.clear_search_visuals()
        self.set_led_color("#f59e0b")  # Yellow/Amber for running
        self.status_lbl.config(text="Trạng thái: Đang tính toán đường đi...")
        
        # Clear log area
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        # Spawn thread
        self.btn_find.config(state=tk.DISABLED)
        self.btn_simulate.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.DISABLED)
        
        threading.Thread(target=self.run_pathfinder_bg, daemon=True).start()

    def run_pathfinder_bg(self):
        """Worker thread method."""
        try:
            # For A* and Dijkstra we force reset. 
            # For incremental algos, if we clicked Find Path, we force reset to search from scratch.
            path = self.pathfinder.find_path(force_init=True)
            self.ui_queue.put(('path_completed', path))
        except Exception as e:
            self.ui_queue.put(('error', str(e)))

    def replan_during_movement(self):
        """
        Dynamically triggers path planning from the enemy's NEXT node position to goal 
        when an obstacle is modified mid-flight.
        """
        if not self.is_simulating or self.enemy_path_index >= len(self.current_path) - 1:
            return
            
        # The enemy is heading towards this next node
        next_node = self.current_path[self.enemy_path_index + 1]
        
        # Check if the remaining path is blocked by the change
        is_blocked = False
        for i in range(self.enemy_path_index + 1, len(self.current_path)):
            coord = self.current_path[i]
            if self.map_manager.is_obstacle(coord[0], coord[1]):
                is_blocked = True
                break
                
        # If blocked or we are using Incremental/D* algorithm (which always update graph edges), replan
        is_dynamic_algo = self.alg_var.get() in ["Incremental A*", "D*"]
        
        if is_blocked or is_dynamic_algo:
            self.write_to_log("🚨 Phát hiện lưới thay đổi! Đang tính lại đường đi...\n")
            
            # Temporarily set delay to 0 for fast dynamic updates
            old_delay = self.pathfinder.delay
            self.pathfinder.set_delay(0.0)
            
            # Resolve new path from the next node
            new_path = self.pathfinder.find_path(start=next_node, force_init=False)
            self.pathfinder.set_delay(old_delay)
            
            if new_path:
                # Merge the traversed path up to next_node with the new path
                completed_part = self.current_path[:self.enemy_path_index + 2]
                self.current_path = completed_part + new_path[1:]
                self.write_to_log(f"✅ Tìm thấy đường đi mới thay thế! Kích thước: {len(self.current_path)}\n")
            else:
                self.write_to_log("❌ ĐƯỜNG ĐI BỊ CHẶN HOÀN TOÀN! Không tìm thấy đường mới.\n")
                self.status_lbl.config(text="Trạng thái: Đường đi bị chặn hoàn toàn!")
                self.set_led_color("#ef4444")
            
            self.redraw_grid()

    def start_enemy_simulation(self):
        """Starts the enemy movement along the current_path."""
        if not self.current_path:
            self.write_to_log("⚠️ Chưa tìm được đường đi! Hãy bấm 'Tìm Đường Lại' trước.\n")
            return
            
        # Make sure start and goal are walkable and path exists
        if self.map_manager.is_obstacle(self.map_manager.start[0], self.map_manager.start[1]) or \
           self.map_manager.is_obstacle(self.map_manager.goal[0], self.map_manager.goal[1]):
            self.write_to_log("⚠️ Điểm xuất phát hoặc điểm đích bị chặn bởi trụ!\n")
            return
            
        self.is_simulating = True
        self.enemy_path_index = 0
        start_x, start_y = self.current_path[0]
        self.enemy_pos = (float(start_x), float(start_y))
        
        self.btn_find.config(state=tk.DISABLED)
        self.btn_simulate.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.DISABLED)
        
        self.write_to_log("\n--- Bắt đầu mô phỏng di chuyển kẻ địch ---\n")
        self.status_lbl.config(text="Trạng thái: Kẻ địch đang di chuyển...")
        self.set_led_color("#3b82f6")  # Blue for running simulation
        
        # Launch animation loop
        self.run_animation_step()

    def run_animation_step(self):
        """Smoothly interpolates enemy position between coordinates using Tkinter after loop."""
        if not self.is_simulating:
            return
            
        if self.enemy_path_index >= len(self.current_path) - 1:
            # Destination reached!
            self.is_simulating = False
            self.write_to_log("🎉 Kẻ địch đã đến điểm đích thành công!\n")
            self.status_lbl.config(text="Trạng thái: Kẻ địch đã về đích!")
            self.set_led_color("#10b981")
            
            # Re-enable controls
            self.btn_find.config(state=tk.NORMAL)
            self.btn_simulate.config(state=tk.NORMAL)
            self.btn_reset.config(state=tk.NORMAL)
            return

        # Check if next step is blocked (dynamic block during animation frame)
        curr_x, curr_y = self.current_path[self.enemy_path_index]
        next_x, next_y = self.current_path[self.enemy_path_index + 1]
        
        if self.map_manager.is_obstacle(next_x, next_y):
            # Blocked! Replan again immediately
            self.replan_during_movement()
            if self.map_manager.is_obstacle(next_x, next_y) or self.current_path[self.enemy_path_index + 1] == (next_x, next_y):
                # If still blocked (no path found or path couldn't change), stop enemy
                self.is_simulating = False
                self.write_to_log("🛑 Kẻ địch dừng lại do đường đi bị chặn.\n")
                self.status_lbl.config(text="Trạng thái: Bị chặn!")
                self.set_led_color("#ef4444")
                self.btn_find.config(state=tk.NORMAL)
                self.btn_simulate.config(state=tk.NORMAL)
                self.btn_reset.config(state=tk.NORMAL)
                return

        # Smooth interpolation: we move from current cell to next cell in 5 frames
        # Each frame advances position by 0.20
        ex, ey = self.enemy_pos
        dest_x, dest_y = float(next_x), float(next_y)
        
        # Calculate steps
        dx = dest_x - ex
        dy = dest_y - ey
        
        # If close to destination cell, snap to it and move to next node index
        dist_sq = dx*dx + dy*dy
        if dist_sq < 0.04:
            self.enemy_pos = (dest_x, dest_y)
            self.enemy_path_index += 1
        else:
            # Take small step towards destination (speed factor ~0.2 per frame)
            # Adjust speed based on delay scale (a larger delay scale means slower animation)
            step_size = 0.2
            self.enemy_pos = (ex + dx * step_size, ey + dy * step_size)
            
        self.redraw_grid()
        self.root.after(30, self.run_animation_step)

    def reset_grid(self):
        """Resets towers and path visual caches."""
        if self.is_simulating:
            return
            
        self.map_manager.reset()
        self.clear_search_visuals()
        
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.insert(tk.END, "Đã xóa toàn bộ trụ. Hệ thống sẵn sàng.\n")
        self.log_area.config(state=tk.DISABLED)
        
        self.status_lbl.config(text="Trạng thái: Đã reset lưới.")
        self.set_led_color("#10b981")
        self.redraw_grid()

    def clear_search_visuals(self):
        """Clears search footprints (open/closed colors) and active path."""
        self.search_node_states.clear()
        self.current_path.clear()
        self.enemy_pos = None
        self.enemy_path_index = 0
        self.redraw_grid()

    def write_to_log(self, text):
        """Inserts text into the log terminal."""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, text)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def queue_log(self, text):
        """Saves a text log operation to UI queue (thread-safe)."""
        self.ui_queue.put(('log', text + "\n"))

    def queue_node_state(self, x, y, state):
        """Saves a cell color mapping state to UI queue (thread-safe)."""
        self.ui_queue.put(('node', (x, y, state)))

    def process_ui_queue(self):
        """Checks and processes pending UI drawing updates from the queue."""
        # Process a batch of items to keep UI responsive
        batch_limit = 120
        count = 0
        
        while not self.ui_queue.empty() and count < batch_limit:
            item_type, data = self.ui_queue.get()
            count += 1
            
            if item_type == 'log':
                self.write_to_log(data)
                
            elif item_type == 'node':
                x, y, state = data
                coord = (x, y)
                if state in ["open", "closed"]:
                    self.search_node_states[coord] = state
                elif state == "path":
                    # We will append to current_path if not already inside path drawing process
                    # Normally solver returns full path at end, but this handles incremental visualization
                    pass
                elif state == "reset":
                    if coord in self.search_node_states:
                        del self.search_node_states[coord]
                        
                self.redraw_grid()
                
            elif item_type == 'path_completed':
                path = data
                # Re-enable controls
                self.btn_find.config(state=tk.NORMAL)
                self.btn_simulate.config(state=tk.NORMAL)
                self.btn_reset.config(state=tk.NORMAL)
                
                if path:
                    self.current_path = path
                    self.status_lbl.config(text=f"Trạng thái: Tìm đường hoàn tất! Độ dài: {len(path)}")
                    self.set_led_color("#10b981")
                else:
                    self.current_path = []
                    self.status_lbl.config(text="Trạng thái: Đường đi không khả thi!")
                    self.set_led_color("#ef4444")
                    
                self.redraw_grid()
                
            elif item_type == 'error':
                err_msg = data
                self.btn_find.config(state=tk.NORMAL)
                self.btn_simulate.config(state=tk.NORMAL)
                self.btn_reset.config(state=tk.NORMAL)
                
                self.write_to_log(f"💥 Lỗi hệ thống: {err_msg}\n")
                self.status_lbl.config(text="Trạng thái: Xảy ra lỗi!")
                self.set_led_color("#ef4444")
                
        # Re-schedule check
        self.root.after(30, self.process_ui_queue)
