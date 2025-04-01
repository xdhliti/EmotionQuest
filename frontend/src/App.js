import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import loading from './assets/loading.gif';

function App() {
  const [signals, setSignals] = useState({
    inicializar: "0",
    acertou: "0",
    imagem: "000",
    score: "0000",
    score_dec: "0",
    reset: "0"
  });



  const [highlight, setHighlight] = useState({
    inicializar: false,
    acertou: false,
    score: false,
    reset: false
  });

  const prevScoreRef = useRef("0");
  //const prevResetRef = useRef("1");

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
          //prevResetRef.current = data.reset;
          setHighlight(newHighlight);
        })
        .catch(error => console.error('Erro ao buscar sinais:', error));
    }, 200);
  
    return () => clearInterval(interval);
  }, [signals]);


  const imageMap = {
    "001": "feliz.png",
    "010": "imagem2.png",
    "011": "imagem3.png",
    "100": "imagem4.png"
  };

  const imageSrc = imageMap[signals.imagem]
    ? `http://localhost:5000/static/${imageMap["001"]}`
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

      <footer className="game-footer">
        <p>Desafie sua mente e divirta-se!</p>
      </footer>
    </div>
  );
}

export default App;
