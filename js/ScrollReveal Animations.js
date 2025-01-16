const hd = ScrollReveal({
    distance: "100px",
    duration: 2000,
    delay: 400,
    reset: true,
});
hd.reveal(".header", { origin: "top" });
hd.reveal(".navbar", { origin: "top" });




const sr = ScrollReveal({
    distance: "100px",
    duration: 2000,
    delay: 400,
    reset: true,
    container: ".container"
});

sr.reveal(".about-me, .about-me-h1", { interval: 200 });
sr.reveal(".part-time-job h1, .part-time-job .job-bartender", { interval: 600 });
sr.reveal(".part-time-job .job-bartender", { interval: 400 });
sr.reveal(".part-time-job .job-home-tutor", { interval: 200 });
sr.reveal(".hobbies", { interval: 400 });
sr.reveal(".chennel", { interval: 800 });

sr.reveal(".strength h1, .technical-skills ", { interval: 800 });
sr.reveal(".personal-strengths ", { interval: 800 });
sr.reveal(".strength-words ", { interval: 1000 });
sr.reveal(".portfolio h1", { interval: 400 });
sr.reveal(".personal-works h2", { interval: 400 });
sr.reveal(".personal-works .works-introduction", { interval: 400 });
sr.reveal(".team-works h2", { interval: 400 });
sr.reveal(".team-works .works-introduction", { interval: 400 });
sr.reveal(".footer", { interval: 400 });


