impl GuessGame.start {
    print("Welcome to Guess the Number!");
    print(f"Your guess is {self.guess}");
    visit --> turn;
}

impl GuessGame.process_guess {
    if self.guess > self.correct_number {
        print("Too high!");
    } elif self.guess < self.correct_number {
        print("Too low!");
    } else {
        print("Congratulations! You guessed correctly.");
        disengage;
    }
}
