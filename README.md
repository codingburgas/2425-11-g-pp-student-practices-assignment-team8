# Extracurricular Activity Recommender System

## 📌 Project Overview

This project aims to assist students in choosing the most suitable extracurricular activities through a web platform powered by machine learning. Built using **Flask** and **Python**, the application collects data via a student survey and uses it to train a machine learning model to make personalized recommendations.

## 🧠 Core Features

### 🔍 Intelligent Recommendation Engine
- Implements a machine learning model (Linear Regression, Perceptron, Logistic Regression, or Neural Network).
- Trained on student-submitted survey data.
- Entirely built without using high-level ML libraries like scikit-learn or Keras.

### 📄 Survey-Based Dataset
- Custom survey form used to collect student data.
- Features reflect creativity, technical thinking, dexterity, and other competencies.

### 🌐 Web Interface
- **User Authentication** with multiple roles: *Student*, *Teacher*, *Admin*.
- **Recommendation Portal**: students get personalized suggestions.
- **Club Portal**: view and apply to clubs; teachers manage applications.
- **Admin Dashboard**: manage users and view AI performance.

## 🧩 Tech Stack

- **Backend**: Python, Flask
- **Frontend**: Flask-Bootstrap
- **Database**: SQLAlchemy with Flask-Migrate
- **Extensions Used**:
  - Flask-WTF
  - Flask-SQLAlchemy
  - Flask-Login
  - Flask-Migrate
  - Flask-Mail
- **Unit Testing**: Custom test suite for major features
- **AI**: Custom ML algorithms using only `numpy`, `pandas`, `matplotlib`, and optionally `torch`/`tensorflow` only for tensor operations on GPU



