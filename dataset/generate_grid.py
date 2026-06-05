# Generate synthetic thermal grid for wildfire detection project
# Creates datasets for different grid sizes

import struct
import random
import os
import shutil

import matplotlib.pyplot as plt
import numpy as np

# always save files inside dataset folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# small sizes for table + large size to show real speedup
GRID_SIZES = [500, 1000, 2000, 5000]

# fire zones: row, column, temperature
fire_zones = [
    [180, 220, 380],
    [420, 610, 340],
    [720, 150, 310],
    [850, 780, 395],
    [310, 880, 265],
    [2500, 2100, 360],
    [4100, 3200, 330],
    [4700, 900, 390],
]

radius = 40


def make_grid(rows, cols):
    random.seed(42)

    # Step 1: normal background temperature
    grid = np.random.uniform(20, 60, size=(rows, cols))

    # Step 2 and 3: plant fire zones with noise
    for zone in fire_zones:
        center_row = zone[0]
        center_col = zone[1]
        fire_temp = zone[2]

        for i in range(center_row - radius, center_row + radius):
            for j in range(center_col - radius, center_col + radius):
                if i < 0 or i >= rows or j < 0 or j >= cols:
                    continue

                distance = ((i - center_row) ** 2 + (j - center_col) ** 2) ** 0.5

                if distance <= radius:
                    noise = random.uniform(-15, 15)
                    grid[i][j] = fire_temp + noise
                elif distance <= radius + 15:
                    noise = random.uniform(-10, 10)
                    grid[i][j] = 120 + noise

    return grid.astype(np.float32)


def save_grid(grid, rows, cols, size):
    bin_name = f"thermal_grid_{size}.bin"
    png_name = f"grid_visual_{size}.png"

    # Step 4: save binary file
    with open(bin_name, "wb") as file:
        file.write(struct.pack("i", rows))
        file.write(struct.pack("i", cols))
        file.write(grid.tobytes())

    # Step 5: save image (skip very large grids to save time)
    if size <= 2000:
        plt.imshow(grid, cmap="hot")
        plt.title("Thermal Grid Input Data (" + str(size) + "x" + str(size) + ")")
        plt.colorbar(label="Temperature (C)")
        plt.savefig(png_name)
        plt.close()
        print("Saved", bin_name, "and", png_name)
    else:
        print("Saved", bin_name, "(image skipped for large grid)")

    fire_count = int(np.sum(grid > 200))

    print("Grid size:", rows, "x", cols)
    print("Fire pixels (>200 C):", fire_count)
    print()


for size in GRID_SIZES:
    print("Generating", size, "x", size, "grid...")
    grid = make_grid(size, size)
    save_grid(grid, size, size, size)

# default file used by C++ programs
shutil.copy("thermal_grid_5000.bin", "thermal_grid.bin")

print("All datasets generated.")
print("Default dataset is now thermal_grid.bin (5000x5000).")
