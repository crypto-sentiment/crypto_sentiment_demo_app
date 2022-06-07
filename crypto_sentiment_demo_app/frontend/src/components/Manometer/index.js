import React from "react";
import styles from "./Manometer.module.scss";

function Manometer({sentIndex}) {
  const angle = sentIndex*1.8-90;
  var angle_string = "rotate(" + angle + " 1058.17 1083.32)";
  var left_color;
  var center_color;
  var right_color;
  if (sentIndex<=33){
    left_color="#75715c"
    center_color = "#ECEDEE"
    right_color = "#ECEDEE"
  } else if (sentIndex > 33 && sentIndex <= 66){
    left_color="#ECEDEE"
    center_color = "#E2C35F"
    right_color = "#ECEDEE"
  }else{
    left_color="#ECEDEE"
    center_color ="#ECEDEE"
    right_color = "#C17416"
  };

  return (
    <div className={styles.indexCard}>
      <h2 className="ml-20 mb-50">Crypto Sentiment Barometer</h2>
      <div className={styles.manometer}>
        <svg
          width="400"
          height="240"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 2116.34 1083.32"
        >
          <path
            d="M723.88 527.54l-203.88 -337.57c-305.4,182.71 -509.67,515.49 -509.57,895.67l383.61 -0.09c-0.06,-237.86 132.45,-445.75 329.84,-558.01z"
            fill={left_color}
          />
          <path
            d="M552.15 171.5l192 344.97c94.15,-49.34 201.94,-77.36 316.48,-77.39 113.38,-0.03 220.16,27.38 313.66,75.75l190.15 -346.07c-149.6,-81.42 -321.32,-127.7 -503.9,-127.65 -184.44,0.04 -357.76,47.35 -508.39,130.39z"
            fill={center_color}
          />
          <path
            d="M1598.69 188.24l-202.81 338.26c198.29,111.95 331.6,320.24 331.66,558.72l383.61 -0.09c-0.09,-381.2 -205.61,-714.64 -512.46,-896.89z"
            fill={right_color}
          />
        </svg>
        <img src="/img/man/back.svg" alt="back" />
        <svg
          width="400"
          height="240"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 2116.34 1083.32"
        >
          <path
            d="M1039.11 920.57l0 -480.84 21.68 -160.29 21.69 160.29 0 480.84 -43.37 0zm0 -240.42m10.84 -320.56m21.68 0m10.85 320.56m-21.69 240.42"
            fill="#2B2A29"
            transform={angle_string}
          />
        </svg>
      </div>
    </div>
  );
}

export default Manometer;
