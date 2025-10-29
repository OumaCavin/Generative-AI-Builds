# 📋 Task Manager Lite – AI Assistant

[![Jac Language](https://img.shields.io/badge/Built%20With-Jac%20Lang-0A66C2?style=for-the-badge&logoColor=white)](https://www.jac-lang.org/)
[![Python](https://img.shields.io/badge/Powered%20By-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![AI Engine](https://img.shields.io/badge/AI-Powered-7B68EE?style=for-the-badge&logo=brain&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)


**Task Manager Lite** is a lightweight AI-powered assistant built using **JAC** and **Streamlit**.  
It intelligently handles **task management**, **email writing**, and **general chat** through a modern frontend and an AI backend powered by the **Jaseci Model interface**.

---

## 🚀 Features

- 📋 Add, summarize, and manage personal tasks  
- ✉️ Generate emails (meeting invites, follow-ups, etc.)  
- 💬 Chat and get productivity or lifestyle advice  
- 🔀 Smart routing by context type (TaskHandling, EmailHandling, GeneralChat)  
- 🧠 Powered by the Jaseci `Model` API for AI-assisted responses  

---

## 🧩 Project Structure

```

├── task_manager.jac      # Handles user login & initializes Streamlit frontend
├── frontend.jac          # Defines interactive Streamlit UI and AI logic
├── README.md             # Project documentation

````

---

## ⚙️ Setup Instructions

### 1. Navigate into the project
If cloned as part of your main repo:
```bash
cd Generative-AI-Builds/jac-projects/task-manager-lite
````

### 2. Activate your Jac environment

```bash
source ../../jac-env/bin/activate
```

### 3. Install dependencies

Ensure Python ≥ 3.12 and Streamlit are installed:

```bash
pip install streamlit requests
```

### 4. Configure Environment (Optional)

If your backend requires an API key, set it in your environment:

```bash
export AI_API_KEY="your_api_key_here"
```

---

## 🧠 Run the JAC Backend

Start the backend server:

```bash
jac serve task_manager.jac
```

This runs the backend locally at:

```
http://localhost:8000
```

---

## 💻 Run the Streamlit Frontend

Run the frontend interface:

```bash
jac streamlit frontend.jac
```

You’ll see output like:

```
Local URL: http://localhost:8501
```

Open that link in your browser to start using Task Manager Lite.

---

## 🧩 Architecture Overview

**Frontend (`task_manager.jac` / `frontend.jac`)**

* Provides an interactive Streamlit interface.
* Sends requests to the Jaseci backend endpoint (`/walker/task_manager`).

**Backend Walker**

* Uses the Jaseci `Model` interface for AI logic:

  ```jac
  glob.llm = Model(model_name="your_default_model", verbose=False);
  response = glob.llm.chat("Your AI prompt here");
  ```
* Returns a structured JSON-like response to the frontend.

---

## 🧰 Example Prompts

Try asking:

* “Add a task to prepare my presentation by Monday.”
* “Write a short email to follow up with a client.”
* “Summarize my current tasks.”
* “Give me 3 tips for managing time effectively.”

---


## 🧑‍💻 Author

**Cavin Otieno Ouma**

🖥️ *MIS Developer & AI Enthusiast*

 📧 [cavin.otieno012@gmail.com](mailto:cavin.otieno012@gmail.com)
 🔗 [LinkedIn Profile](https://www.linkedin.com/in/cavin-otieno-9a841260/)
 📂 Project Repo: [Video Narrator on GitHub](https://github.com/OumaCavin/Generative-AI-Builds/tree/main/jac-projects/task-manager-lite)
 🌐 Main Repository: [Generative-AI-Builds](https://github.com/OumaCavin/Generative-AI-Builds.git)

---

## 🪪 License

This project is licensed under the **MIT License**.
See the [MIT License](https://choosealicense.com/licenses/mit/) file for details.
