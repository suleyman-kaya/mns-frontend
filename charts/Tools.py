import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import plotly
import json
import numpy as np

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


def create_energy_graph(df, selected_laps, x_multiplier=1, y_multiplier=1):
    fig = go.Figure()
    
    for lap in selected_laps:
        lap_data = df[df['lap_lap'] == lap]
        
        energy_change = lap_data['jm3_netjoule'].diff().fillna(0)
        
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist']*x_multiplier,
            y=energy_change*y_multiplier,
            mode='lines',
            name=f'Lap {lap}'
        ))
    
    fig.update_layout(
        title='Instantaneous Energy Consumption',
        xaxis_title='Lap Distance [m]',
        yaxis_title='Energy Change [Joule]',
        width=970,
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="linear"
        ),
        yaxis=dict(
            type="linear"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=[
                    dict(label="Linear Scale",
                         method="relayout",
                         args=[{"xaxis.type": "linear", "yaxis.type": "linear"}]),
                    dict(label="Log Scale",
                         method="relayout",
                         args=[{"xaxis.type": "log", "yaxis.type": "log"}]),
                ]
            )
        ]
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_gps_speed_graph(df, selected_laps, x_multiplier=1, y_multiplier=1):
    fig = go.Figure()
    
    for lap in selected_laps:
        lap_data = df[df['lap_lap'] == lap]
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist']*x_multiplier,
            y=lap_data['gps_speed']*y_multiplier,
            mode='lines',
            name=f'Lap {lap}'
        ))
    
    fig.update_layout(
        title='GPS Speed',
        xaxis_title='Lap Distance [m]',
        yaxis_title='Vehicle Speed [km/h]',
        width=970,
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="linear"
        ),
        yaxis=dict(
            type="linear"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=[
                    dict(label="Linear Scale",
                         method="relayout",
                         args=[{"xaxis.type": "linear", "yaxis.type": "linear"}]),
                    dict(label="Log Scale",
                         method="relayout",
                         args=[{"xaxis.type": "log", "yaxis.type": "log"}]),
                ]
            )
        ]
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_battery_graph(df, selected_laps, x_multiplier=1, y_multiplier=1):
    fig = go.Figure()
    
    for lap in selected_laps:
        lap_data = df[df['lap_lap'] == lap]
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist']*x_multiplier,
            y=lap_data['jm3_voltage']*y_multiplier,
            mode='lines',
            name=f'Voltage Lap {lap}'
        ))
        fig.add_trace(go.Scatter(
            x=lap_data['lap_dist']*x_multiplier,
            y=lap_data['jm3_current']*y_multiplier,
            mode='lines',
            name=f'Current Lap {lap}'
        ))
    
    fig.update_layout(
        title='Battery Analysis',
        xaxis_title='Lap Distance [m]',
        yaxis_title='Value',
        width=970,
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="linear"
        ),
        yaxis=dict(
            type="linear"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=[
                    dict(label="Linear Scale",
                         method="relayout",
                         args=[{"xaxis.type": "linear", "yaxis.type": "linear"}]),
                    dict(label="Log Scale",
                         method="relayout",
                         args=[{"xaxis.type": "log", "yaxis.type": "log"}]),
                ]
            )
        ]
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
                size=15,
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
             x=0.0,
             xanchor="left",
             y=1.16,
             yanchor="top"
        ),
        dict(
            buttons=list([
                dict(args=[{"mapbox.style": "open-street-map"}],
                     label="OpenStreetMap",
                     method="relayout"),
                dict(args=[{"mapbox.style": "carto-positron"}],
                     label="Carto Positron",
                     method="relayout"),
                dict(args=[{"mapbox.style": "carto-darkmatter"}],
                     label="Carto DarkMatter",
                     method="relayout")
            ]),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.0,
            xanchor="left",
            y=1.09,
            yanchor="top"
        ),
    ])

    fig.update_layout(
        updatemenus=updatemenus,
        title={
            'text': "GPS Track",
            'y':0.95,
            'x':0.5,
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

    # Add zoom controls
    fig.update_layout(
        mapbox_zoom=14,
        mapbox_center_lat=df['gps_latitude'].mean(),
        mapbox_center_lon=df['gps_longitude'].mean(),
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_energy_heatmap(df, selected_laps):
    fig = go.Figure()
    
    for i, lap in enumerate(selected_laps):
        lap_data = df[df['lap_lap'] == lap]
        
        energy_change = lap_data['jm3_netjoule'].diff()
        energy_change = energy_change.fillna(0)
        
        fig.add_trace(go.Scattermapbox(
            lat=lap_data['gps_latitude'],
            lon=lap_data['gps_longitude'],
            mode='markers+lines',
            marker=go.scattermapbox.Marker(
                size=15,
                color=energy_change,
                colorscale=px.colors.sequential.Hot[::-1],
                showscale=True,
                colorbar=dict(title="Energy Change")
            ),
            text=energy_change,
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
                           {'title': f'Energy Consumption Heatmap - Lap {lap}'}]) for i, lap in enumerate(selected_laps)
             ]),
             direction="down",
             pad={"r": 10, "t": 10},
             showactive=True,
             x=0.0,
             xanchor="left",
             y=1.16,
             yanchor="top"
        ),
        dict(
            buttons=list([
                dict(args=[{"mapbox.style": "open-street-map"}],
                     label="OpenStreetMap",
                     method="relayout"),
                dict(args=[{"mapbox.style": "carto-positron"}],
                     label="Carto Positron",
                     method="relayout"),
                dict(args=[{"mapbox.style": "carto-darkmatter"}],
                     label="Carto DarkMatter",
                     method="relayout")
            ]),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.0,
            xanchor="left",
            y=1.09,
            yanchor="top"
        ),
    ])

    fig.update_layout(
        updatemenus=updatemenus,
        title={
            'text': "Energy Consumption Heatmap",
            'y':0.95,
            'x':0.5,
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

    # Add zoom controls
    fig.update_layout(
        mapbox_zoom=14,
        mapbox_center_lat=df['gps_latitude'].mean(),
        mapbox_center_lon=df['gps_longitude'].mean(),
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_custom_chart(df, selected_laps, x_axis, y_axis, use_candlestick, x_multiplier=1, y_multiplier=1):
    fig = go.Figure()
    
    for lap in selected_laps:
        lap_data = df[df['lap_lap'] == lap]
        
        if use_candlestick:
            grouped_data = lap_data.groupby(x_axis)[y_axis].agg(['min', 'max', 'first', 'last']).reset_index()
            
            """
            Custom chart için, özellikle candlestick chart kullanımı söz konusu olduğunda, biraz farklı bir yaklaşım gerekiyor.
            Çünkü candlestick chart'ta open, high, low ve close değerleri var.
            Bu durumda, x ve y çarpanlarını ayrı ayrı uygulamak yerine, sadece y değerlerine uygulamamız daha mantıklı olacaktır.
            ama şimdilik kullanıcıya özgürlük tanımak için x'e de ekleyelim.
            """

            fig.add_trace(go.Candlestick(
                x=grouped_data[x_axis]*x_multiplier,
                open=grouped_data['first']*y_multiplier,
                high=grouped_data['max']*y_multiplier,
                low=grouped_data['min']*y_multiplier,
                close=grouped_data['last']*y_multiplier,
                name=f'Lap {lap} Candlestick'
            ))
            
            avg_data = lap_data.groupby(x_axis)[y_axis].mean().reset_index()
            fig.add_trace(go.Scatter(
                x=avg_data[x_axis],
                y=avg_data[y_axis],
                mode='lines',
                name=f'Lap {lap} Average',
                line=dict(color='rgba(255, 165, 0, 0.5)', width=2)
            ))
        else:
            fig.add_trace(go.Scatter(
                x=lap_data[x_axis]*x_multiplier,
                y=lap_data[y_axis]*y_multiplier,
                mode='lines',
                name=f'Lap {lap}'
            ))
    
    fig.update_layout(
        title=f'{y_axis} vs {x_axis}',
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        width=970,
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="linear"
        ),
        yaxis=dict(
            type="linear"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=[
                    dict(label="Linear Scale",
                         method="relayout",
                         args=[{"xaxis.type": "linear", "yaxis.type": "linear"}]),
                    dict(label="Log Scale",
                         method="relayout",
                         args=[{"xaxis.type": "log", "yaxis.type": "log"}]),
                ]
            )
        ]
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
