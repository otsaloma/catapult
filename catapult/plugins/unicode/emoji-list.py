#!/usr/bin/env python3

import bs4

from pathlib import Path

text = Path("emoji-list.html").read_text("utf-8")
soup = bs4.BeautifulSoup(text, "html.parser")
with open("emoji-list.txt", "w") as f:
    for tr in soup.select("table tr"):
        if code := tr.select("td.code"):
            code = code[0].text
            if len(tr.select("td.name")) == 2:
                name, terms = tr.select("td.name")
                name = name.text.upper()
                terms = terms.text.replace(" | ", "|")
                print((code, name, terms))
                f.write(f"{code};{name};{terms}\n")
