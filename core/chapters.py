def number_value(value):
    try:
        return float(value) if value is not None else float("inf")
    except ValueError:
        return float("inf")


def chapter_sort_key(c):
    attrs = c["attributes"]
    return (
        number_value(attrs.get("volume")),
        number_value(attrs.get("chapter")),
        attrs.get("title") or "",
    )


def chapter_label(c):
    attrs = c["attributes"]
    v, n, t = attrs.get("volume"), attrs.get("chapter"), attrs.get("title")
    text = f"Tomo {v} | " if v else ""
    text += f"Cap. {n}" if n else ""
    text += f" | {t}" if t else ""
    return text if text else c["id"]


def group_by_volume(chapters):
    volumes = {}
    for c in chapters:
        key = c["attributes"].get("volume") or "Sin tomo"
        volumes.setdefault(key, []).append(c)
    return volumes
