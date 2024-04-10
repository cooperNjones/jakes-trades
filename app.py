import os
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def generate_plot():
    if 'file' not in request.files:
        return "No file uploaded"
    
    file = request.files['file']
    if file.filename == '':
        return "Empty file"
    
    if not file.filename.endswith('.csv'):
        return "File is not a CSV"
    
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error reading CSV: {e}"
    
    grouped = df.groupby(['right', 'wrong'])
    instance_count = grouped.size().reset_index(name='count')
    fig = px.scatter(instance_count, x="wrong", y="right", size="count", color="count",
                     hover_name=instance_count.index, hover_data={'right': True, 'wrong': True, 'count': True})
    
    hover_text = []
    for idx, group in grouped:
        count = len(group)
        colors_info = ', '.join([f"{color} = {count}" for color, count in group['colors'].value_counts().items()])
        hover_text.append(f"Count: {count}<br>Colors: {colors_info}")
    
    fig.update_traces(hovertext=hover_text, hoverinfo='text')
    plot_html = fig.to_html(full_html=False)

    # Calculate the most popular point
    counts = df.groupby(['right', 'wrong']).size().reset_index(name='count')
    most_popular_combination = counts.loc[counts['count'].idxmax()]
    most_popular_point = {
        'right': most_popular_combination['right'],
        'wrong': most_popular_combination['wrong']
    }
    
    return render_template('plot.html', plot_html=plot_html, most_popular_point=most_popular_point)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
