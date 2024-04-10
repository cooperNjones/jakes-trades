from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import openai
import os

app = Flask(__name__)

# Route for uploading CSV file
@app.route('/plot')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def generate_plot():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return "No file uploaded"
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return "Empty file"
    
    # Check if file is a CSV
    if not file.filename.endswith('.csv'):
        return "File is not a CSV"
    
    # Read the uploaded CSV file
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"Error reading CSV: {e}"
    
    # Group the DataFrame by "right" and "wrong" coordinates
    grouped = df.groupby(['right', 'wrong'])
    
    # Compute the count of instances for each plot point
    instance_count = grouped.size().reset_index(name='count')
    
    # Create the scatter plot with custom colors and sizes
    fig = px.scatter(instance_count, x="wrong", y="right", size="count", color="count",
                     hover_name=instance_count.index, hover_data={'right': True, 'wrong': True, 'count': True})
    
    # Add hover text showing count and colors for each point
    hover_text = []
    for idx, group in grouped:
        count = len(group)
        colors_info = ', '.join([f"{color} = {count}" for color, count in group['colors'].value_counts().items()])
        hover_text.append(f"Count: {count}<br>Colors: {colors_info}")
    
    fig.update_traces(hovertext=hover_text, hoverinfo='text')
    
    # Convert the plot to HTML
    plot_html = fig.to_html(full_html=False)
    
    # Render the plot page
    return render_template('plot.html', plot_html=plot_html)

if __name__ == '__main__':
    app.run(debug=True)
