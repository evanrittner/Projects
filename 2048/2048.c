/* Simple ncurses inplementation of the game 2048. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ncurses.h>

#define NCOL 4
#define NROW 4
#define MIN_HEIGHT (4 * (NROW) + 5)
#define MIN_WIDTH  (7 * (NCOL) + 1)
#define MAX(a, b) (((a) > (b)) ? (a) : (b))

#ifdef DEBUG
    #define log_fprintf(...) fprintf(__VA_ARGS__)
#else
    #define log_fprintf(...) // left undefined
#endif /* DEBUG */


FILE *logfp;
enum DIRECTIONS {UP = 0x1, LEFT = 0x2, DOWN = 0x4, RIGHT = 0x8};


/*
**  Print the outline of the board.
*/
void print_blank_board(int height, int width) {
    int vert_offset = (height - MIN_HEIGHT) / 2;
    int horiz_offset = (width - MIN_WIDTH) / 2;

    // Title
    int title_spaces = (MIN_WIDTH - 4) / 2;
    mvprintw(vert_offset, horiz_offset, "%*s", title_spaces + 4, "2048");

    // Print the board top line
    move(vert_offset + 2, horiz_offset);
    for (int col = 0; col < NCOL; col++) {
        if (col == 0) addch(ACS_ULCORNER);
        else addch(ACS_TTEE);

        for (int i = 0; i < 6; i++) addch(ACS_HLINE);
    }
    addch(ACS_URCORNER);
    

    for (int row = 0; row < NROW; row++) {
        // Print empty tiles
        for (int line = 0; line < 3; line++) {
            move(vert_offset + 4 * row + line + 3, horiz_offset);

            for (int col = 0; col < NCOL; col++) {
                addch(ACS_VLINE);
        
                for (int i = 0; i < 6; i++) addch(' ');
            }
            addch(ACS_VLINE);
        }
        
        move(vert_offset + 4 * row + 6, horiz_offset);

        if (row != (NROW - 1)) {
            // Print line between rows of tiles
            for (int col = 0; col < NCOL; col++) {
                if (col == 0) addch(ACS_LTEE);
                else addch(ACS_PLUS);

                for (int i = 0; i < 6; i++) addch(ACS_HLINE);
            }
            addch(ACS_RTEE);

        } else {
            // Print the bottom line
            for (int col = 0; col < NCOL; col++) {
                if (col == 0) addch(ACS_LLCORNER);
                else addch(ACS_BTEE);

                for (int i = 0; i < 6; i++) addch(ACS_HLINE);
            }
            addch(ACS_LRCORNER);
        }
    }

    refresh();
}


/*
**  Update the printed board with the current cell values and the score.
*/
void print_update(int *board, int score, int height, int width) {
    int vert_offset = (height - MIN_HEIGHT) / 2;
    int horiz_offset = (width - MIN_WIDTH) / 2;
    
    // Board
    char box_str[7]; // 7 = width of cell + 1
    int right_spaces;

    for (int row = 0; row < NROW; row++) {
        for (int col = 0; col < NCOL; col++) {
            move(4 * row + vert_offset + 4, 7 * col + horiz_offset + 1);

            if (board[NCOL * row + col]) { // if the cell is not empty
                snprintf(box_str, 7, "%d", 1 << board[NCOL * row + col]);
                right_spaces = (6 - strlen(box_str)) / 2;
                
                printw("%*s", 6 - right_spaces, box_str);
                for (int i = 0; i < right_spaces; i++) addch(' ');
            
            } else {
                addstr("      ");   
            }
        }
    }

    // Score
    char score_str[MIN_WIDTH + 1]; 
    snprintf(score_str, MIN_WIDTH + 1, "Score: %d", score); 
    int score_offset = (MIN_WIDTH - strlen(score_str)) / 2;

    mvprintw(vert_offset + (MIN_HEIGHT - 1), horiz_offset + score_offset, score_str);

    refresh();
}


/*
**  Randomly fills an empty cell on the board with a '2'. Returns the index of the 
**  cell that got filled, or -1 if the board is already full.
*/
int place_piece(int *board) {
    int num_empty = 0;
    int empty_indices[NROW * NCOL];

    for (int i = 0; i < (NROW * NCOL); i++) {
        if (board[i] == 0) {
            empty_indices[num_empty++] = i;
        }
    }

    // Check if board is full (if so, return -1)
    if (num_empty == 0) return -1;
    
    // Pick a random empty cell and fill it with a 2 (represented with a 1)
    int index = empty_indices[rand() / (RAND_MAX / num_empty)];

    board[index] = 1;
    
    return index;
}


/*
**  Get user input. Allows WASD or arrow keys to provide directions; returns 
**  one of enum DIRECTION. If the player inputs 'q' or Esc, return -1.
*/
int get_direction() {
    while (1) {
        switch (getch()) {
            
            case 'w': 
            case KEY_UP:
                return UP;

            case 'a':
            case KEY_LEFT:
                return LEFT;

            case 's':
            case KEY_DOWN:
                return DOWN;

            case 'd':
            case KEY_RIGHT:
                return RIGHT;

            case 'q':
            case 27:  // 'Esc' key
                return -1;
        }
    }
}


/*
**  Given a source game board and a direction to move, follow the rules of 2048,
**  sliding and combining tiles, and write the result to output. To modify a board
**  in-place, pass it as both input and output. direction should be one of enum
**  DIRECTION. Returns the amount to increase the score from the move (i.e. the
**  total value of all cells that combined during the move).
*/
int move_board(int *board, int direction) {
    // Note: in this function, "perp" means perpendicular and "plel" means parallel
    // (specifically, in reference to the direction we're moving the board)
    int perp_move, plel_move, start;
    int score_inc = 0; // Accumulated increment to the score
    
    switch (direction) {
        case UP:
            perp_move = 1;     // move across columns, left to right,
            plel_move = NCOL;  // and in each, move top to bottom
            start = 0;         // starting from index 0 (top left)
            break;

        case LEFT:
            perp_move = NCOL;  // move down across the rows
            plel_move = 1;     // and within the rows, go left to right
            start = 0;         // starting from index 0 (top left)
            break;

        case DOWN:
            perp_move = 1;     // etc.
            plel_move = -NCOL;
            start = NCOL * (NROW - 1); // bottom left
            break;

        case RIGHT:
            perp_move = NCOL;
            plel_move = -1;
            start = NCOL - 1; // top right
            break;

        default:
            return 0;
    }

    log_fprintf(logfp, "Perp move: %d, Parallel move: %d, start: %d\n", perp_move, plel_move, start);

    // perp_count is the length of the perpendicular dimension of movement, i.e.
    // the length of a row when direction == UP or DOWN, and vice versa
    // plel_count is the opposite
    int perp_count = ((direction == UP || direction == DOWN) ? NCOL : NROW); 
    int plel_count = ((direction == UP || direction == DOWN) ? NROW : NCOL);

    int current, tmp_index, line_index;
    int tmp_line[MAX(NROW, NCOL) + 1];  // compile-time const large enough for both rows and columns

    for (int line_no = 0; line_no < perp_count; line_no++) {
        // Algorithm:
        // Make a temporary array, consisting of all the non-empty cells in order
        // Walk along the array; if a cell matches the next, put their sum on the board,
        //   then skip the second value that was combined. If a cell's neighbor doesn't
        //   match, just put the value in unmodified  
       
        tmp_index = 0;
        for (int i = 0; i < MAX(NROW, NCOL); i++) tmp_line[i] = -1; // fill with a sentinel of -1 (like \0 for strings)

        for (line_index = 0; line_index < plel_count; line_index++) {
            current = start + (line_no * perp_move) + (line_index * plel_move);
            
            if (board[current]) {
                tmp_line[tmp_index++] = board[current];
            }
        }

        log_fprintf(logfp, "Line no. %d, temp array: [", line_no);
        for (int i = 0; i < plel_count; i++) log_fprintf(logfp, "%d, ", tmp_line[i]);
        log_fprintf(logfp, "]\n");

        tmp_index = 0;
        line_index = 0;

        for (line_index = 0; line_index < plel_count; line_index++) {
            current = start + (line_no * perp_move) + (line_index * plel_move);

            if (tmp_index >= plel_count || tmp_line[tmp_index] == -1) {
                board[current] = 0;
                log_fprintf(logfp, "Setting index %d to 0 (tmp_index = %d)\n", current, tmp_index);
                
            } else if (tmp_line[tmp_index] == tmp_line[tmp_index + 1]) {
                log_fprintf(logfp, "Combining tmp indices %d and %d to be %d at index %d\n", tmp_index, tmp_index + 1, tmp_line[tmp_index] + 1, current);
                board[current] = tmp_line[tmp_index] + 1;
                tmp_index++; // extra increment, since we just combined two cells

                // Add to the accumulated score
                score_inc += (1 << board[current]);

            } else {
                board[current] = tmp_line[tmp_index];
                log_fprintf(logfp, "Just placing %d at index %d (tmp_index = %d)\n", board[current], current, tmp_index);
            }

            tmp_index++;
        }
    }

    return score_inc;
}


/*
**  Diagnostic function; writes the board to a log file
*/
void log_board(int *board) {
    for (int row = 0; row < NROW; row++) {
        for (int col = 0; col < NCOL; col++) {
            log_fprintf(logfp, "%d\t", board[NCOL * row + col]);
        }
        log_fprintf(logfp, "\n");
    }
}


int main() {
    int *board = calloc(NROW * NCOL, sizeof(int)); // Each cell holds the log_2 of its value (0 -> empty)
    int *prev_board = malloc(NROW * NCOL * sizeof(int)); // Array to check if a move changed anything
    int score = 0;  // When two cells merge, score is increased by the sum of the merged cells
    int max = 1;    // The highest numbered cell made this game (saved as the log_2 of the max)

    // ncurses initialization
    initscr();
    cbreak();
    noecho();
    curs_set(0);
    keypad(stdscr, TRUE);
    
    int height, width;
    getmaxyx(stdscr, height, width);

    if (height < MIN_HEIGHT || width < MIN_WIDTH) { // terminal too small
        endwin();
        printf(
            "error: terminal window is too small (minimum %d high and %d wide; currently %d x %d)\n", 
            MIN_HEIGHT, MIN_WIDTH, height, width
        );
        return 1;
    }
    
#ifdef DEBUG
    logfp = fopen("log.txt", "w");
    setvbuf(logfp, NULL, _IONBF, 1);
    srand(0); // fix random number generation for testing
#endif

    // Initialize prev_board to impossible state so that first '2' is placed
    for (int i = 0; i < (NROW * NCOL); i++) {
        prev_board[i] = -1;
    }

    // Print the blank board (the only things changed during the game are the cells and the score)
    print_blank_board(height, width);

    int location, direction, score_inc, check_index;

    // Main loop
    while (1) {
        // Check if the previous move actually changed the state of the board
        for (check_index = 0; check_index < (NROW * NCOL); check_index++) {
            if (prev_board[check_index] != board[check_index])
                break;
        }

        // If the previous move changed the board, generate a new '2' on an empty cell
        if (check_index < NROW * NCOL) {
            location = place_piece(board);
            if (location == -1) break;  // Board is full => game over
            log_fprintf(logfp, "\nLocation: %d\n", location);
        }

        // Set prev_board to the current board
        for (int i = 0; i < (NROW * NCOL); i++) {
            prev_board[i] = board[i];
        }

        // Show the player the board
        print_update(board, score, height, width);
        log_board(board);

        // Get the player's move
        direction = get_direction();
        if (direction == -1) break;  // User exited with 'q' or Esc
        log_fprintf(logfp, "Direction: %d\n", direction);

        // Calculate the result of the move
        score_inc = move_board(board, direction);

        // Update the score and max
        score += score_inc;
        max = 0;
        for (int i = 0; i < (NROW * NCOL); i++) {
            max = (max > board[i] ? max : board[i]);
        }
    }
    

    // Clean up
    endwin();
    free(board);
    free(prev_board);
#ifdef DEBUG
    fclose(logfp);
#endif

    // Print closing message
    printf("\t\tGame Over!\n\tScore: %d\tMaximum Tile: %d\n", score, 1 << max);

    return 0;
}
