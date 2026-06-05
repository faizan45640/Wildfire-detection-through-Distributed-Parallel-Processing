# Wildfire Detection through Distributed Parallel Processing

PDC Lab project: detect fire pixels in a thermal grid using serial, OpenMP, and MPI+OpenMP.

## Project Structure

```
dataset/          generate_grid.py, thermal grids, input images
serial/           wildfire_serial.cpp
parallel/         wildfire_openmp.cpp, wildfire_parallel.cpp
results/          timings, graphs, fire maps
hostfile          MPI hostfile (fill in when using 2 laptops)
report/           report write-up (to be completed)
```

## Setup

```bash
sudo pacman -S gcc openmpi python-numpy python-matplotlib
```

## Build

```bash
g++ -o wildfire_serial serial/wildfire_serial.cpp
g++ -fopenmp -o wildfire_openmp parallel/wildfire_openmp.cpp
mpicxx -fopenmp -o wildfire_parallel parallel/wildfire_parallel.cpp
```

## Generate Dataset

```bash
cd dataset
python3 generate_grid.py
cd ..
```

## Run Programs

```bash
./wildfire_serial
OMP_NUM_THREADS=4 ./wildfire_openmp
mpirun -np 4 ./wildfire_parallel
```

## Run All Local Benchmarks and Graphs

```bash
chmod +x run_benchmarks.sh
./run_benchmarks.sh
```

This generates datasets, runs timing tests, and saves graphs in `results/`.

## Two-Laptop MPI (later)

Copy the example hostfile and add your Tailscale IPs (do not commit real IPs):

```bash
cp hostfile.example hostfile
nano hostfile
```

Then run from the machine that has the dataset:

```bash
mpirun -np 4 --hostfile hostfile ./wildfire_parallel
```
