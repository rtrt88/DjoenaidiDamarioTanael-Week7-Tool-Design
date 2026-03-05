"""
TextInsightTool: simple, business-friendly text analysis (standard library only).

This module implements a small custom tool that can be used to quickly summarize
key characteristics of a piece of text such as a news article, press release,
earnings transcript excerpt, or internal business memo.

The tool is intentionally simple and readable: it uses lightweight heuristics
for sentence counting, keyword extraction, and sentiment classification.
"""

from __future__ import annotations

from collections import Counter
import re
from typing import Any, Dict, List


class Tool:
    def __init__(self, name: str, description: str, fn):
        self.name = name
        self.description = description
        self.fn = fn

    def execute(self, **kwargs):
        return self.fn(**kwargs)


def analyze_text(text: str, top_n: int = 5) -> dict:
    """
    Analyze a piece of text and return a compact, JSON-serializable summary.

    Purpose
    -------
    This function provides lightweight, business-friendly signals from free-form
    text such as news articles, reports, memos, or announcements. It uses simple
    heuristics (not ML) to compute:
    - basic size/effort metrics (word count, sentence count, reading time)
    - topic hints (top keyword frequency after removing common stopwords)
    - a rough tone label (positive / negative / neutral) using a small lexicon

    Parameters
    ----------
    text : str
        The text to analyze. Must be a Python `str`. The function will call
        `text.strip()` and reject inputs that are empty or whitespace-only.
    top_n : int, default=5
        How many keywords to return in `top_keywords`. Must be an integer > 0.

    Output schema (success)
    -----------------------
    On success, returns a dict with the following structure (all values are
    JSON-serializable: bool, dict, int, float, list[str], str):

    {
      "success": True,
      "data": {
        "word_count": int,
        "sentence_count": int,
        "estimated_reading_time_min": float,
        "top_keywords": list[str],
        "sentiment": "positive" | "negative" | "neutral"
      }
    }

    - `estimated_reading_time_min` is computed assuming 200 words per minute and
      rounded to 2 decimal places.

    Structured error format
    -----------------------
    If validation fails or an unexpected exception occurs, returns:

    {
      "success": False,
      "error": {
        "type": str,     # e.g. "TypeError" or "ValueError"
        "message": str   # human-readable error message
      }
    }

    Edge cases handled
    ------------------
    - Non-string `text` -> structured TypeError.
    - Empty/whitespace-only `text` -> structured ValueError.
    - Non-integer `top_n` or `top_n <= 0` -> structured error.
    - Keyword extraction:
        - stopwords are removed
        - numeric tokens are ignored
        - if no keywords remain, `top_keywords` is an empty list
        - ties are broken deterministically (frequency desc, then word asc)
    - Sentence counting is intentionally simple (splits on `.`, `!`, `?`) and
      returns at least 1 for any non-empty input.
    """

    try:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        stripped = text.strip()
        if not stripped:
            raise ValueError("text must not be empty or whitespace-only")

        if not isinstance(top_n, int):
            raise TypeError("top_n must be an integer")
        if top_n <= 0:
            raise ValueError("top_n must be greater than 0")

        words = _tokenize_words(stripped)
        word_count = len(words)

        sentence_count = _count_sentences_simple(stripped)
        estimated_reading_time_min = round(word_count / 200.0, 2)

        top_keywords = _extract_top_keywords(words=words, top_n=top_n)
        sentiment = _classify_sentiment(words=words)

        return {
            "success": True,
            "data": {
                "word_count": int(word_count),
                "sentence_count": int(sentence_count),
                "estimated_reading_time_min": float(estimated_reading_time_min),
                "top_keywords": list(top_keywords),
                "sentiment": str(sentiment),
            },
        }
    except (TypeError, ValueError) as exc:
        return {
            "success": False,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }
    except Exception as exc:  # defensive: keep tool output predictable
        return {
            "success": False,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }


class TextInsightTool:
    """
    A simple custom tool wrapper around `analyze_text`.

    Clear purpose
    -------------
    This tool is designed for quick analysis of business or news text where you
    want a compact JSON-like summary that can be stored, compared, or piped into
    other systems (dashboards, ETL jobs, or downstream NLP steps).

    Parameter schema
    ----------------
    Inputs:
    - text (str, required): the text to analyze
    - top_n (int, optional, default=5): number of top keywords to return

    Outputs:
    - dict in the exact success/error formats documented in `analyze_text`
    """

    name: str = "TextInsightTool"
    description: str = (
        "Analyze a text snippet (word/sentence counts, reading time, "
        "top keywords, simple sentiment)."
    )
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to analyze."},
            "top_n": {
                "type": "integer",
                "description": "Number of top keywords to return.",
                "default": 5,
                "minimum": 1,
            },
        },
        "required": ["text"],
        "additionalProperties": False,
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "word_count": {"type": "integer"},
                    "sentence_count": {"type": "integer"},
                    "estimated_reading_time_min": {"type": "number"},
                    "top_keywords": {"type": "array", "items": {"type": "string"}},
                    "sentiment": {"type": "string"},
                },
                "required": [
                    "word_count",
                    "sentence_count",
                    "estimated_reading_time_min",
                    "top_keywords",
                    "sentiment",
                ],
            },
            "error": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["type", "message"],
            },
        },
        "required": ["success"],
    }

    def __init__(self) -> None:
        self._tool = Tool(name=self.name, description=self.description, fn=analyze_text)

    def execute(self, **kwargs: Any) -> dict:
        return self._tool.execute(**kwargs)


_STOPWORDS: set[str] = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "her",
    "his",
    "i",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "she",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "with",
    "you",
    "your",
}

_POSITIVE_WORDS: set[str] = {
    "good",
    "great",
    "positive",
    "up",
    "growth",
    "improve",
    "improved",
    "improving",
    "strong",
    "success",
    "successful",
    "profit",
    "profits",
    "gain",
    "gains",
    "bullish",
    "optimistic",
    "benefit",
    "benefits",
}

_NEGATIVE_WORDS: set[str] = {
    "bad",
    "poor",
    "negative",
    "down",
    "decline",
    "declined",
    "declining",
    "weak",
    "risk",
    "risks",
    "loss",
    "losses",
    "bearish",
    "pessimistic",
    "problem",
    "problems",
    "fail",
    "failed",
    "failure",
}


def _tokenize_words(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z']+", text.lower())
    return [t.strip("'") for t in tokens if t.strip("'")]


def _count_sentences_simple(text: str) -> int:
    # Simple heuristic: count groups separated by . ! ? (ignores abbreviations).
    parts = re.split(r"[.!?]+", text)
    non_empty = [p for p in (s.strip() for s in parts) if p]
    return max(1, len(non_empty))


def _extract_top_keywords(words: List[str], top_n: int) -> List[str]:
    candidates = [
        w
        for w in words
        if w not in _STOPWORDS and len(w) > 1 and not w.isnumeric()
    ]
    if not candidates:
        return []

    counts = Counter(candidates)
    # Deterministic tie-break: frequency desc, then word asc.
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for (w, _count) in items[:top_n]]


def _classify_sentiment(words: List[str]) -> str:
    pos = sum(1 for w in words if w in _POSITIVE_WORDS)
    neg = sum(1 for w in words if w in _NEGATIVE_WORDS)
    score = pos - neg
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"

