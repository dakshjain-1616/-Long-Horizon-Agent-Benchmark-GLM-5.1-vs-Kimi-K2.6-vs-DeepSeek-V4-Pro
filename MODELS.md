# Model Support

All three models can be reached via **OpenRouter** with one key, or via each
provider's direct API. Pricing below is verified live on OpenRouter as of
**April 2026**.

| Model | OpenRouter ID | Direct ID | Direct base URL | Input $/M | Output $/M | Context |
|---|---|---|---|---|---|---|
| **GLM-5.1** (Z.ai) | `z-ai/glm-5.1` | `glm-5.1` | `https://open.bigmodel.cn/api/paas/v4` | **$1.05** | **$3.50** | 203K |
| **Kimi K2.6** (Moonshot AI) | `moonshotai/kimi-k2.6` | `kimi-k2.6` | `https://api.moonshot.cn/v1` | **$0.7448** | **$4.655** | 256K |
| **DeepSeek V4-Pro** | `deepseek/deepseek-v4-pro` | `deepseek-v4-pro` | `https://api.deepseek.com/v1` | **$0.435** | **$0.87** | 1M |

Sources:

- DeepSeek V4-Pro: <https://openrouter.ai/deepseek/deepseek-v4-pro>
- Kimi K2.6: <https://openrouter.ai/moonshotai/kimi-k2.6>
- GLM-5.1: <https://openrouter.ai/z-ai/glm-5.1>

## Picking a path

- **OpenRouter (recommended)**: set `OPENROUTER_API_KEY` and the CLI auto-routes.
  No other env vars needed. One bill, one key.
- **Direct APIs**: set the corresponding `GLM_API_KEY` / `KIMI_API_KEY` /
  `DEEPSEEK_API_KEY`. Useful if you have provider-side credits or strict data
  residency rules.

## Mock Mode

Add `--mock` to any `lhb` command — every model client returns deterministic
canned responses, no network, no key required.

```bash
lhb run -m kimi-k2.6 -t refactor_function --mock
```
