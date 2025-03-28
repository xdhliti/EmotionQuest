from flask import Flask, render_template_string, jsonify
import threading
import time
from WF_SDK import device, static, supplies

app = Flask(__name__)

# Variável global que armazena o padrão atual simulado (3 bits)
current_input = "001"  # Começa com "001"

# Conecta e configura o dispositivo Analog Discovery 2
device_name = "Analog Discovery 2"
device_data = device.open()
device.name = device_name

# Configura a fonte de alimentação para 3.3V
sup_data = supplies.data()
sup_data.master_state = True
sup_data.state = True
sup_data.voltage = 3.3
supplies.switch(device_data, sup_data)

# Configura os pinos digitais:
# Pinos 0, 1 e 2 como entrada (para leitura dos 3 bits)
for pin in range(0, 3):
    static.set_mode(device_data, pin, False)
    
# (Se necessário, configure outros pinos conforme seu setup; aqui não enviamos sinais para a FPGA)

# Função de simulação: alterna entre os padrões válidos
def poll_input_simulado():
    global current_input
    valid_patterns = ["001", "010", "011", "100"]
    index = 0
    while True:
        current_input = valid_patterns[index]
        index = (index + 1) % len(valid_patterns)
        time.sleep(0.5)

# Inicia a thread de simulação de leitura de entrada
threading.Thread(target=poll_input_simulado, daemon=True).start()

# Página HTML com exibição da imagem correspondente ao padrão recebido
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Teste Conexão Analog Discovery</title>
    <script>
        function updateInput() {
            fetch('/input')
            .then(response => response.json())
            .then(data => {
                var imgSrc = "";
                // Mapeia o padrão recebido para a imagem correspondente
                if (data.input === "001") {
                    imgSrc = "imagem1.jpeg";
                } else if (data.input === "010") {
                    imgSrc = "/static/imagem2.png";
                } else if (data.input === "011") {
                    imgSrc = "/static/imagem3.png";
                } else if (data.input === "100") {
                    imgSrc = "/static/imagem4.png";
                } else {
                    imgSrc = "";
                }
                document.getElementById('inputDisplay').src = imgSrc;
                document.getElementById('inputValue').innerText = data.input;
            });
        }
        setInterval(updateInput, 500);
    </script>
</head>
<body>
    <h1>Teste Conexão Analog Discovery</h1>
    <div style="text-align: center;">
        <h2>Padrão Simulado: <span id="inputValue">000</span></h2>
        <img id="inputDisplay" style="width:200px; height:auto;" alt="Imagem de entrada">
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_page)

# Endpoint que retorna o padrão atual (simulado)
@app.route('/input')
def get_input():
    return jsonify({'input': current_input})

if __name__ == '__main__':
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("Encerrado pelo usuário.")
    finally:
        # Procedimentos de finalização: encerra operações e desliga a fonte
        static.close(device_data)
        sup_data.master_state = False
        supplies.switch(device_data, sup_data)
        supplies.close(device_data)
        device.close(device_data)
