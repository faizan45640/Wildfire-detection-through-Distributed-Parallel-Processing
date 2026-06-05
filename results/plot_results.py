# Plot performance graphs for wildfire detection project

import struct

import matplotlib.pyplot as plt
import numpy as np

TIMINGS_FILE = "results/timings.txt"
BENCHMARK_SIZE = 5000


def read_timings():
    data = []

    file = open(TIMINGS_FILE, "r")
    for line in file:
        line = line.strip()
        if line == "" or line.startswith("#") or line.startswith("version"):
            continue

        parts = line.split(",")
        if len(parts) != 4:
            continue

        data.append({
            "version": parts[0],
            "grid_size": int(parts[1]),
            "workers": int(parts[2]),
            "time_ms": float(parts[3]),
        })

    file.close()
    return data


def get_time(data, version, grid_size, workers):
    for row in data:
        if row["version"] == version and row["grid_size"] == grid_size and row["workers"] == workers:
            return row["time_ms"]
    return 0


def plot_execution_bar(data):
    serial_time = get_time(data, "serial", BENCHMARK_SIZE, 1)
    openmp_time = get_time(data, "openmp", BENCHMARK_SIZE, 4)
    mpi_time = get_time(data, "mpi", BENCHMARK_SIZE, 4)

    names = ["Serial", "OpenMP (4T)", "MPI+OMP (4P)"]
    times = [serial_time, openmp_time, mpi_time]

    plt.figure(figsize=(8, 5))
    plt.bar(names, times, color=["#4C72B0", "#55A868", "#C44E52"])
    plt.ylabel("Execution Time (ms)")
    plt.title("Execution Time Comparison (" + str(BENCHMARK_SIZE) + "x" + str(BENCHMARK_SIZE) + ")")
    plt.tight_layout()
    plt.savefig("results/graph1_execution_time.png")
    plt.close()


def plot_speedup(data):
    serial_time = get_time(data, "serial", BENCHMARK_SIZE, 1)
    workers_list = [1, 2, 4, 8]
    speedups = []

    for workers in workers_list:
        parallel_time = get_time(data, "openmp", BENCHMARK_SIZE, workers)
        if parallel_time > 0:
            speedups.append(serial_time / parallel_time)
        else:
            speedups.append(0)

    plt.figure(figsize=(8, 5))
    plt.plot(workers_list, speedups, marker="o")
    plt.xlabel("Number of OpenMP Threads")
    plt.ylabel("Speedup")
    plt.title("OpenMP Speedup vs Threads (" + str(BENCHMARK_SIZE) + "x" + str(BENCHMARK_SIZE) + ")")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/graph2_speedup.png")
    plt.close()


def plot_efficiency(data):
    serial_time = get_time(data, "serial", BENCHMARK_SIZE, 1)
    workers_list = [1, 2, 4, 8]
    efficiency = []

    for workers in workers_list:
        parallel_time = get_time(data, "openmp", BENCHMARK_SIZE, workers)
        if parallel_time > 0 and workers > 0:
            speedup = serial_time / parallel_time
            efficiency.append((speedup / workers) * 100.0)
        else:
            efficiency.append(0)

    plt.figure(figsize=(8, 5))
    plt.plot(workers_list, efficiency, marker="o", color="green")
    plt.xlabel("Number of OpenMP Threads")
    plt.ylabel("Efficiency (%)")
    plt.title("OpenMP Efficiency vs Threads (" + str(BENCHMARK_SIZE) + "x" + str(BENCHMARK_SIZE) + ")")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/graph3_efficiency.png")
    plt.close()


def read_firemap(path):
    file = open(path, "rb")
    rows = struct.unpack("i", file.read(4))[0]
    cols = struct.unpack("i", file.read(4))[0]

    firemap = np.zeros((rows, cols))

    for i in range(rows):
        for j in range(cols):
            value = struct.unpack("i", file.read(4))[0]
            firemap[i][j] = value

    file.close()
    return firemap


def plot_firemap():
    firemap = read_firemap("results/serial_firemap.bin")

    plt.figure(figsize=(8, 8))
    plt.imshow(firemap, cmap="Reds", origin="upper")
    plt.title("Fire Detection Output (Serial)")
    plt.xlabel("Column")
    plt.ylabel("Row")
    plt.colorbar(label="Fire (1) / No Fire (0)")
    plt.tight_layout()
    plt.savefig("results/graph4_firemap.png")
    plt.close()


def main():
    data = read_timings()

    plot_execution_bar(data)
    plot_speedup(data)
    plot_efficiency(data)
    plot_firemap()

    print("Saved results/graph1_execution_time.png")
    print("Saved results/graph2_speedup.png")
    print("Saved results/graph3_efficiency.png")
    print("Saved results/graph4_firemap.png")


if __name__ == "__main__":
    main()
