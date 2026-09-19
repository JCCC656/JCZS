import streamlit as st
from urllib.request import urlopen, Request, build_opener, HTTPCookieProcessor
from urllib.error import URLError, HTTPError
from http.cookiejar import CookieJar
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import random
import time

st.title('简易爬虫 · 伪装增强版')
st.write('jin学习用，别搞事情')

# ================= 伪装资源池 =================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.baidu.com/",
    "https://www.bing.com/",
    "https://www.so.com/",
    "https://www.sogou.com/",
]

ACCEPT_LANGS = [
    "zh-CN,zh;q=0.9,en;q=0.8",
    "en-US,en;q=0.9,zh-CN;q=0.8",
    "zh-CN,zh;q=0.9",
]

CLIENT_HINTS = [
    ('"Chromium";v="131", "Not_A Brand";v="24", "Google Chrome";v="131"', "?0", '"Windows"'),
    ('"Chromium";v="130", "Not_A Brand";v="24", "Google Chrome";v="130"', "?0", '"macOS"'),
    ('"Not_A Brand";v="24", "Microsoft Edge";v="131", "Chromium";v="131"', "?0", '"Windows"'),
    ('"Firefox";v="133", "Not_A Brand";v="24"', "?0", '"Windows"'),
    ('"Chromium";v="131", "Not_A Brand";v="24", "Google Chrome";v="131"', "?1", '"Android"'),
    ('"Chromium";v="131", "Not_A Brand";v="24", "Google Chrome";v="131"', "?1", '"iOS"'),
]


def build_headers(url: str) -> dict:
    parsed = urlparse(url)
    ua = random.choice(USER_AGENTS)
    ch_ua, ch_mobile, ch_platform = random.choice(CLIENT_HINTS)

    headers = {
        "User-Agent": ua,
        "Referer": random.choice(REFERERS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGS),
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "sec-ch-ua": ch_ua,
        "sec-ch-ua-mobile": ch_mobile,
        "sec-ch-ua-platform": ch_platform,
        "Cache-Control": "max-age=0",
        "DNT": "1",
    }
    if parsed.netloc:
        headers["Host"] = parsed.netloc
    return headers


def human_delay():
    time.sleep(random.uniform(1.0, 3.0))


# ================= 界面 =================
url = st.text_input('输入网址吧')

with st.sidebar:
    st.header("伪装开关")
    use_random_ua = st.checkbox("User-Agent 随机池", value=True)
    use_referer = st.checkbox("Referer 伪装", value=True)
    use_delay = st.checkbox("随机延时 1~3 秒", value=True)
    use_cookie = st.checkbox("启用 Cookie 容器", value=True)

if st.button('开爬！'):
    if not url:
        st.warning("我chovy,输网址给我输好了啊!")
    else:
        try:
            headers = build_headers(url)
            if not use_random_ua:
                headers.pop("User-Agent", None)
            if not use_referer:
                headers.pop("Referer", None)

            if use_delay:
                with st.spinner(f"伪装延时中..."):
                    human_delay()

            req = Request(url, headers=headers)

            if use_cookie:
                opener = build_opener(HTTPCookieProcessor(CookieJar()))
                res = opener.open(req, timeout=15)
            else:
                res = urlopen(req, timeout=15)

            with res:
                html = res.read()
                status = res.status

            try:
                content = html.decode('utf-8')
            except UnicodeDecodeError:
                content = html.decode('gbk', errors='ignore')

            soup = BeautifulSoup(content, 'html.parser')
            pure_text = soup.get_text()

            st.success(f"成功 | 状态码 {status}")
            with st.expander("本次实际发送的请求头"):
                st.json(headers)
            st.text_area("纯文字内容", pure_text, height=400)

        except HTTPError as e:
            st.error(f"HTTP 错误：{e.code} {e.reason}")
        except URLError as e:
            st.error(f"网络错误：{e.reason}")
        except Exception as e:
            st.error(f"失败,{e}")
