from src.backends.base import ModelBackend
from src.backends.simulated import SimulatedBackend


def get_backend(name: str) -> ModelBackend:
    normalized = name.lower().strip()

    if normalized in {"simulated", "mock"}:
        return SimulatedBackend()

    if normalized == "ollama":
        from src.backends.ollama_backend import OllamaBackend

        return OllamaBackend()

    available = ["simulated", "ollama"]
    raise ValueError(
        f"Unknown backend '{name}'. Available backends: {', '.join(available)}"
    )
