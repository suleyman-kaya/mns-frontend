from flask import Flask, render_template, request
import pandas as pd
import plotly
import plotly.graph_objs as go
import json
from io import StringIO
from Tools import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # CSV dosyasını oku
    df = pd.read_csv('../data/data.csv')
    
    selected_laps = request.form.getlist('laps') if request.method == 'POST' else df['lap_lap'].unique().tolist()
    selected_laps = [int(lap) for lap in selected_laps]  # Convert to integers

    lap_data = process_lap_data(df)
    
    return render_template('index.html', 
                           laps=df['lap_lap'].unique().tolist(),
                           selected_laps=selected_laps,
                           energy_graph=create_energy_graph(df, selected_laps),
                           gps_speed_graph=create_gps_speed_graph(df, selected_laps),
                           battery_graph=create_battery_graph(df, selected_laps),
                           gps_map=create_gps_map(df, selected_laps),  # selected_laps ekledik
                           energy_heatmap=create_energy_heatmap(df, selected_laps),  # selected_laps ekledik
                           lap_data=json.dumps(lap_data))

if __name__ == '__main__':
    app.run(debug=True)