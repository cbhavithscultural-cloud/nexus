import json, os, sys, datetime, urllib.request
import time, urllib.error
KEY = os.environ["GEMINI_API_KEY"]
CANDS = [m for m in [os.environ.get("MODEL"), "gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3-flash-preview", "gemini-flash-latest", "gemini-2.5-flash-lite"] if m]
BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now = datetime.datetime.now(IST); today = now.date().isoformat()
def rd(p, d):
    try: return json.load(open(p))
    except Exception: return d
INIT = {"oi":0,"bci":0,"po":[0,1],"pb":[0,1],"gh":[0,1],"ip":0,"li":0}
LJ = rd("data/latest.json", {}); prev = LJ.get("sections", {})
st = rd("data/state.json", dict(INIT))
if LJ.get("date") and LJ.get("v") != 2: st, prev = dict(INIT), {}  # discard content from the old script version once
TD = rd(f"data/days/{today}.json", {})
done = TD.get("sections", {}) if TD.get("v") == 2 and not os.environ.get("FORCE") else {}
dstat = TD.get("status", {}) if done else {}  # sections already ok today are reused, only failed ones retry
RULES = ("Return ONLY one JSON object, no markdown. Never invent papers, links, dates, numbers or job openings. "
         "Paraphrase; no long quotes. If unsure, say so in a 'confidence' field. Plain beginner-friendly language.")
def call(prompt, search):
    global CANDS
    if os.environ.get("DRY"): return {"stub": True, "prompt_start": prompt[:60], "url": "https://example.com"}
    body = {"contents": [{"parts": [{"text": RULES + "\n" + prompt}]}]}
    if search: body["tools"] = [{"google_search": {}}]
    else: body["generationConfig"] = {"responseMimeType": "application/json"}
    last = None
    for model in list(CANDS):
        for attempt in range(4):
            try:
                r = urllib.request.Request(BASE + model + ":generateContent", json.dumps(body).encode(), {"x-goog-api-key": KEY, "content-type": "application/json"})
                out = json.load(urllib.request.urlopen(r, timeout=300))
                t = "".join(p.get("text", "") for p in out["candidates"][0]["content"]["parts"])
                res = json.loads(t[t.index("{"):t.rindex("}") + 1])
                CANDS = [model]; time.sleep(8); return res
            except urllib.error.HTTPError as e:
                detail = e.read().decode()[:160]; last = RuntimeError("HTTP %s on %s: %s" % (e.code, model, detail))
                if e.code in (429, 500, 503) and attempt < 3: time.sleep(20 * 2 ** attempt); continue
                break
    raise last
def ask(prompt, search=False, need=True):
    if search:
        try: return call(prompt, True)
        except Exception:
            if need: raise  # news/jobs: never invent without live search
    r = call(prompt, False)
    r["confidence"] = "Unverified: AI-written from model knowledge, no live sources"
    if search: r["note"] = "Written without live web search; verify links before trusting."
    return r
soft_ask = lambda p, s=False: ask(p, s, False)
SYL = {"oi": ["What is intelligence and learning","Cells and neurons","How neurons signal","Synapses and neural networks","Stem cells and differentiation","Brain organoids","Recording electrical activity with electrode arrays","What Organoid Intelligence has and has not shown"],
 "bci": ["What is a BCI","Neurons and motor cortex","EEG basics","Invasive vs non-invasive recording","Sampling and Nyquist","Filtering and artefacts","Features and classification","Motor imagery decoding"]}
PAP = {"oi": [("Cerebral organoids model human brain development and microcephaly (Lancaster 2013)","10.1038/nature12517"),("In vitro neurons learn and exhibit sentience when embodied in a simulated game-world (Kagan 2022)","10.1016/j.neuron.2022.09.001"),("Organoid intelligence (OI): the new frontier in biocomputing and intelligence-in-a-dish (Smirnova 2023)","10.3389/fsci.2023.1017235")],
 "bci": [("Brain-computer interfaces for communication and control (Wolpaw 2002)","10.1016/S1388-2457(02)00057-3"),("Neuronal ensemble control of prosthetic devices by a human with tetraplegia (Hochberg 2006)","10.1038/nature04970"),("A high-performance speech neuroprosthesis (Willett 2023)","10.1038/s41586-023-06377-x")]}
REPOS = ["ros-navigation/navigation2", "ROBOTIS-GIT/turtlebot3", "moveit/moveit2"]
PD = ["Why this research exists","Research design and method","Results and figures","Engineering, limits and ethics","Bigger picture, then a 3-question check"]
GD = ["Understand the project","How it works","Run it in simulation and engineering judgement"]
INT = ["Percentages","Self-introduction practice","Ratios","Debugging a robot sensor scenario","Time and work","Explaining a project clearly"]
LI = ["Headline","About section","Project description","GitHub profile","Skills section","Networking message"]
FIELDS = "Fields: objective, why_it_matters, prerequisites, simple_explanation, step_by_step, technical_depth, misconceptions, knowledge_check (3 questions with answers), exercise, summary, next_lesson, confidence."
def news(): return ask(f"Today is {today}. Search the web for up to 3 significant real robotics developments published before {today} 00:00 IST, newest first. category must be one of: Research, Business, Product, Industry view, Deployment, Open source. Only items you actually retrieved. Schema: {{\"items\":[{{\"category\",\"title\",\"published\",\"source\",\"url\",\"what\",\"who\",\"how\",\"why\",\"limits\",\"learn\",\"confidence\"}}]}}", True)
def jobs(): return ask(f"Today is {today}. Search for real robotics, embedded, BCI and neural-engineering internship/research opportunities and hiring news, India first. Label each as vacancy, hiring_announcement, trend or prediction; say whether still open is verified. Schema: {{\"items\":[{{\"title\",\"type\",\"location\",\"published\",\"source\",\"url\",\"still_open_verified\",\"note\"}}],\"action\":\"one practical step\"}}", True)
def lesson(k):
    i = st[k] % len(SYL[k]); r = ask(f"Write lesson {i+1} for {'Organoid Intelligence' if k=='oi' else 'Brain-Computer Interface'} beginners: '{SYL[k][i]}'. Teach prerequisites first. Separate demonstrated facts from hypotheses. {FIELDS}"); st[k] += 1; return r
def paper(k, s):
    pi, day = st[s]; t, doi = PAP[k][pi % len(PAP[k])]
    r = soft_ask(f"Five-day paper investigation, day {day} of 5: '{PD[day-1]}'. Paper: {t}, DOI {doi}. Search to confirm the abstract and details; say if only abstract was available. Do not invent results. Schema: {{\"paper\",\"doi\",\"day\",\"focus\",\"explanation\",\"limits\",\"check\",\"access_level\",\"confidence\"}}", True)
    r["doi_link"] = "https://doi.org/" + doi
    if "note" in r: r["access_level"] = "Full text NOT read. Written from model knowledge. Verify against the DOI link."
    st[s] = [pi + 1, 1] if day == 5 else [pi, day + 1]; return r
def github():
    ri, day = st["gh"]; repo = REPOS[ri % len(REPOS)]
    m = json.load(urllib.request.urlopen(urllib.request.Request("https://api.github.com/repos/" + repo, headers=({"Authorization": "Bearer " + os.environ["GH_TOKEN"]} if os.environ.get("GH_TOKEN") else {})), timeout=60))
    meta = {k: m.get(k) for k in ("full_name", "html_url", "description", "pushed_at", "language", "archived")}; meta["license"] = (m.get("license") or {}).get("spdx_id")
    r = soft_ask(f"Three-day GitHub project investigation, day {day} of 3: '{GD[day-1]}'. Verified repo metadata: {json.dumps(meta)}. Search for the README/docs. Do not claim code was run. Include a small challenge and a knowledge check.", True)
    r["verified_metadata"] = meta; st["gh"] = [ri + 1, 1] if day == 3 else [ri, day + 1]; return r
def simple(k, label, topics):
    i = st[k] % len(topics); r = ask(f"{label} session (15 min) on '{topics[i]}': short explanation, practical example, one exercise, a model answer with why it works, and one improvement tip."); st[k] += 1; return r
START = time.time()
res, status = {}, {}
for name, f in [("news", news), ("jobs", jobs), ("oi_lesson", lambda: lesson("oi")), ("bci_lesson", lambda: lesson("bci")),
                ("oi_paper", lambda: paper("oi", "po")), ("bci_paper", lambda: paper("bci", "pb")), ("github", github),
                ("internship", lambda: simple("ip", "Internship preparation", INT)), ("linkedin", lambda: simple("li", "LinkedIn profile improvement", LI))]:
    if str(dstat.get(name, "")).startswith("ok"): res[name] = done[name]; status[name] = "ok"; continue
    if time.time() - START > 1200: res[name] = prev.get(name); status[name] = "skipped: time budget used"; continue
    try: res[name] = f(); status[name] = "ok"
    except Exception as e: res[name] = prev.get(name); status[name] = "failed (kept previous): " + str(e)[:150]
out = {"v": 2, "date": today, "generated_at": now.isoformat(), "status": status, "sections": res}
json.dump(out, open("data/latest.json", "w"), indent=1); json.dump(out, open(f"data/days/{today}.json", "w"), indent=1); json.dump(st, open("data/state.json", "w"))
print(status)
