import React, { useState } from "react";
import axios from "axios";
import ResultCard from "./components/ResultCard";
import styles from "./App.module.css";
import { toPng } from "html-to-image";
import { useRef } from "react";

type LipColorResult = {
  undertone: string;
  hex: string;
  average_lip_color: {
    r: number;
    g: number;
    b: number;
  };
  recommended_shades: {
    name: string;
    hex: string;
    image: string;
    link: string;
    confidence: number;
  }[];
};

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<LipColorResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resultRef = useRef<HTMLDivElement>(null);

  const handleDownload = () => {
    if (!resultRef.current) return;

    toPng(resultRef.current).then((dataUrl) => {
      const link = document.createElement("a");
      link.download = "matchmylip-result.png";
      link.href = dataUrl;
      link.click();
    });
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("image", selectedFile);

    setIsLoading(true);
    setResult(null);
    setError(null); // Clear previous error

    try {
      const response = await axios.post(
        "http://localhost:5000/api/recommend",
        formData
      );

      if (response.data.error) {
        setError(response.data.error); // Set backend error
      } else {
        setResult(response.data);
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.app}>
      <h1>💄 MatchMyLip</h1>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
      />
      <button onClick={handleUpload}>Analyze</button>

      {isLoading && <p className={styles.spinner}>Analyzing your lips... 💅</p>}
      {error && <p className={styles.error}>{error}</p>}

      {result && (
        <>
          <div className={styles.summary}>
            <p>
              <strong>Undertone:</strong> {result.undertone}
            </p>
            <p>
              <strong>Detected Lip Color:</strong>
              <span
                style={{
                  backgroundColor: result.hex,
                  color: "#fff",
                  padding: "2px 8px",
                  marginLeft: "8px",
                }}
              >
                {result.hex}
              </span>
            </p>
          </div>

          <div ref={resultRef}>
            <div className="summary">
              <p>
                <strong>Undertone:</strong> {result.undertone}
              </p>
              <p>
                <strong>Lip Color:</strong>{" "}
                <span style={{ backgroundColor: result.hex }}>
                  {result.hex}
                </span>
              </p>
            </div>
            <div className="recommendations">
              {result.recommended_shades.map((shade, index) => (
                <ResultCard key={index} shade={shade} />
              ))}
            </div>
          </div>
          <button onClick={handleDownload} className="download-btn">
            💾 Save Your Match
          </button>
        </>
      )}
    </div>
  );
}

export default App;
