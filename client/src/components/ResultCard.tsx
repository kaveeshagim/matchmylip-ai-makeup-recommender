import React from "react";
import "./ResultCard.css";

type Shade = {
  name: string;
  hex: string;
  image: string;
  link: string;
};

type Props = {
  shade: Shade;
};

const ResultCard: React.FC<Props> = ({ shade }) => {
  return (
    <div className="card">
      <img src={shade.image} alt={shade.name} />
      <h3>{shade.name}</h3>
      <p>
        Color: <span style={{ backgroundColor: shade.hex }}>{shade.hex}</span>
      </p>
      <a href={shade.link} target="_blank" rel="noopener noreferrer">
        Buy Now
      </a>
    </div>
  );
};

export default ResultCard;
