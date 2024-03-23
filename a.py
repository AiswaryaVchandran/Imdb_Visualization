import pandas as pd

import plotly.graph_objs as go
import plotly.offline as pyo
import dash
#import dash_html_components as html
from dash import html
from dash import dcc

from dash.dependencies import Input, Output

a = pd.read_csv("imdb.csv")
df=pd.DataFrame(a)
# Cleaning the data to remove the null values
df.dropna(inplace=True)
#Data Precprocessing
df['Runtime'] = df['Runtime'].str.extract('(\d+)').astype(int)
df = df.drop(['Poster_Link', 'Overview', 'Star1', 'Star2', 'Star3', 'Star4'], axis=1)

#print(df)

# Create the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(style={'backgroundColor': '#b3cde0'}, children=[
    html.H1('IMDb MOVIES DASHBOARD',style={'text-decoration': 'underline'}),
    dcc.Dropdown(
        id='dropdown-genre',
        options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique()],
        
        placeholder='Select a genre'
    ),
     html.Div([
        html.Div([
            dcc.Graph(id='graph-top-rated-movies'),
        ], className='col-md-6', style={'display': 'inline-block', 'width': '49%'}),
        html.Div([
            dcc.Graph(id='graph-movie-genres'),
        ], className='col-md-6', style={'display': 'inline-block', 'width': '49%'}),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='graph-rating-vs-year'),
        ], className='col-md-6', style={'display': 'inline-block', 'width': '49%'}),
        html.Div([
            dcc.Graph(id='graph-rating-by-director'),
        ], className='col-md-6', style={'display': 'inline-block', 'width': '49%'}),
    ], className="row"),

        
         # Bar chart for gross revenue and rating
    dcc.Graph(id='graph-revenue-rating'),
  

   
])

# Define the callbacks
@app.callback(Output('graph-top-rated-movies', 'figure'),
              [Input('dropdown-genre', 'value')])
def update_top_rated_movies(genre):
    filtered_df = df[df['Genre'] == genre].sort_values(by='No_of_Votes', ascending=False).head(10)
    trace = go.Bar(x=filtered_df['Series_Title'], y=filtered_df['No_of_Votes'], name='Top Rated Movies',marker=dict(color='#8ecae6'))
    return {'data': [trace], 'layout': go.Layout(title=f'Top Rated {genre} Movies',paper_bgcolor='white',
                                                 
                                                 yaxis={'title': 'No.of votes'},margin={'b': 200})}

@app.callback(Output('graph-movie-genres', 'figure'),
              [Input('dropdown-genre', 'value')])
def update_movie_genres(genre):
    filtered_df = df[df['Genre'] == genre]
    counts = filtered_df['Certificate'].value_counts()
    trace = go.Pie(labels=counts.index, values=counts.values,
                   marker=dict(colors=['#011f4b', 'azure3', '#03396c', '#e0fbfc', '#219ebc']))
    return {'data': [trace], 'layout': go.Layout(title=f'Certificate given for {genre}',paper_bgcolor='white')}

@app.callback(Output('graph-rating-vs-year', 'figure'),
              [Input('dropdown-genre', 'value')])
def update_rating_vs_year(genre):
    filtered_df = df[df['Genre'] == genre]
    trace = go.Scatter(x=filtered_df['Series_Title'], y=filtered_df['Runtime'], mode='markers')
    return {'data': [trace], 'layout': go.Layout(title=f'Runtime for each movie under{genre}',
                                                 xaxis={ 'tickangle': 45},paper_bgcolor='white',
                                                 yaxis={'title': 'Runtime in min'},margin={'b': 200})}

@app.callback(Output('graph-rating-by-director', 'figure'),
              [Input('dropdown-genre', 'value')])
def update_rating_by_director(genre):
    filtered_df = df[df['Genre'] == genre]
    pivot_df = pd.pivot_table(filtered_df, values='No_of_Votes', index='Director', columns='Released_Year')
    trace = go.Heatmap(x=pivot_df.columns, y=pivot_df.index, z=pivot_df.values, colorscale='RdBu')
    return {'data': [trace], 'layout': go.Layout(title=f'Movie Rating by Director and Year for {genre}',
                                                 xaxis={'title': 'Year'},paper_bgcolor='white',
                                                 yaxis={'title': 'Director'},margin={'l': 150})}

@app.callback(
    dash.dependencies.Output('graph-revenue-rating', 'figure'),
    [dash.dependencies.Input('dropdown-genre', 'value')]
)
def update_revenue_rating(genre):
    filtered_df = df[df['Genre'] == genre]
    trace = go.Bar(
        x=filtered_df['Series_Title'],
        y=filtered_df['Gross'],
        name='Gross Revenue',
        marker=dict(color='#8ecae6')
    )
    trace2 = go.Scatter(
        x=filtered_df['Series_Title'],
        y=filtered_df['IMDB_Rating'],
        name='IMDB Rating',
        yaxis='y2',
        mode='markers',
        marker=dict(size=10, color='#023047', symbol='circle')
    )

    layout = go.Layout(
        title=f'Gross Revenue and Rating for {genre} Movies',
        yaxis=dict(
            title='Gross Revenue (in millions)',
            tickformat='$,.0f'
        ),
        yaxis2=dict(
            title='IMDB Rating',
            overlaying='y',
            side='right',
            range=[0, 10]
        ),
        margin=dict(l=150, r=20, t=50, b=150),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return {'data': [trace, trace2], 'layout': layout}





if __name__ == '__main__':
    app.run_server(debug=True)