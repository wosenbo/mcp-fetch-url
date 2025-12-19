from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
import requests
import chardet
from bs4 import BeautifulSoup

mcp = FastMCP("Fetch URL Tool")


@mcp.tool()
def fetch_url(
    url: str = Field(..., description="url to fetch"),
):
    r = requests.get(url)
    r.raise_for_status()
    detected = chardet.detect(r.content)
    encoding = detected["encoding"]
    if encoding is None:
        encoding = "utf-8"
    else:
        encoding = encoding.lower()
        if encoding != "gbk" and encoding != "gb2312":
            encoding = "utf-8"
    r.encoding = encoding
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator="\n", strip=True)
    return text


def main():
    mcp.run()


if __name__ == "__main__":
    main()
    # print(fetch_url("https://blog.sqsl.art/personal-website-ways"))
    # print(fetch_url("http://www.yini.org/club/garden.html"))
    # print(fetch_url("http://ajiang.net/gb/main.asp?page=123&pagesize=10&keyword="))
