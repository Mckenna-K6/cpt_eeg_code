from flask import Flask, jsonify, render_template_string
from cortex import Cortex
import threading
import time

app = Flask(__name__)

EMOTIV_CLIENT_ID = ''
EMOTIV_CLIENT_SECRET = ''

attention_data = []  # List of (timestamp, attention_value)

class Subscribe:
    def __init__(self, app_client_id, app_client_secret):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=False)

        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(new_met_data=self.on_new_met_data)
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, streams=['met']):
        self.streams = streams
        self.c.open()

    def on_create_session_done(self, *args, **kwargs):
        print("Session created. Subscribing to streams...")
        self.c.sub_request(self.streams)

    def on_new_met_data(self, *args, **kwargs):
        global attention_data
        data = kwargs.get('data')
        timestamp = time.time()
        focus_value = data.get('foc')
        print(f"Focus: {focus_value}")
        if focus_value is not None:
            attention_data.append((timestamp, focus_value))

    def on_inform_error(self, *args, **kwargs):
        print("Error:", kwargs)

def run_emotiv():
    sub = Subscribe(EMOTIV_CLIENT_ID, EMOTIV_CLIENT_SECRET)
    sub.start()

# Start Emotiv in background
threading.Thread(target=run_emotiv, daemon=True).start()

@app.route('/')
def index():
    # HTML page with a chart
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attention Tracker</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h2>Real-Time Attention (Focus) Data</h2>
        <canvas id="focusChart" width="800" height="400"></canvas>
        <script>
            async function fetchData() {
                const response = await fetch('/data');
                const result = await response.json();
                return result;
            }

            async function renderChart() {
                const data = await fetchData();
                const ctx = document.getElementById('focusChart').getContext('2d');
                const chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.map(d => new Date(d[0] * 1000).toLocaleTimeString()),
                        datasets: [{
                            label: 'Attention (Focus)',
                            data: data.map(d => d[1]),
                            fill: false,
                            borderColor: 'blue',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                suggestedMin: 0,
                                suggestedMax: 1
                            }
                        }
                    }
                });
            }

            renderChart();
            setInterval(renderChart, 5000);  // Refresh every 5 seconds
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/data')
def data():
    return jsonify(attention_data)

if __name__ == '__main__':
    app.run(debug=True)
