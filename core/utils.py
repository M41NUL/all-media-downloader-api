def format_size(size_bytes) -> str:
    if not size_bytes or size_bytes <= 0:
        return "unknown"

    size_bytes = float(size_bytes)
    units = ["B", "KB", "MB", "GB"]
    unit_index = 0

    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes = size_bytes / 1024
        unit_index += 1

    return f"{size_bytes:.2f} {units[unit_index]}"


def format_duration(seconds) -> str:
    if not seconds or seconds <= 0:
        return "unknown"

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


def clean_caption(text) -> str:
    if not text:
        return "no caption available"

    return text.strip()
