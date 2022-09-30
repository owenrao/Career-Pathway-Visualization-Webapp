import json
import requests
import plotly.express as px
import plotly.graph_objects as go
import plotly
import pandas as pd
import numpy as np
from collections import defaultdict
from itertools import cycle

def plot_validation(func,x):
  try: result = func(x)
  except KeyError: return None
  return result

us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands": "VI" }

states_abbrev = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
            'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
            'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
            'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
            'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=go.layout.Margin(
        l=5, #left margin
        r=5, #right margin
        b=40, #bottom margin
        t=5, #top margin
    )
)

#get the occupation title, code, and mean annual income
def get_occ_title(title):
  
  firebase_url = 'https://dsci551project1-9a127-default-rtdb.firebaseio.com/.json?orderBy="occ_title"&equalTo="{}"'.format(title)
  response = requests.get(firebase_url)
  resp_json = response.json()

  if resp_json:
    return pd.DataFrame(resp_json).transpose()
  else:
    raise Exception('Occupational title not found in Firebase database.')

#function to convert the json firebase request json to a DataFrame (for plotting)
def fb_to_df(resp_json):

  return pd.DataFrame(resp_json).transpose()

#takes a dataframe and a year and plots a map of 
def plot_annual_income_map(df):

  occ_title = df['occ_title'][1]

  df['state'] = [us_state_to_abbrev[state] for state in list(df['area_title'])]

  years = list(df['year'].unique())

  #get list of states per year
  states = []
  for year in years:
    states.append(list(df[df['year'] == year]['state'].unique()))

  #get an (fast) intersection of all states across years
  if states:
    states_intersection = set.intersection(*map(set,states))
  else:
    raise Exception('Data missing state-level information.')

  #makes sure states are in "mappable" states (cont us, hawaii, alaska)
  states_intersection = list(set(states_intersection) & set(states_abbrev))
  
  means = []
  for state in states_intersection:
    means.append(df[df['state'] == state]['a_mean'].mean())

  data_dict = {'state':states_intersection, 'a_mean': means}
  plot_df = pd.DataFrame(data_dict)
    
  
  fig = go.Figure(data=go.Choropleth(
    locations=plot_df['state'], # Spatial coordinates
    z = plot_df['a_mean'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'matter',
    #text = df['hover_text'],
    colorbar_title = "USD",
  ))

  fig.update_layout(
    #title_text = 'Mean Annual Income for {} by State'.format(occ_title),
    geo_scope='usa', # limite map scope to USA
  )
  fig.update_layout(layout)
  
  #fig.show()
  
  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#takes occupational title and returns json dump of figure
def plot_hourly_income_map(df):

  occ_title = df['occ_title'][1]

  df['state'] = [us_state_to_abbrev[state] for state in list(df['area_title'])]

  years = list(df['year'].unique())

  #get list of states per year
  states = []
  for year in years:
    states.append(list(df[df['year'] == year]['state'].unique()))

  #get an (fast) intersection of all states across years
  if states:
    states_intersection = set.intersection(*map(set,states))
  else:
    raise Exception('Data missing state-level information.')

  #makes sure states are in "mappable" states (cont us, hawaii, alaska)
  states_intersection = list(set(states_intersection) & set(states_abbrev))
  
  means = []
  for state in states_intersection:
    means.append(df[df['state'] == state]['h_mean'].mean())

  data_dict = {'state':states_intersection, 'h_mean': means}
  plot_df = pd.DataFrame(data_dict)
    
  
  fig = go.Figure(data=go.Choropleth(
    locations=plot_df['state'], # Spatial coordinates
    z = plot_df['h_mean'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'matter',
    #text = df['hover_text'],
    colorbar_title = "USD",
  ))

  fig.update_layout(
    #title_text = 'Mean Hourly Income for {} by State'.format(occ_title),
    geo_scope='usa', # limite map scope to USA
  )
  fig.update_layout(layout)
  #fig.show()
  
  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#takes occupational title and returns json dump of figure
def plot_total_employment_map(df):

  occ_title = df['occ_title'][1]

  df['state'] = [us_state_to_abbrev[state] for state in list(df['area_title'])]

  years = list(df['year'].unique())

  #get list of states per year
  states = []
  for year in years:
    states.append(list(df[df['year'] == year]['state'].unique()))

  #get an (fast) intersection of all states across years
  if states:
    states_intersection = set.intersection(*map(set,states))
  else:
    raise Exception('Data missing state-level information.')

  #makes sure states are in "mappable" states (cont us, hawaii, alaska)
  states_intersection = list(set(states_intersection) & set(states_abbrev))
  
  means = []
  for state in states_intersection:
    means.append(df[df['state'] == state]['tot_emp'].mean())

  data_dict = {'state':states_intersection, 'tot_emp': means}
  plot_df = pd.DataFrame(data_dict)
    
  
  fig = go.Figure(data=go.Choropleth(
    locations=plot_df['state'], # Spatial coordinates
    z = plot_df['tot_emp'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'matter',
    #text = df['hover_text'],
    colorbar_title = "Number of People Employed",
  ))

  fig.update_layout(
    #title_text = 'Total Employment for {} by State'.format(occ_title),
    geo_scope='usa', # limite map scope to USA
  )
  fig.update_layout(layout)
  
  #fig.show()
  
  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#takes occupational title and returns json dump of figure
def plot_employment_per_1000_map(df):

  occ_title = df['occ_title'][1]

  df['state'] = [us_state_to_abbrev[state] for state in list(df['area_title'])]

  years = list(df['year'].unique())

  #get list of states per year
  states = []
  for year in years:
    states.append(list(df[df['year'] == year]['state'].unique()))

  #get an (fast) intersection of all states across years
  if states:
    states_intersection = set.intersection(*map(set,states))
  else:
    raise Exception('Data missing state-level information.')

  #makes sure states are in "mappable" states (cont us, hawaii, alaska)
  states_intersection = list(set(states_intersection) & set(states_abbrev))
  
  means = []
  for state in states_intersection:
    means.append(df[df['state'] == state]['jobs_1000'].mean())

  data_dict = {'state':states_intersection, 'jobs_1000': means}
  plot_df = pd.DataFrame(data_dict)
    
  
  fig = go.Figure(data=go.Choropleth(
    locations=plot_df['state'], # Spatial coordinates
    z = plot_df['jobs_1000'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'matter',
    #text = df['hover_text'],
    colorbar_title = "Emp per 1k Jobs"
  ))

  fig.update_layout(
    #title_text = 'Employment per 1000 Jobs for {} by State'.format(occ_title),
    geo_scope='usa', # limite map scope to USA
  )
  fig.update_layout(layout)
  
  #fig.show()
  
  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

"""
Function that takes an occ title and returns aggregated (mean) information across states & years of the form:
{'occ_title' :  title,
  'a_mean': value,
  'h_mean' : value,
  'tot_emp': value,
  'jobs_1000' : value,
  'educational_requirement' : value}
"""

def get_occ_info(df):

  occ_title = df['occ_title'][1]
  
  info_dict = {}

  info_dict['occ_title'] = occ_title
  for col in ['a_mean','h_mean','tot_emp','jobs_1000']:
    try: info_dict[col] = round(float(df[col].mean()),2)
    except: info_dict[col] = None
  info_dict['educational_requirement'] = str(df['educational requirement'].value_counts().index[0]) #this takes the mode if there are multiple

  return info_dict


def plot_annual_income_change_line(df):

  occ_title = df['occ_title'][1]

  years = list(df['year'].unique())
  a_means = []

  for year in years:
    a_means.append(df[df['year'] == year]['a_mean'].mean())

  years = [str(year) for year in years]

  fig = go.Figure()
  fig.add_trace(go.Scatter(x=years, y=a_means,
                    mode='lines+markers',
                    name='lines+markers'))
  

  fig.update_layout(
    #title='Annual Mean Income Changes for {}'.format(occ_title),
    xaxis_title="Year",
    xaxis_tickfont_size=14,
    yaxis=dict(
      title='Mean Annual Income',
      titlefont_size=16,
      tickfont_size=14,
    )
  )
  fig.update_layout(layout)
    
  #fig.show()
  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def plot_tot_emp_change_bar(df):

  occ_title = df['occ_title'][1]
  years = list(df['year'].unique())

  tot_emp = []

  for year in years:
    tot_emp.append(df[df['year'] == year]['tot_emp'].sum())

  years = [str(year) for year in years]

  fig = go.Figure()
  fig.add_trace(go.Bar(x=years, y=tot_emp))
  

  fig.update_layout(
    #title='Yearly Total Number of {} Employed'.format(occ_title),
    xaxis_title="Year",
    xaxis_tickfont_size=14,
    yaxis=dict(
      title='Number of People Employed',
      titlefont_size=16,
      tickfont_size=14,
    )
  )
  fig.update_layout(layout)
    
  
  #fig.show()

  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


#takes json data from a specific prefession and plots the hourly and annual income percentiles
def plot_annual_percentiles(df):

  occ_title = df['occ_title'][1]

  years = list(df['year'].unique())
  percentiles = ['a_pct10', 'a_pct25', 'a_pct75', 'a_pct90']
  pct_readable = ['10th', '25th', '75th', '90th']
  means = []
  palette = cycle(px.colors.qualitative.Plotly)

  year_dfs = []
  for year in years:
    year_dfs.append(df[df['year'] == year])


  for year_df in year_dfs:
    means.append(list(round(year_df[percentiles].mean(),4)))

  fig = go.Figure()

  for i, year in enumerate(years):
    fig.add_trace(go.Bar(x=pct_readable,
                  y=means[i],
                  name=year,
                  marker_color=next(palette)
                  ))


  fig.update_layout(
    #title='Annual Income Percentile Changes for {}'.format(occ_title),
    xaxis_title="Income Percentile",
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='USD',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
  )
  fig.update_layout(layout)
  #fig.show()

  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def plot_income_distribution_bar(df):

  occ_title = df['occ_title'][1]

  min = df['a_mean'].min()
  max = df['a_mean'].max()
  interval = (max - min)/10

  ranges = np.arange(min, max + interval, interval)

  counts = list(df.groupby(pd.cut(df.a_mean, ranges)).count()['a_mean'])

  fig = go.Figure()
  fig.add_trace(go.Bar(x=ranges,
                  y=counts,
                  marker=dict(
                      color=ranges,
                      colorbar=dict(
                          title="Colorbar"
        ),
        colorscale="Matter"
      )
    )
  )
  
  fig.update_layout(
  #title='Income Distribution for {}'.format(occ_title),
  xaxis_title="Income Bracket",
  xaxis_tickfont_size=14,
  yaxis=dict(
      title='Values (States) Per Income Bracket',
      titlefont_size=16,
      tickfont_size=14,
  ),

  legend=dict(
      x=0,
      y=1.0,
      bgcolor='rgba(255, 255, 255, 0)',
      bordercolor='rgba(255, 255, 255, 0)'
  ),
  barmode='group',
  bargap=0.15, # gap between bars of adjacent location coordinates.
  bargroupgap=0.1 # gap between bars of the same location coordinate.
  )
  fig.update_layout(layout)

  #fig.show()

  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def plot_data(data):
    locations = [us_state_to_abbrev[location['area_title']] for location in data.values()]
  
    data_vals = defaultdict(list)

    for value in data.values():
        data_vals['state'].append(us_state_to_abbrev[value['area_title']])
        data_vals['Mean Annual Income'].append(value['a_mean'])

    df = pd.DataFrame(data_vals)

    fig = go.Figure(data=go.Choropleth(
        locations=df['state'], # Spatial coordinates
        z = df['Mean Annual Income'].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "USD",
    ),layout=layout)

    fig.update_layout(
        #title_text = '2019-2020 Mean Annual Income by State',
        geo_scope='usa', # limite map scope to USA
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)