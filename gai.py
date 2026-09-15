import streamlit as st

st.title("改首字")

raw_name=st.text_input('enter your names')
lst=raw_name.split(',')

for i in range(len(lst)):#len是取长
    if lst[i] and lst[i][0]=='张':
        lst[i]="王"+lst[i][1:]

st.write(lst)

