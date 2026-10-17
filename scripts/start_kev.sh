exec llama-server \
  -hf ggml-org/Kev-4B-GGUF:Q4_K_M \
  --host 127.0.0.1 \
  --port 12346

  # export SYSTEM_ONE=http://127.0.0.1:12346/v1/systemone
