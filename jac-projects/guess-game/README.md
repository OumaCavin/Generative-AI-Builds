# 🎮 Number Guessing Game – (JAC + LiteLLM + Gemini)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![JacLang](https://img.shields.io/badge/JacLang-Latest-orange?style=for-the-badge&logo=graphql)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)



This is a simple **AI-powered number guessing game** built with **JAC language**.  
It demonstrates how to progressively learn Jac concepts while integrating **Gemini (Google AI Studio)** through **LiteLLM** and **BLLM**.

---

## 🚀 Features
- ✅ Step-by-step progression from Python → Jac (Steps 0–6).  
- ✅ Uses **Gemini 2.5 Flash** for AI-powered hints.  
- ✅ Supports multiple LLM backends (OpenAI, Gemini, etc.).  
- ✅ Shows how to save API keys permanently (Linux/macOS + Windows).  

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

````

---


## 📦 Requirements


Ensure you have the following installed:

- Python 3.12+  
- [Poetry](https://python-poetry.org/) or `pip`  
- jaclang, byllm
- A valid `GEMINI_API_KEY` environment variable 

Install dependencies:

```bash
pip install jaclang jaseci jaseci-ai-tools litellm bllm
````

---

## ⚙️ Setup Instructions

### 1️⃣ Install Jac and bllm

```bash
pip install jaclang
pip install bllm
```

### 2️⃣ Get a Gemini API Key

1. Go to **[Google AI Studio](https://aistudio.google.com/)**
2. Create a new project.
3. Generate a new API key under **"API Keys"**.
4. Copy your key (e.g., `AIzaSy...`).

### 3️⃣ Export API Key

#### 🔑 API Key Setup (Gemini – Google AI Studio)

We use the **Gemini API key** (AI Studio) for authentication.

#### Temporary (session only)

Linux/macOS:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Windows (PowerShell):

```powershell
setx GEMINI_API_KEY "your_api_key_here"
```

#### Permanent Setup

##### Linux/macOS

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.profile`):

```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

##### Windows

In PowerShell:

```powershell
setx GEMINI_API_KEY "your_api_key_here"
```

Restart your terminal to apply the change.

✅ Verify with:

```bash
echo $GEMINI_API_KEY   # Linux/macOS
echo %GEMINI_API_KEY%  # Windows (cmd)
```

### 4️⃣ Update Model in JAC

In `guess_game6.jac`, we use Gemini 2.5 Flash:

```jac
# ✅ Update (Gemini AI Studio)
glob llm = Model(model_name="gemini/gemini-2.5-flash", verbose=False);
```
⚠️ Note: If you use `gemini-2.5-flash` (without the `gemini/` prefix), LiteLLM assumes **Vertex AI** and requires GCP setup.
Always use the `gemini/` prefix for AI Studio.

---

## 🔥 Jac in a Flash

A progressive **Number Guessing Game** built in **6 steps**, each introducing a new Jac concept.

### 🗂️ Summary Table

| Step | File(s)                                   | Concept                | Example Output                                   |
| ---- | ----------------------------------------- | ---------------------- | ------------------------------------------------ |
| 0    | `guess_game.py`                           | Python Version         | `Too high! / Too low! / Congratulations!`        |
| 1    | `guess_game1.jac`                         | First Class            | `Too high! / Congratulations!`                   |
| 2    | `guess_game2.jac`                         | User Interaction       | `Too low! / Congratulations!`                    |
| 3    | `guess_game3.jac`, `guess_game3.impl.jac` | Separation of Concerns | `Too low! / Congratulations!`                    |
| 4    | `guess_game4.jac`, `guess_game4.impl.jac` | Walking the Graph      | `Too high! / Too low! / Congratulations!`        |
| 5    | `guess_game5.jac`, `guess_game5.impl.jac` | Scale Agnostic         | Mixed outputs (demoing scalability issues)       |
| 6    | `guess_game6.jac`, `guess_game6.impl.jac` | AI-Enhanced Gameplay   | `AI Hint 🤖: "Think a bit higher..."`            |

---

### **Step 0 – Python Version**

```bash
python3 guess_game.py
````

✅ Output:

```
Guess a number between 1 and 10: 5
Too high!
You have 9 attempts left.
...
Congratulations! You guessed correctly.
```

---

### **Step 1 – First Class**

```bash
jac run guess_game1.jac
```

✅ Output:

```
Guess a number between 1 and 10: 5
Too high!
Congratulations! You guessed correctly.
```

---

### **Step 2 – User Interaction**

```bash
jac run guess_game2.jac
```

✅ Output:

```
Guess a number between 1 and 10: 5
Too high!
Guess a number between 1 and 10: 1
Too low!
...
Congratulations! You guessed correctly.
```

---

### **Step 3 – Separation of Concerns**

```bash
jac run guess_game3.jac
```

✅ Output:

```
Guess a number between 1 and 10: 5
Too low!
...
Congratulations! You guessed correctly.
```

---

### **Step 4 – Walking the Graph**

```bash
jac run guess_game4.jac
```

✅ Output:

```
Guess a number between 1 and 10: 5
Too high!
Guess a number between 1 and 10: 3
Too low!
...
Congratulations! You guessed correctly.
```

---

### **Step 5 – Scale Agnostic**

```bash
jac run guess_game5.jac
```

✅ Output (mixed):

```
Too high!
Too high!
Congratulations! You guessed correctly.
Too low!
```

---

### **Step 6 – AI-Enhanced Gameplay (Gemini)**

```bash
jac run guess_game6.jac
```

✅ Output:

```
Higher! It's not quite 3, but you're getting warmer... like a freshly baked cookie!
You're getting warmer, but you need to aim a little higher! Think of it like a ladder – you're on the rung right below the one you want!
Congratulations! You guessed correctly.
Oops! You're so close, but you're aiming a little too high – like a basketball player shooting for the moon! Try a smaller number.
```

---
## ⚡ Notes & Troubleshooting

* If you get `401 UNAUTHENTICATED`: check your API key is set correctly.
* If you get `404 NOT_FOUND`: ensure you’re using a valid **model name** from AI Studio (`gemini/gemini-2.5-flash`).
* If you see `ModuleNotFoundError: No module named 'google'`, you likely tried Vertex AI. Stick to AI Studio API key instead.

---


## 📖 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).




