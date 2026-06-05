// OpenMP parallel wildfire detection
// Same logic as serial, but rows are processed in parallel

#include <iostream>
#include <fstream>
#include <vector>
#include <ctime>
#include <omp.h>

using namespace std;

const float FIRE_THRESHOLD = 200.0;

int main() {
    int rows, cols;

    // Step 1: read grid (same as serial)
    ifstream input("dataset/thermal_grid.bin", ios::binary);
    if (!input) {
        cout << "Error: could not open dataset/thermal_grid.bin" << endl;
        return 1;
    }

    input.read((char*)&rows, sizeof(int));
    input.read((char*)&cols, sizeof(int));

    float** grid = new float*[rows];
    for (int i = 0; i < rows; i++) {
        grid[i] = new float[cols];
    }

    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            input.read((char*)&grid[i][j], sizeof(float));
        }
    }
    input.close();

    int** firemap = new int*[rows];
    for (int i = 0; i < rows; i++) {
        firemap[i] = new int[cols];
        for (int j = 0; j < cols; j++) {
            firemap[i][j] = 0;
        }
    }

    vector<int> fire_rows;
    vector<int> fire_cols;
    int fire_count = 0;

    int num_threads = omp_get_max_threads();
    cout << "OpenMP threads: " << num_threads << endl;

    // Step 2: start timer
    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    // Step 3, 4, 5, 6: parallel loop with reduction and critical section
    #pragma omp parallel for reduction(+:fire_count) schedule(dynamic)
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (grid[i][j] > FIRE_THRESHOLD) {
                firemap[i][j] = 1;
                fire_count++;

                // critical section protects shared coordinate lists
                #pragma omp critical
                {
                    fire_rows.push_back(i);
                    fire_cols.push_back(j);
                }
            }
        }
    }

    // Step 7: stop timer
    clock_gettime(CLOCK_MONOTONIC, &end_time);

    double time_ms = (end_time.tv_sec - start_time.tv_sec) * 1000.0;
    time_ms = time_ms + (end_time.tv_nsec - start_time.tv_nsec) / 1000000.0;

    // Step 8: print results
    int total_pixels = rows * cols;

    cout << "Total pixels processed: " << total_pixels << endl;
    cout << "Total fire pixels found: " << fire_count << endl;
    cout << "Execution time (ms): " << time_ms << endl;
    cout << "Fire coordinates (row, col):" << endl;

    for (int k = 0; k < fire_count; k++) {
        cout << "(" << fire_rows[k] << ", " << fire_cols[k] << ")" << endl;
    }

    // free memory
    for (int i = 0; i < rows; i++) {
        delete[] grid[i];
        delete[] firemap[i];
    }
    delete[] grid;
    delete[] firemap;

    return 0;
}
