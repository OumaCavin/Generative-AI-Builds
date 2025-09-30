# 🎯 Number Guessing Game – Jac Learning Steps

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge\&logo=python)
![JacLang](https://img.shields.io/badge/JacLang-Latest-orange?style=for-the-badge\&logo=graphql)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A collection of simple projects to learn and demonstrate the **Jac Language** – a graph-based programming language that combines declarative and imperative paradigms.

---

## 📂 Project Structure

```
Generative-AI-Builds/
│── jac-projects/
│   ├── guess-game/
│   │   ├── guess_game.py                # Step 0 – Python version 
│   │   ├── guess_game1.jac              # Step 1 – Direct Jac translation
│   │   ├── guess_game2.jac              # Step 2 – Declaring fields with has
│   │   ├── guess_game3.jac              # Step 3 – Object definitions
│   │   ├── guess_game3.impl.jac
│   │   ├── guess_game4.jac              # Step 4 – Graph walking
│   │   ├── guess_game4.impl.jac
│   │   ├── guess_game5.jac              # Step 5 – Scale agnostic design
│   │   ├── guess_game5.impl.jac
│   │   ├── guess_game6.jac              # Step 6 – AI-enhanced gameplay
│   │   ├── guess_game6.impl.jac
│   │   └── README.md
```

---

## 🔥 Jac in a Flash

A progressive **Number Guessing Game** built in **6 steps**, each introducing a new Jac concept.

### 🗂️ Summary Table

| Step | File(s)                                   | Concept                | Example Output                                   |
| ---- | ----------------------------------------- | ---------------------- | ------------------------------------------------ |
| 0    | `guess_game.py`                           | Python Version         | Classic CLI guessing game                        |
| 1    | `guess_game1.jac`                         | First Class            | `Game created: Guess a number between 1 and 100` |
| 2    | `guess_game2.jac`                         | User Interaction       | `Too low! Try again.`                            |
| 3    | `guess_game3.jac`, `guess_game3.impl.jac` | Separation of Concerns | `Starting Guess Game...`                         |
| 4    | `guess_game4.jac`, `guess_game4.impl.jac` | Walking the Graph      | `Walker starting game...`                        |
| 5    | `guess_game5.jac`, `guess_game5.impl.jac` | Scale Agnostic         | `Game 1: Correct! 🎉`                            |
| 6    | `guess_game6.jac`, `guess_game6.impl.jac` | AI-Enhanced Gameplay   | `AI Hint 🤖: "Think a bit higher..."`            |

---

### **Step 0 – Python Version**

```bash
python3 guess_game.py
```

✅ Output:

```
Guess a number between 1 and 10:
Too low! Try again.
Congratulations! You guessed correctly.
```

---

### **Step 1 – First Class**

```bash
jac run guess_game1.jac
```

✅ Output:

```
Game created: Guess a number between 1 and 100
```

---

### **Step 2 – User Interaction**

```bash
jac run guess_game2.jac
```

✅ Output:

```
Welcome to Jac Guess Game!
Enter your guess: 50
Too low! Try again.
```

---

### **Step 3 – Separation of Concerns**

```bash
jac run guess_game3.jac
```

✅ Output:

```
Game setup complete.
Starting Guess Game...
```

---

### **Step 4 – Walking the Graph**

```bash
jac run guess_game4.jac
```

✅ Output:

```
Walker starting game...
Guess: 30
Too low!
```

---

### **Step 5 – Scale Agnostic**

```bash
jac run guess_game5.jac
```

✅ Output:

```
Game 1: Correct! 🎉
Game 2: Too high!
```

---

### **Step 6 – AI-Enhanced Gameplay**

```bash
jac run guess_game6.jac
```

✅ Output:

```
Welcome to AI-Powered Guess Game!
AI Hint 🤖: "Think a bit higher, maybe in the 40s."
```

---

## 📖 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

