import json


def sse_event(event_type: str, data: dict | str) -> dict:
    if isinstance(data, dict):
        data = json.dumps(data)
    return {"event": event_type, "data": data}
