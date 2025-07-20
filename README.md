# Job Tracker App

A modern job application tracking system built using **Flask**, designed to help users manage and monitor their job search efficiently.

---

## Live Application

=> [Link](https://job-tracker-app-4lnh.onrender.com)

---

## Features

- Google Sign-In authentication
- Add and track job statuses: Wishlist, Applied, Interview, Offer, Rejected
- Upload and manage resumes
- Import/export job data using CSV
- Toggle between dark and light themes
- Automatic email reminders for follow-ups

---

## Getting Started

### Prerequisites

- Python 3.x
- Git
- Virtual Environment support (`venv`)

---

### Installation

Follow these steps to run the application locally:

```bash
# Clone the repository
git clone https://github.com/irohit02/job-tracker-app.git
cd job-tracker-app

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run the Flask development server
flask run
```

---

## Tech Stack

- Python · Flask  
- SQLite / PostgreSQL  
- HTML · CSS · Bootstrap  
- Flask-Mail · Flask-Dance · Google OAuth  
- CSV handling · Jinja2 Templates

---

## Project Overview

This tool was created to streamline job tracking during the placement season. It helps you stay organized, follow up on time, and manage your resume data — all from one dashboard.
