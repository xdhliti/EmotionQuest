import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import loading from './assets/loading.gif';

function App() {
  const [signals, setSignals] = useState({
    inicializar: "0",
    acertou: "0",
    imagem: "0000",
    score: "0000",
    score_dec: "0",
    reset: "0",
    nivel: "0"
  });

  const [highlight, setHighlight] = useState({
    inicializar: false,
    acertou: false,
    score: false,
    reset: false
  });

  const prevScoreRef = useRef("0");

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('http://localhost:5000/input')
        .then(response => response.json())
        .then(data => {
          const newHighlight = { ...highlight };
          console.log('signals', signals);

          if (data.inicializar === "1" && data.reset === "0") {
            newHighlight.inicializar = true;
          } else {
            newHighlight.inicializar = false;
          }

          if (data.acertou === "1" && signals.acertou !== "1") {
            newHighlight.acertou = true;
            setTimeout(() => {
              setHighlight(prev => ({ ...prev, acertou: false }));
            }, 1000);
          }

          if (data.reset === "1" && signals.reset !== "1") {
            newHighlight.reset = true;
          } else {
            newHighlight.reset = false;
          }

          if (parseInt(data.score_dec) > parseInt(prevScoreRef.current)) {
            newHighlight.score = true;
            setTimeout(() => {
              setHighlight(prev => ({ ...prev, score: false }));
            }, 1000);
          }

          setSignals(data);
          prevScoreRef.current = data.score_dec;
          setHighlight(newHighlight);
        })
        .catch(error => console.error('Erro ao buscar sinais:', error));
    }, 200);

    return () => clearInterval(interval);
  }, [signals]);

  const matrizOpcoes = [
    ["feliz", "triste", "raiva", "confuso"],
    ["feliz", "triste", "raiva", "confuso"],
    ["feliz", "triste", "raiva", "confuso"],
    ["feliz", "triste", "raiva", "confuso"],
    ["feliz", "triste", "raiva", "confuso"],
    ["feliz", "triste", "raiva", "confuso"],
    ["feliz", "triste", "raiva", "confuso"],
  ];

  const imageMap = {
    "0000": "feliz.png",
    "0001": "triste.jpg",
    "0010": "raiva.jpg",
    "0011": "surpreso.jpg",
    "0100": "medo.jpg",
    "0101": "nojo.jpg",
    "0110": "desprezo.jpg",
    "0111": "duvida.jpg",
    "1000": "tedio.jpg",
    "1001": "interesse.jpg",
    "1010": "vergonha.jpg",
    "1011": "apaixonado.jpg",
    "1100": "cansado.jpg",
    "1101": "dor.jpg",
    "1110": "empolgacao.jpg",
  };

  const imageSrc = imageMap[signals.imagem] && signals.inicializar === "1"
    ? `http://localhost:5000/static/${imageMap[signals.imagem]}`
    : loading;

  const isLoading = imageMap[signals.imagem] ? false : true;
  const imgText = isLoading ? "Carregando..." : "Adivinhe a emoção da imagem!";

  return (
    <div className="game-container">
      <header className="game-header">
        <h1>EmotionQuest</h1>
      </header>

      <div className="game-info">
        <div className={`info-card ${highlight.inicializar ? 'highlight-green' : ''}`}>
          <h2>Jogar</h2>
        </div>
        <div className={`info-card ${highlight.acertou ? 'highlight-green' : ''}`}>
          <h2>Acertou</h2>
        </div>
        <div className={`info-card ${highlight.score ? 'highlight-green' : ''}`}>
          <h2>Score</h2>
          <p>{signals.score_dec}</p>
        </div>
        <div className={`info-card ${highlight.reset ? 'highlight-red' : ''}`}>
          <h2>Reset</h2>
        </div>
      </div>

      <div className="game-display">
        <h2>{imgText}</h2>
        <img src={imageSrc} alt="Advinhe a emoção com base na imagem!" />
      </div>

      {/* Adicionando os cards de opção abaixo da imagem */}
      <div className="options-container">
        {matrizOpcoes[0].map((opcao, index) => (
          <div key={index} className="option-card">
            <h3>{opcao}</h3>
          </div>
        ))}
      </div>

      <footer className="game-footer">
        <p>Desafie sua mente e divirta-se!</p>
      </footer>
    </div>
  );
}

export default App;
