"""A Number Guessing Game"""

import random;
import from byllm.llm { Model }

# Use an LLM (you can adjust to gpt-4o or gemini)
glob llm = Model(model_name="gemini/gemini-2.0-flash", verbose=False);

"""Provide a fun hint if guess is incorrect"""
def give_hint(guess: int, correct_number: int) -> str by llm();

walker GuessGame {
    has guess: int;

    can start with `root entry;
    can process_guess with turn entry;
}

node turn {
    has correct_number: int = random.randint(1, 10);
}

with entry:__main__ {
    root spawn GuessGame(3);
    root spawn GuessGame(4);
    root spawn GuessGame(5);
    root spawn GuessGame(6);
}
