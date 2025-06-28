def export_jobs_csv(jobs, username: str):
    proxy = io.StringIO()
    writer = csv.writer(proxy)
    writer.writerow(["Company","Role","Link","Location","Salary",
                     "Status","Tags","Applied On"])
    for j in jobs:
        writer.writerow([
            j.company, j.role, j.link, j.location, j.salary,
            j.status, j.tags, j.date_applied.isoformat()
        ])
    mem = io.BytesIO(proxy.getvalue().encode("utf-8"))
    mem.seek(0)
    fname = f"{username}_jobs_{datetime.date.today():%Y%m%d}.csv"
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=fname)


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime, csv, io
from flask import send_file

def resume_job_similarity(resume_text, jd_text):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([resume_text, jd_text])
    return round(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100, 2)

def export_jobs_csv(jobs, username: str):
    proxy = io.StringIO()
    writer = csv.writer(proxy)
    writer.writerow(["Company", "Role", "Link", "Location", "Salary", "Status", "Tags", "Applied On"])
    for j in jobs:
        writer.writerow([
            j.company, j.role, j.link, j.location, j.salary,
            j.status, j.tags, j.date_applied.isoformat()
        ])
    mem = io.BytesIO(proxy.getvalue().encode("utf-8"))
    mem.seek(0)
    fname = f"{username}_jobs_{datetime.date.today():%Y%m%d}.csv"
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=fname)
