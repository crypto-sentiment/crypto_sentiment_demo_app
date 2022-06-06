import React from "react";


function IndexLine(props) {
    var circleColor;
    if (props.value<=33){
        circleColor="#75715C"
    }else if(props.value > 33 && props.value <= 66){
        circleColor="#E2C35F"
    }else{
        circleColor="#C17416"
    };
    var indexLabel;
    if (props.value<=33){
        indexLabel="Negative"
    }else if(props.value > 33 && props.value <= 66){
        indexLabel="Neutral"
    }else{
        indexLabel="Positive"
    };
  return (
    <div className="d-flex flex-row justify-between">
    <div className="ml-20">
      <p>{props.name}</p>
      <h3>{indexLabel}</h3>
    </div>
    <svg
      width={50}
      height={50}
      viewBox="0 0 24 24"
      xmlns="<http://www.w3.org/2000/svg>"
    >
      <circle cx="12" cy="12" r="12" fill={circleColor} />
      <text textAnchor="middle" x="12" y="16">
        <tspan>{props.value}</tspan>
      </text>
    </svg>
  </div>
  )}

  export default IndexLine;
