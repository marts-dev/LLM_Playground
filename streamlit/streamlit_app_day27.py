import streamlit as st
import json
from pathlib import Path

from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo

st.set_page_config(layout='wide')

with st.sidebar:
  st.title("🗓️ #30DaysOfStreamlit")
  st.header("Day 27 - Streamlit Elements")
  st.write("Build a draggable and resizable dashboard with Streamlit Elements.")
  st.write("---")

  media_url = st.text_input("Media URL", value="https://www.youtube.com/watch?v=vIQQR_yq-8I")

# Initialize default data for code editor and chart.
#
# For this tutorial, we will need data for a Nivo Bump Chart.
# You can get random data there, in tab 'data': https"//nivo.rocks/bump/
#
# As you will see below, this session state item will be updated when our
# code editor change, and it will be read by Nivo Bump chart to draw the data.

if 'data' not in st.session_state:
  st.session_state.data = Path("data.json").read_text()

# Define a default dashboard layout.
# Dashboard grif has 12 columns by default.
#
# For more information on available parameters:
# https://github.com/react-grid-layout/react-grid-layout#grid-item-props

layout = [
  #Editor item is positioned in corrdinates x=0, y=0 and takes 6/12 columns and has a height of 3
  dashboard.Item("editor", 0, 0, 6, 3),
  #Chart item is positioned in coordinates x=6, y=0 and takes 6/12 columns and has a height of 3
  dashboard.Item("chart", 6, 0, 6, 3),
  #Media item is positioned in coordinates x=0, y=2 and takes 12/12 columns and has a height of 4
  dashboard.Item("media", 0, 2, 12, 4)
]

# Create a frame to displkay elements
with elements('demo'):
  # Create a dashboard with the layout specified above
  with dashboard.Grid(layout, draggableHandle=".draggable"):
    # First card, the code editor
    with mui.Card(key="editor", sx={"display": "flex", "flexDirection": "column"}):
      mui.CardHeader(title="Editor", className="draggable")
      with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
        # Here is our Monaco code editor.
        #
        # First, we set the default value to st.session_state.data that we initialized above.
        # Second, we define the language to use, JSON here.
        #
        # Then, we want to retrieve changes made to editor's content.
        # By checking Monaco documentation, there is an onChange property that takes a function.
        # This function is called everytime a change is made, and the updated content value is passed in
        # the first parameter (cf. onChange: https://github.com/suren-atoyan/monaco-react#props)
        #
        # Streamlit Elements provide a special sync() function. This function creates a callback that will
        # automatically forward its parameters to Streamlit's session state items.
        #
        # Examples
        # --------
        # Create a callback that forwards its first parameter to a session state item called "data":
        # >>> editor.Monaco(onChange=sync("data"))
        # >>> print(st.session_state.data)
        #
        # Create a callback that forwards its second parameter to a session state item called "ev":
        # >>> editor.Monaco(onChange=sync(None, "ev"))
        # >>> print(st.session_state.ev)
        #
        # Create a callback that forwards both of its parameters to session state:
        # >>> editor.Monaco(onChange=sync("data", "ev"))
        # >>> print(st.session_state.data)
        # >>> print(st.session_state.ev)
        #
        # Now, there is an issue: onChange is called everytime a change is made, which means everytime
        # you type a single character, your entire Streamlit app will rerun.
        #
        # To avoid this issue, you can tell Streamlit Elements to wait for another event to occur
        # (like a button click) to send the updated data, by wrapping your callback with lazy().
        #
        # For more information on available parameters for Monaco:
        # https://github.com/suren-atoyan/monaco-react
        # https://microsoft.github.io/monaco-editor/api/interfaces/monaco.editor.IStandaloneEditorConstructionOptions.html
        editor.Monaco(
          defaultValue=st.session_state.data,
          language="json",
          onChange=lazy(sync('data'))
        )
      
      with mui.CardActions:
        mui.Button("Apply changes", onClick=sync())
    # Second card, the Nivo Bump chart
    # We will use the same flexbox configuration as the first card to auto adjust the content height
    with mui.Card(key='chart', sx={'display': 'flex', 'flexDirection': 'column'}):
      mui.CardHeader(title='Chart', className='draggable')
      with mui.CardContent(sx={'flex': 1, 'minHeight': 0}):
        # This is where we will draw our Bump chart.
        #
        # For this exercise, we can just adapt Nivo's example and make it work with Streamlit Elements.
        # Nivo's example is available in the 'code' tab there: https://nivo.rocks/bump/
        #
        # Data takes a dictionary as parameter, so we need to convert our JSON data from a string to
        # a Python dictionary first, with `json.loads()`.
        #
        # For more information regarding other available Nivo charts:
        # https://nivo.rocks/
        nivo.Bump(
          data=json.loads(st.session_state.data),
          colors={'scheme': 'spectral'},
          lineWidth=3,
          activeLineWidth=6,
          inactiveLineWidth=3,
          inactiveOpacity=0.15,
          pointSize=10,
          activePointSize=16,
          inactivePointSize=0,
          pointColor={'theme': 'background'},
          pointBorderWidth=3,
          activePointBorderWidth=3,
          pointBorderColor={'from': 'serie.color'},
          axisTop={
            'tickSize': 5,
            'tickPadding': 5,
            'tickRotation': 0,
            'legend': '',
            'legendPosition': 'middle',
            'legendOffset': -36
          },
          axisBottom={
            'tickSize': 5,
            'tickPadding': 5,
            'tickRotation': 0,
            'legend': '',
            'legendPosition': 'middle',
            'legendOffset': 32
          },
          axisLeft={
            'tickSize': 5,
            'tickPadding': 5,
            'tickRotation': 0,
            'legend': 'ranking',
            'legendPosition': 'middle',
            'legendOffset': -40
          },
          margin={'top': 40, 'right': 100, 'bottom': 40, 'left': 60},
          axisRight=None,
        )
    
    # Third element of the dashboard, the Media player
    with mui.Card(key='media', sx={'display': 'flex', 'flexDirection': 'column'}):
      mui.CardHeader(title='Media Player', className='draggable')
      with mui.CardContent(sx={'flex': 1, 'minHeight': 0}):
        # This element is powered by ReactPlayer, it supports many more players other
        # than YouTube. You can check it out there: https://github.com/cookpete/react-player#props
        media.Player(url=media_url, width="100%", height="100%", controls=True)