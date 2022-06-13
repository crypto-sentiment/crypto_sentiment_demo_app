import React from "react";
import styles from "./HistoricalValues.module.scss";
import IndexLine from "./IndexLine";

function HistoricalValues(props) {
  const indexesForPeriods =
  [
    {"name":"Previous close","value":Math.round(100 * props.yesteyday_value)},
    {"name":"1 week ago","value":Math.round(100 * props.last_week_value)},
    {"name":"1 month ago","value":Math.round(100 * props.last_month_value) }
  ];

  return (
    <div className={styles.indexCard}>
      <h2 className="ml-20">Historical Values</h2>
      {indexesForPeriods.map((obj) => (
          <IndexLine name={obj.name} value={obj.value} />
        ))}
    </div>
  );
}

export default HistoricalValues;
