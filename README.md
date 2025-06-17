# 🚀 EVAL EDGE – Online Judge Platform

![Eval Edge Banner](./screenshots/banner.png) <!-- Replace with your own banner or logo -->

[![Website](https://img.shields.io/badge/Live%20Site-www.evaledge.xyz-blue?style=flat-square&logo=google-chrome)](https://www.evaledge.xyz)
[![Dockerized](https://img.shields.io/badge/Dockerized-Yes-blue?logo=docker&style=flat-square)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

A modern, open-source, Dockerized Django Online Judge for code evaluation and problem-solving.  
**Production deployed at:** [www.evaledge.xyz](https://www.evaledge.xyz)

---

## ✨ Features

- 📝 **Online Code Submission & Judging**
- 📚 **Problem Management & Test Cases**
- 👤 **User Registration & Authentication**
- 🐳 **Easy Docker Deployment (AWS/EC2/ECR Ready)**
- ⚡ **Fast, Real-Time Feedback**
- 🔒 **Secure, Production-Ready Setup**

---

## 📸 Screenshots

> **Tip:** Add your own screenshots in the `screenshots/` folder and update the paths below.

| Home Page                        | Problem View                       | Submission Result                |
|-----------------------------------|------------------------------------|----------------------------------|
| ![](./screenshots/home.png)       | ![](./screenshots/problem.png)     | ![](./screenshots/result.png)    |

---

## 🗂️ Project Structure

online_judge/
├── codes/ # Submitted code files
├── inputs/ # Input test cases for problems
├── online_judge/ # Django project settings and core logic
├── outputs/ # Output files/results from code execution
├── problems/ # Problem definitions and metadata
├── static/ # Static assets (CSS, JS, images)
├── staticfiles/ # Collected static files (for production)
├── templates/ # HTML templates for UI
├── users/ # User management and authentication
├── .dockerignore
├── db.sqlite3
├── manage.py
└── Dockerfile


---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- Python 3.8+
- (Optional) AWS CLI for deployment

### Local Development

Clone the repository
git clone https://github.com/yourusername/EVALEDGE-OJ-Project.git
cd EVALEDGE-OJ-Project/online_judge

Build and run with Docker
docker build -t evaledge-oj .
docker run -d -p 8000:8000 --name evaledge-oj evaledge-oj

Run migrations and create superuser
docker exec -it evaledge-oj python manage.py migrate
docker exec -it evaledge-oj python manage.py createsuperuser

Visit the app!
http://localhost:8000

---

## ☁️ Production Deployment (AWS EC2 + Docker)

1. **Push Docker Image to AWS ECR**
2. **Launch EC2 Instance & Install Docker**
3. **Pull and Run the Container**
    ```
    docker pull <your-ecr-repo-url>:latest
    docker run -d --restart always -p 8000:8000 \
      --name evaledge-oj \
      -e DJANGO_SECRET_KEY=your_secret_key \
      -e DATABASE_URL=your_database_url \
      <your-ecr-repo-url>:latest
    ```
4. **(Optional) Set up Nginx as a reverse proxy for HTTPS and static files**

---

## ⚙️ Environment Variables

| Variable             | Description                        | Example                        |
|----------------------|------------------------------------|--------------------------------|
| DJANGO_SECRET_KEY    | Django secret key                  | `supersecretkey`               |
| DATABASE_URL         | Database connection string         | `postgres://user:pass@host/db` |
| DJANGO_DEBUG         | Debug mode (`True`/`False`)        | `False`                        |
| ALLOWED_HOSTS        | Comma-separated allowed hosts      | `www.evaledge.xyz`             |

---

## 🛠️ Usage

- **Admin Panel:** `/admin/` for managing users, problems, and submissions.
- **Submit Solutions:** Browse problems and submit code for evaluation.
- **View Results:** See real-time feedback and results of submissions.

---

## 🤝 Contributing

Pull requests are welcome!  
For major changes, please [open an issue](https://github.com/yourusername/EVALEDGE-OJ-Project/issues) first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🌐 Live Demo

[www.evaledge.xyz](https://www.evaledge.xyz)

---

> **Made with ❤️ by Shrasti.**

