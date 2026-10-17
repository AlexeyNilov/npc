#!/usr/bin/env bash

# export SYSTEM_ONE=http://127.0.0.1:12346/v1/systemone
# Clef evaluates the complete prompt in one physical batch.
exec llama serve \
  -hf ggml-org/Clef-Flash-GGUF:Q4_K_M \
  --batch-size 2048 \
  --ubatch-size 2048 \
  --host 127.0.0.1 \
  --port 12346
