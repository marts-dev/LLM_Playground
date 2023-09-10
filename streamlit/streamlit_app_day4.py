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
def style_negative(v, props=''):
    """ Style negative values in dataframe """
    try:
        return props if v < 0 else None
    except:
        pass

def style_positive(v, props=''):
    """ Style positive values in dataframe """
    try:
        return props if v > 0 else None
    except:
        pass

def audience_simple(country):
    """ Show top represented countries """
    if country == 'US':
        return 'USA'
    elif country == 'IN':
        return 'India'
    else:
        return 'Other'

#load data
@st.cache_data
def load_data():
    df_raw = pd.read_csv(
        './data/Aggregated_Metrics_By_Video.csv'
    )
    
    df_raw.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                    'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                    'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']
    
    df_raw['Video publish time'] = pd.to_datetime(df_raw['Video publish time'], format='%b %d, %Y')
    df_raw['Average view duration'] = df_raw['Average view duration'].apply(lambda x: datetime.strptime(x, '%H:%M:%S'))
    df_raw['Avg_duration_sec'] = df_raw['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_raw['Engagement_ratio'] = (df_raw['Comments added'] + df_raw['Shares'] + df_raw['Dislikes'] + df_raw['Likes']) / df_raw.Views
    df_raw['Views / sub gained'] = df_raw['Views'] / df_raw['Subscribers gained']
    df_raw.sort_values('Video publish time', ascending=False, inplace=True)
    df_agg_sub = pd.read_csv('./data/Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    df_comments = pd.read_csv('./data/Aggregated_Metrics_By_Video.csv')
    df_time = pd.read_csv('./data/Video_Performance_Over_Time.csv', parse_dates=['Date'])
    df_time['Date'] = pd.to_datetime(df_time['Date'], format='%d %b %Y')
    return df_raw, df_agg_sub, df_comments, df_time

#Create dataframes
df_agg, df_agg_sub, df_comments, df_time = load_data()

#Engineer data
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months=12)
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median(numeric_only=True)

#create differences from the median for values
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:, numeric_cols] = (df_agg_diff.iloc[:, numeric_cols] - median_agg).div(median_agg)

#merge daily data with publish data to get delta
df_time_diff = pd.merge(df_time, df_agg.loc[:, ['Video', 'Video publish time']], left_on='External Video ID', right_on='Video')
df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days

#get last 12 months of data rather than all data
date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months=12)
df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo]

#get daily view data (first30), median & percentiles
views_days = pd.pivot_table(df_time_diff_yr, index='days_published', values='Views', aggfunc=[
    np.mean,
    np.median,
    lambda x: np.percentile(x, 80),
    lambda x: np.percentile(x, 20)
]).reset_index()
views_days.columns = ['days_published', 'mean_views', 'median_views', '80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0, 30)]
views_cumulative = views_days.loc[:, ['days_published', 'median_views', '80pct_views', '20pct_views']]
views_cumulative.loc[:,['median_views', '80pct_views', '20pct_views']] = views_cumulative.loc[:,['median_views', '80pct_views', '20pct_views']].cumsum()

####################################
# Streamlit interface related code #
####################################
#Build Dashboard
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics', 'Individual Video Analysis'))

## Aggregate metrics
if add_sidebar == 'Aggregate Metrics':
    st.write('Ken Jee YouTube Aggregated Data')

    df_agg_metrics = df_agg[[
        'Video publish time',
        'Views', 'Likes',
        'Subscribers',
        'Shares',
        'Comments added',
        'RPM(USD)',
        'Average % viewed',
        'Avg_duration_sec',
        'Engagement_ratio',
        'Views / sub gained'
    ]]
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months=6)
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months=12)
    metric_medians6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median(numeric_only=True)
    metric_medians12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median(numeric_only=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    count = 0
    for i in metric_medians6mo.index:
        with columns[count]:
            # To get the percent change over time
            delta = (metric_medians6mo[i] - metric_medians12mo[i])/metric_medians12mo[i]
            st.metric(label=i, value=round(metric_medians6mo[i], 1), delta=f"{delta:.2%}")
            count += 1
            if count >= 5:
                count = 0
    # get date information / trim to relevant data
    df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
    df_agg_diff_final = df_agg_diff.loc[:, [
        'Video title',
        'Publish_date',
        'Views',
        'Likes',
        'Subscribers',
        'Shares',
        'Comments added',
        'RPM(USD)',
        'Average % viewed',
        'Avg_duration_sec',
        'Engagement_ratio',
        'Views / sub gained'
    ]]

    df_agg_numeric_lst = df_agg_diff_final.median(numeric_only=True).index.tolist()
    df_to_pct = {}
    for i in df_agg_numeric_lst:
        df_to_pct[i] = '{:.1%}'.format

    st.dataframe(df_agg_diff_final.style.hide()
                .applymap(
                    style_negative,
                    props='color:red;'
                )
                .applymap(
                    style_positive,
                    props='color:green;'
                )
                .format(df_to_pct)
    )

if add_sidebar == 'Individual Video Analysis':
    videos = tuple(df_agg['Video title'])
    st.write('Individual Video Performance')
    video_select = st.selectbox('Pick a Video', videos)

    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code'].apply(audience_simple)
    agg_sub_filtered.sort_values('Is Subscribed', inplace=True)

    fig = px.bar(agg_sub_filtered, x = 'Views', y = 'Is Subscribed', color = 'Country', orientation='h')
    st.plotly_chart(fig)

    agg_time_filtered = df_time_diff[df_time_diff['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0, 30)]
    first_30 = first_30.sort_values('days_published')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=views_cumulative['days_published'],
        y=views_cumulative['20pct_views'],
        mode='lines',
        name='20th percentile',
        line=dict(color='purple', dash='dash')
        )
    )
    fig2.add_trace(go.Scatter(
        x=views_cumulative['days_published'],
        y=views_cumulative['median_views'],
        mode='lines',
        name='50th percentile',
        line=dict(color='black', dash='solid')
        )
    )
    fig2.add_trace(go.Scatter(
        x=views_cumulative['days_published'],
        y=views_cumulative['80pct_views'],
        mode='lines',
        name='80th percentile',
        line=dict(color='royalblue', dash='dash')
        )
    )
    fig2.add_trace(go.Scatter(
        x=first_30['days_published'],
        y=first_30['Views'].cumsum(),
        mode='lines',
        name='Current Video',
        line=dict(color='firebrick', width=8)
        )
    )

    fig2.update_layout(
        title='View comparison first 30 days',
        xaxis_title='Days Since Published',
        yaxis_title='Cumulative views'
    )

    st.plotly_chart(fig2)