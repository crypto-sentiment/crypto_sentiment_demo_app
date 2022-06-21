import React from "react";
import styles from "./Inference.module.scss";
import InferenceBar from "./InferenceBar";

function Inference({
  inputValue,
  setInputValue,
  requestResult,
  setRequestResult,
}) {
  const host = process.env.REACT_APP_HOST;
  const fetchData = (val) => {
    fetch(
      `${host}:8001/classify?` +
        new URLSearchParams({
          title: val,
        }),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Origin": `${host}:8000`,
        },
        mode:'cors',
      }
    )
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setRequestResult(json);
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
      {requestResult.map((obj) => (
        <InferenceBar
          negative={obj.Negative}
          neutral={obj.Neutral}
          positive={obj.Positive}
        />
      ))}

    </div>
  );
}

export default Inference;
