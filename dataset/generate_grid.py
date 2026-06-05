# Generate synthetic thermal grid for wildfire detection project
# Output: thermal_grid.bin and grid_visual.png

import struct
import random

import matplotlib.pyplot as plt
import numpy as np

# change size here: 500, 1000, or 2000
ROWS = 1000
COLS = 1000

# Step 1: create grid with normal temperature (20 to 60 C)
grid = np.zeros((ROWS, COLS))

for i in range(ROWS):
    for j in range(COLS):
        grid[i][j] = random.uniform(20, 60)

# Step 2: plant fire zones at fixed locations
# format: row, column, temperature
fire_zones = [
    [180, 220, 380],
    [420, 610, 340],
    [720, 150, 310],
    [850, 780, 395],
    [310, 880, 265],
]

# Step 3: add fire and noise around each zone
radius = 40

for zone in fire_zones:
    center_row = zone[0]
    center_col = zone[1]
    fire_temp = zone[2]

    for i in range(center_row - radius, center_row + radius):
        for j in range(center_col - radius, center_col + radius):
            if i < 0 or i >= ROWS or j < 0 or j >= COLS:
                continue

            distance = ((i - center_row) ** 2 + (j - center_col) ** 2) ** 0.5

            if distance <= radius:
                noise = random.uniform(-15, 15)
                grid[i][j] = fire_temp + noise

            # small hot area around fire (realistic look)
            elif distance <= radius + 15:
                noise = random.uniform(-10, 10)
                grid[i][j] = 120 + noise

# Step 4: save binary file for C++ programs
# file format: rows (int), cols (int), then all temperatures (float)
with open("thermal_grid.bin", "wb") as file:
    file.write(struct.pack("i", ROWS))
    file.write(struct.pack("i", COLS))

    for i in range(ROWS):
        for j in range(COLS):
            file.write(struct.pack("f", grid[i][j]))

print("Saved thermal_grid.bin")

# Step 5: save image for report
plt.imshow(grid, cmap="hot")
plt.title("Thermal Grid Input Data")
plt.colorbar(label="Temperature (C)")
plt.savefig("grid_visual.png")
plt.close()

print("Saved grid_visual.png")
print("Grid size:", ROWS, "x", COLS)

# count fire pixels for checking
fire_count = 0
for i in range(ROWS):
    for j in range(COLS):
        if grid[i][j] > 200:
            fire_count = fire_count + 1

print("Fire pixels (>200 C):", fire_count)
