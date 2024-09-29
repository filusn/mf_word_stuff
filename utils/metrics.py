import difflib

from fuzzywuzzy import fuzz
from Levenshtein import distance as levenshtein_distance
from rapidfuzz import fuzz as rapidfuzz_fuzz


def calculate_sequence_matcher(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).ratio()


def calculate_levenshtein(s1, s2):
    return 1 - (levenshtein_distance(s1, s2) / max(len(s1), len(s2)))


def calculate_jaccard(s1, s2):
    # Tokenize into words
    words1 = set(s1.split())
    words2 = set(s2.split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0


def calculate_fuzzy_matching(s1, s2):
    return fuzz.ratio(s1, s2) / 100  # Normalize to [0,1]


def calculate_rapidfuzz_matching(s1, s2):
    return rapidfuzz_fuzz.ratio(s1, s2) / 100  # Normalize to [0,1]
