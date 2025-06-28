(() => {
  const cards = document.querySelectorAll(".job-card");
  if (!cards.length) return;

  const modal = new bootstrap.Modal(document.getElementById("jobDetailModal"));
  const $ = id => document.getElementById(id);

  const ui = {
    title: $("detailTitle"),
    role: $("detailRole"),
    loc: $("detailLoc"),
    sal: $("detailSal"),
    status: $("detailStatus"),
    date: $("detailDate"),
    tags: $("detailTags"),
    notes: $("detailNotes"),
    resWrap: $("resumeLinkWrap"),
    resA: $("detailResume"),
    edit: $("detailEdit"),
    del: $("detailDeleteForm")
  };

  cards.forEach(card => {
    card.addEventListener("click", () => {
      fetch(`/api/job/${card.dataset.id}`)
        .then(response => response.json())
        .then(job => {
          ui.title.textContent = job.company;
          ui.role.textContent = job.role || "—";
          ui.loc.textContent = job.location || "—";
          ui.sal.textContent = job.salary || "—";
          ui.tags.textContent = job.tags || "—";
          ui.notes.textContent = job.notes || "No notes";
          ui.date.textContent = job.date;
          ui.status.textContent = job.status;
          ui.status.className = `status-badge badge-${job.status.toLowerCase()}`;

          if (job.resume_url) {
            ui.resA.href = job.resume_url;
            ui.resWrap.style.display = "block";
          } else {
            ui.resWrap.style.display = "none";
          }

          ui.edit.href = `/job/${job.id}/edit`;
          ui.del.action = `/job/${job.id}/delete`;

          modal.show();
        })
        .catch(error => console.error("Job detail fetch error:", error));
    });
  });
})();
