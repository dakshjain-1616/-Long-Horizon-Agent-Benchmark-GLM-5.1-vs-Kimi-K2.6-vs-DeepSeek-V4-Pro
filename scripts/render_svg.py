"""Render docs/diagrams/quality-vs-calls.svg from real benchmark JSONs."""

import json
import random
from pathlib import Path

random.seed(7)

MODELS = [
    ("Claude Opus 4.7", "results/opus/results_opus-4.7.json", "#10b981", "#065f46"),
    ("Kimi K2.6", "results/kimi/results_kimi-k2.6.json", "#a855f7", "#581c87"),
    ("DeepSeek V4-Pro", "results/deepseek/results_deepseek-v4-pro.json", "#3b82f6", "#1e3a8a"),
]

X0, X1 = 100, 900   # plot area x
Y0, Y1 = 80, 450    # plot area y (top, bottom)
X_MAX = 50          # tool-call axis cap
Y_MAX = 1.0


def x_to_px(calls: float) -> float:
    return X0 + (min(calls, X_MAX) / X_MAX) * (X1 - X0)


def y_to_px(q: float) -> float:
    return Y1 - (q / Y_MAX) * (Y1 - Y0)


def render() -> str:
    parts: list[str] = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 580" '
        'font-family="-apple-system, system-ui, Segoe UI, Roboto, sans-serif" '
        'font-size="13" width="960" height="580" fill="#0f172a">'
    )
    parts.append(
        '<rect data-bg="true" x="0" y="0" width="960" height="580" '
        'fill="#f8fafc" stroke="#0f172a" stroke-width="2"/>'
    )
    parts.append(
        '<text x="480" y="30" text-anchor="middle" font-weight="700" font-size="18" fill="#111827">'
        'Quality vs Tool-Call Count — measured</text>'
    )
    parts.append(
        '<text x="480" y="50" text-anchor="middle" fill="#6b7280">'
        '20 tasks · per-task scatter · judged by GPT-5.5 · April 2026</text>'
    )

    parts.append(
        '<g stroke="#1f2937" stroke-width="1.5">'
        f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}"/>'
        f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}"/>'
        '</g>'
    )

    parts.append(
        f'<text x="32" y="{(Y0+Y1)//2}" text-anchor="middle" font-weight="600" '
        f'fill="#374151" transform="rotate(-90 32 {(Y0+Y1)//2})">Quality score (0 - 1)</text>'
    )
    parts.append(
        '<text x="500" y="510" text-anchor="middle" font-weight="600" fill="#374151">'
        'Tool-call count (capped at 50)</text>'
    )

    yt = '<g font-size="11" fill="#6b7280" text-anchor="end">'
    for q in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        py = y_to_px(q)
        yt += (
            f'<line x1="95" y1="{py:.0f}" x2="100" y2="{py:.0f}" stroke="#1f2937"/>'
            f'<text fill="#111827" x="92" y="{py+4:.0f}">{q:.1f}</text>'
        )
    yt += '</g>'
    parts.append(yt)

    xt = '<g font-size="11" fill="#6b7280" text-anchor="middle">'
    for c in [0, 10, 20, 30, 40, 50]:
        px = x_to_px(c)
        xt += (
            f'<line x1="{px:.0f}" y1="{Y1}" x2="{px:.0f}" y2="{Y1+5}" stroke="#1f2937"/>'
            f'<text fill="#111827" x="{px:.0f}" y="{Y1+20}">{c}</text>'
        )
    xt += '</g>'
    parts.append(xt)

    grid = '<g stroke="#e5e7eb" stroke-width="1">'
    for q in [0.2, 0.4, 0.6, 0.8]:
        py = y_to_px(q)
        grid += f'<line x1="{X0}" y1="{py:.0f}" x2="{X1}" y2="{py:.0f}"/>'
    grid += '</g>'
    parts.append(grid)

    legend_y = Y0 + 10
    for i, (name, path, color, dark) in enumerate(MODELS):
        d = json.loads(Path(path).read_text())
        rs = d["task_results"]
        avg_q = sum(r["quality_score"] for r in rs) / len(rs)
        total_cost = sum(r["total_cost"] for r in rs)

        for r in rs:
            cx = x_to_px(r["num_tool_calls"]) + random.uniform(-3, 3)
            cy = y_to_px(r["quality_score"]) + random.uniform(-3, 3)
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" '
                f'fill="{color}" fill-opacity="0.55" stroke="{dark}" stroke-width="1"/>'
            )

        avg_y = y_to_px(avg_q)
        parts.append(
            f'<line x1="{X0}" y1="{avg_y:.1f}" x2="{X1}" y2="{avg_y:.1f}" '
            f'stroke="{dark}" stroke-width="1.4" stroke-dasharray="6,4" opacity="0.7"/>'
        )

        ly = legend_y + i * 22
        parts.append(
            f'<rect x="650" y="{ly-10}" width="14" height="14" fill="{color}" '
            f'stroke="{dark}" stroke-width="1"/>'
            f'<text x="672" y="{ly+1}" font-weight="700" fill="{dark}">{name}</text>'
            f'<text x="672" y="{ly+15}" font-size="11" fill="#374151">'
            f'avg quality {avg_q:.2f} · total cost ${total_cost:.2f}</text>'
        )

    parts.append(
        '<text x="500" y="555" text-anchor="middle" fill="#6b7280" font-size="11">'
        'Each dot = one task (jittered). Dashed line = per-model average quality. '
        'Source: results/{opus,kimi,deepseek}/results_*.json</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    Path("docs/diagrams/quality-vs-calls.svg").write_text(render())
    print("rendered")
