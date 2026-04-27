# Model Support Documentation

## Supported Models

This benchmark supports the following model providers:

### GLM-5.1 (Zhipu AI)
- **Provider**: Zhipu AI
- **Model ID**: `glm-5.1`
- **API Base**: `https://open.bigmodel.cn/api/paas/v4`
- **Documentation**: https://open.bigmodel.cn/
- **Features**: Strong reasoning, tool use support
- **Cost Tracking**: Input: $0.003/1K tokens, Output: $0.006/1K tokens

### Kimi K2.6 (Moonshot AI)
- **Provider**: Moonshot AI
- **Model ID**: `kimi-k2-6`
- **API Base**: `https://api.moonshot.cn/v1`
- **Documentation**: https://platform.moonshot.cn/
- **Features**: Long context (up to 2M tokens), agentic capabilities
- **Cost Tracking**: Input: $0.005/1K tokens, Output: $0.015/1K tokens

### DeepSeek V4-Pro
- **Provider**: DeepSeek
- **Model ID**: `deepseek-v4-pro`
- **API Base**: `https://api.deepseek.com/v1`
- **Documentation**: https://platform.deepseek.com/
- **Features**: Excellent coding, reasoning, and tool use
- **Cost Tracking**: Input: $0.002/1K tokens, Output: $0.008/1K tokens

## Configuration

Models are configured via environment variables or config file:

```yaml
# config.yaml
models:
  - name: glm-5.1
    api_key: ${GLM_API_KEY}
    base_url: https://open.bigmodel.cn/api/paas/v4
  - name: kimi-k2.6
    api_key: ${KIMI_API_KEY}
    base_url: https://api.moonshot.cn/v1
  - name: deepseek-v4-pro
    api_key: ${DEEPSEEK_API_KEY}
    base_url: https://api.deepseek.com/v1
```

## Mock Mode

For testing without API keys, enable mock mode:

```bash
export LHB_MOCK_MODE=true
# or
python -m long_horizon_bench.cli run --mock
```

Mock mode simulates model responses for testing the benchmark infrastructure.

## Adding New Models

To add a new model provider:

1. Create a new client class in `src/long_horizon_bench/models/`
2. Inherit from `BaseModelClient`
3. Implement required methods: `chat()`, `count_tokens()`, `get_cost()`
4. Add model configuration to `config.yaml`

See `src/long_horizon_bench/models/base.py` for the interface definition.
