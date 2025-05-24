import re
from rapidfuzz import fuzz
from typing import Tuple

def basic_stats(text: str) -> Tuple[int, int, int]:
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    words = len(re.findall(r'\w+', text))
    chars = len(text)
    return paragraphs, words, chars

def is_duplicate(hash_, existing_hashes, threshold: int = 100):
    for h in existing_hashes:
        if fuzz.ratio(hash_, h) >= threshold:
            return h
    return None
