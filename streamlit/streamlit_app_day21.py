import streamlit as st
import time

st.title('st.progress')

with st.expander('About this app'):
  st.write('You can now display the progress of your calculations in a Streamlit app with the `st.progress` command.')

my_bar = st.progress(0)

for precent_complete in range(100):
  time.sleep(0.05)
  my_bar.progress(precent_complete + 1)

st.balloons()