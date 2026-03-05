## Tool Overview

`TextInsightTool` analyzes a short piece of text (for example a news article, company update, or internal memo) and returns:

- **word count**: how many words the text contains
- **sentence count**: a simple estimate of how many sentences there are
- **estimated reading time**: minutes to read, assuming 200 words per minute
- **top keywords**: the most frequent non‑stopwords in the text
- **simple sentiment**: `positive`, `negative`, or `neutral` based on a small rule-based lexicon

All results are returned in a structured, JSON‑serializable dictionary so they are easy to inspect or pass into other parts of a project.

## How to Run the Demo

From the project root, run:

```bash
python demo.py
```

This will:

- run a **successful case** on a short business/news-style paragraph
- run an **error case** with an empty string to show structured error handling

## Design Decisions

- **Standard library only**: everything is implemented with core Python modules to keep the assignment lightweight and easy to run in any basic environment.
- **Simple rule-based sentiment**: sentiment is decided by counting positive and negative words from a small, hand-written lexicon.
- **Keyword frequency approach**: keywords are chosen by counting word frequencies after removing common English stopwords and very simple tokens.
- **Structured error returns**: instead of raising uncaught exceptions, the tool returns a clear error object so callers can handle failures gracefully.

## Limitations

- **Basic keyword extraction**: it does not understand multi-word phrases, synonyms, or domain-specific terminology.
- **Heuristic sentiment**: the sentiment label is not model-based and can be wrong on sarcasm, mixed tone, or domain-specific language.
- **Approximate sentence splitting**: sentences are detected using simple punctuation rules, so counts may be off for complex writing or abbreviations.

