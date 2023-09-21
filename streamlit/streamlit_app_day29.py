import streamlit as st
import pandas as pd
import requests

#Import for navbar
from streamlit_option_menu import option_menu

#Import dynamic tagging
from streamlit_tags import st_tags, st_tags_sidebar

#Imports for aggrid
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid import GridUpdateMode, DataReturnMode

#Import for loading interactive keyboard shortcuts into the app
from dashboard_utils.gui import keyboard_to_url
from dashboard_utils.gui import load_keyboard_class

if 'widen' not in st.session_state:
  layout = 'centered'
else:
  layout = 'wide' if st.session_state.widen else 'centered'

st.set_page_config(layout=layout, page_title='Zero-Shot Text Classifier', page_icon='🤗')

load_keyboard_class()

if not 'valid_inputs_received' in st.session_state:
  st.session_state['valid_inputs_received'] = False

col1, col2 = st.columns([0.4, 2])

with col1:
  st.image('.\logo.png', width=110)

with col2:
  st.caption('')
  st.title('Zero-Shot Text Classifier')

st.write('')

st.markdown(
  '''
Classify keyphrases fast and on-the-fly with this mighty app. No ML training needed!

Create classifying labels (e.g. `Positive`, `Negative` and `Neutral`), paste your keyphrases, and you're off!
'''
)
st.write('')
st.sidebar.write('')
############################################
# The code below is to display the menu bar
with st.sidebar:
  selected = option_menu(
    '',
    ['Demo (5 phrases max)', 'Unlocked Mode'],
    icons=['bi-joystick', 'bi-key-fill'],
    menu_icon='',
    default_index=1
  )
###########################################
# The code below is to display the shortcuts
st.sidebar.header('Shortcuts')
st.sidebar.write(
  '<span class="kbdx">G</span>  &nbsp; GitHub',
  unsafe_allow_html=True
)
st.sidebar.write(
  '<span class="kbdx">&thinsp;.&thinsp;</span>  &nbsp; GitHub Dev (VS Code)',
  unsafe_allow_html=True
)
st.sidebar.markdown('---')

st.sidebar.header('About')
st.sidebar.markdown(
  """
App created by [Datachaz](https://twitter.com/DataChaz) using 🎈[Streamlit](https://streamlit.io) and 🤗[HuggingFace](https://huggingface.co/inference-api)'s [Distilbart-mnli-12-3](https://huggingface.co/valhalla/distilbart-mnli-12-3) model.

"""
)

st.sidebar.markdown(
  "[Streamlit](https://streamlit.io) is a Python library that allows the creation of interactive, data-driven web applications in Python."
)

st.sidebar.header("Resources")
st.sidebar.markdown(
  """
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Cheat sheet](https://docs.streamlit.io/library/cheatsheet)
- [Book](https://www.amazon.com/dp/180056550X) (Getting Started with Streamlit for Data Science)
- [Blog](https://blog.streamlit.io/how-to-master-streamlit-for-data-science/) (How to master Streamlit for data science)
"""
)

st.sidebar.header('Deploy')
st.sidebar.markdown(
  "You can quickly deploy Streamlit apps using [Streamlit Cloud](https://streamlit.io/cloud) in just a few clicks."
)

def send_query(api_key, payload):
  def query(payload):
      response = requests.post(API_URL, headers=headers, json=payload)
      # For displaying the status code from API response
      # st.write(response.status_code)
      return response.json()
  API_KEY = api_key
  API_URL = (
    "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"
  )

  headers = {"Authorization": f"Bearer {API_KEY}"}
  return query(payload)

def is_form_input_valid(submitted, multiselectComponent, linesList, key):
  if not submitted and not st.session_state.valid_inputs_received:
    return False

  elif submitted and not key:
    st.warning("Please input your Hugging Face API key")
    st.session_state.valid_inputs_received = False
    return False

  elif submitted and not linesList:
    st.warning("There is no keyphrases to classify")
    st.session_state.valid_inputs_received = False
    return False

  elif submitted and not multiselectComponent:
    st.warning("You have not added any labels, please add some!")
    st.session_state.valid_inputs_received = False
    return False

  elif submitted and len(multiselectComponent) == 1:
    st.warning("Please make sure to add at least two labels for classification")
    st.session_state.valid_inputs_received = False
    return False
    
  elif submitted or st.session_state.valid_inputs_received:
    return True
  
def text_form(max_lines):
  multiselectComponent = st_tags(
    label='',
    text="Add labels - 3 max",
    value=["Transactional", "Informational", "Navigational"],
    suggestions=[
      "Navigational",
      "Transactional",
      "Informational",
      "Positive",
      "Negative",
      "Neutral",
    ],
    maxtags=3
  )

  new_line = "\n"
  phrases = [
    "I want to buy something in this store",
    "How to ask a question about a product",
    "Request a refund through the Google Play store",
    "I have a broken screen, what should I do?",
    "Can I have the link to the product?",
  ]
  sample = f"{new_line.join(map(str, phrases))}"

  MAX_LINES = max_lines
  text = st.text_area(
    "Enter keyphrases to classify",
    sample,
    height=200,
    key="2",
    help="At least two keyphrases for the classifier to work, one per line, "
    + str(MAX_LINES)
    + " keyphrases max as part of the demo"
  )
  lines = text.split("\n") # A list of lines
  linesList = []
  for x in lines:
    linesList.append(x)
  linesList = list(dict.fromkeys(linesList)) # Remove duplicates
  linesList = list(filter(None, linesList)) # Remove duplicates

  if len(linesList) > MAX_LINES:
    st.info(
      f"🚨 Only the first "
      + str(MAX_LINES)
      + "keyphrases will be reviewed. Unlock that limit by switching to 'Unlocked Mode'"
    )

  linesList = linesList[:MAX_LINES]

  return (multiselectComponent, linesList)

def main():
  st.caption('')

with st.form(key="my_form"):
  if selected != "Demo (5 phrases max)":
    API_KEY = st.text_input(
          "Enter your 🤗 HuggingFace API key",
          help="Once you created you HuggiginFace account, you can get your free API token in your settings page: https://huggingface.co/settings/tokens",
      )
  else:
    API_KEY = st.secrets['HUGGINGFACE_API_KEY']
  multiselectComponent, linesList = text_form(5)
  submit_button = st.form_submit_button(label="Submit")

if not is_form_input_valid(submit_button, multiselectComponent, len(linesList), API_KEY):
  st.stop()

else:
  try:
    if submit_button:
      st.session_state.valid_inputs_received = True
    
    listToAppend = []

    for row in linesList:
      output = send_query(
        API_KEY,
        {
          "inputs": row,
          "parameters": {"candidate_labels": multiselectComponent},
          "options": {"wait_for_model": True}
        }
      )
      listToAppend.append(output)
      #df = pd.DataFrame.from_dict(output)

    st.success('✅ Done!')

    df = pd.DataFrame.from_dict(listToAppend)

    st.caption("")
    st.markdown("### Check classifier results")
    st.caption("")

    st.checkbox(
      "Widen layout",
      key="widen",
      help="Tick this box to toggle the layout to 'Wide' mode"
    )

    st.caption("")
    # List comprehension to convert the decimals to percentages
    f = [[f"{x:.2%}" for x in row] for row in df["scores"]]
    df["classification scores"] = f
    df.drop('scores', inplace=True, axis=1)

    # This is to rename the column
    df.rename(columns={"sequence": "keyphrase"}, inplace=True)

    # The code below is for Ag-grid
    gb = GridOptionsBuilder.from_dataframe(df)
    # enables pivoting on all columns
    gb.configure_default_column(
      enablePivot=True, enablevalue=True, eneableRowGroup=True,
      groupable=True,
      #Show row group panel added in library file
    )
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_side_bar()
    gridOptions = gb.build()

    response = AgGrid(
      df,
      gridOptions=gridOptions,
      enable_enterprise_modules=True,
      update_mode=GridUpdateMode.MODEL_CHANGED,
      data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
      height=300,
      fit_columns_on_grid_load=False,
      configure_side_bar=True
    )

    col3, col4 = st.columns([2, 2])
    with col3:
      @st.cache_data
      def convert_df(df):
        # Important: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")
      
      csv = convert_df(df)

      st.download_button(
        label="Download results as CSV",
        data=csv,
        file_name="results.csv",
        mime="text/csv"
      )
  except ValueError as ve:
    st.warning("❄️ Add a valid HuggingFace API key in the text box above ☝️")
    st.stop()
