import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as st
import threading
import queue
import time
import os
import path_step_monitor

def rotate_photo_image(src_img, angle):
    """
    Rotates a tk.PhotoImage by 90, 180, or 270 degrees clockwise.
    Returns a new tk.PhotoImage.
    """
    w = src_img.width()
    h = src_img.height()
    dst_img = tk.PhotoImage(width=w, height=h)
    for y in range(h):
        for x in range(w):
            if angle == 90:
                nx, ny = w - 1 - y, x
            elif angle == 180:
                nx, ny = w - 1 - x, h - 1 - y
            elif angle == 270:
                nx, ny = y, h - 1 - x
            else:
                nx, ny = x, y
                
            if src_img.transparency_get(x, y):
                dst_img.transparency_set(nx, ny, True)
            else:
                r, g, b = src_img.get(x, y)
                dst_img.put(f"#{r:02x}{g:02x}{b:02x}", to=(nx, ny))
    return dst_img

class TowerDefenseGUI:
    def __init__(self, root, map_manager, pathfinder):
        self.root = root
        self.map_manager = map_manager
        self.pathfinder = pathfinder
        
        # Configure root window
        self.root.title("Tower Defense Pathfinding Simulator")
        self.root.geometry("1240x720")
        self.root.configure(bg="#0f172a")  # Slate 900
        
        # UI Queue for thread-safe updates
        self.ui_queue = queue.Queue()
        
        # Grid visual state cache (tracks node state colors to keep search artifacts)
        # 0: empty, 1: open, 2: closed, 3: path
        self.search_node_states = {}
        self.tower_turret_angles = {}
        self.active_lasers = []
        self.enemy_angle = 0
        
        # Active path lists
        self.current_path = []
        
        # Enemy simulation state
        self.enemy_id = None
        self.enemy_pos = None  # (float_x, float_y) current sub-pixel position
        self.enemy_path_index = 0
        self.is_simulating = False
        self.simulation_thread = None
        
        # Setup assets
        self.load_assets()
        
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

    def load_assets(self):
        """Loads all Kenney 2D tileset sprites, subsamples them, and caches rotations."""
        self.assets = {}
        assets_base_dir = os.path.dirname(os.path.abspath(__file__))
        default_size_dir = os.path.join(assets_base_dir, "assets", "Default size")
        
        # Mapping of friendly names to tile file numbers (1-indexed, padded to 3 digits)
        tile_mapping = {
            "grass": 24,         # Flat green grass
            "road": 93,          # Flat sand road (path)
            "start": 130,        # Green command pad
            "goal": 182,         # Red concrete base
            "base_square": 181,  # Concrete square base
            "base_round": 180,   # Concrete round base
            
            # Turrets
            "turret_basic": 249, # Green single barrel
            "turret_ice": 206,   # Cyan rocket launcher
            "turret_fire": 250,  # Red/orange double barrel
            
            # Tank Bodies
            "tank_normal_body": 245,  # Green tank body
            "tank_fast_body": 270,    # Fighter body
            "tank_tanky_body": 247,   # Brown tank body
            
            # Tank Turrets
            "tank_normal_turret": 246, # Red/green turret
            "tank_fast_turret": 271,   # Grey/dark turret
            "tank_tanky_turret": 248,  # Heavy grey turret
        }
        
        for name, num in tile_mapping.items():
            filename = f"towerDefense_tile{num:03d}.png"
            filepath = os.path.join(default_size_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    # Load and subsample 64x64 -> 32x32
                    img = tk.PhotoImage(file=filepath).subsample(2, 2)
                    self.assets[name] = img
                    
                    # Pre-calculate 4 rotations (0, 90, 180, 270)
                    self.assets[f"{name}_0"] = img
                    
                    # We only rotate elements that actually rotate: turrets and tank parts
                    if "turret" in name or "tank" in name:
                        self.assets[f"{name}_90"] = rotate_photo_image(img, 90)
                        self.assets[f"{name}_180"] = rotate_photo_image(img, 180)
                        self.assets[f"{name}_270"] = rotate_photo_image(img, 270)
                except Exception as e:
                    print(f"Error loading asset {name} ({filename}): {e}")
            else:
                print(f"Asset file not found: {filepath}")

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
        self.alg_combo = ttk.Combobox(ctrl_frame, textvariable=self.alg_var, 
                                       values=["A*",  "BFS", "DFS", "Greedy Best-First", "Backtracking (DFS)", "Belief State Search", "Steepest Ascent Hill Climbing", "Expectimax", "AND-OR Search", "alpha_beta","IDAstar","Local_Beam_Search","UCS", "forward_checking","DFS_Searching_for_partially_observable_problems" ], 
                                       state="readonly")
        self.alg_combo.pack(fill=tk.X, padx=15, pady=(2, 5))
        self.alg_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Category info text for clarity
        cat_info = "🔍 NHÓM THUẬT TOÁN:\n• Tìm đường: A*, DFS, Hill Climbing, BFS\n• Trạng thái: Belief State Search\n• AI Xác suất: Expectimax, AND-OR"
        cat_lbl = tk.Label(ctrl_frame, text=cat_info, bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 8), justify=tk.LEFT)
        cat_lbl.pack(fill=tk.X, padx=15, pady=(0, 10))
        
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
        self.btn_find.pack(fill=tk.X, padx=15, pady=3)
        
        self.btn_all_paths = self.create_styled_button(ctrl_frame, "Tìm Mọi Đường Đi (DFS)", self.start_all_paths_thread, "#06b6d4", "#0891b2")
        self.btn_all_paths.pack(fill=tk.X, padx=15, pady=3)
        
        self.btn_simulate = self.create_styled_button(ctrl_frame, "Bắt Đầu Mô Phỏng", self.start_enemy_simulation, "#10b981", "#059669")
        self.btn_simulate.pack(fill=tk.X, padx=15, pady=3)
        
        self.btn_minimax_simulate = self.create_styled_button(ctrl_frame, "AI Sinh Quái (Minimax)", self.start_minimax_enemy_simulation, "#ec4899", "#db2777")
        self.btn_minimax_simulate.pack(fill=tk.X, padx=15, pady=3)
        
        self.btn_sa = self.create_styled_button(ctrl_frame, "Tự Động Xếp Trụ (SA)", self.start_sa_thread, "#8b5cf6", "#7c3aed")
        self.btn_sa.pack(fill=tk.X, padx=15, pady=3)
        
        self.btn_mc = self.create_styled_button(ctrl_frame, "Xếp Trụ (Min-Conflicts)", self.start_min_conflicts_thread, "#f59e0b", "#d97706")
        self.btn_mc.pack(fill=tk.X, padx=15, pady=3)
        
        self.btn_reset = self.create_styled_button(ctrl_frame, "Reset Lưới", self.reset_grid, "#ef4444", "#dc2626")
        self.btn_reset.pack(fill=tk.X, padx=15, pady=3)
        
        self.btn_clear_path = self.create_styled_button(ctrl_frame, "Xóa Tìm Kiếm", self.clear_search_visuals, "#475569", "#334155")
        self.btn_clear_path.pack(fill=tk.X, padx=15, pady=3)
        
        # Quick guide
        guide_text = "💡 Hướng dẫn:\n• Click trái: Đặt trụ\n• Kéo trái: Vẽ nhanh trụ\n• Click/Kéo phải: Xóa trụ\n• Bắt đầu tìm đường trước khi chạy mô phỏng."
        guide_lbl = tk.Label(ctrl_frame, text=guide_text, bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 8), justify=tk.LEFT)
        guide_lbl.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)
        
        # 2. Center Panel: Canvas grid
        self.grid_frame = tk.Frame(main_frame, bg="#0f172a")
        self.grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calculate cell size based on grid 20x20 inside 640x640
        self.grid_size = 20
        self.cell_size = 32
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
                cx = x1 + self.cell_size // 2
                cy = y1 + self.cell_size // 2
                
                # 1. Background Grass (or Road if on path)
                if coord in self.current_path:
                    self.canvas.create_image(cx, cy, image=self.assets.get("road"), tags="grid_elements")
                else:
                    self.canvas.create_image(cx, cy, image=self.assets.get("grass"), tags="grid_elements")
                
                # 2. Start and Goal nodes
                if coord == self.map_manager.start:
                    self.canvas.create_image(cx, cy, image=self.assets.get("start"), tags="grid_elements")
                elif coord == self.map_manager.goal:
                    self.canvas.create_image(cx, cy, image=self.assets.get("goal"), tags="grid_elements")
                
                # 3. Obstacles / Towers
                elif self.map_manager.is_obstacle(x, y):
                    t_type = self.map_manager.get_tower_at(x, y) or "Basic"
                    if t_type == "Ice":
                        base_img = self.assets.get("base_round")
                        turret_prefix = "turret_ice"
                    elif t_type == "Fire":
                        base_img = self.assets.get("base_square")
                        turret_prefix = "turret_fire"
                    else:
                        base_img = self.assets.get("base_round")
                        turret_prefix = "turret_basic"
                        
                    turret_angle = self.tower_turret_angles.get((x, y), 0)
                    turret_img = self.assets.get(f"{turret_prefix}_{turret_angle}") or self.assets.get(turret_prefix)
                    
                    self.canvas.create_image(cx, cy, image=base_img, tags="grid_elements")
                    self.canvas.create_image(cx, cy, image=turret_img, tags="grid_elements")
                
                # 4. Open / Closed Search States (represented as glowing sci-fi borders over grass)
                if self.search_node_states.get(coord) == "closed":
                    self.canvas.create_rectangle(x1 + 2, y1 + 2, x1 + self.cell_size - 2, y1 + self.cell_size - 2,
                                                 outline="#3b82f6", width=2, tags="grid_elements")
                elif self.search_node_states.get(coord) == "open":
                    self.canvas.create_rectangle(x1 + 2, y1 + 2, x1 + self.cell_size - 2, y1 + self.cell_size - 2,
                                                 outline="#06b6d4", width=2, tags="grid_elements")

        # Redraw final path connecting line if path exists
        if len(self.current_path) > 1:
            points = []
            for px, py in self.current_path:
                cx = px * self.cell_size + self.cell_size // 2
                cy = py * self.cell_size + self.cell_size // 2
                points.append((cx, cy))
            
            # Draw line segments to make path look premium (glowing yellow/gold line)
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i+1]
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#fbbf24", width=3, capstyle=tk.ROUND, tags="path_elements")

        # Draw active laser beams
        if self.active_lasers:
            for tx, ty, ecx, ecy, color in self.active_lasers:
                tcx = tx * self.cell_size + self.cell_size // 2
                tcy = ty * self.cell_size + self.cell_size // 2
                self.canvas.create_line(tcx, tcy, ecx, ecy, fill=color, width=3, capstyle=tk.ROUND, tags="path_elements")
            # Clear lasers so they only flash for one frame
            self.active_lasers.clear()

        # Re-render enemy if simulating
        if self.is_simulating and self.enemy_pos is not None:
            self.draw_enemy()

    def draw_enemy(self):
        """Draws the enemy tank body and turret facing the direction of movement."""
        if self.enemy_pos is None:
            return
            
        ex, ey = self.enemy_pos
        ecx = ex * self.cell_size + self.cell_size // 2
        ecy = ey * self.cell_size + self.cell_size // 2
        
        enemy_type = getattr(self, "enemy_type", "Normal")
        if enemy_type == "Fast":
            body_prefix = "tank_fast_body"
            turret_prefix = "tank_fast_turret"
        elif enemy_type == "Tanky":
            body_prefix = "tank_tanky_body"
            turret_prefix = "tank_tanky_turret"
        else:
            body_prefix = "tank_normal_body"
            turret_prefix = "tank_normal_turret"
            
        enemy_angle = getattr(self, "enemy_angle", 0)
        
        body_img = self.assets.get(f"{body_prefix}_{enemy_angle}") or self.assets.get(body_prefix)
        turret_img = self.assets.get(f"{turret_prefix}_{enemy_angle}") or self.assets.get(turret_prefix)
        
        self.canvas.create_image(ecx, ecy, image=body_img, tags="path_elements")
        self.canvas.create_image(ecx, ecy, image=turret_img, tags="path_elements")
        
        # HP bar overlay
        bar_w = 26
        bar_h = 4
        hp_ratio = self.enemy_hp / getattr(self, "enemy_max_hp", 100.0)
        hp_w = int(bar_w * hp_ratio)
        
        bx1 = ecx - bar_w // 2
        by1 = ecy - self.cell_size // 2 - 4
        bx2 = bx1 + bar_w
        by2 = by1 + bar_h
        
        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill="#ef4444", outline="#475569", tags="path_elements")
        if hp_w > 0:
            self.canvas.create_rectangle(bx1, by1, bx1 + hp_w, by2, fill="#10b981", outline="", tags="path_elements")

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
        tower_type = self.tower_var.get()
        if self.map_manager.add_tower(x, y, tower_type):
            self.write_to_log(f"Đặt {tower_type} tại ô ({x}, {y})\n")
            self.redraw_grid()
            
            # Dynamic Re-planning during simulation
            if self.is_simulating:
                self.replan_during_movement()

    def on_canvas_left_drag(self, event):
        """Draws towers continuously on click & drag."""
        x, y = self.get_cell_coord(event)
        tower_type = self.tower_var.get()
        if self.map_manager.add_tower(x, y, tower_type):
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
        self.set_buttons_state(tk.DISABLED)
        
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

    def start_sa_thread(self):
        """Spawns background thread to run Simulated Annealing layout optimization."""
        if self.is_simulating:
            self.write_to_log("⚠️ Vui lòng chờ mô phỏng kẻ địch chạy xong!\n")
            return
            
        self.clear_search_visuals()
        self.set_led_color("#f59e0b")
        self.status_lbl.config(text="Trạng thái: Đang chạy Simulated Annealing...")
        
        # Clear log area
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        self.set_buttons_state(tk.DISABLED)
        
        def run_sa_bg():
            from algorithms import simulated_annealing
            import path_step_monitor
            try:
                path_step_monitor.set_silenced(True)
                simulated_annealing.run_annealing(
                    self.map_manager,
                    num_towers=18,
                    steps=80,
                    update_ui_callback=lambda: self.ui_queue.put(('map_update', None)),
                    log_callback=lambda text: self.ui_queue.put(('log', text))
                )
                self.ui_queue.put(('sa_completed', None))
            except Exception as e:
                self.ui_queue.put(('error', str(e)))
            finally:
                path_step_monitor.set_silenced(False)
                
        threading.Thread(target=run_sa_bg, daemon=True).start()

    def start_min_conflicts_thread(self):
        """Spawns background thread to run Min-Conflicts CSP layout optimization."""
        if self.is_simulating:
            self.write_to_log("⚠️ Vui lòng chờ mô phỏng kẻ địch chạy xong!\n")
            return
            
        self.clear_search_visuals()
        self.set_led_color("#f59e0b")
        self.status_lbl.config(text="Trạng thái: Đang chạy Min-Conflicts...")
        
        # Clear log area
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        self.set_buttons_state(tk.DISABLED)
        
        def run_mc_bg():
            from algorithms import min_conflicts
            import path_step_monitor
            try:
                path_step_monitor.set_silenced(True)
                min_conflicts.run_min_conflicts(
                    self.map_manager,
                    num_towers=18,
                    max_steps=100,
                    update_ui_callback=lambda: self.ui_queue.put(('map_update', None)),
                    log_callback=lambda text: self.ui_queue.put(('log', text))
                )
                self.ui_queue.put(('mc_completed', None))
            except Exception as e:
                self.ui_queue.put(('error', str(e)))
            finally:
                path_step_monitor.set_silenced(False)
                
        threading.Thread(target=run_mc_bg, daemon=True).start()

    def start_minimax_enemy_simulation(self):
        """Runs Minimax search to choose the optimal creep type, then starts simulation."""
        if self.is_simulating:
            return
            
        if not self.current_path:
            self.write_to_log("⚠️ Chưa tìm được đường đi! Hãy bấm 'Tìm Đường Lại' trước.\n")
            return
            
        self.write_to_log("\n--- Bắt đầu đấu trí Minimax cho Creep ---\n")
        from algorithms import minimax
        
        best_creep, minimax_val, log_steps = minimax.decide_optimal_creep(self.map_manager, self.current_path)
        
        for step in log_steps:
            self.write_to_log(step + "\n")
            
        self.write_to_log(f"🤖 AI chọn loại quái: {best_creep.upper()} (Điểm đánh giá Minimax: {minimax_val:.1f})\n")
        
        self.enemy_type = best_creep
        if best_creep == "Tanky":
            self.enemy_max_hp = 200.0
            self.enemy_hp = 200.0
            self.enemy_speed = 0.1
        elif best_creep == "Fast":
            self.enemy_max_hp = 60.0
            self.enemy_hp = 60.0
            self.enemy_speed = 0.35
        else:
            self.enemy_max_hp = 100.0
            self.enemy_hp = 100.0
            self.enemy_speed = 0.2
            
        self.is_simulating = True
        self.enemy_path_index = 0
        start_x, start_y = self.current_path[0]
        self.enemy_pos = (float(start_x), float(start_y))
        self.enemy_angle = 0
        self.tower_turret_angles.clear()
        self.active_lasers.clear()
        
        self.enemy_slowed = False
        self.enemy_strategy = getattr(self.map_manager, "last_and_or_strategy", {})
        
        self.set_buttons_state(tk.DISABLED)
        
        self.status_lbl.config(text=f"Trạng thái: Creep {best_creep} (HP: {self.enemy_hp:.0f}/{self.enemy_max_hp:.0f}) đang di chuyển...")
        self.set_led_color("#3b82f6")
        
        self.run_animation_step()

    def start_all_paths_thread(self):
        """Spawns background thread to count all simple paths using Backtracking DFS."""
        if self.is_simulating:
            self.write_to_log("⚠️ Vui lòng chờ mô phỏng kẻ địch chạy xong!\n")
            return
            
        self.clear_search_visuals()
        self.set_led_color("#f59e0b")
        self.status_lbl.config(text="Trạng thái: Đang quét tất cả đường đi...")
        
        # Clear log area
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        self.set_buttons_state(tk.DISABLED)
        
        def run_all_paths_bg():
            from algorithms import backtracking
            try:
                paths = backtracking.solve_all_paths(
                    self.map_manager.start,
                    self.map_manager.goal,
                    self.map_manager,
                    max_steps=2000
                )
                self.ui_queue.put(('all_paths_completed', paths))
            except Exception as e:
                self.ui_queue.put(('error', str(e)))
                
        threading.Thread(target=run_all_paths_bg, daemon=True).start()

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

    def set_buttons_state(self, state):
        """Enables or disables all control buttons at once."""
        self.btn_find.config(state=state)
        self.btn_simulate.config(state=state)
        self.btn_minimax_simulate.config(state=state)
        self.btn_reset.config(state=state)
        self.btn_sa.config(state=state)
        self.btn_mc.config(state=state)
        self.btn_all_paths.config(state=state)

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
        self.enemy_angle = 0
        self.tower_turret_angles.clear()
        self.active_lasers.clear()
        
        # Initialize enemy simulation variables
        self.enemy_type = "Normal"
        self.enemy_max_hp = 100.0
        self.enemy_hp = 100.0
        self.enemy_speed = 0.2
        self.enemy_slowed = False
        self.enemy_strategy = getattr(self.map_manager, "last_and_or_strategy", {})
        
        self.set_buttons_state(tk.DISABLED)
        
        self.write_to_log("\n--- Bắt đầu mô phỏng di chuyển kẻ địch ---\n")
        self.status_lbl.config(text="Trạng thái: Kẻ địch đang di chuyển... HP: 100.0/100")
        self.set_led_color("#3b82f6")  # Blue for running simulation
        
        # Launch animation loop
        self.run_animation_step()

    def run_animation_step(self):
        """Smoothly interpolates enemy position between coordinates using Tkinter after loop."""
        import math
        if not self.is_simulating:
            return
            
        if self.enemy_path_index >= len(self.current_path) - 1:
            # Destination reached!
            self.is_simulating = False
            self.write_to_log("🎉 Kẻ địch đã đến điểm đích thành công!\n")
            self.status_lbl.config(text=f"Trạng thái: Về đích thành công! HP còn lại: {self.enemy_hp:.1f}")
            self.set_led_color("#10b981")
            
            # Re-enable controls
            self.set_buttons_state(tk.NORMAL)
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
                self.set_buttons_state(tk.NORMAL)
                return

        # Smooth interpolation: we move from current cell to next cell
        # Step size is halved when enemy is slowed/frozen
        ex, ey = self.enemy_pos
        dest_x, dest_y = float(next_x), float(next_y)
        
        dx = dest_x - ex
        dy = dest_y - ey
        
        # Calculate enemy angle facing movement direction
        if abs(dx) > abs(dy):
            self.enemy_angle = 90 if dx > 0 else 270
        else:
            self.enemy_angle = 180 if dy > 0 else 0
        
        dist_sq = dx*dx + dy*dy
        if dist_sq < 0.04:
            self.enemy_pos = (dest_x, dest_y)
            self.enemy_path_index += 1
            
            # Resolve tower attacks on entering new cell
            cx, cy = int(dest_x), int(dest_y)
            alg_name = self.alg_var.get()
            
            if alg_name in ["Expectimax", "AND-OR Search"] or getattr(self, "enemy_type", "Normal") in ["Fast", "Tanky"]:
                import random
                total_damage = 0.0
                frozen_by_tower = False
                enemy_type = getattr(self, "enemy_type", "Normal")
                
                for (tx, ty), t_type in self.map_manager.towers.items():
                    dist = math.sqrt((tx - cx)**2 + (ty - cy)**2)
                    in_range = False
                    laser_color = "#fbbf24"
                    
                    if t_type == "Basic" and dist <= 3.0:
                        in_range = True
                        laser_color = "#fbbf24"  # Gold
                        if enemy_type == "Fast":
                            dmg = 12.0
                        elif enemy_type == "Tanky":
                            dmg = 8.0
                        else:
                            dmg = 10.0
                        total_damage += dmg
                        self.write_to_log(f"💥 Tháp Basic tại ({tx},{ty}) bắn: {dmg:.1f} sát thương!\n")
                    elif t_type == "Fire" and dist <= 4.0:
                        in_range = True
                        laser_color = "#f97316"  # Orange-Red
                        if enemy_type == "Fast":
                            dmg = 7.2
                        elif enemy_type == "Tanky":
                            dmg = 27.0
                        else:
                            dmg = 18.0
                        
                        if random.random() < 0.40 and enemy_type == "Normal":
                            total_damage += dmg * 1.6
                            self.write_to_log(f"💥 Tháp Fire tại ({tx},{ty}) CHÍ MẠNG: {dmg*1.6:.1f} sát thương!\n")
                        else:
                            total_damage += dmg
                            self.write_to_log(f"🔫 Tháp Fire tại ({tx},{ty}) bắn: {dmg:.1f} sát thương.\n")
                    elif t_type == "Ice" and dist <= 2.0:
                        in_range = True
                        laser_color = "#06b6d4"  # Cyan
                        if enemy_type == "Fast":
                            dmg = 12.0
                        elif enemy_type == "Tanky":
                            dmg = 7.6
                        else:
                            dmg = 9.5
                        
                        if random.random() < 0.30:
                            total_damage += dmg * 2.0
                            frozen_by_tower = True
                            self.write_to_log(f"❄️ Tháp Ice tại ({tx},{ty}) ĐÓNG BĂNG: {dmg*2.0:.1f} sát thương + làm chậm!\n")
                        else:
                            total_damage += dmg
                            self.write_to_log(f"🔫 Tháp Ice tại ({tx},{ty}) bắn: {dmg:.1f} sát thương.\n")
                            
                    if in_range:
                        # Rotate tower turret toward the enemy
                        tdx = cx - tx
                        tdy = cy - ty
                        if abs(tdx) > abs(tdy):
                            t_angle = 90 if tdx > 0 else 270
                        else:
                            t_angle = 180 if tdy > 0 else 0
                        self.tower_turret_angles[(tx, ty)] = t_angle
                        
                        # Add laser beam flash effect
                        ecx = cx * self.cell_size + self.cell_size // 2
                        ecy = cy * self.cell_size + self.cell_size // 2
                        self.active_lasers.append((tx, ty, ecx, ecy, laser_color))
                            
                if total_damage > 0:
                    self.enemy_hp -= total_damage
                    if self.enemy_hp < 0:
                        self.enemy_hp = 0.0
                    self.write_to_log(f"❤️ Máu còn lại: {self.enemy_hp:.1f}/{getattr(self, 'enemy_max_hp', 100.0)}\n")
                    
                if self.enemy_hp <= 0:
                    self.is_simulating = False
                    self.enemy_pos = (dest_x, dest_y)
                    self.redraw_grid()
                    self.write_to_log("💀 Kẻ địch đã bị tiêu diệt giữa đường do hết máu!\n")
                    self.status_lbl.config(text="Trạng thái: Bị tiêu diệt!")
                    self.set_led_color("#ef4444")
                    self.set_buttons_state(tk.NORMAL)
                    return
                    
                # Update slow state
                self.enemy_slowed = frozen_by_tower
                self.status_lbl.config(text=f"Trạng thái: Kẻ địch di chuyển... HP: {self.enemy_hp:.1f}/{getattr(self, 'enemy_max_hp', 100.0)}")
                
                # AND-OR Search dynamic path rerouting
                if alg_name == "AND-OR Search" and self.enemy_path_index < len(self.current_path):
                    status = "slowed" if self.enemy_slowed else "normal"
                    next_step = self.enemy_strategy.get((cx, cy, status))
                    
                    if next_step and next_step != self.current_path[self.enemy_path_index]:
                        self.write_to_log(f"🔀 Nhánh rẽ chiến lược AND-OR: ({cx}, {cy}) -> {next_step} [Trạng thái: {status}]\n")
                        
                        completed = self.current_path[:self.enemy_path_index]
                        path_suffix = [next_step]
                        curr_node = next_step
                        visited_suffix = {next_step}
                        while curr_node != self.map_manager.goal:
                            nxt = self.enemy_strategy.get((curr_node[0], curr_node[1], "normal"))
                            if not nxt or nxt in visited_suffix:
                                break
                            path_suffix.append(nxt)
                            visited_suffix.add(nxt)
                            curr_node = nxt
                        self.current_path = completed + path_suffix
        else:
            speed = getattr(self, "enemy_speed", 0.2)
            step_size = (speed * 0.5) if self.enemy_slowed else speed
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
                self.set_buttons_state(tk.NORMAL)
                
                if path:
                    self.current_path = path
                    self.status_lbl.config(text=f"Trạng thái: Tìm đường hoàn tất! Độ dài: {len(path)}")
                    self.set_led_color("#10b981")
                else:
                    self.current_path = []
                    self.status_lbl.config(text="Trạng thái: Đường đi không khả thi!")
                    self.set_led_color("#ef4444")
                    
                self.redraw_grid()
                
            elif item_type == 'map_update':
                self.redraw_grid()
                
            elif item_type == 'sa_completed':
                self.set_buttons_state(tk.NORMAL)
                self.write_to_log("✅ Đã tạo mê cung bằng Simulated Annealing xong!\n")
                self.status_lbl.config(text="Trạng thái: Hoàn tất Simulated Annealing")
                self.set_led_color("#10b981")
                self.redraw_grid()
                
            elif item_type == 'mc_completed':
                self.set_buttons_state(tk.NORMAL)
                self.write_to_log("✅ Đã tối ưu hóa vị trí tháp bằng Min-Conflicts xong!\n")
                self.status_lbl.config(text="Trạng thái: Hoàn tất Min-Conflicts")
                self.set_led_color("#10b981")
                self.redraw_grid()
                
            elif item_type == 'all_paths_completed':
                all_paths = data
                self.set_buttons_state(tk.NORMAL)
                self.set_led_color("#10b981")
                
                if all_paths:
                    self.write_to_log(f"✅ Tìm thấy tất cả {len(all_paths)} đường đi bằng Backtracking DFS.\n")
                    self.status_lbl.config(text=f"Trạng thái: DFS tìm thấy {len(all_paths)} đường đi.")
                    # Show the first found path as current active path
                    self.current_path = all_paths[0]
                else:
                    self.write_to_log("❌ Không tìm thấy đường đi khả thi nào!\n")
                    self.status_lbl.config(text="Trạng thái: Không tìm thấy đường đi.")
                    self.current_path = []
                self.redraw_grid()
                
            elif item_type == 'error':
                err_msg = data
                self.set_buttons_state(tk.NORMAL)
                
                self.write_to_log(f"💥 Lỗi hệ thống: {err_msg}\n")
                self.status_lbl.config(text="Trạng thái: Xảy ra lỗi!")
                self.set_led_color("#ef4444")
                
        # Re-schedule check
        self.root.after(30, self.process_ui_queue)
