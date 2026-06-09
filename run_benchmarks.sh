#!/bin/bash
# Run all local benchmarks and save timings to results/timings.txt

cd "$(dirname "$0")"

echo "Building programs..."
g++ -o wildfire_serial serial/wildfire_serial.cpp
g++ -fopenmp -o wildfire_openmp parallel/wildfire_openmp.cpp
mpicxx -fopenmp -o wildfire_parallel parallel/wildfire_parallel.cpp

echo "Generating datasets..."
python3 dataset/generate_grid.py

RESULTS="results/timings.txt"
SUMMARY="results/timings_summary.txt"
LARGE_SIZE=5000

echo "version,grid_size,workers,time_ms" > "$RESULTS"

get_serial_time() {
    output=$(./wildfire_serial 2>&1)
    echo "$output" | grep "Execution time" | awk '{print $4}'
}

get_openmp_time() {
    output=$(OMP_NUM_THREADS=$1 ./wildfire_openmp 2>&1)
    echo "$output" | grep "Execution time" | awk '{print $4}'
}

get_mpi_time() {
    mpirun --allow-run-as-root -np $1 ./wildfire_parallel 2>&1 | grep "Execution time" | awk '{print $4}'
}

for size in 500 1000 2000 $LARGE_SIZE; do
    echo "Benchmarking grid ${size}x${size}..."

    cp "dataset/thermal_grid_${size}.bin" dataset/thermal_grid.bin

    serial_time=$(get_serial_time)
    echo "serial,${size},1,${serial_time}" >> "$RESULTS"
    echo "  serial: ${serial_time} ms"

    if [ "$size" = "$LARGE_SIZE" ]; then
        for threads in 1 2 4 8; do
            openmp_time=$(get_openmp_time $threads)
            echo "openmp,${size},${threads},${openmp_time}" >> "$RESULTS"
            echo "  openmp (${threads} threads): ${openmp_time} ms"
        done

        for procs in 2 4; do
            mpi_time=$(get_mpi_time $procs)
            echo "mpi,${size},${procs},${mpi_time}" >> "$RESULTS"
            echo "  mpi (${procs} processes): ${mpi_time} ms"
        done
    fi
done

cp "dataset/thermal_grid_${LARGE_SIZE}.bin" dataset/thermal_grid.bin

echo "Performance Results" > "$SUMMARY"
echo "===================" >> "$SUMMARY"
echo "" >> "$SUMMARY"
printf "%-10s %-10s %-10s %-12s\n" "Version" "Grid" "Workers" "Time (ms)" >> "$SUMMARY"
printf "%-10s %-10s %-10s %-12s\n" "-------" "----" "-------" "---------" >> "$SUMMARY"

while IFS=',' read -r version grid workers time; do
    if [ "$version" = "version" ]; then
        continue
    fi
    printf "%-10s %-10s %-10s %-12s\n" "$version" "${grid}x${grid}" "$workers" "$time" >> "$SUMMARY"
done < "$RESULTS"

echo ""
echo "Saved $RESULTS"
echo "Saved $SUMMARY"

echo "Running plot script..."
python3 results/plot_results.py

echo "Done."
