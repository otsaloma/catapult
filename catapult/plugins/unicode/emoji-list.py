#!/usr/bin/env python3

import bs4

from pathlib import Path

text = Path("emoji-list.html").read_text("utf-8")
soup = bs4.BeautifulSoup(text, "html.parser")
with open("emoji-list.txt", "w") as f:
    for tr in soup.select("table tr"):
        if code := tr.select("td.code"):
            code = code[0].text
            if terms := tr.select("td.name:last-child"):
                terms = terms[0].text.replace(" | ", "|")
                f.write(f"{code};{terms}\n")
