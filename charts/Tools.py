import pandas as pd
import plotly.graph_objs as go
import plotly
import json

# CSV dosyasını oku
df = pd.read_csv('../data/data.csv')

def process_lap_data(df):
    lap_data = []
    for lap in df['lap_lap'].unique():
        lap_df = df[df['lap_lap'] == lap]
        
        # Lap süresi hesaplama
        lap_time = lap_df['lap_obc_timestamp'].max() - lap_df['lap_obc_timestamp'].min()
        
        # Toplam mesafe hesaplama (son lap_dist değeri)
        distance = lap_df['lap_dist'].max()
        
        # Ortalama hız hesaplama (km/h)
        avg_speed = (distance / 1000) / (lap_time / 3600) if lap_time > 0 else 0
        
        # Maksimum hız (km/h)
        max_speed = lap_df['gps_speed'].max()
        
        # Kullanılan enerji (Joule)
        joules_used = lap_df['lap_jm3_netjoule'].max()

        lap_data.append({
            'lap_lap': int(lap),
            'time': round(lap_time, 1),
            'distance': round(distance, 1),
            'avg_speed': round(avg_speed, 1),
            'max_speed': round(max_speed, 1),
            'joules_used': int(joules_used)
        })
    
    return lap_data



def create_energy_graph(df, selected_laps):
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



def create_gps_speed_graph(df, selected_laps):
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



def create_battery_graph(df, selected_laps):
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



def create_gps_map(df):
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
        text=df['gps_speed'],
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



def create_energy_heatmap(df):
    energy_data = df['jm3_netjoule']
    min_energy = energy_data.min()
    max_energy = energy_data.max()
    
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