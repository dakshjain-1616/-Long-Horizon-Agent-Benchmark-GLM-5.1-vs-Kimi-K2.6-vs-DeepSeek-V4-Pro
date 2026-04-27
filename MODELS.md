# Model Support Documentation

## Supported Models

### GLM-5.1 (Zhipu AI)
- Model ID: glm-5.1
- API Base: https://open.bigmodel.cn/api/paas/v4
- Input: $0.003/1K tokens, Output: $0.006/1K tokens

### Kimi K2.6 (Moonshot AI)
- Model ID: kimi-k2-6
- API Base: https://api.moonshot.cn/v1
- Input: $0.005/1K tokens, Output: $0.015/1K tokens

### DeepSeek V4-Pro
- Model ID: deepseek-v4-pro
- API Base: https://api.deepseek.com/v1
- Input: $0.002/1K tokens, Output: $0.008/1K tokens

## Mock Mode

Enable mock mode for testing without API keys:
```bash
export LHB_MOCK_MODE=true
python -m long_horizon_bench.cli run --mock
```
