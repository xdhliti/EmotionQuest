import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [signals, setSignals] = useState({
    inicializar: "0",
    acertou: "0",
    imagem: "000",
    score: "0000",  // Valor em hexadecimal (ex: "0F")
    score_dec: "0", // Valor decimal (ex: 15)
    reset: "0"
  });

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('http://localhost:5000/input')
        .then(response => response.json())
        .then(data => setSignals(data))
        .catch(error => console.error('Erro ao buscar sinais:', error));
    }, 200);

    return () => clearInterval(interval);
  }, []);

  // Converte o score em hexadecimal para decimal
  //const scoreDecimal = parseInt(signals.score, 16);

  // Mapeia o código da imagem para o nome do arquivo
  const imageMap = {
    "001": "imagem1.png",
    "010": "imagem2.png",
    "011": "imagem3.png",
    "100": "imagem4.png"
  };

  // Referencia a imagem a partir do backend (assumindo que as imagens estão em /static do Flask)
  const imageSrc = `http://localhost:5000/static/${imageMap[signals.imagem] || 'placeholder.png'}`;

  return (
    <div className="game-container">
      <header className="game-header">
        <h1>EmotionQuest</h1>
      </header>

      <div className="game-info">
        <div className="info-card">
          <h2>Inicializar</h2>
          <p>{signals.inicializar === "1" ? "Sim" : "Não"}</p>
        </div>
        <div className="info-card">
          <h2>Acertou</h2>
          <p>{signals.acertou === "1" ? "Sim" : "Não"}</p>
        </div>
        <div className="info-card">
          <h2>Score</h2>
          {/* <p><span>{scoreDecimal}</span></p> */}
          <p><span>{signals.score_dec}</span></p>
        </div>
        <div className="info-card">
          <h2>Reset</h2>
          <p>{signals.reset === "1" ? "Sim" : "Não"}</p>
        </div>
      </div>

      <div className="game-display">
        <h2>Imagem</h2>
        <img src={imageSrc} alt="Advinhe a emoção com base na imagem!" />
      </div>

      <footer className="game-footer">
        <p>EmotionQuest - Advinhe a emoção!</p>
      </footer>
    </div>
  );
}

export default App;
