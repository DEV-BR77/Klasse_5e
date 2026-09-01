def homework_items(payload):
    data = payload.get("data", payload) if isinstance(payload, dict) else payload
    lessons = data.get("lessons", []) if isinstance(data, dict) else []
    subjects = {
        str(item.get("id")): item.get("subject") or ""
        for item in lessons
        if isinstance(item, dict) and item.get("id") is not None
    }
    homeworks = data.get("homeworks", []) if isinstance(data, dict) else data
    if not isinstance(homeworks, list):
        return []
    normalized = []
    for source in homeworks:
        if not isinstance(source, dict):
            continue
        item = dict(source)
        item.setdefault("subject", subjects.get(str(item.get("lessonId")), ""))
        text = str(item.get("text") or item.get("homework") or item.get("description") or "").strip()
        remark = str(item.get("remark") or "").strip()
        if text and remark and remark != text:
            item["text"] = f"{text} - {remark}"
        elif remark:
            item["text"] = remark
        if "status" not in item:
            item["status"] = "completed" if item.get("completed") else "open"
        normalized.append(item)
    return normalized
