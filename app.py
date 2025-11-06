import json
import os
from flask import Flask, render_template_string, jsonify
from threading import Thread
import time

app = Flask(__name__)

DATA_FILE = 'data.log'

# 存储最新的解析数据
latest_data = {"temperature": 0.0, "humidity": 0.0, "timestamp": time.time()}

# ----------------- 数据读取和解析逻辑 -----------------
def read_latest_data():
    """读取 data.log 文件的最后一行并解析温湿度数据"""
    global latest_data
    try:
        # 打开文件，从末尾开始读取以找到最新一行
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                
                # 示例数据格式: T:25.5,H:62.1
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
                    # 打印到控制台，方便调试
                    # print(f"Parsed data: {latest_data}") 
                
    except FileNotFoundError:
        print(f"Error: {DATA_FILE} not found. Ensure RISC-V simulator is running.")
        
# ----------------- Flask 路由 -----------------

# API 接口，供前端 AJAX 请求
@app.route('/api/data')
def get_data():
    """返回最新的温湿度数据"""
    # 确保在返回前读取一次最新数据
    read_latest_data() 
    
    # 设置 CORS 头部，确保前端可以访问
    response = jsonify(latest_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 根路由，返回前端 HTML 页面
@app.route('/')
def index():
    """返回包含 Chart.js 的前端页面"""
    
    # HTML 包含所有前端代码，不需要单独创建文件（简化 Demo）
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
            h1 { color: #800000; } /* RISC-V 颜色 */
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RISC-V 模拟温湿度数据实时监测</h1>
            <p>数据源自 QEMU 模拟运行的 RISC-V C 程序 (裸机环境)。</p>
            <canvas id="tempChart"></canvas>
            <div id="latestData" style="margin-top: 20px; font-size: 1.2em;">
                最新数据: 温度 --°C, 湿度 --%
            </div>
        </div>

        <script>
            // 图表配置和初始化
            const MAX_POINTS = 20; // 图表最多显示 20 个点
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

            // 定时获取数据并更新图表
            function updateChart() {
                // 请求 Flask API 接口
                fetch('/api/data')
                    .then(response => response.json())
                    .then(data => {
                        const date = new Date(data.timestamp * 1000);
                        const timeLabel = date.toLocaleTimeString();

                        // 更新图表数据
                        labels.push(timeLabel);
                        tempValues.push(data.temperature.toFixed(1));
                        humidValues.push(data.humidity.toFixed(1));

                        // 保持图表上点数不超过 MAX_POINTS
                        if (labels.length > MAX_POINTS) {
                            labels.shift();
                            tempValues.shift();
                            humidValues.shift();
                        }
                        
                        myChart.update();

                        // 更新最新数据文本
                        document.getElementById('latestData').innerHTML = 
                            `最新数据: 温度 <b>${data.temperature.toFixed(1)}</b>°C, 湿度 <b>${data.humidity.toFixed(1)}</b>%`;

                    })
                    .catch(error => {
                        console.error('获取数据失败:', error);
                    });
            }

            // 每 2 秒更新一次图表 (匹配 RISC-V 程序的采样间隔)
            setInterval(updateChart, 2000); 
            // 首次加载立即更新一次
            updateChart(); 
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    # 在 Codespaces 中，端口必须设置为 5000，且 host 必须是 '0.0.0.0'
    print("----------------------------------------------------------------")
    print("🚀 Flask 后端服务启动成功! 请点击 Codespaces 端口转发的链接访问.")
    print("----------------------------------------------------------------")
    # 自动重启功能，便于开发
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)