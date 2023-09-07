"""
Created on Thu Sept 7 11:19 2023

@author: Martin
"""

#import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

#function definitions

#load data
df_raw = pd.read_csv(
    './data/metacritic_games_2023.csv',
    parse_dates=['release_date']
)
df_raw['release_date'] = pd.to_datetime(df_raw['release_date'], format='%b %d, %Y')
