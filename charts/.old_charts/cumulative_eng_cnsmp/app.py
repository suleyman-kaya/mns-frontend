from flask import Flask, render_template
import pandas as pd
import plotly
import plotly.graph_objs as go
import json

app = Flask(__name__)

# CSV dosyasını oku
df = pd.read_csv('../../../data/data.csv')

@app.route('/')
def index():
    fig = go.Figure()
    
    for lap in df['lap_lap'].unique():
        lap_data = df[df['lap_lap'] == lap]
        cumulative_energy = lap_data['jm3_netjoule'].cumsum()  # Cumulative energy calculation
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
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('index.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)
