import os
import tkinter as tk

assets_dir = r"d:\Tower-Defense-AI\tower_defense_sim\assets\Default size"
root = tk.Tk()
root.withdraw()

categories = {
    "grass": [],
    "dirt/road": [],
    "base": [],
    "blue/cyan (ice)": [],
    "red/orange (fire)": [],
    "yellow/green (basic)": [],
    "grey/dark (other)": []
}

for i in range(1, 300):
    filename = f"towerDefense_tile{i:03d}.png"
    filepath = os.path.join(assets_dir, filename)
    if not os.path.exists(filepath):
        continue
    
    img = tk.PhotoImage(file=filepath)
    w, h = img.width(), img.height()
    
    trans_count = 0
    r_sum, g_sum, b_sum = 0, 0, 0
    sampled = 0
    
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            sampled += 1
            if img.transparency_get(x, y):
                trans_count += 1
            else:
                rgb = img.get(x, y)
                r_sum += rgb[0]
                g_sum += rgb[1]
                b_sum += rgb[2]
                
    pct_trans = (trans_count / sampled) * 100
    n_solid = sampled - trans_count
    if n_solid > 0:
        avg_r = int(r_sum / n_solid)
        avg_g = int(g_sum / n_solid)
        avg_b = int(b_sum / n_solid)
    else:
        avg_r, avg_g, avg_b = 0, 0, 0
        
    info = {
        "id": i,
        "filename": filename,
        "trans": pct_trans,
        "color": (avg_r, avg_g, avg_b)
    }
    
    # Classify
    if pct_trans < 5:
        # Solid tile
        if avg_g > avg_r + 30 and avg_g > avg_b + 30:
            categories["grass"].append(info)
        else:
            categories["dirt/road"].append(info)
    else:
        # Transparent overlay
        # Detect grey bases
        is_grey = abs(avg_r - avg_g) < 15 and abs(avg_g - avg_b) < 15 and abs(avg_r - avg_b) < 15
        if is_grey and 100 < avg_r < 200 and pct_trans > 30:
            categories["base"].append(info)
        elif avg_b > avg_r + 20 and avg_g > avg_r + 20: # Cyan/blue
            categories["blue/cyan (ice)"].append(info)
        elif avg_r > avg_g + 30 and avg_g > avg_b: # Red/orange/yellow
            categories["red/orange (fire)"].append(info)
        elif avg_g > avg_r + 25: # Green
            categories["yellow/green (basic)"].append(info)
        else:
            categories["grey/dark (other)"].append(info)

for cat, items in categories.items():
    print(f"\n--- Category: {cat} (Count: {len(items)}) ---")
    for item in items[:15]:
        print(f"  Tile {item['id']:03d}: trans={item['trans']:.1f}%, color={item['color']}")
