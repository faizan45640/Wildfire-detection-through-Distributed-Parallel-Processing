// Serial wildfire detection
// Reads thermal grid and finds fire pixels (temperature > 200 C)

#include <iostream>
#include <fstream>
#include <vector>
#include <ctime>

using namespace std;

const float FIRE_THRESHOLD = 200.0;

int main() {
    int rows, cols;

    // Step 1: read grid size from file header
    ifstream input("dataset/thermal_grid.bin", ios::binary);
    if (!input) {
        cout << "Error: could not open dataset/thermal_grid.bin" << endl;
        return 1;
    }

    input.read((char*)&rows, sizeof(int));
    input.read((char*)&cols, sizeof(int));

    // Step 2: allocate 2D array
    float** grid = new float*[rows];
    for (int i = 0; i < rows; i++) {
        grid[i] = new float[cols];
    }

    // Step 3: load all temperature values
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            input.read((char*)&grid[i][j], sizeof(float));
        }
    }
    input.close();

    // fire map: 1 = fire, 0 = no fire
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

    // Step 4: start timer
    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    // Step 5: check every pixel one by one
    int total_pixels = 0;

    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            total_pixels++;

            if (grid[i][j] > FIRE_THRESHOLD) {
                firemap[i][j] = 1;
                fire_count++;
                fire_rows.push_back(i);
                fire_cols.push_back(j);
            }
        }
    }

    // Step 6: stop timer
    clock_gettime(CLOCK_MONOTONIC, &end_time);

    double time_ms = (end_time.tv_sec - start_time.tv_sec) * 1000.0;
    time_ms = time_ms + (end_time.tv_nsec - start_time.tv_nsec) / 1000000.0;

    // Step 7: print results
    cout << "Total pixels processed: " << total_pixels << endl;
    cout << "Total fire pixels found: " << fire_count << endl;
    cout << "Execution time (ms): " << time_ms << endl;
    cout << "Fire coordinates (row, col):" << endl;

    for (int k = 0; k < fire_count; k++) {
        cout << "(" << fire_rows[k] << ", " << fire_cols[k] << ")" << endl;
    }

    // Step 8: save fire map
    ofstream output("results/serial_firemap.bin", ios::binary);
    if (!output) {
        cout << "Error: could not open results/serial_firemap.bin" << endl;
        return 1;
    }

    output.write((char*)&rows, sizeof(int));
    output.write((char*)&cols, sizeof(int));

    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            output.write((char*)&firemap[i][j], sizeof(int));
        }
    }
    output.close();

    cout << "Saved results/serial_firemap.bin" << endl;

    // free memory
    for (int i = 0; i < rows; i++) {
        delete[] grid[i];
        delete[] firemap[i];
    }
    delete[] grid;
    delete[] firemap;

    return 0;
}
