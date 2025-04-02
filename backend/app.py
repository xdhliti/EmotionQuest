from flask import Flask, jsonify
from flask_cors import CORS  # Permite acesso de origens diferentes
import threading
import time
from WF_SDK import device, static, supplies
from WF_SDK.pattern import generate, function


app = Flask(__name__)
CORS(app) 

current_signals = {
    "inicializar": "0",
    "imagem": "000",
    "score": "0000",   # 4 bits para score
    "score_dec": 0,
    "reset": "0",
    "dificuldade": "0"
}

device_name = "Analog Discovery 2"
device_data = device.open()
device.name = device_name
sup_data = supplies.data()
sup_data.master_state = True
sup_data.state = True
sup_data.voltage = 3.3
supplies.switch(device_data, sup_data)

generate(device_data, 0, function.pulse, 1000, duty_cycle=50)

print("Dispositivo aberto com sucesso.")
# Configura os pinos 1 a 10 como entradas
for pin in range(1, 12):
    static.set_mode(device_data, pin, False)
import random

def poll_input():
    global current_signals
    last_print_time = time.time()
    print_interval = random.uniform(1, 2)  # define o intervalo inicial aleatório entre 1 e 2 segundos
    while True:
        # Sinal de inicializar (pino 1)
        init_signal = 1 if static.get_state(device_data, 1) else 0
        # Sinal de reset (pino 2)
        reset_signal = 1 if static.get_state(device_data, 2) else 0

        # Sinal da imagem (3 bits: pinos 3, 4, 5 e 6)
        imagem_val = 0
        current_time = time.time()
        if current_time - last_print_time >= print_interval:
            for i in range(3, 7):
                if static.get_state(device_data, i):
                    print(f"Pin {i} : 1")
                    imagem_val |= (1 << (i - 3))
                else:
                    print(f"Pin {i} : 0")
            last_print_time = current_time
            print_interval = random.uniform(1, 2)  # novo intervalo para a próxima impressão
        else:
            for i in range(3, 7):
                if static.get_state(device_data, i):
                    imagem_val |= (1 << (i - 3))

        imagem_str = format(imagem_val, '04b')

        # Sinal do score (4 bits: pinos 7, 8, 9 e 10)
        score_val = 0
        for i in range(7, 11):
            if static.get_state(device_data, i):
                score_val |= (1 << (i - 7))
        score_str = format(score_val, '04b')

        # Sinal de dificuldade (pino 11)
        dificuldade_signal = 1 if static.get_state(device_data, 11) else 0

        current_signals = {
            "inicializar": str(init_signal),
            "imagem": imagem_str,
            "score": score_str,
            "score_dec": score_val,
            "reset": str(reset_signal),
            "dificuldade": str(dificuldade_signal)
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
        static.close(device_data)
        sup_data.master_state = False
        supplies.switch(device_data, sup_data)
        supplies.close(device_data)
        device.close(device_data)
