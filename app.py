from dis import dis
import enum
from faulthandler import disable
from sysconfig import get_scheme_names
import streamlit as st
import pandas as pd
import numpy as np
import emoji, re
import json

@st.cache(allow_output_mutation=True)
def load_full_table():
    return pd.read_csv("full_table.csv")
@st.cache(allow_output_mutation=True)
def get_users(table):
    counts = table.groupby("Author")["Content"].count().sort_values(ascending=False).reset_index(level=0)
    print(type(counts))
    return counts
@st.cache(allow_output_mutation=True)
def find_all_words_all_users(table):
    users = table["Author"].unique()
    user_dict_dict = {}
    for u in users:
        user_dict_dict[u] = find_all_words(table, u)
    return user_dict_dict
@st.cache(allow_output_mutation=True)
def find_all_words(table, user):
    usronly = table[table["Author"] == user]["Content"]
    out = {}
    for w in usronly:
        if(type(w) != str):
            continue
        splitted = re.sub(emoji.get_emoji_regexp(), r"", w).replace("\n", "").split(" ")
        for wf in splitted:
            if wf.strip() == "":
                continue
            if wf in out:
                out[wf]["count"] += 1
            else:
                out[wf] = {}
                out[wf]["word"] = wf
                out[wf]["count"] = 1
    return out

def get_message_count(table, user):
    return table[table["Author"]==user]["Content"].values[0]
@st.cache(allow_output_mutation=True)
def search_all_words(inp_word, word_arr):
    char_vals = ["a","e","ı","i","o","ö","u","ü",""]
    word_possibilities = []
    wordlen = len(inp_word)
    for w in word_arr:
        current_index = 0
        found = True
        for c in w:
            if c in char_vals:
                continue
            if current_index >= wordlen:
                found = False
                break
            if c == inp_word[current_index]:
                current_index += 1
            else:
                found = False
                break
        if found and current_index >= wordlen:
            word_possibilities.append((w, word_arr[w]["count"]))
    return sorted(word_possibilities, key=lambda x:x[1], reverse=True)

if not "selected_some" in st.session_state:
    st.session_state["selected_some"] = False
if not "has_dict" in st.session_state:
    st.session_state["has_dict"] = False
testword = "ml ptl slk cn"
if "word" in st.session_state:
    testword = st.session_state["word"]
def on_changed_text():
    print("lna")
st.title("Discord Mesaj İnceleyici")
with st.spinner("Mesajlar yükleniyor..."):
    full_table = load_full_table()
with st.spinner("Yazar listesi oluşturuluyor"):
    users = get_users(full_table)
with st.expander("Kullanıcı Seçin", expanded=True):
    rb = st.radio("Kullanıcılar", users)
targetname = rb
info_state = st.caption("Seçilen kullanıcı: {}".format(targetname))
info_state_2 = st.caption("Mesaj sayısı: {}".format(get_message_count(users, targetname)))

bt = st.button("Kelimeleri Çıkart")
word_dict = None
if bt:
    st.session_state["selected_some"] = True
    with st.spinner("Yazar sözlüğü oluşturuluyor..."):
        word_dict = find_all_words(full_table, targetname)
    st.session_state["has_dict"] = True
    st.session_state["user"] = targetname
    st.caption("Kelime sayısı: {}".format(len(word_dict)))
if st.session_state["has_dict"] and st.session_state["user"] == targetname:
    word_dict = find_all_words(full_table, targetname)
    with st.expander("Çözümleme", expanded=True):
        target_wrd = st.text_input("Çözülecek öbeği giriniz:", value=testword)
        st.session_state["word"] = target_wrd
        submit_button = st.button(label='Çöz')
        if submit_button:
            if word_dict is None:
                st.error("Kullanıcı verisi çıkartılmadı!")
            else:
                words_to_search = target_wrd.split(" ")
                guess_list = []
                for w in words_to_search:
                    guess_list.append(search_all_words(w, word_dict))
                if len(guess_list) > 0:
                    st.header("Sonuçlar")
                    collist = st.columns(len(guess_list))
                    for i,col in enumerate(collist):
                        with col:
                            for word in guess_list[i]:
                                st.markdown(f"#### {word[0]}")