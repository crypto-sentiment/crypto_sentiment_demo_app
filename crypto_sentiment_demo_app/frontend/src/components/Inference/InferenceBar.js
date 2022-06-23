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
              style={{ width: `${props.positive * 100}%`, background: 'linear-gradient(90deg, #c17416, #bbac8d)' }}
            ></span>
          </div>
          <p>positive</p>
        </li>
        <p>{Math.round(props.positive * 1000)/10}</p>
      </div>
      <div className={styles.barObject}>
        <li>
          <div className={styles.progress}>
            <span
              className={styles.progressBar}
              style={{ width: `${props.neutral * 100}%`, background: 'linear-gradient(90deg, #E2C35F, #e0d19d)' }}
            ></span>
          </div>
          <p>neutral</p>
        </li>
        <p>{Math.round(props.neutral * 1000)/10}</p>
      </div>
      <div className={styles.barObject}>
        <li>
          <div className={styles.progress}>
            <span
              className={styles.progressBar}
              style={{ width: `${props.negative * 100}%`, background: 'linear-gradient(90deg, #75715C, #aca99b)' }}
            ></span>
          </div>
          <p>negative</p>
        </li>
        <p>{Math.round(props.negative * 1000)/10}</p>
      </div>
    </div>
  );
}

export default InferenceBar;
