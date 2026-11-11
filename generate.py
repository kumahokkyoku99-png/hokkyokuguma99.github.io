from pathlib import Path
from html import escape
from datetime import date, datetime
import re


# --------------------------------------------------
# Configuration
# --------------------------------------------------

POSTS_FOLDER = Path("content/posts")
OUTPUT_FOLDER = Path("blog")
SITE_NAME = "Polar Bear's Blog"
SITE_BASE = "/hokkyokuguma99.github.io"


# --------------------------------------------------
# Front matter
# --------------------------------------------------

def split_front_matter(markdown):
    """
    Split YAML-style front matter from the Markdown body.

    Supported metadata:
      title: My title
      date: 2026-10-08
      excerpt: A short description
      category: Travel
      tags: [Travel, Japan]

    Also supports block-style tags:
      tags:
        - Travel
        - Japan
    """
    lines = markdown.splitlines()

    if not lines or lines[0].strip() != "---":
        return {}, markdown

    closing = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            closing = i
            break

    if closing is None:
        return {}, markdown

    metadata = {}
    current_key = None

    for line in lines[1:closing]:
        # YAML block list, e.g.:
        # tags:
        #   - Travel
        if re.match(r"^\s*-\s+", line) and current_key:
            metadata.setdefault(current_key, []).append(
                line.strip()[2:].strip().strip("\"'")
            )
            continue

        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not match:
            continue

        key, value = match.groups()
        current_key = key.lower()
        value = value.strip()

        if not value:
            metadata[current_key] = []
        elif value.startswith("[") and value.endswith("]"):
            items = value[1:-1].split(",")
            metadata[current_key] = [
                item.strip().strip("\"'")
                for item in items if item.strip()
            ]
        else:
            metadata[current_key] = value.strip("\"'")

    body = "\n".join(lines[closing + 1:]).lstrip()
    return metadata, body


# --------------------------------------------------
# Small Markdown parser
# --------------------------------------------------

def inline_markdown(text):
    """Convert a small, safe subset of Markdown inline syntax to HTML."""
    text = escape(text)

    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Links: [label](https://example.com)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^ )]+)\)",
        r'<a href="\2">\1</a>',
        text
    )

    # Bold and italic
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"<em>\1</em>", text)

    return text


def parse_markdown(markdown):
    """
    Convert basic Markdown to HTML.

    Supports headings, paragraphs, unordered/ordered lists,
    blockquotes, bold, italic, inline code, and simple links.
    """
    lines = markdown.splitlines()
    html = []
    paragraph = []
    list_type = None

    def flush_paragraph():
        if paragraph:
            html.append(
                "<p>" + " ".join(inline_markdown(x) for x in paragraph) + "</p>"
            )
            paragraph.clear()

    def close_list():
        nonlocal list_type
        if list_type:
            html.append(f"</{list_type}>")
            list_type = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            html.append(
                f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>"
            )
            continue

        unordered = re.match(r"^[-*+]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)

        if unordered or ordered:
            flush_paragraph()
            desired = "ul" if unordered else "ol"
            if list_type != desired:
                close_list()
                html.append(f"<{desired}>")
                list_type = desired
            item = unordered.group(1) if unordered else ordered.group(1)
            html.append(f"<li>{inline_markdown(item)}</li>")
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            close_list()
            quote = stripped[1:].strip()
            html.append(f"<blockquote><p>{inline_markdown(quote)}</p></blockquote>")
            continue

        close_list()
        paragraph.append(stripped)

    flush_paragraph()
    close_list()

    return "\n".join(html)


# --------------------------------------------------
# Post information and excerpts
# --------------------------------------------------

def clean_excerpt(text):
    """Create a plain-text excerpt from Markdown."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`#>]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_post_info(post_path):
    markdown = post_path.read_text(encoding="utf-8")
    metadata, body = split_front_matter(markdown)

    title = str(metadata.get("title") or post_path.stem.replace("-", " ").replace("_", " ").title())
    post_date = str(metadata.get("date") or "")
    category = str(metadata.get("category") or "")

    excerpt = metadata.get("excerpt")
    if isinstance(excerpt, list):
        excerpt = " ".join(excerpt)
    if not excerpt:
        for line in body.splitlines():
            candidate = line.strip()
            if candidate and not candidate.startswith("#"):
                excerpt = clean_excerpt(candidate)
                break
    excerpt = str(excerpt or "Read this article.")

    tags = metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    if not isinstance(tags, list):
        tags = []

    return {
        "slug": post_path.stem,
        "title": title,
        "date": post_date,
        "category": category,
        "excerpt": excerpt,
        "tags": tags,
        "body": body,
    }


def date_sort_key(post):
    try:
        return datetime.fromisoformat(post["date"]).date()
    except (ValueError, TypeError):
        return date.min


# --------------------------------------------------
# HTML layout
# --------------------------------------------------

def page_template(title, content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)} | {escape(SITE_NAME)}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            max-width: 820px;
            margin: 0 auto;
            padding: 32px 22px;
            color: #292929;
            background: #fff;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.75;
        }}
        header {{ margin-bottom: 48px; }}
        header a {{ color: inherit; text-decoration: none; font-weight: 700; }}
        a {{ color: #386b91; }}
        h1, h2, h3 {{ line-height: 1.3; }}
        h1 {{ font-size: 2.3rem; }}
        .post-list {{ list-style: none; padding: 0; }}
        .post-item {{ padding: 22px 0; border-bottom: 1px solid #e5e5e5; }}
        .post-item h2 {{ margin: 0 0 5px; font-size: 1.35rem; }}
        .post-item h2 a {{ color: inherit; text-decoration: none; }}
        .post-item h2 a:hover {{ text-decoration: underline; }}
        .post-meta {{ color: #777; font-size: .88rem; }}
        .post-excerpt {{ margin: 8px 0 0; color: #555; }}
        main img {{ max-width: 100%; height: auto; }}
        blockquote {{ margin-left: 0; padding-left: 18px; border-left: 3px solid #ddd; color: #666; }}
        code {{ padding: 2px 5px; background: #f2f2f2; border-radius: 4px; }}
        footer {{ margin-top: 60px; color: #888; font-size: .85rem; }}
    </style>
</head>
<body>
    <header><a href="{SITE_BASE}/"> {escape(SITE_NAME)} </a></header>
    <main>
        {content}
    </main>
    <footer><a href="{SITE_BASE}/blog/">All posts</a></footer>
</body>
</html>
"""




# --------------------------------------------------
# Generate Jekyll include for the homepage
# --------------------------------------------------

INCLUDES_FOLDER = Path("_includes")
LATEST_POSTS_LIMIT = 3


def generate_latest_posts_include(posts):
    """
    Generate an HTML fragment that Jekyll can insert into index.md
    using: {% include latest_posts.html %}
    """
    INCLUDES_FOLDER.mkdir(parents=True, exist_ok=True)

    latest_posts = sorted(posts, key=date_sort_key, reverse=True)[:LATEST_POSTS_LIMIT]
    items = []

    for post in latest_posts:
        meta_parts = []
        if post["date"]:
            meta_parts.append(escape(post["date"]))
        if post["category"]:
            meta_parts.append(escape(post["category"]))

        meta_html = (
            f'<p class="latest-post__meta">{" · ".join(meta_parts)}</p>'
            if meta_parts else ""
        )

        items.append(f"""
        <article class="latest-post">
            <h3 class="latest-post__title">
                <a href="{SITE_BASE}/blog/{escape(post["slug"])}/">{escape(post["title"])}</a>
            </h3>
            {meta_html}
            <p class="latest-post__excerpt">{escape(post["excerpt"])}</p>
        </article>
        """)

    if items:
        posts_html = "\\n".join(items)
    else:
        posts_html = '<p class="latest-post__empty">No posts yet. Check back soon!</p>'

    include_html = f"""
<section class="latest-posts">
    <h2>Latest Posts</h2>
    <div class="latest-posts__list">
        {posts_html}
    </div>
    <p class="latest-posts__more">
        <a href="{SITE_BASE}/blog/">View all posts →</a>
    </p>
</section>
"""

    output_file = INCLUDES_FOLDER / "latest_posts.html"
    output_file.write_text(include_html.strip() + "\n", encoding="utf-8")
    print(f"Generated homepage include: {output_file}")


# --------------------------------------------------
# Generate article pages and Blog index
# --------------------------------------------------

def generate_site():
    if not POSTS_FOLDER.exists():
        print(f"Posts folder not found: {POSTS_FOLDER}")
        return

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    post_files = sorted(POSTS_FOLDER.glob("*.md"))
    posts = []

    for post_path in post_files:
        post = get_post_info(post_path)
        posts.append(post)

        article_body = parse_markdown(post["body"])
        date_html = (
            f'<p class="post-meta">{escape(post["date"])}</p>'
            if post["date"] else ""
        )

        article_content = f"""
            <article>
                <h1>{escape(post["title"])}</h1>
                {date_html}
                {article_body}
            </article>
        """

        post_folder = OUTPUT_FOLDER / post["slug"]
        post_folder.mkdir(parents=True, exist_ok=True)

        output_file = post_folder / "index.html"
        output_file.write_text(
            page_template(post["title"], article_content),
            encoding="utf-8"
        )
        print(f"Generated article: {output_file}")

    # New: generate the Blog index at /blog/
    posts.sort(key=date_sort_key, reverse=True)

    # Generate the latest-posts fragment used by the Jekyll homepage.
    generate_latest_posts_include(posts)

    list_items = []
    for post in posts:
        meta_parts = []
        if post["date"]:
            meta_parts.append(escape(post["date"]))
        if post["category"]:
            meta_parts.append(escape(post["category"]))

        meta_html = (
            f'<div class="post-meta">{" · ".join(meta_parts)}</div>'
            if meta_parts else ""
        )

        list_items.append(f"""
            <li class="post-item">
                <h2><a href="{SITE_BASE}/blog/{escape(post["slug"])}/">{escape(post["title"])}</a></h2>
                {meta_html}
                <p class="post-excerpt">{escape(post["excerpt"])}</p>
            </li>
        """)

    if list_items:
        index_content = f"""
            <h1>Blog</h1>
            <p class="post-meta">{len(posts)} article(s)</p>
            <ul class="post-list">
                {''.join(list_items)}
            </ul>
        """
    else:
        index_content = """
            <h1>Blog</h1>
            <p>No posts yet. Check back soon!</p>
        """

    blog_index = OUTPUT_FOLDER / "index.html"
    blog_index.write_text(
        page_template("Blog", index_content),
        encoding="utf-8"
    )
    print(f"Generated Blog index: {blog_index}")


if __name__ == "__main__":
    generate_site()
