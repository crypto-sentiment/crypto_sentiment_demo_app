import React from "react";
import styles from "./Inference.module.scss";

function InferenceBar(props) {
  return (
    <div>
      <div className={styles.barObject}>
        <li>
          <div className={styles.progress}>
            <span
              className={styles.progressBar}
              style={{ width: `${props.positive * 100}%` }}
            ></span>
          </div>
          <p>positive</p>
        </li>
        <p>{Math.floor(props.positive * 100) / 100}</p>
      </div>
      <div className={styles.barObject}>
        <li>
          <div className={styles.progress}>
            <span
              className={styles.progressBar}
              style={{ width: `${props.neutral * 100}%` }}
            ></span>
          </div>
          <p>neutral</p>
        </li>
        <p>{Math.floor(props.neutral * 100) / 100}</p>
      </div>
      <div className={styles.barObject}>
        <li>
          <div className={styles.progress}>
            <span
              className={styles.progressBar}
              style={{ width: `${props.negative * 100}%` }}
            ></span>
          </div>
          <p>negative</p>
        </li>
        <p>{Math.floor(props.negative * 100) / 100}</p>
      </div>
    </div>
  );
}

export default InferenceBar;
