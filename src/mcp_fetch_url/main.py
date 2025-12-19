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
    try:
        # 定义常见的浏览器User-Agent（例如Chrome）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 发送请求，获取原始字节内容，带上User-Agent头
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查请求是否成功

        # 获取原始字节数据
        raw_content = response.content

        # 使用chardet检测编码
        detected = chardet.detect(raw_content)
        encoding = detected.get('encoding', 'utf-8')

        # 支持指定的编码：优先尝试detected编码，如果失败则逐一尝试GBK、GB2312、UTF-8
        decoded_content = None
        for enc in [encoding, 'gbk', 'gb2312', 'utf-8']:
            try:
                decoded_content = raw_content.decode(enc)
                break  # 成功解码，跳出循环
            except (UnicodeDecodeError, LookupError):
                continue

        if decoded_content is None:
            raise ValueError("无法解码响应内容为可读文本")

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(decoded_content, 'html.parser')

        # 移除所有<script>和<style>标签及其内容
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()

        # 移除所有HTML元素中的style属性
        for tag in soup.find_all(True):  # True匹配所有标签
            for tag_name in ['style', 'align', 'class', 'target', 'onclick', 'color', 'width', 'height']:
                if tag_name in tag.attrs:
                    del tag[tag_name]

        # 返回过滤后的HTML字符串
        filtered_html = str(soup)

        return filtered_html

    except requests.RequestException as e:
        raise ValueError(f"请求URL失败: {e}")
    except Exception as e:
        raise ValueError(f"处理内容时出错: {e}")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
    # print(fetch_url("https://blog.sqsl.art/personal-website-ways"))
    # print(fetch_url("http://www.yini.org/club/garden.html"))
    # print(fetch_url("http://ajiang.net/gb/main.asp?page=123&pagesize=10&keyword="))
