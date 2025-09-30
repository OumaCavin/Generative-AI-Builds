impl GuessGame.start_game {
    print("Welcome to Guess the Number!");
    self.correct_number = random.randint(1, 10);
    for attempt in range(10) {
        guess = input("Guess a number between 1 and 10: ");
        if guess.isdigit() {
            self.process_guess(int(guess));
        } else {
            print("That's not a valid number! Try again.");
        }
    }
    disengage;
}

impl GuessGame.process_guess {
    if guess > self.correct_number {
        print("Too high!");
    } elif guess < self.correct_number {
        print("Too low!");
    } else {
        print("Congratulations! You guessed correctly.");
        disengage;
    }
}
