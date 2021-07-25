/* https://fivethirtyeight.com/features/can-you-hop-across-the-chessboard/ */

#include <ctype.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*  
**  Usage:
**
**  First, a board source file needs to be made. In this directory is one, with the same layout as the original Riddler.
**  It consists of four integers, representing the number of rows, number of columns, the starting position row,
**  and the starting position column, respectively. Then, there are characters representing each piece, following
**  the key below.
**  
**  To run the program, pass the path to the board source file as a command line argument. To use stdin, pass "-".
**  The program will print the distance and the path from the start to each destination (the black kings). If DEBUG is 
**  defined during compilation (use -D DEBUG), then the program will print the minimum distances to each point on the
**  board at each step of the pathfinding algorithm (you probably want to redirect this to a file).
**
**  Key to pieces: 
**  P = pawn; K = knight; S = bishop; R = rook; Q = queen; X = black king; B = other black pieces 
*/

typedef struct {
    char type;
    bool visited;
    int distance;
    int prev;
} Vertex;


void visit(int new, int current, Vertex *vertices) {
    if ((vertices[new].type != 'B') && (!vertices[new].visited) && (vertices[current].distance + 1 < vertices[new].distance)) {
        vertices[new].distance = vertices[current].distance + 1;
        vertices[new].prev = current;
    }
}


int main(int argc, char **argv) {
    // Receive input data
    if (argc != 2) {
        fprintf(stderr, "error: a filepath (or the character '-' for stdin) should be the sole argument\n");
        exit(EXIT_FAILURE);
    }

    FILE *fp = (strcmp(argv[1], "-") ? fopen(argv[1], "r") : stdin);
    if (fp == NULL) {
        fprintf(stderr, "error: file %s could not be opened\n", argv[1]);
        exit(EXIT_FAILURE);
    }

    int nrow, ncol, start_r, start_c;
    if (fscanf(fp, "%d %d %d %d", &nrow, &ncol, &start_r, &start_c) < 4) {
        fprintf(stderr, "error: input data formatted incorrectly\n");
        exit(EXIT_FAILURE);
    }

    Vertex *vertices = malloc(nrow * ncol * sizeof(Vertex));

    for (int i = 0; i < nrow * ncol; i++) {
        vertices[i].type = fgetc(fp);

        if (vertices[i].type == EOF) {
            fprintf(stderr, "error: input data formatted incorrectly\n");
            exit(EXIT_FAILURE);

        } else if (isspace(vertices[i].type)) { 
            i--; // skip over newlines w/o saving them

        } else {
            vertices[i].visited = false;
            vertices[i].distance = INT_MAX;
            vertices[i].prev = -1;
        }
    }

    int current = ncol * start_r + start_c;
    vertices[current].distance = 0;

    int min_dist, index_min;
    bool top, bottom, left, right;

    // Run Dijkstra's algorithm
    do {
        // Calculate neighbor distances

        // pre-calculate if we're at the top edge, bottom edge, etc.
        top = (current < ncol);
        bottom = (current >= ncol * (nrow - 1));
        left = (current % ncol == 0);
        right = (current % ncol == nrow - 1);

        switch (vertices[current].type) { // beware: use of fallthroughs below
            case 'Q':
            case 'R':
                // side neighbors
                if (!top)    visit(current - ncol, current, vertices);
                if (!bottom) visit(current + ncol, current, vertices);
                if (!left)   visit(current - 1,    current, vertices);
                if (!right)  visit(current + 1,    current, vertices);
                
                if (vertices[current].type == 'R') break;
            
            case 'S':
                // bottom diagonal neighbors
                if (!bottom && !left)  visit(current + ncol - 1, current, vertices);
                if (!bottom && !right) visit(current + ncol + 1, current, vertices);

            case 'P':
                // top diagonal neighbors
                if (!top && !left)  visit(current - ncol - 1, current, vertices);
                if (!top && !right) visit(current - ncol + 1, current, vertices);
                
                break;

            case 'K':
                if (current >= 2 * ncol) { // not in top two rows
                    if (!left)  visit(current - 2 * ncol - 1, current, vertices);
                    if (!right) visit(current - 2 * ncol + 1, current, vertices);
                }

                if (current < 48) { // not in bottom two rows
                    if (!left)  visit(current + 2 * ncol - 1, current, vertices);
                    if (!right) visit(current + 2 * ncol + 1, current, vertices);
                }

                if (current % 8 > 1) { // not in left two columns
                    if (!top)    visit(current - ncol - 2, current, vertices);
                    if (!bottom) visit(current + ncol - 2, current, vertices);
                }

                if (current % ncol < ncol - 2) { // not in right two columns
                    if (!top)    visit(current - ncol + 2, current, vertices);
                    if (!bottom) visit(current + ncol + 2, current, vertices);
                }

            // no more cases (cannot move from black pieces)
        }

        vertices[current].visited = true;

#ifdef DEBUG
        printf("Row %d, Column %d\n", current / ncol, current % ncol);
        int val;
        for (int r = 0; r < nrow; r++) {
            for (int c = 0; c < ncol; c++) {
                val = vertices[ncol * r + c].distance;
                if (val < 100) {
                    printf("| %2d ", val);
                } else {
                    printf("| XX ");
                }
            }
            printf("|\n");
        }
        printf("\n\n");
#endif

        // Find next 'current' vertex: the unvisited vertex with the minimum distance
        min_dist = INT_MAX;
        index_min = -1;

        for (int i = 0; i < nrow * ncol; i++) {
            if (!vertices[i].visited && vertices[i].distance < min_dist) {
                min_dist = vertices[i].distance;
                index_min = i;
            }
        }

        current = index_min;

    } while (min_dist < INT_MAX);

    // Display output
    for (int i = 0; i < nrow * ncol; i++) {
        if (vertices[i].type == 'X') { // All the destinations, i.e. black kings
            if (vertices[i].distance < INT_MAX) {
                int index = i;
                
                printf("King at (%d, %d) | Distance: %2d | Path: ", index / ncol, index % ncol, vertices[i].distance);
                
                while (true) {
                    printf("(%d, %d) ", index / ncol, index % ncol);
                    if (vertices[index].distance == 0) break;
                    index = vertices[index].prev;
                }
                printf("\n");

            } else {
                printf("King at (%d, %d) is unreachable\n", i / ncol, i % ncol);
            }
        }
    }

    free(vertices);

    return EXIT_SUCCESS;
}
