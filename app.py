import json
import os
from flask import Flask, render_template_string, jsonify
from threading import Thread
import time

app = Flask(__name__)
DATA_FILE = 'data.log'
latest_data = {"temperature": 0.0, "humidity": 0.0, "timestamp": time.time()}

def read_latest_data():
    global latest_data
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                if last_line.startswith("T:"):
                    parts = last_line.split(',')
                    temp_str = parts[0].split(':')[1]
                    humid_str = parts[1].split(':')[1]
                    
                    temperature = float(temp_str)
                    humidity = float(humid_str)
                    
                    latest_data = {
                        "temperature": temperature,
                        "humidity": humidity,
                        "timestamp": time.time()
                    }
                
    except FileNotFoundError:
        print(f"Error: {DATA_FILE} not found. Ensure RISC-V simulator is running.")
        

@app.route('/api/data')
def get_data():
    read_latest_data() 

    response = jsonify(latest_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RISC-V IoT 数据可视化 Demo</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
        <style>
            body { font-family: sans-serif; text-align: center; }
            .container { width: 80%; margin: auto; }
            h1 { color: #800000; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RISC-V 模拟温湿度数据实时监测</h1>
            <p>数据源自 QEMU 模拟运行的 RISC-V C 程序</p>
            <canvas id="tempChart"></canvas>
            <div id="latestData" style="margin-top: 20px; font-size: 1.2em;">
                最新数据: 温度 --°C, 湿度 --%
            </div>
        </div>

        <script>
            const MAX_POINTS = 20;
            const labels = [];
            const tempValues = [];
            const humidValues = [];

            const ctx = document.getElementById('tempChart').getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '温度 (°C)',
                        data: tempValues,
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1,
                        yAxisID: 'y'
                    }, {
                        label: '湿度 (%)',
                        data: humidValues,
                        borderColor: 'rgb(54, 162, 235)',
                        tension: 0.1,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: '温度 (°C)' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: { drawOnChartArea: false },
                            title: { display: true, text: '湿度 (%)' }
                        }
                    }
                }
            });

            function updateChart() {
                fetch('/api/data')
                    .then(response => response.json())
                    .then(data => {
                        const date = new Date(data.timestamp * 1000);
                        const timeLabel = date.toLocaleTimeString();
                        labels.push(timeLabel);
                        tempValues.push(data.temperature.toFixed(1));
                        humidValues.push(data.humidity.toFixed(1));
                        if (labels.length > MAX_POINTS) {
                            labels.shift();
                            tempValues.shift();
                            humidValues.shift();
                        }
                        
                        myChart.update();
                        document.getElementById('latestData').innerHTML = 
                            `最新数据: 温度 <b>${data.temperature.toFixed(1)}</b>°C, 湿度 <b>${data.humidity.toFixed(1)}</b>%`;

                    })
                    .catch(error => {
                        console.error('获取数据失败:', error);
                    });
            }
            setInterval(updateChart, 2000); 
            updateChart(); 
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    print("Flask 后端服务启动成功! 请点击 Codespaces 端口转发的链接访问.")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)