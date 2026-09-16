import streamlit as st

st.title('你怎么敢随便点别人的陌生链接的')

st.write("密码0729")

password=st.text_input('输入数密码喵')
if password=='0729':
 st.write('密码正确喵,倒计时5秒')
 for i in range(5):
  st.write(i+1)
 for i in range(99):
  st.write("v我50")
elif password!='':
 st.write('密码错误喵')
