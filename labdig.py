from flask import Flask, render_template_string, jsonify
import threading
import time
from WF_SDK import device, static, supplies

app = Flask(__name__)

# Variável global para armazenar os sinais atuais lidos do dispositivo
current_signals = {
    "inicializar": "0",
    "acertou": "0",
    "imagem": "000",
    "score": "0000",   # 4 bits para score
    "score_dec": 0,
    "reset": "0"
}

# Conecta e configura o dispositivo
device_name = "Analog Discovery 2"
device_data = device.open()
device.name = device_name

# Configura a fonte de alimentação para 3.3V (caso necessário para o circuito)
sup_data = supplies.data()
sup_data.master_state = True
sup_data.state = True
sup_data.voltage = 3.3
supplies.switch(device_data, sup_data)

# Mapeamento dos pinos (sem utilizar o pino 0):
# Pino 1: inicializar (1 bit)
# Pino 2: acertou (1 bit)
# Pinos 3 a 5: imagem (3 bits)
# Pinos 6 a 9: score (4 bits)
# Pino 10: reset (1 bit)
# Configura os pinos 1 a 10 como entradas (o Analog Discovery 2 somente receberá dados)
for pin in range(1, 11):
    static.set_mode(device_data, pin, False)

# Função que faz o polling contínuo dos sinais de entrada
def poll_input():
    global current_signals
    while True:
        # Sinal de inicializar (pino 1)
        init_signal = 1 if static.get_state(device_data, 1) else 0
        # Sinal de acertou (pino 2)
        acertou_signal = 1 if static.get_state(device_data, 2) else 0

        # Sinal da imagem (3 bits: pinos 3, 4 e 5)
        imagem_val = 0
        for i in range(3, 6):
            if static.get_state(device_data, i):
                imagem_val |= (1 << (i - 3))
        imagem_str = format(imagem_val, '03b')

        # Sinal do score (4 bits: pinos 6, 7, 8 e 9)
        score_val = 0
        for i in range(6, 10):
            if static.get_state(device_data, i):
                score_val |= (1 << (i - 6))
        score_str = format(score_val, '04b')

        # Sinal de reset (pino 10)
        reset_signal = 1 if static.get_state(device_data, 10) else 0

        current_signals = {
            "inicializar": str(init_signal),
            "acertou": str(acertou_signal),
            "imagem": imagem_str,
            "score": score_str,
            "score_dec": score_val,
            "reset": str(reset_signal)
        }
        time.sleep(0.01)  # atualiza a cada 10ms

# Inicia a thread de polling dos sinais
threading.Thread(target=poll_input, daemon=True).start()

# Página HTML com uma interface para exibir os sinais recebidos
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Interface FPGA - Recebendo Sinais</title>
    <script>
        function updateInputs() {
            fetch('/input')
            .then(response => response.json())
            .then(data => {
                document.getElementById('inicializar').innerText = (data.inicializar === "1") ? "Sim" : "Não";
                document.getElementById('acertou').innerText = (data.acertou === "1") ? "Sim" : "Não";
                document.getElementById('score').innerText = data.score + " (decimal: " + data.score_dec + ")";
                document.getElementById('reset').innerText = (data.reset === "1") ? "Sim" : "Não";
                
                var imgSrc = "";
                // Mapeia o sinal da imagem para uma imagem específica
                if (data.imagem === "001") {
                    imgSrc = "/static/imagem1.png";
                } else if (data.imagem === "010") {
                    imgSrc = "/static/imagem2.png";
                } else if (data.imagem === "011") {
                    imgSrc = "/static/imagem3.png";
                } else if (data.imagem === "100") {
                    imgSrc = "/static/imagem4.png";
                } else {
                    imgSrc = "/static/placeholder.png";
                }
                document.getElementById('imagemDisplay').src = imgSrc;
            });
        }
        setInterval(updateInputs, 200);
    </script>
</head>
<body>
    <h1>Interface FPGA - Recebendo Sinais</h1>
    <div>
        <p><strong>Inicializar:</strong> <span id="inicializar">Não</span></p>
        <p><strong>Acertou:</strong> <span id="acertou">Não</span></p>
        <p><strong>Score:</strong> <span id="score">0000 (decimal: 0)</span></p>
        <p><strong>Reset:</strong> <span id="reset">Não</span></p>
    </div>
    <div style="margin-top:20px; text-align: center;">
        <h2>Imagem:</h2>
        <img id="imagemDisplay" src="/static/placeholder.png" style="width:200px; height:auto;" alt="Imagem recebida">
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_page)

# Endpoint que retorna os sinais atuais lidos
@app.route('/input')
def get_input():
    return jsonify(current_signals)

if __name__ == '__main__':
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("Encerrado pelo usuário.")
    finally:
        # Finaliza a comunicação com o dispositivo de forma segura
        static.close(device_data)
        sup_data.master_state = False
        supplies.switch(device_data, sup_data)
        supplies.close(device_data)
        device.close(device_data)
