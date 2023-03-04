import glob
import os
from pathlib import Path
import subprocess

from PIL import Image

scan_folder = r"W:\\SteamLibrary\\steamapps\\common\\Umineko Chiru Modded 2023-03-04"
output_folder = r"C:\\temp\\converted"

convert = False
optimize = True

for path in glob.iglob(os.path.join(scan_folder, '**/*'), recursive=True):
	path = Path(path)
	if path.suffix.lower() not in ['.png', '.jpg']:
		continue

	image = Image.open(path)

	if image.width == 2429 and image.height == 1366:
		rel_path = path.relative_to(scan_folder)
		output_path = Path(os.path.join(output_folder, rel_path))

		print(f"Processing {output_path}...")

		if convert:
			os.makedirs(output_path.parent.absolute(), exist_ok=True)
			image.resize((1920, 1080)).save(output_path)

		if optimize:
			subprocess.check_call(['ect', '-9', output_path])
