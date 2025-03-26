from flask import Flask, render_template_string, jsonify
import threading
import time
from WF_SDK import device, static, supplies

app = Flask(__name__)

# Variáveis globais para manter o estado atual da leitura e da última saída enviada
current_input = "000"
last_output = "000"

# Conecta e configura o dispositivo
device_name = "Analog Discovery 2"
device_data = device.open()
device.name = device_name

# Configura a fonte de alimentação para 3.3V
sup_data = supplies.data()
sup_data.master_state = True
sup_data.state = True
sup_data.voltage = 3.3
supplies.switch(device_data, sup_data)

# PINO 0: Entrada 1 (bits para a imagem)
# PINO 1: Entrada 2 (bits para a imagem)
# PINO 2: Entrada 3 (bits para a imagem)
# PINO 3: NIVEL_SELECT (0: 3.3V, 1: 5V)
# PINO 4: INICIO (0: 3.3V, 1: 5V)
# PINO 5: RESET (0: 3.3V, 1: 5V)
# Configura os pinos:
# Pinos 0,1,2 como entrada
for pin in range(0, 6):
    static.set_mode(device_data, pin, False)
# Pinos 3,4,5 como saída
for pin in range(6, 8):
    static.set_mode(device_data, pin, True)

# Função que faz o polling contínuo dos pinos de entrada
def poll_input():
    global current_input
    while True:
        value = 0
        for i in range(3):
            # Supondo que static.get_state retorne um booleano
            if static.get_state(device_data, i):
                value |= (1 << i)
        current_input = format(value, '03b')
        time.sleep(0.01)  # Atualiza a cada 10ms

# Inicia a thread de polling
threading.Thread(target=poll_input, daemon=True).start()

# Página HTML com os botões e exibição da imagem correspondente ao valor de entrada
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Interface FPGA</title>
    <script>
        function sendPattern(pattern) {
            fetch('/send/' + pattern)
            .then(response => response.json())
            .then(data => {
                console.log("Padrão enviado: " + data.sent);
            });
        }
        function updateInput() {
            fetch('/input')
            .then(response => response.json())
            .then(data => {
                var imgSrc = "";
                // Mapeia o valor lido para a imagem correspondente
                if (data.input === "001") {
                    imgSrc = "imagem1.png";
                } else if (data.input === "010") {
                    imgSrc = "imagem2.png";
                } else if (data.input === "011") {
                    imgSrc = "imagem3.png";
                } else if (data.input === "100") {
                    imgSrc = "imagem4.png";
                } else {
                    // Caso não seja um padrão conhecido, limpa a imagem ou exibe uma padrão (placeholder)
                    imgSrc = "";
                }
                document.getElementById('inputDisplay').src = imgSrc;
            });
        }
        setInterval(updateInput, 200);
    </script>
</head>
<body>
    <h1>Interface FPGA</h1>
    <div>
        <button onclick="sendPattern('001')">001</button>
        <button onclick="sendPattern('010')">010</button>
        <button onclick="sendPattern('011')">011</button>
        <button onclick="sendPattern('100')">100</button>
    </div>
    <div style="margin-top: 20px; text-align: center;">
        <h2>Entrada da FPGA:</h2>
        <img id="inputDisplay" style="width:200px; height:auto;" alt="Imagem de entrada">
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_page)

# Endpoint para enviar um padrão de saída à FPGA
@app.route('/send/<pattern>')
def send(pattern):
    global last_output
    valid_patterns = ['001', '010', '011', '100']
    if pattern not in valid_patterns:
        return jsonify({'error': 'padrão inválido'}), 400
    value = int(pattern, 2)
    # Atualiza os pinos de saída (pinos 3,4,5)
    for i in range(3):
        bit = bool(value & (1 << i))
        static.set_state(device_data, i + 3, bit)
    last_output = pattern
    return jsonify({'sent': pattern})

# Endpoint para retornar o valor atual de entrada da FPGA
@app.route('/input')
def get_input():
    return jsonify({'input': current_input})

if __name__ == '__main__':
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("Encerrado pelo usuário.")
    finally:
        # Procedimentos de finalização: encerra I/O e desliga a fonte
        static.close(device_data)
        sup_data.master_state = False
        supplies.switch(device_data, sup_data)
        supplies.close(device_data)
        device.close(device_data)
