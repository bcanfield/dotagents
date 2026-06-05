#!/usr/bin/env python3
"""Deterministic AI-tell scanner for the humanize skill's audit pass.

Usage: python3 check_tells.py <file.md|file.txt>
Prints one line per check; fix every FAIL, then re-run. Judgment-call
patterns (rule of three, mirror structure, treadmill test) aren't here —
the audit step in SKILL.md covers those.
"""
import re
import sys

# tier 1 vocabulary — replace on sight
BANNED_WORDS = [
    "delve", "leverage", "leveraging", "crucial", "pivotal", "robust", "seamless",
    "seamlessly", "landscape", "tapestry", "symphony", "testament", "foster",
    "fostering", "showcase", "showcasing", "underscore", "underscoring", "boasts",
    "meticulous", "meticulously", "vibrant", "elevate", "garner", "bolster",
    "game-changer", "groundbreaking", "cutting-edge", "paradigm", "realm",
    "harness", "utilize", "supercharge", "nuanced", "multifaceted", "embark",
    "spearhead", "intricate", "intricacies",
]
# tier 2 — once per piece is tolerable, twice is a tell
TIER2_WORDS = ["comprehensive", "holistic", "innovative", "dynamic", "valuable", "notably"]
BANNED_PHRASES = [
    "in today's", "fast-paced", "ever-evolving", "digital age",
    "it's important to note", "it is important to note", "it's worth noting",
    "it should be noted", "in conclusion", "in summary", "unlock the potential",
    "only time will tell", "evolving landscape", "excited to announce",
    "excited to share", "honored to announce", "i hope this email finds you well",
    "i hope this helps", "let's dive in", "let's unpack", "here's the thing",
    "stands as a", "serves as a", "plays a vital role", "pivotal moment",
    "take it to the next level", "at the end of the day", "exciting times ahead",
    "the future looks bright", "growth opportunity", "learning experience",
    "great question", "as of my knowledge cutoff", "as of my last update",
]
FORMAL_TRANSITIONS = [
    "moreover", "furthermore", "additionally", "consequently", "nevertheless",
    "nonetheless", "subsequently", "hence",
]
# "it's not just X, it's Y" and friends
NEG_PARALLEL = re.compile(
    r"(it'?s not (just|only|about|merely)|isn'?t (just|only|about|merely)"
    r"|not only\b.*\bbut\b|this is not about)",
    re.IGNORECASE,
)
# "The result? Disaster." style infomercial reveals
RHETORICAL_REVEAL = re.compile(r"^\s*(the )?\w{3,20}\?\s+[A-Z]", re.MULTILINE)
# leaked chatbot/citation artifacts
ARTIFACTS = re.compile(
    r"(\[(your|insert) [^\]]{1,30}\]|oai_citation|citeturn\d|contentReference"
    r"|utm_source=(chatgpt|openai|copilot))",
    re.IGNORECASE,
)
CONTRACTION = re.compile(r"\b\w+'(s|t|re|ll|ve|d|m)\b")


def sentences(text):
    # crude but fine: split on sentence-ending punctuation
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"[#*>`\-]", "", text))
    return [p.strip() for p in parts if len(p.strip().split()) >= 2]


def main(path):
    text = open(path).read()
    low = text.lower()
    fails = 0

    def report(name, ok, detail=""):
        nonlocal fails
        if not ok:
            fails += 1
        print(f"{name}: {'PASS' if ok else 'FAIL'}{' ' + detail if detail else ''}")

    hits = sorted({w for w in BANNED_WORDS if re.search(rf"\b{re.escape(w)}\b", low)})
    report("banned_words", not hits, ", ".join(hits))

    t2 = sorted({w for w in TIER2_WORDS if len(re.findall(rf"\b{re.escape(w)}\b", low)) > 1})
    report("tier2_repeated", not t2, ", ".join(t2))

    phits = sorted({p for p in BANNED_PHRASES if p in low})
    report("banned_phrases", not phits, ", ".join(phits))

    trans = sum(len(re.findall(rf"\b{t}\b", low)) for t in FORMAL_TRANSITIONS)
    report("formal_transitions", trans <= 2, f"{trans} found (max 2)")

    np = NEG_PARALLEL.findall(text)
    report("negative_parallelism", not np, f"{len(np)} hit(s)")

    em = text.count("—") + text.count(" -- ")
    report("em_dashes", em <= 2, f"{em} found (max 2)")

    rv = RHETORICAL_REVEAL.findall(text)
    report("rhetorical_reveals", len(rv) == 0, f"{len(rv)} hit(s)")

    art = ARTIFACTS.findall(text)
    report("leaked_artifacts", not art, f"{len(art)} hit(s)")

    sl = [len(s.split()) for s in sentences(text)]
    short, long_ = min(sl, default=0), max(sl, default=0)
    report("sentence_variety", short < 8 and long_ > 20, f"min={short} max={long_}")

    c = len(CONTRACTION.findall(text))
    report("contractions", c >= 2, f"{c} found (want 2+)")

    print(f"word_count: {len(text.split())}")
    print(f"result: {'CLEAN' if fails == 0 else f'{fails} FAIL(s) — fix and re-run'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main(sys.argv[1])
