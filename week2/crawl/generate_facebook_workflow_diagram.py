#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a workflow diagram for week2/crawl/facebook_with_profile.py as a JPG.

The diagram captures the high-level flow:
  Input (N, URL) → init_session → loop: fetch_page → extract_post_info → aggregate → Output
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color=(0, 0, 0), width: int = 4, head_len: int = 14, head_width: int = 10):
    draw.line([start, end], fill=color, width=width)
    # arrow head
    # Compute a simple arrow head based on the last segment direction
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    # perpendicular
    px, py = -uy, ux
    tip = end
    left = (int(tip[0] - ux * head_len + px * head_width), int(tip[1] - uy * head_len + py * head_width))
    right = (int(tip[0] - ux * head_len - px * head_width), int(tip[1] - uy * head_len - py * head_width))
    draw.polygon([tip, left, right], fill=color)


def draw_box(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont, fill=(255, 255, 255), outline=(0, 0, 0)):
    x0, y0, x1, y1 = xy
    # rounded rectangle (simple: rectangle)
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=3)
    # wrap text to fit box width
    padding = 12
    max_width = (x1 - x0) - 2 * padding
    # rough estimate of characters per line using font.getlength
    words = text.split()
    lines = []
    cur = []
    for w in words:
        trial = (" ".join(cur + [w])).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    # center text vertically
    line_height = font.size + 4
    text_height = len(lines) * line_height
    ty = y0 + ((y1 - y0) - text_height) // 2
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        tx = x0 + (x1 - x0 - tw) // 2
        draw.text((tx, ty + i * line_height), line, fill=(0, 0, 0), font=font)


def main(output_path: str = "week2/crawl/facebook_workflow.jpg"):
    width, height = 1400, 900
    bg = (250, 250, 250)
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    # Title
    title = "Facebook Crawl Workflow"
    tw = draw.textlength(title, font=title_font)
    draw.text(((width - tw) // 2, 20), title, fill=(0, 0, 0), font=title_font)

    # Define boxes
    boxes = {}
    boxes["input"] = (100, 100, 1300, 180)
    boxes["init"] = (250, 230, 1150, 330)
    boxes["fetch"] = (120, 400, 760, 560)
    boxes["extract"] = (820, 400, 1360, 560)
    boxes["aggregate"] = (250, 620, 1150, 740)

    # Box texts
    input_text = "Input: N (desired posts), URL (profile/page)"
    init_text = (
        "init_session: GET profile page → parse <script> → extract fb_dtsg token, "
        "initial end_cursor, and variables; prepare variables (cursor, count=3, id/beforeTime)"
    )
    fetch_text = (
        "fetch_page: POST GraphQL (DOC_ID/REQ_NAME, variables) → stream line JSON → "
        "read page_info.end_cursor as next_cursor → collect post nodes"
    )
    extract_text = (
        "extract_post_info: normalize node → {post_url, text, likes, comments, shares, "
        "cover_urls, author, timestamp/formatted_time, hashtags}"
    )
    aggregate_text = (
        "Aggregate & Output: append posts; variables['cursor']=next_cursor; loop up to ceil(N/3) "
        "or until no next_cursor; return (all_posts, {'posts': all_posts})"
    )

    # Draw boxes
    draw_box(draw, boxes["input"], input_text, body_font)
    draw_box(draw, boxes["init"], init_text, body_font)
    draw_box(draw, boxes["fetch"], fetch_text, body_font)
    draw_box(draw, boxes["extract"], extract_text, body_font)
    draw_box(draw, boxes["aggregate"], aggregate_text, body_font)

    # Arrows
    def mid_bottom(xy):
        x0, y0, x1, y1 = xy
        return ((x0 + x1) // 2, y1)

    def mid_top(xy):
        x0, y0, x1, y1 = xy
        return ((x0 + x1) // 2, y0)

    def mid_right(xy):
        x0, y0, x1, y1 = xy
        return (x1, (y0 + y1) // 2)

    def mid_left(xy):
        x0, y0, x1, y1 = xy
        return (x0, (y0 + y1) // 2)

    # input → init
    draw_arrow(draw, mid_bottom(boxes["input"]), mid_top(boxes["init"]))
    # init → fetch
    draw_arrow(draw, mid_bottom(boxes["init"]), mid_top(boxes["fetch"]))
    # fetch → extract
    draw_arrow(draw, mid_right(boxes["fetch"]), mid_left(boxes["extract"]))
    # extract → aggregate
    draw_arrow(draw, mid_bottom(boxes["extract"]), mid_top(boxes["aggregate"]))
    # aggregate → fetch (loop via cursor)
    loop_start = (boxes["aggregate"][0] + 20, boxes["aggregate"][1])
    loop_end = (boxes["fetch"][0] + 20, boxes["fetch"][1])
    draw_arrow(draw, loop_start, loop_end)
    loop_label = "Loop while next_cursor exists (variables['cursor'] ← next_cursor)"
    lw = draw.textlength(loop_label, font=body_font)
    draw.text((loop_start[0] + 10, (loop_start[1] + loop_end[1]) // 2 - 20), loop_label, fill=(0, 0, 0), font=body_font)

    img.save(output_path, format="JPEG", quality=95)


if __name__ == "__main__":
    main()


