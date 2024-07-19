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

    x_multiplier = float(request.form.get('x_multiplier', 1))
    y_multiplier = float(request.form.get('y_multiplier', 1))

    lap_data = process_lap_data(df)
    
    # Kullanılabilir sütunların listesini al
    available_columns = df.columns.tolist()
    
    return render_template('index.html', 
                           laps=df['lap_lap'].unique().tolist(),
                           selected_laps=selected_laps,
                           energy_graph=create_energy_graph(df, selected_laps, x_multiplier, y_multiplier),
                           gps_speed_graph=create_gps_speed_graph(df, selected_laps, x_multiplier, y_multiplier),
                           battery_graph=create_battery_graph(df, selected_laps, x_multiplier, y_multiplier),
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
    x_multiplier = float(data['x_multiplier'])
    y_multiplier = float(data['y_multiplier'])
    
    df = pd.read_csv('../data/data.csv')
    
    chart = create_custom_chart(df, selected_laps, x_axis, y_axis, use_candlestick, x_multiplier, y_multiplier)
    
    return json.dumps(chart)


@app.route('/update_all_graphs', methods=['POST'])
def update_all_graphs():
    data = request.json
    try:
        x_multiplier = float(data.get('x_multiplier', 1))
        y_multiplier = float(data.get('y_multiplier', 1))
    except ValueError:
        return json.dumps({"error": "Invalid multiplier values"}), 400
    
    selected_laps = data['selected_laps']
    
    graphs = {
        'energy-plot': create_energy_graph(df, selected_laps, x_multiplier, y_multiplier),
        'gps-speed-plot': create_gps_speed_graph(df, selected_laps, x_multiplier, y_multiplier),
        'battery-plot': create_battery_graph(df, selected_laps, x_multiplier, y_multiplier)
        }
    
    return json.dumps(graphs)

if __name__ == '__main__':
    app.run(debug=True)