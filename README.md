# 📊 Job Tracker App

A modern Flask app to track job applications.

🌐 **Live App**: [https://job-tracker-app-4lnh.onrender.com](https://job-tracker-app-4lnh.onrender.com)

## ✨ Features

- Google Sign-In
- Track status (Wishlist, Applied, Interview, Offer, Rejected)
- Upload resumes
- CSV import/export
- Dark mode UI
- Reminder emails

## 🛠️ Run Locally

```bash
git clone https://github.com/irohit02/job-tracker-app.git
cd job-tracker-app
cp .env.example .env
python -m venv venv
venv\Scripts\activate      # or source venv/bin/activate (Linux/mac)
pip install -r requirements.txt
flask run
