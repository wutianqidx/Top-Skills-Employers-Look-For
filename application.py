import dash
import base64
import dash_html_components as html
import dash.dependencies as dd
import dash_core_components as dcc
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from io import BytesIO

app = dash.Dash(__name__)

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Read in data
data_dir = 'data/Amazon_Total_Qualifications.txt'
data = pd.read_table(data_dir, sep = '\t')

# Dropdown options for Companys
available_companys = ['Amazon']

# Dropdown options for Jobs
available_jobs = [	'data-science', 'research-science', 'machine-learning-science',
					'business-intelligence', 'software-development']


app.layout = html.Div([
    html.H1('Top Skills Preferred for Your Career'),

    html.Br(),

    # Dropdown for Companys
    html.Div([  "Please select a Company:",
                dcc.Dropdown(
                id='companys-dropdown',
                options=[{'label': i, 'value': i} for i in available_companys],
                value='Amazon')], 
                style={ 'display': 'inline-block'}),

    html.Br(),
    html.Br(),

    # Dropdown for Jobs
    html.Div([	"Please select a job title:",
				dcc.Dropdown(
        		id='jobs-dropdown',
        		options=[{'label': i, 'value': i} for i in available_jobs],
        		value='business-intelligence')], 
				style={'width': '18%', 'display': 'inline-block'}),

    html.Br(),
    html.Br(),
    html.Br(),

    # WordCould
    html.P('WordCloud Generated:'),
	html.Img(id="image_wc"),

    html.Br(),
    html.Br(),
    html.Br(),

    # frequnency bar chart
    dcc.Graph(id='graph-freq')

])

def plot_wordcloud(data, selected_job):
    selected_data = data.loc[data.Category == selected_job].reset_index(drop=True)
    selected_data["All_Qualifications"] = selected_data.Basic_Qualifications + selected_data.Preferred_Qualifications
    selected_qualifications= ''.join(selected_data.All_Qualifications)
    my_stopwords = {'and', 'experience', 'e', 'g', 'in', 'a', 'years', 'of', 'with', 'ability', 'to',
                    'such', 'as', 'working', 'the', 'related', 'field' ,'or', 'work', 'for', 'using',
                    'etc', 'other', 'At', 'least', 'similar', 'equivalent', 's', 'on', 'M' ,'one', 'degree',
                    'knowledge', 'building', 'strong', 'skill', 'skills', 'relevant', 'advanced', 'R',
                    'demonstrated', 'tools', 'proficiency', 'environment', 'technical', 'engineering'}
    
    wc = WordCloud(background_color='white', min_font_size = 8, prefer_horizontal = 1, stopwords = my_stopwords)
    wc.generate(selected_qualifications)
    frequencies = wc.process_text(selected_qualifications)
    return wc.to_image(), frequencies

@app.callback(dd.Output('image_wc', 'src'), dd.Output('graph-freq', 'figure'), [dd.Input('jobs-dropdown', 'value')])
def make_image(selected_job):
    img = BytesIO()
    img_wc, frequencies = plot_wordcloud(data = data, selected_job = selected_job)
    img_wc.save(img, format='PNG')

    freq_table = pd.DataFrame(frequencies.items(), columns=['Skill', 'Frequency'])
    freq_table = freq_table.sort_values(by='Frequency', ascending=False).reset_index(drop=True)[:20][::-1]
    fig = px.bar(freq_table, x='Frequency', y='Skill', title='Top 20 Skills for ' + selected_job)
    fig.update_layout(yaxis= dict(dtick = 1))

    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode()), fig


application = app.server

if __name__ == '__main__':
    application.run(debug=True, port=8080)
