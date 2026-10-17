#!/usr/bin/env bash

# export SYSTEM_ONE=http://127.0.0.1:12346/v1/systemone
# d3 evaluates the complete prompt in one physical batch.
exec llama serve \
  -hf ggml-org/vllm-d3-mini-GGUF:Q4_K_M \
  --batch-size 2048 \
  --ubatch-size 2048 \
  --host 127.0.0.1 \
  --port 12346
