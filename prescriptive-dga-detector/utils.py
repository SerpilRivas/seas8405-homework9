import math
import re

ALNUM_RE = re.compile(r"[a-z0-9]")

def base_domain(domain: str) -> str:
    d = (domain or "").strip().lower()
    d = d.split("@")[-1]
    parts = [p for p in d.split(".") if p]
    if len(parts) >= 2:
        return parts[-2]
    return parts[0] if parts else ""

def only_alnum(s: str) -> str:
    return "".join(ch for ch in s.lower() if ALNUM_RE.match(ch))

def shannon_entropy(s: str) -> float:
    s = only_alnum(s)
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())

def extract_features(domain: str) -> dict:
    base = base_domain(domain)
    cleaned = only_alnum(base)
    return {"length": len(cleaned), "entropy": shannon_entropy(base)}
