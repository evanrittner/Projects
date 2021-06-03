#include <vector>
#include <array>
#include <iostream>

using std::vector; using std::array;


const array<array<array<int, 2>, 2>, 8> TRANSFORM {{
    { {{1, 0},  {0, 1}}  },   // rotation of 0
    { {{0, -1}, {1, 0}}  },   // rotation of 90
    { {{-1, 0}, {0, -1}} },   // rotation of 180
    { {{0, 1},  {-1, 0}} },   // rotation of 270
    { {{1, 0},  {0, -1}} },   // reflect across x
    { {{-1, 0}, {0, 1}}  },   // reflect across y
    { {{0, -1}, {-1, 0}} },   // reflect across main diag
    { {{0, 1},  {1, 0}}  }    // reflect across other diag
}};

const array<array<int, 7>, 7> BASE = {{ 
    { {0, 0, 0, 0, -1, 0, -1} },
    { {0, 0, 0, 0, 0, 0, -1} },
    { {0, 0, 0, 0, 0, 0, 0} },
    { {0, 0, 0, 0, 0, 0, 0} },
    { {0, 0, 0, 0, 0, 0, 0} },
    { {0, 0, -1, 0, 0, 0, 0} },
    { {0, 0, 0, -1, -1, -1, -1} }
}};


struct Tile {
    vector<vector<int>> points; 
    vector<int> transformations;
};

class ShapeIterator {
    public:
    vector<vector<int>> points;
    vector<int> orientations;

    std::vector<vector<int>>::const_iterator point_iter;
    std::vector<int>::const_iterator orientation_iter;

    int x, y, o;

    //Constructor provided selected points
    ShapeIterator(vector<vector<int>> p, vector<int> o)
        : points(p), orientations(o), point_iter(points.cbegin()),
        orientation_iter(orientations.cbegin()), x((*point_iter)[0]),
        y((*point_iter)[1]), o((*orientation_iter)) { }

    //Constructor just provided with orientations (assume all points in BASE)
    ShapeIterator(vector<int> o) 
        : orientations(o), orientation_iter(orientations.cbegin()),
        o(*orientation_iter) {
            for (int i = 0; i != 7; ++i) {
                for (int j = 0; j != 7; ++j) {
                    if (BASE.at(i).at(j) == 0) {
                        points.emplace_back(i, j);
                    }
                }
            }
            point_iter = points.cbegin();
        }

    void operator++() {
        if (++orientation_iter == orientations.cend()) {
            orientation_iter = orientations.cbegin();
            ++point_iter;

            x = (*point_iter).at(0);
            y = (*point_iter).at(1);
        }

        o = *orientation_iter;
    }

    void reset(vector<vector<int>> new_points) {
        points = new_points;
        point_iter = points.cbegin();
        orientation_iter = orientations.cbegin();

        x = (*point_iter).at(0);
        y = (*point_iter).at(1);
        o = *orientation_iter;
    }
};


const array<Tile, 8> TILE = {{
    {{{0, 0}, {1, 0}, {1, 1}, {-1, 0}, {-1, -1}},         {0, 1, 4, 6}},
    {{{0, 0}, {1, 0}, {2, 0}, {0, 1}, {0, 2}},            {0, 1, 2, 3}},
    {{{0, 0}, {0, 1}, {-1, 0}, {1, 0}, {2, 0}},           {0, 1, 2, 3, 4, 5, 6, 7}},
    {{{0, 0}, {0, 1}, {-1, 0}, {-1, 1}, {1, 0}, {1, 1}},  {0, 1}},
    {{{0, 0}, {0, 1}, {-2, 0}, {-1, 0}, {1, 1}},          {0, 1, 2, 3, 4, 5, 6, 7}},
    {{{0, 0}, {0, 1}, {-1, 0}, {-1, 1}, {1, 0}},          {0, 1, 2, 3, 4, 5, 6, 7}},
    {{{0, 0}, {-1, 0}, {-1, 1}, {1, 0}, {1, 1}},          {0, 1, 2, 3}},
    {{{0, 0}, {-2, 0}, {-1, 0}, {1, 0}, {1, 1}},          {0, 1, 2, 3, 4, 5, 6, 7}}
}};


int main(int argc, char **argv) {
    vector<vector<int>> grid(7, vector<int> (7, 0));
    for (int i = 0; i != 7; ++i) for (int j = 0; j != 7; ++j) {
        grid.at(i).at(j) = BASE.at(i).at(j);
    }

    vector<ShapeIterator> iterators;
    for (int i = 0; i != 8; ++i) {
        iterators.emplace_back(TILE[i].transformations);
    }


    int current_index = 0;
    while (0 <= current_index && current_index < 9) {
        //Clear all points in the grid with the current index (+1)
        for (int i = 0; i != 7; ++i) for (int j = 0; j != 7; ++j) {
            if (grid.at(i).at(j) == current_index + 1)
                grid.at(i).at(j) = 0;
        }

        //Iterate through the iterator until we find a triplet
        // (x, y, o) that lets us fit
        //If one exists, place shape in grid, and increment index, 
        // reset the next iterator w/ the new points, and let the while loop loop
        //If not, back up to the previous index, 
        // letting it continue from where it left off
        while (true) {
            if (grid.at(iterators.at(current_index).x).at(iterators.at(current_index).y) == 0) {
                bool shape_fits = false;

                //Calculate position of shape after transformation
                vector<vector<int>> shape;

                for (vector<int> point : TILE[current_index].points) {
                    vector<int> transformed_point = {

                        TRANSFORM[iterators.at(current_index).o][0][0] * point[0] 
                        + TRANSFORM[iterators.at(current_index).o][0][1] * point[1] 
                        + iterators.at(current_index).x,

                        TRANSFORM[iterators.at(current_index).o][1][0] * point[0] 
                        + TRANSFORM[iterators.at(current_index).o][1][1] * point[1]
                        + iterators.at(current_index).y
                    };

                    if (0 <= transformed_point.at(0) && 0 <= transformed_point.at(1) //point is w/in grid and free
                        && transformed_point.at(0) < 7 && transformed_point.at(1) < 7
                        && grid.at(transformed_point.at(0)).at(transformed_point.at(1)) == 0) {

                        //keep track, but don't place the shape yet
                        shape.push_back(transformed_point);

                    } else {
                        shape_fits = false;
                        break; //this combination of x, y, orientation doesn't work
                    }
                }

                if (shape_fits) { //then actually place it on the grid
                    ++current_index;

                    for (vector<int> point : shape) {
                        grid.at(point.at(0)).at(point.at(1)) = current_index;
                    }
                    
                    //Determine avalable points in grid to send to next shape iterator
                    vector<vector<int>> free_points;
                    for (int i = 0; i != 7; ++i) for (int j = 0; j != 7; ++j) {
                        if (grid.at(i).at(j) == 0) {
                            free_points.emplace_back(i, j);
                        }
                    }
                    iterators.at(current_index).reset(free_points);
                    
                    break; //out of inner while(true) (not outer)
                }
            }

            ++iterators.at(current_index);

            if (iterators.at(current_index).x != 0
                || iterators.at(current_index).y != 0
                || iterators.at(current_index).y != 0) {
                //Made it back to the beginning => can't fit this shape => need to go back
                --current_index;
                break;
            }
        } 
    }


    //Print result
    for (vector<int> row : grid) {
        for (int n : row) {
            std::cout << n << ' ';
        }
        std::cout << std::endl;
    }

    return 0;
}
