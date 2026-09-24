import re


def safe_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", str(name)).strip()[:150]
