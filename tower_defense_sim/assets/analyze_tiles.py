import os
import tkinter as tk

assets_dir = r"d:\Tower-Defense-AI\tower_defense_sim\assets\Default size"
root = tk.Tk()
root.withdraw() # hide main window

results = []
for i in range(1, 300):
    filename = f"towerDefense_tile{i:03d}.png"
    filepath = os.path.join(assets_dir, filename)
    if not os.path.exists(filepath):
        continue
    
    img = tk.PhotoImage(file=filepath)
    w, h = img.width(), img.height()
    
    total_pixels = w * h
    trans_pixels = 0
    r_sum, g_sum, b_sum = 0, 0, 0
    
    # Sample pixels (every 2nd pixel to speed up)
    sample_step = 2
    sampled_total = 0
    
    for y in range(0, h, sample_step):
        for x in range(0, w, sample_step):
            sampled_total += 1
            if img.transparency_get(x, y):
                trans_pixels += 1
            else:
                rgb = img.get(x, y)
                r_sum += rgb[0]
                g_sum += rgb[1]
                b_sum += rgb[2]
                
    pct_trans = (trans_pixels / sampled_total) * 100
    avg_r = (r_sum / (sampled_total - trans_pixels)) if (sampled_total - trans_pixels) > 0 else 0
    avg_g = (g_sum / (sampled_total - trans_pixels)) if (sampled_total - trans_pixels) > 0 else 0
    avg_b = (b_sum / (sampled_total - trans_pixels)) if (sampled_total - trans_pixels) > 0 else 0
    
    results.append({
        'id': i,
        'filename': filename,
        'trans_pct': pct_trans,
        'avg_color': (int(avg_r), int(avg_g), int(avg_b))
    })

# Print top candidates
print("=== SOLID TILES (trans_pct < 1%) ===")
solid_tiles = [r for r in results if r['trans_pct'] < 1]
# Sort by greenness (g - r and g - b) to find grass
green_tiles = sorted(solid_tiles, key=lambda x: (x['avg_color'][1] - x['avg_color'][0] - x['avg_color'][2]), reverse=True)
print("Top 10 Green Solid Tiles:")
for t in green_tiles[:10]:
    print(f"Tile {t['id']:03d}: avg_color={t['avg_color']}")

# Sort by brownness (r > g > b) to find dirt/roads
brown_tiles = [t for t in solid_tiles if t['avg_color'][0] > t['avg_color'][1] and t['avg_color'][1] > t['avg_color'][2]]
brown_tiles = sorted(brown_tiles, key=lambda x: x['avg_color'][0], reverse=True)
print("\nTop 10 Brown Solid Tiles:")
for t in brown_tiles[:10]:
    print(f"Tile {t['id']:03d}: avg_color={t['avg_color']}")

# Find transparent tiles (trans_pct between 20% and 80%) for towers/enemies
print("\n=== SEMI-TRANSPARENT TILES (20% - 90% trans) ===")
semi_trans = [r for r in results if 20 <= r['trans_pct'] <= 90]
# Look for ones with blue tint (Ice), red tint (Fire), green tint, etc.
print("Examples of Semi-Transparent Tiles:")
for t in semi_trans[:15]:
    print(f"Tile {t['id']:03d}: trans_pct={t['trans_pct']:.1f}%, avg_color={t['avg_color']}")
