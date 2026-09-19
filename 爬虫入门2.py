import streamlit as st
st.title('简易爬虫')
st.write('这只是jin学习时用streamlit随便写的，别搞事情')

#用程序去模拟浏览器，输入一网址，获取资源
#ds老师莫名给改了一大串，我边加边改罢
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
#request请求。urlopen打开
url =st.text_input('输入网址吧')
#d老师说必须加一个触发按钮，防止输一个字母就开始跑
if st.button('开爬！'):
    if not url:
        st.warning("我chovy,输网址给我输好了啊!")
    else:
        try:#d老师说这是伪装
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            req = Request(url,headers=headers)

            #发起请求读取内容
            with urlopen(req) as res:
                html = res.read()

            try:
                content=html.decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                pure_text = soup.get_text()  # 这一行才是真正的“转文字”
            except UnicodeDecodeError:
                content=html.decode('gbk',errors='ignore')
                soup = BeautifulSoup(content, 'html.parser')
                pure_text = soup.get_text()  # 这一行才是真正的“转文字”

            st.success("成功")
            st.text_area("纯文字内容", pure_text, height=400)
        except Exception as e:
         st.error(f"失败,{e}")
