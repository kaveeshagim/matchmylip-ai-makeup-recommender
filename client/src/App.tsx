import React, { useState } from "react";
import axios from "axios";
import ResultCard from "./components/ResultCard";
import styles from "./App.module.css";

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
  }[];
};

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<LipColorResult | null>(null);

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      const response = await axios.post(
        "http://localhost:5000/api/recommend",
        formData
      );
      console.log("Upload successful", response.data);
      setResult(response.data);
    } catch (error) {
      console.error("Upload failed", error);
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

          <div className={styles.recommendations}>
            {result.recommended_shades.map((shade, index) => (
              <ResultCard key={index} shade={shade} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
