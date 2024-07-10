from flask import Flask, render_template, request
import pandas as pd
import plotly
import plotly.graph_objs as go
import json

app = Flask(__name__)

# CSV dosyasını oku
df = pd.read_csv('../data/data.csv')

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_laps = request.form.getlist('laps') if request.method == 'POST' else df['lap_lap'].unique().tolist()
    selected_laps = [int(lap) for lap in selected_laps]  # Convert to integers
    return render_template('index.html', 
                           laps=df['lap_lap'].unique().tolist(),
                           selected_laps=selected_laps,
                           energy_graph=create_energy_graph(selected_laps),
                           gps_speed_graph=create_gps_speed_graph(selected_laps),
                           battery_graph=create_battery_graph(selected_laps),
                           gps_map=create_gps_map(),
                           energy_heatmap=create_energy_heatmap())

def create_energy_graph(selected_laps):
    fig = go.Figure()
    
    for lap in selected_laps:
        lap_data = df[df['lap_lap'] == lap]
        cumulative_energy = lap_data['jm3_netjoule'].cumsum()
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist'],
            y=cumulative_energy,
            mode='lines',
            name=f'Lap {lap}'
        ))
    
    fig.update_layout(
        title='Cumulative Energy Consumption',
        xaxis_title='Lap Distance [m]',
        yaxis_title='Cumulative Energy [Joule]',
        height=600
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_gps_speed_graph(selected_laps):
    fig = go.Figure()
    
    for lap in selected_laps:
        lap_data = df[df['lap_lap'] == lap]
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist'],
            y=lap_data['gps_speed'],  # No conversion
            mode='lines',
            name=f'Lap {lap}'
        ))
    
    fig.update_layout(
        title='GPS Speed',
        xaxis_title='Lap Distance [m]',
        yaxis_title='Vehicle Speed [km/h]',
        height=600
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_battery_graph(selected_laps):
    fig = go.Figure()
    
    for lap in selected_laps:
        lap_data = df[df['lap_lap'] == lap]
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist'],
            y=lap_data['jm3_voltage'],
            mode='lines',
            name=f'Voltage Lap {lap}'
        ))
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist'],
            y=lap_data['jm3_current'],
            mode='lines',
            name=f'Current Lap {lap}'
        ))
    
    fig.update_layout(
        title='Battery Analysis',
        xaxis_title='Lap Distance [m]',
        yaxis_title='Value',
        height=600
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_gps_map():
    fig = go.Figure(go.Scattermapbox(
        lat=df['gps_latitude'],
        lon=df['gps_longitude'],
        mode='markers+lines',
        marker=go.scattermapbox.Marker(
            size=5,
            color=df['gps_speed'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Speed (km/h)")
        ),
        text=df['gps_speed'],  # m/s'den km/h'ye çevir
        hoverinfo='text'
    ))

    fig.update_layout(
        title='GPS Track',
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=df['gps_latitude'].mean(), lon=df['gps_longitude'].mean()),
            zoom=14
        ),
        height=600
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_energy_heatmap():
    energy_data = df['jm3_netjoule']
    min_energy = energy_data.min()
    max_energy = energy_data.max()
    
    # Create a custom colorscale
    colorscale = [
        [0, "blue"], [0.25, "cyan"],
        [0.5, "lime"], [0.75, "yellow"],
        [1, "red"]
    ]
    
    fig = go.Figure(go.Densitymapbox(
        lat=df['gps_latitude'],
        lon=df['gps_longitude'],
        z=energy_data,
        radius=10,
        colorscale=colorscale,
        zmin=min_energy,
        zmax=max_energy,
        colorbar=dict(title="Energy [Joule]")
    ))

    fig.update_layout(
        title='Energy Consumption Heatmap',
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=df['gps_latitude'].mean(), lon=df['gps_longitude'].mean()),
            zoom=14
        ),
        height=600
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

if __name__ == '__main__':
    app.run(debug=True)
