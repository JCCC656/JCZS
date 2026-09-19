import streamlit as st
import requests
import time
import random
import os
from urllib.parse import urlparse
from typing import Any

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) "
    "Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.baidu.com/",
    "https://www.bing.com/",
]

ACCEPT_LANGUAGES = [
    "zh-CN,zh;q=0.9,en;q=0.8",
    "en-US,en;q=0.9,zh-CN;q=0.8",
]
def build_headers(url: str, random_ua: bool = True, referer: bool = True) -> dict:
    parsed = urlparse(url)
    headers = {
        "Accept": "text/html,application/xhtml+xml,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Host": parsed.netloc,
    }
    if random_ua:
        headers["User-Agent"] = random.choice(USER_AGENTS)
    if referer:
        headers["Referer"] = random.choice(REFERERS)
    return headers


def random_delay(min_s: float = 1.0, max_s: float = 3.0) -> float:
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)
    return delay


def guess_extension(content_type: str, url: str) -> str:
    ct = content_type.lower()
    for key, ext in [
        ("image/jpeg", ".jpg"), ("image/png", ".png"),
        ("image/gif", ".gif"), ("image/webp", ".webp"),
        ("video/mp4", ".mp4"), ("video/webm", ".webm"),
        ("application/pdf", ".pdf"), ("application/json", ".json"),
        ("text/html", ".html"),
    ]:
        if key in ct:
            return ext
    _, ext = os.path.splitext(urlparse(url).path)
    return ext or ".bin"


def classify_content(content_type: str) -> str:
    ct = content_type.lower()
    if ct.startswith("text/") or any(k in ct for k in ("json", "xml", "javascript")):
        return "text"
    if ct.startswith("image/"):
        return "image"
    if ct.startswith("video/"):
        return "video"
    if ct.startswith("audio/"):
        return "audio"
    return "binary"
def fetch(url: str, random_ua: bool = True, referer: bool = True,
          delay: bool = True, use_proxy: bool = False,
          proxy: str = "", save_dir: str = "downloads") -> dict:
    headers = build_headers(url, random_ua, referer)
    proxies = {"http": proxy, "https": proxy} if use_proxy and proxy else None
    wait = random_delay() if delay else 0.0

    try:
        resp = requests.get(url, headers=headers, proxies=proxies,
                            timeout=30, allow_redirects=True, stream=True)
        content_type = resp.headers.get("Content-Type", "")
        kind = classify_content(content_type)

        result = {
            "ok": True, "status": resp.status_code, "delay": round(wait, 2),
            "headers_sent": headers, "response_headers": dict(resp.headers),
            "content_type": content_type, "kind": kind,
            "final_url": resp.url, "size_bytes": 0,
            "saved_path": None, "text": None, "bytes": None,
        }

        if kind == "text":
            resp.encoding = resp.encoding or resp.apparent_encoding
            result["text"] = resp.text
            result["size_bytes"] = len(resp.text.encode("utf-8", errors="ignore"))
            return result

        os.makedirs(save_dir, exist_ok=True)
        ext = guess_extension(content_type, resp.url)
        path = os.path.join(save_dir,
                            f"download_{int(time.time())}_{random.randint(1000, 9999)}{ext}")

        total = 0
        with open(path, "wb") as f:
            for chunk in resp.iter_content(1024 * 64):
                if chunk:
                    f.write(chunk)
                    total += len(chunk)

        result["size_bytes"] = total
        result["saved_path"] = path

        if total <= 20 * 1024 * 1024:
            with open(path, "rb") as f:
                result["bytes"] = f.read()
        return result

    except Exception as e:
        return {"ok": False, "error": str(e), "headers_sent": headers}
st.set_page_config(page_title="反爬虫伪装演示", page_icon="🕷️", layout="wide")
st.title("ds老师的爬虫")
st.caption("教学用途：演示爬虫伪装手段，可获取文字 / 图片 / 视频等")
st.warning("⚠️ 仅用于网络安全教学演示，请勿用于未授权爬取，别乱搞哦")

with st.sidebar:
    target = st.text_input("目标 URL", value="https://httpbin.org/headers")
    use_ua = st.checkbox("随机 User-Agent", value=True)
    use_ref = st.checkbox("随机 Referer", value=True)
    use_delay = st.checkbox("随机延时", value=True)
    use_proxy = st.checkbox("使用代理", value=False)
    proxy = st.text_input("代理地址", placeholder="http://127.0.0.1:7890")
    start = st.button("🚀 开始请求", type="primary")

if start:
    if not target.strip():
        st.error("请填写目标 URL")
        st.stop()

    with st.spinner("请求中..."):
        r = fetch(target.strip(), use_ua, use_ref, use_delay, use_proxy, proxy)

    if not r["ok"]:
        st.error(f"请求失败：{r.get('error')}")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("状态码", r["status"])
    c2.metric("类型", r["kind"])
    c3.metric("大小", f"{r['size_bytes']} B")
    c4.metric("延时", f"{r['delay']} s")
    st.caption(f"URL：{r['final_url']} ｜ Content-Type：{r['content_type']}")

    with st.expander("📤 请求头"):
        st.json(r["headers_sent"])
    with st.expander("📥 响应头"):
        st.json(r["response_headers"])

    st.divider()
    kind = r["kind"]

    if kind == "text":
        st.subheader("📝 文字内容")
        st.text_area("响应文本", r["text"], height=400)
    elif kind in ("image", "video", "audio"):
        label = {"image": "🖼️ 图片", "video": "🎬 视频", "audio": "🎵 音频"}[kind]
        st.subheader(f"{label}预览")
        if r["bytes"]:
            {"image": st.image, "video": st.video, "audio": st.audio}[kind](r["bytes"])
        else:
            st.info("文件过大，未加载预览，可直接下载。")
        if r["saved_path"]:
            st.success(f"已保存：{r['saved_path']}")
            with open(r["saved_path"], "rb") as f:
                st.download_button(f"⬇️ 下载{label}", f,
                                   file_name=os.path.basename(r["saved_path"]))
    else:
        st.subheader("📦 二进制内容")
        if r["saved_path"]:
            st.success(f"已保存：{r['saved_path']}")
            with open(r["saved_path"], "rb") as f:
                st.download_button("⬇️ 下载文件", f,
                                   file_name=os.path.basename(r["saved_path"]))
