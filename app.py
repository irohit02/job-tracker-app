from __future__ import annotations
from pathlib import Path
from datetime import date, datetime
import os, io, csv, secrets, textwrap

from flask import (
    Flask, render_template, redirect, url_for, request, flash,
    jsonify, send_from_directory, Response
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.utils import secure_filename
from flask_dance.contrib.google import make_google_blueprint, google
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import DevConfig

#Flask setup
app = Flask(__name__)
app.config.from_object(DevConfig)

BASE_DIR      = Path(__file__).resolve().parent
from pathlib import Path

UPLOAD_FOLDER = Path(app.root_path) / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)  
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)  
ALLOWED_PDF   = {"pdf"}


db      = SQLAlchemy(app)
bcrypt  = Bcrypt(app)
mail    = Mail(app)
login   = LoginManager(app); login.login_view = "login"

#Google OAuth (optional)
if os.getenv("GOOGLE_OAUTH_CLIENT_ID"):
    bp = make_google_blueprint(
        client_id     = os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        scope=["profile","email"],
        redirect_url="/login/google/authorized"
    )
    app.register_blueprint(bp, url_prefix="/login")
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"   # dev only

#Models
class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255))
    jobs     = db.relationship("Job", backref="owner", lazy=True)

class Job(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    company       = db.Column(db.String(120), nullable=False)
    role          = db.Column(db.String(120), nullable=False)
    location      = db.Column(db.String(120))
    salary        = db.Column(db.String(120))
    status        = db.Column(db.String(50),  default="Wishlist")
    tags          = db.Column(db.String(255))
    notes         = db.Column(db.Text)
    date_applied  = db.Column(db.Date, default=date.today)
    remind_on     = db.Column(db.Date)
    resume_file   = db.Column(db.String(255))

@login.user_loader
def load_user(uid): return User.query.get(int(uid))

def pdf_ok(fn:str): return "." in fn and fn.rsplit(".",1)[1].lower() in ALLOWED_PDF

# Auth routes
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u = User(username=request.form["username"],
                 email   =request.form["email"],
                 password=bcrypt.generate_password_hash(
                          request.form["password"]).decode())
        db.session.add(u); db.session.commit()
        flash("Registered – login now","success")
        return redirect(url_for("login"))
    return render_template("register.html", config=app.config)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = User.query.filter_by(email=request.form["email"]).first()
        if u and bcrypt.check_password_hash(u.password, request.form["password"]):
            login_user(u); return redirect(url_for("dashboard"))
        flash("Invalid credentials","danger")
    return render_template("login.html", config=app.config)

@app.route("/login/google/authorized")
def google_authorized():
    if not google.authorized: return redirect(url_for("google.login"))
    info = google.get("/oauth2/v2/userinfo").json()
    user = User.query.filter_by(email=info["email"]).first()
    if not user:
        user = User(username=info.get("name","Google-User"),
                    email=info["email"],
                    password=bcrypt.generate_password_hash(secrets.token_hex()).decode())
        db.session.add(user); db.session.commit()
    login_user(user); flash("Google login successful","success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout(): logout_user(); return redirect(url_for("login"))

#Dashboard
@app.route("/")
@login_required
def dashboard():
    q  = request.args.get("q","").strip()
    fl = request.args.get("status","")

    qry = Job.query.filter_by(owner=current_user)
    if q:  qry = qry.filter(db.or_(Job.company.ilike(f"%{q}%"),
                                   Job.role.ilike(f"%{q}%")))
    if fl: qry = qry.filter_by(status=fl)
    jobs = qry.order_by(Job.date_applied.desc()).all()

    counts = {s: sum(1 for j in jobs if j.status==s)
              for s in ["Wishlist","Applied","Interview","Offer","Rejected"]}
    counts["total"] = len(jobs)
    return render_template("dashboard.html", jobs=jobs, counts=counts,
                           q=q, statusF=fl)

#Job CRUD
@app.route("/job/new", methods=["GET", "POST"])
@login_required
def job_new():
    if request.method == "POST":
        pdf = request.files.get("resume")
        fn = None
        if pdf and pdf.filename and pdf_ok(pdf.filename):
            fn = secure_filename(pdf.filename)
            pdf.save(UPLOAD_FOLDER / fn)

        rstr = request.form.get("remind_on")
        remind_on = datetime.strptime(rstr, "%Y-%m-%d").date() if rstr else None

        job = Job(
            owner=current_user,
            company=request.form["company"],
            role=request.form["role"],
            location=request.form.get("location"),
            salary=request.form.get("salary"),
            status=request.form["status"],
            tags=request.form.get("tags"),
            notes=request.form.get("notes"),
            date_applied=datetime.strptime(request.form.get("date_applied") or date.today().isoformat(), "%Y-%m-%d").date(),
            remind_on=remind_on,
            resume_file=fn
        )

        db.session.add(job)
        db.session.commit()
        flash("Job added", "success")
        return redirect(url_for("dashboard"))
    return render_template("job_form.html", job=None)


@app.route("/job/<int:jid>/edit", methods=["GET","POST"])
@login_required
def job_edit(jid):
    job = Job.query.get_or_404(jid)
    if job.owner != current_user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        for f in ["company", "role", "location", "salary", "status", "tags", "notes"]:
            setattr(job, f, request.form.get(f))

        job.date_applied = datetime.strptime(request.form.get("date_applied"), "%Y-%m-%d").date()

        rstr = request.form.get("remind_on")
        job.remind_on = datetime.strptime(rstr, "%Y-%m-%d").date() if rstr else None

        pdf = request.files.get("resume")
        if pdf and pdf.filename and pdf_ok(pdf.filename):
            fn = secure_filename(pdf.filename)
            pdf.save(UPLOAD_FOLDER / fn)
            job.resume_file = fn

        db.session.commit()
        flash("Updated", "success")
        return redirect(url_for("dashboard"))

    return render_template("job_form.html", job=job)

@app.route("/job/<int:jid>/delete", methods=["POST"])
@login_required
def job_delete(jid):
    job = Job.query.get_or_404(jid)
    if job.owner == current_user:
        db.session.delete(job); db.session.commit(); flash("Deleted","info")
    return redirect(url_for("dashboard"))

@app.route('/job/<int:jid>')
@login_required
def job_detail(jid):
    job = Job.query.get_or_404(jid)
    return render_template("job_detail.html", job=job)


#File serving / APIs
@app.route("/uploads/<path:filename>")
def get_resume(filename): return send_from_directory('uploads', filename)

@app.route("/api/job/<int:jid>")
def api_job(jid):
    j = Job.query.get_or_404(jid)
    if j.owner!=current_user: return jsonify(error="forbidden"),403
    return jsonify(id=j.id, company=j.company, role=j.role, location=j.location,
                   salary=j.salary, status=j.status, tags=j.tags, notes=j.notes,
                   date=j.date_applied.isoformat(),
                   remind=j.remind_on.isoformat() if j.remind_on else None,
                   resume_url = url_for("get_resume", filename=j.resume_file) if j.resume_file else None)


@app.route("/api/analytics")
def api_analytics():
    jobs=Job.query.filter_by(owner=current_user).all()
    summary, trend={},{}
    for j in jobs:
        summary[j.status] = summary.get(j.status,0)+1
        k=j.date_applied.isoformat(); trend[k]=trend.get(k,0)+1
    return jsonify(summary=summary, trend=trend)

@app.route("/api/match", methods=["POST"])
def api_match():
    resume=request.form["resume"]; jd=request.form["jd"]
    vect=TfidfVectorizer(stop_words="english")
    tf=vect.fit_transform([resume.lower(), jd.lower()])
    score=float(cosine_similarity(tf[0:1], tf[1:2])[0][0])*100
    return jsonify(score=round(score,2))

#CSV export / import
@app.route("/export_csv")
def export_csv():
    si=io.StringIO(); w=csv.writer(si)
    w.writerow(["Company","Role","Status","Applied","Location","Salary","Tags","Notes","Reminder"])
    for j in Job.query.filter_by(owner=current_user):
        w.writerow([j.company,j.role,j.status,j.date_applied,j.location,
                    j.salary,j.tags,j.notes,j.remind_on])
    return Response(si.getvalue(),mimetype="text/csv",
        headers={"Content-Disposition":"attachment; filename=jobs.csv"})

@app.route("/import_csv", methods=["POST"])
def import_csv():
    f=request.files.get("csvfile")
    if not (f and f.filename.endswith(".csv")):
        flash("Upload CSV","danger"); return redirect(url_for("dashboard"))
    reader=csv.DictReader(io.StringIO(f.read().decode("utf-8-sig")))
    n=0
    for row in reader:
        if not row.get("Company"): continue
        j=Job(owner=current_user,
              company=row["Company"], role=row.get("Role"),
              status=row.get("Status","Wishlist"),
              date_applied=datetime.strptime(row.get("Applied") or date.today().isoformat(),"%Y-%m-%d"),
              location=row.get("Location"), salary=row.get("Salary"),
              tags=row.get("Tags"), notes=row.get("Notes"),
              remind_on=row.get("Reminder") or None)
        db.session.add(j); n+=1
    db.session.commit(); flash(f"Imported {n} jobs","success")
    return redirect(url_for("dashboard"))

#CLI helper
@app.cli.command("init-db")
def init_db():
    db.create_all(); print("Database initialized ✔")

if __name__=="__main__":
    app.run(debug=True)