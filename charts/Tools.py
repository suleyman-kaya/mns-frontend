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
        width=970,
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
        width=970,
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
        width=970,
        height=600
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



def create_gps_map(df, selected_laps):
    fig = go.Figure()
    
    for i, lap in enumerate(selected_laps):
        lap_data = df[df['lap_lap'] == lap]
        fig.add_trace(go.Scattermapbox(
            lat=lap_data['gps_latitude'],
            lon=lap_data['gps_longitude'],
            mode='markers+lines',
            marker=go.scattermapbox.Marker(
                size=5,
                color=lap_data['gps_speed'],
                colorscale=[
                    [0, "yellow"], [0.25, "lime"],
                    [0.5, "cyan"], [0.75, "blue"],
                    [1, "purple"]
                ],
                showscale=True,
                colorbar=dict(title="Speed (km/h)")
            ),
            text=lap_data['gps_speed'],
            hoverinfo='text',
            name=f'Lap {lap}',
            visible=(i == 0)
        ))

    updatemenus = list([
        dict(active=0,
             buttons=list([
                dict(label=f'Lap {lap}',
                     method='update',
                     args=[{'visible': [i == j for j in range(len(selected_laps))]},
                           {'title': f'GPS Track - Lap {lap}'}]) for i, lap in enumerate(selected_laps)
             ]),
             direction="down",
             pad={"r": 10, "t": 10},
             showactive=True,
             x=0.0,  # Başlığın yanına taşımak için x değerini artırdık
             xanchor="left",
             y=1.12,  # Başlıkla aynı hizaya getirmek için y değerini artırdık
             yanchor="top"
        ),
    ])

    fig.update_layout(
        updatemenus=updatemenus,
        title={
            'text': "GPS Track",
            'y':0.95,
            'x':0.1,  # Başlığı sola kaydırdık
            'xanchor': 'center',
            'yanchor': 'top'
        },
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=df['gps_latitude'].mean(), lon=df['gps_longitude'].mean()),
            zoom=14
        ),
        width=970,
        height=600
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



def create_energy_heatmap(df, selected_laps):
    fig = go.Figure()
    
    for i, lap in enumerate(selected_laps):
        lap_data = df[df['lap_lap'] == lap]
        energy_data = lap_data['jm3_netjoule']
        
        fig.add_trace(go.Densitymapbox(
            lat=lap_data['gps_latitude'],
            lon=lap_data['gps_longitude'],
            z=energy_data,
            radius=10,
            colorscale=[
                [0, "blue"], [0.25, "cyan"],
                [0.5, "lime"], [0.75, "yellow"],
                [1, "red"]
            ],
            zmin=energy_data.min(),
            zmax=energy_data.max(),
            colorbar=dict(title="Energy [Joule]"),
            name=f'Lap {lap}',
            visible=(i == 0)
        ))

    updatemenus = list([
        dict(active=0,
             buttons=list([
                dict(label=f'Lap {lap}',
                     method='update',
                     args=[{'visible': [i == j for j in range(len(selected_laps))]},
                           {'title': f'Energy Consumption Heatmap - Lap {lap}'}]) for i, lap in enumerate(selected_laps)
             ]),
             direction="down",
             pad={"r": 10, "t": 10},
             showactive=True,
             x=0.0,  # Başlığın yanına taşımak için x değerini artırdık
             xanchor="left",
             y=1.12,  # Başlıkla aynı hizaya getirmek için y değerini artırdık
             yanchor="top"
        ),
    ])

    fig.update_layout(
        updatemenus=updatemenus,
        title={
            'text': "Energy Consumption Heatmap",
            'y':0.95,
            'x':0.2,  # Başlığı sola kaydırdık
            'xanchor': 'center',
            'yanchor': 'top'
        },
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=df['gps_latitude'].mean(), lon=df['gps_longitude'].mean()),
            zoom=14
        ),
        width=970,
        height=600
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)