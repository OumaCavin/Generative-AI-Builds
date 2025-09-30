"""A Number Guessing Game"""

import random;

walker GuessGame {
    has guess: int;

    can start with `root entry;
    can process_guess with turn entry;
}

node turn {
    has correct_number: int = random.randint(1, 10);
}

# CLI-only execution
with entry:__main__ {
    root spawn GuessGame(3);
    root spawn GuessGame(4);
    root spawn GuessGame(5);
    root spawn GuessGame(6);
}
