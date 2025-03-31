from flask import Flask, jsonify
from flask_cors import CORS  # Permite acesso de origens diferentes
import threading
import time
from WF_SDK import device, static, supplies

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

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

# Configura os pinos 1 a 10 como entradas
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

# Endpoint que retorna os sinais atuais lidos
@app.route('/input')
def get_input():
    return jsonify(current_signals)

# Endpoint de status simples (opcional)
@app.route('/')
def index():
    return jsonify({"message": "Serviço backend rodando na porta 5000"})

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
