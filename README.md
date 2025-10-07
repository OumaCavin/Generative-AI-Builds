# Generative-AI-Builds

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jac](https://img.shields.io/badge/JacLang-FF6F00?style=for-the-badge&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

A collection of experiments and projects exploring **Generative AI** using the **Jac Programming Language (Jaseci Stack)** and related tools.  
All projects share a single virtual environment (`jac-env/`) for easier dependency management.

---

## 📂 Repository Structure

```
Generative-AI-Builds/
│
├── jac-projects/
│   ├── hello-world/
│   │   ├── hello.jac
│   │   └── README.md
│   │
│   ├── guess-game/
│   │   ├── guess_game.py
│   │   ├── guess_game1.jac
│   │   ├── guess_game2.jac
│   │   ├── guess_game3.jac
│   │   ├── guess_game3.impl.jac
│   │   ├── guess_game4.jac
│   │   ├── guess_game4.impl.jac
│   │   ├── guess_game5.jac
│   │   ├── guess_game5.impl.jac
│   │   ├── guess_game6.jac
│   │   └── guess_game6.impl.jac
│   │
│   ├── video-narrator/
│   │   ├── client.jac
│   │   ├── server.jac
│   │   ├── server.impl.jac
│   │   ├── mcp_server.jac
│   │   ├── mcp_client.jac
│   │   ├── tools.jac
│   │   ├── requirements.txt
│   │   ├── .gitignore
│   │   ├── README.md
│   │   ├── chroma/
│   │   ├── uploads/
│   │   └── assets/
│   │       └── streamlit_ui.png
│   │
│   └── graph-demo/
│       ├── graph_example.jac
│       └── README.md
│
├── .gitignore
├── README.md        # Main repo overview (all JAC projects)
├── LICENSE
└── jac-env/         # Python virtual environment

```

---

## 📂 Jac Projects in this Repository

| Project | Description | Link |
|---------|-------------|------|
| **Hello World** | First Jac program (prints a message) | [hello-world](jac-projects/hello-world) |
| **Guess Game** | Classic number guessing game built step-by-step in Jac | [guess-game](jac-projects/guess-game) |
| **Video Narrator** | Converts silent videos into narrated explanations using LLMs+Streamlite UI | [video-narrator](jac-projects/video-narrator) |
| **Graph Demo** | Demonstrates graph traversal in Jac | [graph-demo](jac-projects/graph-demo) |


---

## 🚀 Getting Started

### Prerequisites

- Ubuntu / WSL2
- Python **3.12+**
- Git
- VS Code (with the [Jac extension](https://marketplace.visualstudio.com/items?itemName=jaseci.jac))

---

### Setup Instructions

Clone the repo:

```bash
git clone https://github.com/OumaCavin/Generative-AI-Builds.git
cd Generative-AI-Builds
````

Create and activate a virtual environment:

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

### Running a Project

Each project lives inside `jac-projects/`.
For example, to run the **Hello World** program:

```bash
cd jac-projects/hello-world
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
* Shared **virtual environment (`jac-env/`)** for all projects
* Dependencies managed via `requirements.txt`

---

## 🌱 Next Steps

* Build more Jac-based AI projects
* Experiment with serving Jac programs (`jac serve`)
* Add containerization via **Docker**
* Deploy projects with **Render**

---

## 🤝 Contributing

Contributions are welcome!
Please fork the repo, create a new branch, and submit a pull request.

---

## 📜 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

