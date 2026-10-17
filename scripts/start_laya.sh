#!/usr/bin/env bash

# export SYSTEM_ONE=http://127.0.0.1:12346/v1/systemone
exec llama serve \
  -hf ggml-org/Laya-GGUF:Q8_0 \
  --host 127.0.0.1 \
  --port 12346
