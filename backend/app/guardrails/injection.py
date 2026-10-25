import re
import unicodedata

# (pattern, label). Matched against a normalized, lowercase version of the query.
RULES = [
    (r"\b(ignore|disregard|forget|override|bypass)\b.{0,40}\b(previous|prior|above|earlier|all|any|your|the)\b.{0,40}\b(instruction|instructions|rules|prompt|guidelines|directives)\b",
     "instruction_override"),
    (r"\b(reveal|show|print|display|repeat|output|tell me)\b.{0,30}\b(system prompt|your prompt|your instructions|hidden prompt|initial prompt)\b",
     "prompt_extraction"),
    (r"\bwhat (is|are|were) your (system )?(prompt|instructions|rules)\b",
     "prompt_extraction"),
    (r"\b(you are now|act as|pretend (to be|you are)|roleplay as|from now on you)\b",
     "role_hijack"),
    (r"\b(dan|developer mode|jailbreak|do anything now|no restrictions|without restrictions|unfiltered)\b",
     "jailbreak_keyword"),
    (r"\b(i am|i'm|this is)\b.{0,20}\b(admin|administrator|ceo|root|the developer|your developer)\b",
     "privilege_claim"),
    (r"\b(bypass|disable|turn off|ignore)\b.{0,20}\b(security|guardrails?|filters?|access control|permissions?|restrictions?)\b",
     "guardrail_bypass"),
    (r"(</?\s*(system|assistant|context|instructions?)\s*>|\[/?(inst|system)\]|###\s*(system|instruction))",
     "fake_delimiter"),
    (r"\b(base64|rot13|hex)\b.{0,30}\b(decode|encoded|instruction)\b",
     "encoding_trick"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE | re.DOTALL), label) for p, label in RULES]

MAX_QUERY_CHARS = 1000


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)           # fold lookalike characters
    text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)  # strip zero-width chars
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_injection(text: str):
    """Return (is_blocked, reason). reason is a short label for logs."""
    if len(text) > MAX_QUERY_CHARS:
        return True, "query_too_long"
    norm = _normalize(text)
    for pattern, label in _COMPILED:
        if pattern.search(norm):
            return True, label
    return False, None


import re as _re

def sanitize_chunks(chunks):
    """Remove only instruction-like sentences. Returns (safe_chunks, dropped_labels)."""
    safe, dropped = [], []
    for c in chunks:
        sentences = _re.split(r"(?<=[.!?])\s+|\n+", c["text"])
        kept = []
        for s in sentences:
            blocked, reason = check_injection(s)
            if blocked and reason != "query_too_long":
                dropped.append(f"{c['source']}:{reason}")
            elif s.strip():
                kept.append(s)
        if kept:
            safe.append({**c, "text": " ".join(kept)})
    return safe, dropped