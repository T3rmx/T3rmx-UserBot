try:
    from html_telegraph_poster import TelegraphPoster
except Exception:  # optional dependency; post_to_telegraph will degrade gracefully
    TelegraphPoster = None


def media_type(message):
    if not message:
        return None
    if getattr(message, "photo", None):
        return "Photo"
    if getattr(message, "audio", None):
        return "Audio"
    if getattr(message, "voice", None):
        return "Voice"
    if getattr(message, "video_note", None):
        return "Round Video"
    if getattr(message, "gif", None):
        return "Gif"
    if getattr(message, "sticker", None):
        return "Sticker"
    if getattr(message, "video", None):
        return "Video"
    if getattr(message, "document", None):
        return "Document"
    return None


async def meme_type(message):
    """Legacy-compatible media classifier for meme/converter helpers."""
    if not message:
        return None
    if isinstance(message, str) and os.path.exists(message):
        return "Document"
    mt = media_type(message)
    if mt == "Document":
        try:
            mime = (getattr(getattr(message, "document", None), "mime_type", "") or "").lower()
            if mime.startswith("image/") and "gif" not in mime:
                return "Photo"
            if "gif" in mime or "video" in mime:
                return "Gif" if "gif" in mime else "Video"
            if mime.startswith("audio/"):
                return "Audio"
        except Exception:
            pass
        return "Document"
    return mt


async def fileinfo(file):
    """Backward-compatible file/media info helper.

    Preferred implementation lives in helpers.functions.functions.fileinfo; this
    wrapper preserves import compatibility for modules importing from helpers.tools.
    """
    try:
        from .functions.functions import fileinfo as _fileinfo

        return await _fileinfo(file)
    except Exception:
        try:
            import json
            from ..helpers.utils.utils import runcmd

            x, *_ = await runcmd(f"mediainfo '{file}' --Output=JSON")
            cat_json = json.loads(x)["media"]["track"]
            dic = {
                "path": file,
                "size": int(cat_json[0].get("FileSize", 0) or 0),
                "extension": cat_json[0].get("FileExtension"),
            }
            try:
                dic["format"] = cat_json[0].get("Format")
                dic["type"] = cat_json[1].get("@type") if len(cat_json) > 1 else None
                if "Duration" in cat_json[0]:
                    dic["duration"] = int(float(cat_json[0]["Duration"]))
                if "OverallBitRate" in cat_json[0]:
                    dic["bitrate"] = int(int(cat_json[0]["OverallBitRate"]) / 1000)
                if len(cat_json) > 1:
                    if "Height" in cat_json[1]:
                        dic["height"] = int(cat_json[1]["Height"])
                    if "Width" in cat_json[1]:
                        dic["width"] = int(cat_json[1]["Width"])
            except Exception:
                pass
            return dic
        except Exception:
            return {"path": file}


import os


async def post_to_telegraph(page_title, html_format_content):
    if TelegraphPoster is None:
        raise RuntimeError(
            "html-telegraph-poster (and its dependencies) is required for Telegraph posting"
        )
    post_client = TelegraphPoster(use_api=True)
    auth_name = "T3rmx UserBot"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=page_title,
        author=auth_name,
        author_url="https://github.com/T3rmx/T3rmx-UserBot",
        text=html_format_content,
    )
    return post_page["url"]

