import feedparser
import httpx
import pathlib
import re
import os
import requests
import git

root = pathlib.Path(__file__).parent.resolve()

def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def get_tils():
    til_readme = "https://raw.githubusercontent.com/milaan9/TIL/master/README.md"
    r = requests.get(til_readme)

    page = requests.get(til_readme)
    all_text = page.text
    search_re = re.findall( r'(\*+).(\[.*?\])(\(.*?\)).?-(.+)', all_text, re.M|re.I)
    dt_til = sorted(search_re, key=lambda search_re: search_re[3], reverse=True)[:3]
    
    til_md = ""
    
    for i in dt_til:
        til_md += "\n" + i[0] + ' ' + i[1] + i[2]         
       
    return til_md

def fetch_blog_entries():
    entries = feedparser.parse("https://milaan9.github.io/blog/feed.xml")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]


if __name__ == "__main__":

    readme = root / "README.md"
    readme_contents = readme.open().read()
    
    entries = fetch_blog_entries()[:3]
    entries_md = "\n".join(
        # ["* [{title}]({url}) - {published}".format(**entry) for entry in entries]
        ["* [{title}]({url})".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(readme_contents, "blog", entries_md)

    til_readme_contents = get_tils()
    rewritten = replace_chunk(rewritten, "tils", til_readme_contents)    
    
    readme.open("w").write(rewritten)
