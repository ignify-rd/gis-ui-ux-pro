"""BM25 search over the CSV knowledge base (stdlib only)."""
import csv
import math
import re
import unicodedata
from pathlib import Path

from schema import FILES, SEARCH_FIELDS

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"

MIN_SCORE = 0.5  # tunable floor; hits below it are dropped

STOPWORDS = {"a", "an", "the", "of", "and", "or", "for", "to", "in", "on", "with",
             "is", "are", "be", "by", "at", "as", "it", "this", "that", "from"}
SYNONYMS = {"colour": "color", "colours": "color", "colors": "color",
            "colormap": "palette", "colormaps": "palette", "palettes": "palette",
            "maps": "map", "mapping": "map"}

DOMAIN_HINTS = {
    "palette": ["color", "ramp", "palette", "colormap", "colour", "legend colors"],
    "problem": ["dashboard for", "app for", "monitoring", "detection", "playbook",
                "tracking"],
    "widget": ["widget", "component", "slider", "panel", "control"],
    "layout": ["layout", "sidebar", "mobile", "wall", "responsive"],
    "direction": ["signature", "look and feel", "visual identity", "visual direction",
                  "art direction"],
    "smell": ["smell", "smells", "anti pattern", "antipattern"],
}


def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    toks = [t for t in re.split(r"[^a-z0-9]+", text) if len(t) > 1 and t not in STOPWORDS]
    return [SYNONYMS.get(t, t) for t in toks]


WIDGET_REF = re.compile(r"\[([A-Za-z0-9-]+)\]")  # fixture ids are upper-case


def widget_refs(text):
    return WIDGET_REF.findall(text)


def paren_tokens(text):
    return [t for g in re.findall(r"\(([^)]*)\)", text) for t in re.split(r"[,;\s]+", g) if t]


def split_list(cell):
    return [p.strip() for p in cell.split(";") if p.strip()]


def parse_kv(cell):
    """'k: v; k2: v2' -> [(k, v), ...]; items without ':' get key ''."""
    out = []
    for item in (cell or "").split(";"):
        item = item.strip()
        if item:
            k, sep, v = item.partition(":")
            out.append((k.strip(), v.strip()) if sep else ("", item))
    return out


def _path(domain, data_dir, stack):
    if domain == "stack":
        if not stack:
            raise ValueError("stack domain requires a stack name")
        return Path(data_dir) / "stacks" / f"{stack}.csv"
    return Path(data_dir) / FILES[domain]


def load_rows(domain, data_dir=DATA_DIR, stack=None):
    with open(_path(domain, data_dir, stack), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.n = len(docs)
        self.avgdl = sum(len(d) for d in docs) / self.n if self.n else 0.0
        self.tfs = []
        self.df = {}
        for d in docs:
            tf = {}
            for t in d:
                tf[t] = tf.get(t, 0) + 1
            self.tfs.append(tf)
            for t in tf:
                self.df[t] = self.df.get(t, 0) + 1

    def scores(self, query_tokens):
        out = []
        for d, tf in zip(self.docs, self.tfs):
            s = 0.0
            for t in set(query_tokens):
                f = tf.get(t, 0)
                if not f:
                    continue
                df = self.df[t]
                idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
                norm = 1 - self.b + self.b * len(d) / self.avgdl
                s += idf * f * (self.k1 + 1) / (f + self.k1 * norm)
            out.append(s)
        return out


def detect_domain(query):
    q = " ".join(re.split(r"[^a-z0-9]+", query.lower()))
    words = {SYNONYMS.get(w, w) for w in q.split()}
    scored = {}
    for dom, hints in DOMAIN_HINTS.items():
        s = 0
        for h in hints:
            if " " in h:
                s += 2 if h in q else 0
            elif h in words:
                s += 1
        scored[dom] = s
    ranked = sorted(scored.items(), key=lambda kv: -kv[1])
    if ranked[0][1] == 0:
        return "rule", None
    runner = ranked[1][0] if ranked[1][1] > 0 else None
    return ranked[0][0], runner


def _suggestions(rows, k=8):
    seen = []
    for r in rows:
        for kw in re.split(r"[;,]", r.get("keywords", "")):
            kw = kw.strip()
            if kw and kw not in seen:
                seen.append(kw)
    return seen[:k]


def search(query, domain=None, n=3, data_dir=DATA_DIR, stack=None):
    auto, runner = False, None
    if stack:
        domain = "stack"
    elif domain is None:
        domain, runner = detect_domain(query)
        auto = True
    rows = load_rows(domain, data_dir, stack)
    toks = normalize(query)
    noise = {"map"} if domain == "problem" else set()  # every problem is about maps
    toks = [t for t in toks if t not in noise]
    hits = []
    if toks and rows:
        def text(r):
            s = " ".join(r.get(c, "") for c in SEARCH_FIELDS[domain])
            return WIDGET_REF.sub("", s) if domain == "problem" else s  # ids are noise tokens
        docs = [[t for t in normalize(text(r)) if t not in noise] for r in rows]
        ranked = sorted(zip(BM25(docs).scores(toks), range(len(rows))), key=lambda x: (-x[0], x[1]))
        hits = [dict(rows[i], _score=s) for s, i in ranked[:n] if s >= MIN_SCORE]
    return {"domain": domain, "auto_detected": auto, "runner_up": runner, "hits": hits,
            "suggestions": [] if hits else _suggestions(rows)}


def get_by_id(domain, id_, data_dir=DATA_DIR):
    for r in load_rows(domain, data_dir):
        if r["id"] == id_:
            return r
    return None


def resolve_widget(item, data_dir=DATA_DIR):
    """Widget row for a problem's `widgets` item: exact id, else top search hit, else None."""
    exact = get_by_id("widget", item, data_dir)
    if exact:
        return exact
    h = search(item, "widget", 1, data_dir)["hits"]
    return {k: v for k, v in h[0].items() if k != "_score"} if h else None


def contract(problem):
    c = {k: (problem.get(k) or "").strip() for k in ("glance_question", "glance_answer")}
    c.update({k: split_list(problem.get(k) or "") for k in ("trust", "flow")})
    return c if any(c.values()) else None
