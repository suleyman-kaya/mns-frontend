from flask import Flask, render_template, request
import pandas as pd
import plotly, json
import plotly.graph_objs as go
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
    
    # Kullanılabilir sütunların listesini al
    available_columns = df.columns.tolist()
    
    return render_template('index.html', 
                           laps=df['lap_lap'].unique().tolist(),
                           selected_laps=selected_laps,
                           energy_graph=create_energy_graph(df, selected_laps),
                           gps_speed_graph=create_gps_speed_graph(df, selected_laps),
                           battery_graph=create_battery_graph(df, selected_laps),
                           gps_map=create_gps_map(df, selected_laps),
                           energy_heatmap=create_energy_heatmap(df, selected_laps),
                           lap_data=json.dumps(lap_data),
                           available_columns=available_columns)

@app.route('/update_custom_chart', methods=['POST'])
def update_custom_chart():
    data = request.json
    x_axis = data['x_axis']
    y_axis = data['y_axis']
    selected_laps = data['selected_laps']
    use_candlestick = data['use_candlestick']
    
    df = pd.read_csv('../data/data.csv')
    
    chart = create_custom_chart(df, selected_laps, x_axis, y_axis, use_candlestick)
    
    return json.dumps(chart)

if __name__ == '__main__':
    app.run(debug=True)