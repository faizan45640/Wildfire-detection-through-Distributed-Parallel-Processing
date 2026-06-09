# Wildfire Detection through Distributed Parallel Processing

PDC Lab project: detect fire pixels in a thermal grid using serial, OpenMP, and MPI+OpenMP.

## Project Structure

```
dataset/          generate_grid.py, thermal grids, input images
serial/           wildfire_serial.cpp
parallel/         wildfire_openmp.cpp, wildfire_parallel.cpp
results/          timings, graphs, fire maps
hostfile          MPI hostfile (fill in when using 4 machines)
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

## Generate Report (Word)

```bash
python3 report/generate_report.py
```

Opens `report/report.docx` in Word/LibreOffice. Replace all `[FILL]` placeholders after running benchmarks on the same network.

## Four-Machine MPI (remote) — step by step

### One-time setup (each person)

On **every** machine (Person 1–4):

```bash
# Install tools (Arch example; Ubuntu: apt install gcc g++ openmpi ...)
sudo pacman -S gcc openmpi python-numpy python-matplotlib

# Clone or copy project to the SAME path on all machines
ln -s "/path/to/Project" ~/wildfire-pdc
cd ~/wildfire-pdc

# Build
g++ -o wildfire_serial serial/wildfire_serial.cpp
g++ -fopenmp -o wildfire_openmp parallel/wildfire_openmp.cpp
mpicxx -fopenmp -o wildfire_parallel parallel/wildfire_parallel.cpp

# Generate dataset (only Person 1 needs to share thermal_grid.bin, or everyone runs generate_grid.py)
python3 dataset/generate_grid.py
cp dataset/thermal_grid_5000.bin dataset/thermal_grid.bin
```

**Person 1 only** — create `hostfile` with all four IPs (`slots=1` each):

```bash
cp hostfile.example hostfile
nano hostfile
```

Example (replace with real Tailscale or LAN IPs and usernames):

```
100.86.81.34 slots=1
talha@100.108.119.45 slots=1
user3@100.108.120.10 slots=1
user4@100.108.120.20 slots=1
```

**SSH:** From Person 1's machine, this must work for every remote person:

```bash
ssh user2@100.108.119.45 'echo ok'
ssh user3@100.108.120.10 'echo ok'
ssh user4@100.108.120.20 'echo ok'
```

All four machines should use the **same OpenMPI version** (e.g. 5.0.10).

### Run the 4-person benchmark (Person 1 only)

When everyone is online on the same WiFi or Tailscale:

```bash
cd ~/wildfire-pdc
chmod +x run_remote_mpi.sh
./run_remote_mpi.sh
```

This runs `mpirun -np 4` across all machines, prints output, and saves:

- `results/remote_timings.txt` — time + fire pixel count for the report

Then regenerate the report (Table 4 auto-fills):

```bash
python3 report/generate_report.py
```

### What to write in the report

| What | Where it comes from |
|------|---------------------|
| Remote MPI time (ms) | `results/remote_timings.txt` or terminal output |
| Fire pixel count | must be **40184** on 5000 grid (proves correctness) |
| Screenshot | paste terminal output into section 7.5 |
| Machine specs | each person fills their row in section 4.3 |

### If MPI fails

1. Try **same WiFi** instead of Tailscale (or vice versa).
2. Uncomment the Tailscale MCA lines inside `run_remote_mpi.sh`.
3. Check firewall allows SSH (port 22) and MPI dynamic ports.
4. Run local test first: `mpirun -np 4 ./wildfire_parallel` (single machine).
