try:
    from html_telegraph_poster import TelegraphPoster
except Exception:  # optional dependency; post_to_telegraph will degrade gracefully
    TelegraphPoster = None


def media_type(message):
    if message and message.photo:
        return "Photo"
    if message and message.audio:
        return "Audio"
    if message and message.voice:
        return "Voice"
    if message and message.video_note:
        return "Round Video"
    if message and message.gif:
        return "Gif"
    if message and message.sticker:
        return "Sticker"
    if message and message.video:
        return "Video"
    if message and message.document:
        return "Document"

async def post_to_telegraph(page_title, html_format_content):
    if TelegraphPoster is None:
        raise RuntimeError("html-telegraph-poster (and its dependencies) is required for Telegraph posting")
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
