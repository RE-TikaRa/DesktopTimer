from PIL import Image  # type: ignore[import-not-found]
from pathlib import Path

# Paths
root = Path(__file__).resolve().parents[1]
ico_path = root / 'img' / 'timer_icon.ico'
backup_path = root / 'img' / 'timer_icon.original.ico'

# Desired sizes for Windows small/large icons
sizes = [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]

if not ico_path.exists():
    raise FileNotFoundError(f"Icon not found: {ico_path}")

# Backup once
if not backup_path.exists():
    backup_path.write_bytes(ico_path.read_bytes())

# Load best available image from current ICO (or treat as a generic image)
im = Image.open(ico_path)
# Ensure we work from the highest resolution version
try:
    # If source is ICO, pick the largest embedded image
    biggest = None
    for size in getattr(im, 'icon_sizes', []):
        if biggest is None or size[0] > biggest[0]:
            biggest = size
    if biggest:
        im = Image.open(ico_path)
        # Reopen largest frame
        im.size  # touch to ensure loaded
except Exception:
    pass

# Convert to RGBA for proper alpha handling
if im.mode != 'RGBA':
    im = im.convert('RGBA')

# Save multi-size ICO (Pillow will resample for each size)
im.save(ico_path, format='ICO', sizes=sizes)
print(f"Rebuilt ICO with sizes: {sizes} -> {ico_path}")
