from pathlib import Path
import re


# -------------------------
# Markdown parser
# -------------------------

def parse_markdown(text):
    lines = text.splitlines()
    html = []

    for line in lines:

        # Headings
        if line.startswith("# "):
            html.append(f"<h1>{line[2:]}</h1>")

        elif line.startswith("## "):
            html.append(f"<h2>{line[3:]}</h2>")

        elif line.startswith("### "):
            html.append(f"<h3>{line[4:]}</h3>")

        # Empty line
        elif line.strip() == "":
            continue

        # Paragraph
        else:
            # Bold
            line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)

            # Italic
            line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)

            html.append(f"<p>{line}</p>")

    return "\n".join(html)


# -------------------------
# Site generator
# -------------------------

def generate_site():

    posts_folder = Path("content/posts")
    output_folder = Path("blog")

    # Make sure the output folder exists
    output_folder.mkdir(exist_ok=True)

    # Find all Markdown files
    posts = posts_folder.glob("*.md")

    for post in posts:

        # Read Markdown
        markdown = post.read_text(encoding="utf-8")

        # Convert Markdown → HTML
        content = parse_markdown(markdown)

        # Create a URL based on the filename
        slug = post.stem

        # Create output directory
        post_folder = output_folder / slug
        post_folder.mkdir(parents=True, exist_ok=True)

        # Create complete HTML page
        html = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>{slug}</title>
</head>

<body>

<header>
    <a href="/">Polar Bear's Blog</a>
</header>

<main>
    {content}
</main>

</body>

</html>
"""

        # Write HTML
        output_file = post_folder / "index.html"
        output_file.write_text(html, encoding="utf-8")

        print(f"Generated: {output_file}")


# -------------------------
# Run generator
# -------------------------

if __name__ == "__main__":
    generate_site()
