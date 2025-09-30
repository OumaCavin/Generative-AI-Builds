"""A Number Guessing Game"""

import random;

walker GuessGame {
    has correct_number: int = random.randint(1, 10);

    can start_game with `root entry;
    def process_guess(guess: int);
}

node turn {
    can check with GuessGame entry;
}

with entry {
    GuessGame() spawn root;
}
