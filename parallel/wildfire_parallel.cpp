// MPI + OpenMP wildfire detection
// MPI splits rows across processes, OpenMP parallelizes inside each process

#include <iostream>
#include <fstream>
#include <ctime>
#include <mpi.h>
#include <omp.h>

using namespace std;

const float FIRE_THRESHOLD = 200.0;

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int rows = 0;
    int cols = 0;
    float* full_grid = NULL;

    // Step 1: master reads full grid from file
    if (rank == 0) {
        ifstream input("dataset/thermal_grid.bin", ios::binary);
        if (!input) {
            cout << "Error: could not open dataset/thermal_grid.bin" << endl;
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        input.read((char*)&rows, sizeof(int));
        input.read((char*)&cols, sizeof(int));

        full_grid = new float[rows * cols];

        for (int i = 0; i < rows * cols; i++) {
            input.read((char*)&full_grid[i], sizeof(float));
        }
        input.close();
    }

    // send rows and cols to all processes
    MPI_Bcast(&rows, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&cols, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // divide rows into equal chunks (handles leftover rows too)
    int* sendcounts = new int[size];
    int* displs = new int[size];
    int offset = 0;

    for (int r = 0; r < size; r++) {
        int chunk_rows = rows / size + (r < rows % size ? 1 : 0);
        sendcounts[r] = chunk_rows * cols;
        displs[r] = offset;
        offset = offset + sendcounts[r];
    }

    int local_rows = rows / size + (rank < rows % size ? 1 : 0);
    float* local_grid = new float[local_rows * cols];
    int* local_firemap = new int[local_rows * cols];

    for (int i = 0; i < local_rows * cols; i++) {
        local_firemap[i] = 0;
    }

    double start_time = MPI_Wtime();

    // Step 2: scatter grid chunks to all processes
    MPI_Scatterv(full_grid, sendcounts, displs, MPI_FLOAT,
                 local_grid, sendcounts[rank], MPI_FLOAT,
                 0, MPI_COMM_WORLD);

    // Step 3: each process runs OpenMP on its chunk
    int local_fire_count = 0;

    #pragma omp parallel for reduction(+:local_fire_count) schedule(dynamic)
    for (int i = 0; i < local_rows; i++) {
        for (int j = 0; j < cols; j++) {
            int index = i * cols + j;

            if (local_grid[index] > FIRE_THRESHOLD) {
                local_firemap[index] = 1;
                local_fire_count++;
            }
        }
    }

    // Step 4: gather fire counts and fire maps to master
    int total_fire_count = 0;
    MPI_Reduce(&local_fire_count, &total_fire_count, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    int* full_firemap = NULL;
    if (rank == 0) {
        full_firemap = new int[rows * cols];
        for (int i = 0; i < rows * cols; i++) {
            full_firemap[i] = 0;
        }
    }

    MPI_Gatherv(local_firemap, local_rows * cols, MPI_INT,
                full_firemap, sendcounts, displs, MPI_INT,
                0, MPI_COMM_WORLD);

    double end_time = MPI_Wtime();
    double time_ms = (end_time - start_time) * 1000.0;

    // Step 5 and 6: master prints results and saves fire map
    if (rank == 0) {
        int total_pixels = rows * cols;

        cout << "MPI processes: " << size << endl;
        cout << "OpenMP threads per process: " << omp_get_max_threads() << endl;
        cout << "Total pixels processed: " << total_pixels << endl;
        cout << "Total fire pixels found: " << total_fire_count << endl;
        cout << "Execution time (ms): " << time_ms << endl;

        ofstream output("results/mpi_firemap.bin", ios::binary);
        output.write((char*)&rows, sizeof(int));
        output.write((char*)&cols, sizeof(int));

        for (int i = 0; i < rows * cols; i++) {
            output.write((char*)&full_firemap[i], sizeof(int));
        }
        output.close();

        cout << "Saved results/mpi_firemap.bin" << endl;

        delete[] full_grid;
        delete[] full_firemap;
    }

    delete[] local_grid;
    delete[] local_firemap;
    delete[] sendcounts;
    delete[] displs;

    MPI_Finalize();
    return 0;
}
