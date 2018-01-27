#!/~/venvs/dash/bin/activate python
# usr/bin/env python
#
# @Author: Brian Austin <austinbrian>
# @Date:   2018-01-11T21:22:08-05:00
# @Email:  austin.brian@gmail.com
# @Filename: dashboard.py
# @Last modified: 2018-01-13T17:01:31-05:00
'''
Experiments with using dash (by plotly) to build dashboards from data.
Here, I'm going to import data from the sheriffs data_prep file.
'''
import data_prep # also imports pandas and numpy
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

df = data_prep.main()

app = dash.Dash()
server = app.server

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

markdown_text = ['''
## What is a detainer request
Sheriffs across the country receive requests from the Department of Homeland
Security, from Immigrations and Customs Enforcement (ICE) agents.''',
'''
## What does this graph show?
This graph demonstrates the surprising lack of a relationship between the
partisanship in a county and the actions of its chief law enforcement when
it comes to immigrants' rights.
''',
'''
## Where does this data come from?
This data is scraped from the University of Syracuse's [TRAC program]
(http://trac.syr.edu/phptools/immigration/detain/).
Until recently, ICE had complied with the university's Freedom of Information
Act requests. But now, under the Trump administration, ICE has refused to turn
over data on the way its agents are handling requests.
''',
'''
## What can I do to help?
ORGANIZATION NAME works in support of activists in local communities to targeting
sheriffs that are threatening local populations.

These sheriffs are harrassing
Hispanic populations, arresting undocumented people for minor driving infractions,
then alerting ICE to their presence. Enough is enough.

If you want to help end this unecessary abuse of a broken immigration system
[donate here](sanctuarysheriffs.us)
''']

app.layout = html.Div([
    html.H1(children='The Sheriffs Project',
            style={
                'textAlign':'center'}),
    dcc.Markdown(markdown_text[0]),
    dcc.Markdown(markdown_text[1]),
    dcc.Graph(
        id= 'detentions-vs-partisanship',
        figure = {
            'data':[
                go.Scatter(
                    x = df[df['state']==i]['pct_clinton'],
                    y = df[df['state']==i]['pct_ice'],
                    text = df[df['state']==i]['countyname'],
                    mode='markers',opacity=0.5,
                    marker={
                        'size':15,
                        'line': {'width':0.5,'color':'white'}
                    },
                    name =i
                ) for i in df.state.unique()
            ],
            'layout':go.Layout(
                xaxis={'title':'Percent of 2016 Votes for Clinton'},
                yaxis={'type':'linear',
                       'title': 'Proportion of ICE requests honored'},
                margin={'l':40,'b':40,'t':10,'r':10},
                legend={'x':0,'y':1},
                hovermode='closest'
            )
        }
    ),
    dcc.Markdown(markdown_text[2]),
    dcc.Markdown(markdown_text[3])
])

if __name__ == '__main__':
    app.run_server()
