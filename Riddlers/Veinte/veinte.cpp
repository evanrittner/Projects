#include <iostream>
#include <vector>
#include <algorithm>

#define END_NUM 20
#define MAX_INCR 4
                            /* this doesn't work for some reason */
using std::vector;

struct Move {
    int prev;
    int next;
    int outcome;

    Move() = default;
    Move(int p, int n, int o) : prev(p), next(n), outcome(o) { }
    bool operator< (const Move m) {return outcome < m.outcome;}
};

vector<int> get_round_strats(int round) {
    if (round == 1)
        return vector<int> {0};
    

    vector<int> goals {0};
    for (int position : get_round_strats(round - 1)) {
        goals.push_back(position + 1);
    }

    vector<int> forced_outcomes(round);
    forced_outcomes[0] = goals[round - 1];
    for (int i = 1; i != round; ++i) {
        forced_outcomes[goals[i]] = goals[i - 1];
    }
    
    vector<Move> strats(END_NUM);
    for (int prev_num = END_NUM - 1; prev_num >= 0; --prev_num) {
        vector<Move> options;
        for (int incr = 1; incr < MAX_INCR; ++incr) {
            if (prev_num + incr > 20)
                continue;

            int my_outcome;
            if (prev_num + incr == 20) {
                my_outcome = goals[round - 1];
            } else {
                int next_outcome = strats[prev_num + incr].outcome;
                my_outcome = forced_outcomes[next_outcome];
            }

            options.emplace_back(prev_num, prev_num + incr, my_outcome);
        }

        Move best_move = *std::max_element(cbegin(options), cend(options));
        strats[prev_num] = best_move;
    }

    int index_2nd = 0;
    for (; index_2nd != strats[1].outcome; ++index_2nd) { }

    vector<int> results(round);
    for (int i = 0; i != round; ++i) {
        results[(i + 1) % round] = goals[(i + index_2nd) % round];
    }

    return results;
}

int main() {
    for (int pos : get_round_strats(3)) {
        std::cout << pos << ' ';
    }
    std::cout << std::endl;
}