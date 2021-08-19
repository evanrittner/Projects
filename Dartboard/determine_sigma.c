#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define R1 0.037383
#define R2 0.093458
#define R3 0.55989 //alternate: 0.59813
#define R4 0.63551
#define R5 0.92352 //alternate: 0.96262


// Determine the percentage of normally-distributed samples, with standard
// deviation sigma and mean (0, 0), that fall: on the board; within the triple
// ring (excluding the triple ring itself); on either bullseye; on the inner
// bullseye
void count_bins(double *bins, double sigma, int count) {
    double radius;

    for (int i = 0; i < 4; i++) bins[i] = 0;

    for (int i = 0; i < count; i++) {
        radius = sigma * sqrt(-2 * log((double) rand() / RAND_MAX));
        
        if (radius <= 1)  bins[0]++;
        if (radius <= R3) bins[1]++;
        if (radius <= R2) bins[2]++;
        if (radius <= R1) bins[3]++;
    }

    for (int i = 0; i < 4; i++) bins[i] /= count;
}


int main(int argc, char** argv) {
    double sigma;
    double bins[4];

    for (int i = 0; i <= 100; i++){
        sigma = (double) i / 100;
        count_bins(bins, sigma, 1000000);
        printf("|%.2f|%f|%f|%f|%f|\n", sigma, bins[0], bins[1], bins[2], bins[3]);
    }

    return 0;
}
