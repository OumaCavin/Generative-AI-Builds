# Generative-AI-Builds

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jac](https://img.shields.io/badge/JacLang-FF6F00?style=for-the-badge&logoColor=white)

A collection of experiments and projects exploring **Generative AI** and new programming paradigms such as the **Jac Programming Language (Jaseci Stack)**.

---

## 🚀 Getting Started

### Prerequisites
- Ubuntu / WSL2  
- Python **3.12+**  
- Git  
- VS Code (with the [Jac extension](https://marketplace.visualstudio.com/items?itemName=jaseci.jac))  

### Setup Instructions

Clone the repo:
```bash
git clone https://github.com/OumaCavin/Generative-AI-Builds.git
cd Generative-AI-Builds
````

Create and activate a virtual environment (recommended):

```bash
python3.12 -m venv jac-env
source jac-env/bin/activate
```

Install Jac:

```bash
pip install jaclang
```

Verify installation:

```bash
jac --version
```

---

## 📂 Project Structure

```
Generative-AI-Builds/
│── jac-projects/       # Folder for Jac programs
│   └── hello.jac       # First Jac program
│── README.md           # Project documentation
│── .gitignore          # Ignore venv & cache files
│── jac-env/            # Virtual environment (not pushed to GitHub)
```

---

## ▶️ Running Your First Jac Program

Example `hello.jac` inside `jac-projects/`:

```jac
with entry {
    print("Hello, Jac World!");
}
```

Run it:

```bash
cd jac-projects
jac run hello.jac
```

Output:

```
Hello, Jac World!
```

---

## 🛠 Development Environment

* **Jac Language** for graph-based AI programs
* **VS Code** with Jac extension for syntax highlighting & error checking
* **Virtual environment** (`venv`) for isolated dependencies

---

## 🌱 Next Steps

* Explore Jac’s graph-based programming model
* Build more complex AI-driven workflows
* Experiment with serving Jac programs as web applications (`jac serve`)

---

## 🤝 Contributing

Contributions are welcome! 🎉
To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m "Add new feature"`)
4. Push to the branch (`git push origin feature-name`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

