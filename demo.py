"""
Simple integration demo for TextInsightTool.

Run:
    python demo.py
"""

from __future__ import annotations

import json

from tool import Tool, analyze_text


text_insight_tool = Tool(
    name="TextInsightTool",
    description="Analyzes text and returns text statistics, keywords, and sentiment.",
    fn=analyze_text,
)


def newsroom_workflow(article_text: str) -> None:
    """
    Simulate a tiny agent/workflow that calls a tool on an article.

    This function prints that it received an article, calls the tool, and then
    prints the structured result in a readable format.
    """

    print("Agent received an article for analysis.")
    result = text_insight_tool.execute(text=article_text, top_n=5)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


def main() -> None:
    print("=== Successful Case ===")
    newsroom_workflow(
        "Shares of Acme Corp rose after the company reported stronger-than-expected "
        "quarterly revenue and said demand remains robust. Management highlighted "
        "improving margins and continued investment in new products, while noting "
        "near-term risks from higher input costs."
    )

    print()
    print("=== Error Case ===")
    newsroom_workflow("")


if __name__ == "__main__":
    main()

