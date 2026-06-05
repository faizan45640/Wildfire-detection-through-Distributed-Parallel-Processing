# Generate synthetic thermal grid for wildfire detection project
# Creates datasets for 500x500, 1000x1000, and 2000x2000

import struct
import random
import os

import matplotlib.pyplot as plt
import numpy as np

# always save files inside dataset folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# sizes for scalability testing
GRID_SIZES = [500, 1000, 2000]

# fire zones: row, column, temperature
fire_zones = [
    [180, 220, 380],
    [420, 610, 340],
    [720, 150, 310],
    [850, 780, 395],
    [310, 880, 265],
]

radius = 40


def make_grid(rows, cols):
    # Step 1: normal background temperature
    grid = np.zeros((rows, cols))

    for i in range(rows):
        for j in range(cols):
            grid[i][j] = random.uniform(20, 60)

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

    return grid


def save_grid(grid, rows, cols, size):
    bin_name = f"thermal_grid_{size}.bin"
    png_name = f"grid_visual_{size}.png"

    # Step 4: save binary file
    with open(bin_name, "wb") as file:
        file.write(struct.pack("i", rows))
        file.write(struct.pack("i", cols))

        for i in range(rows):
            for j in range(cols):
                file.write(struct.pack("f", grid[i][j]))

    # Step 5: save image
    plt.imshow(grid, cmap="hot")
    plt.title("Thermal Grid Input Data (" + str(size) + "x" + str(size) + ")")
    plt.colorbar(label="Temperature (C)")
    plt.savefig(png_name)
    plt.close()

    fire_count = 0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] > 200:
                fire_count = fire_count + 1

    print("Saved", bin_name, "and", png_name)
    print("Grid size:", rows, "x", cols)
    print("Fire pixels (>200 C):", fire_count)
    print()


random.seed(42)

for size in GRID_SIZES:
    grid = make_grid(size, size)
    save_grid(grid, size, size, size)

# keep thermal_grid.bin as the default 1000x1000 file for C++ programs
import shutil
shutil.copy("thermal_grid_1000.bin", "thermal_grid.bin")
shutil.copy("grid_visual_1000.png", "grid_visual.png")

print("All datasets generated.")
