# Results

This folder keeps the final evaluation artifacts used in the README and mini report.

Final local-model runs:

- `ollama_qwen_main_v3_*`: Qwen 2.5 3B on A1--A15.
- `ollama_qwen_benign_v3_*`: Qwen 2.5 3B on benign cases B1--B10.
- `ollama_llama32_main_*`: Llama 3.2 3B on A1--A15.
- `ollama_llama32_benign_*`: Llama 3.2 3B on benign cases B1--B10.
- `ollama_qwen_tool_injection_v2_*`: Qwen 2.5 3B on tool-result injection attacks A16--A20.
- `ollama_llama32_tool_injection_v2_*`: Llama 3.2 3B on tool-result injection attacks A16--A20.
- `simulated_full_*`: controlled simulated ablation over A1--A15.
- `simulated_preference_extension_*`: simulated sanity check for preference-manipulation attacks A21--A23.

Older debugging runs were intentionally removed to avoid confusing obsolete results with the final reported numbers.
