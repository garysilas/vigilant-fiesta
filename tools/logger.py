import json
import time
from contextlib import contextmanager
from typing import Any


def log(stage: str, event: str, duration: float | None = None, **metadata: Any) -> None:
    entry: dict[str, Any] = {"stage": stage, "event": event}
    if duration is not None:
        entry["duration"] = round(duration, 3)
    if metadata:
        entry["metadata"] = metadata
    print(json.dumps(entry))


@contextmanager
def log_stage(stage: str, **metadata: Any):
    start = time.time()
    log(stage, "start", **metadata)
    yield
    elapsed = time.time() - start
    log(stage, "done", duration=elapsed, **metadata)
