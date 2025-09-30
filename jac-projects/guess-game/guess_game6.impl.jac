impl GuessGame.start {
    print("Welcome to AI-Powered Guess the Number!");
    print(f"Your guess is {self.guess}");
    visit --> turn;
}

impl GuessGame.process_guess {
    if self.guess == self.correct_number {
        print("Congratulations! You guessed correctly 🎉");
        disengage;
    } else {
        print(give_hint(self.guess, self.correct_number));
    }
}
