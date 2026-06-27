import os

assets_dir = r"d:\Tower-Defense-AI\tower_defense_sim\assets\Default size"
files = [f for f in os.listdir(assets_dir) if f.endswith(".png")]
files.sort()

html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Kenney Tower Defense Tile Viewer</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: #fff; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 15px; }
        .tile-card { background: #1e1e1e; border: 1px solid #333; padding: 10px; text-align: center; border-radius: 4px; }
        .tile-card img { width: 64px; height: 64px; image-rendering: pixelated; margin-bottom: 5px; }
        .tile-card div { font-size: 11px; word-break: break-all; color: #aaa; }
    </style>
</head>
<body>
    <h1>Kenney Tower Defense Tile Viewer</h1>
    <div class="grid">
"""

for f in files:
    html_content += f"""        <div class="tile-card">
            <img src="./Default size/{f}">
            <div>{f.replace("towerDefense_tile", "").replace(".png", "")}</div>
        </div>
"""

html_content += """    </div>
</body>
</html>
"""

output_path = r"d:\Tower-Defense-AI\tower_defense_sim\assets\tile_viewer.html"
with open(output_path, "w", encoding="utf-8") as f_out:
    f_out.write(html_content)

print(f"Generated tile viewer at {output_path}")
