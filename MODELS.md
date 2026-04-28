# Model Support

All three contestant models — plus the **GPT-5.5 judge** — can be reached via
**OpenRouter** with one key, or via each provider's direct API. Pricing below
is verified live on OpenRouter as of **April 2026**.

| Model | Role | OpenRouter ID | Direct ID | Direct base URL | Input $/M | Output $/M | Context |
|---|---|---|---|---|---|---|---|
| **Claude Opus 4.7** (Anthropic) | contestant | `anthropic/claude-opus-4-7` | `claude-opus-4-7` | `https://api.anthropic.com/v1` | **$5.00** | **$25.00** | 200K |
| **Kimi K2.6** (Moonshot AI) | contestant | `moonshotai/kimi-k2.6` | `kimi-k2.6` | `https://api.moonshot.cn/v1` | **$0.7448** | **$4.655** | 256K |
| **DeepSeek V4-Pro** | contestant | `deepseek/deepseek-v4-pro` | `deepseek-v4-pro` | `https://api.deepseek.com/v1` | **$0.435** | **$0.87** | 1M |
| **GPT-5.5** (OpenAI) | judge | `openai/gpt-5.5` | `gpt-5.5` | `https://api.openai.com/v1` | **$5.00** | **$30.00** | — |

Sources:

- Claude Opus 4.7: <https://openrouter.ai/anthropic/claude-opus-4-7>
- DeepSeek V4-Pro: <https://openrouter.ai/deepseek/deepseek-v4-pro>
- Kimi K2.6: <https://openrouter.ai/moonshotai/kimi-k2.6>
- GPT-5.5 (judge): <https://openrouter.ai/openai/gpt-5.5>

## Picking a path

- **OpenRouter (recommended)**: set `OPENROUTER_API_KEY` and the CLI auto-routes
  every contestant *and* the GPT-5.5 judge through one key. One bill, one key.
- **Direct APIs**: set the corresponding `ANTHROPIC_API_KEY` / `KIMI_API_KEY` /
  `DEEPSEEK_API_KEY`. Useful if you have provider-side credits or strict data
  residency rules. (The judge always goes through OpenRouter.)

## Mock Mode

Add `--mock` to any `lhb` command — every model client returns deterministic
canned responses, no network, no key required.

```bash
lhb run -m kimi-k2.6 -t refactor_function --mock
```
