import React from "react";
import styles from "./Inference.module.scss";
import InferenceBar from "./InferenceBar";

function Inference(
//   {
//   inputValue,
//   setInputValue,
//   requestResult,
//   setRequestResult,
// }
) {
  const host = process.env.REACT_APP_HOST;
  const [inputValue, setInputValue] = React.useState("");
  const [requestResult, setRequestResult] = React.useState([]);
  const [isLoaded, setIsLoaded] = React.useState(false);


  const fetchData = (val) => {
    fetch(
      `${host}:8001/classify`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        mode: 'cors',
        body: JSON.stringify({ title: val })
      }
    )
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setRequestResult(json);
        setIsLoaded(true);
      });
  };
  console.log(requestResult);
  return (
    <div>
      <div className={styles.searchBlock}>
        <input
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          placeholder="Enter any news..."
        />
      </div>
      <button className={styles.button} onClick={() => fetchData(inputValue)}>
        Compute
      </button>
      {isLoaded && <InferenceBar
        negative={requestResult.Negative}
        neutral={requestResult.Neutral}
        positive={requestResult.Positive}
      />}
    </div>
  );
}

export default Inference;
