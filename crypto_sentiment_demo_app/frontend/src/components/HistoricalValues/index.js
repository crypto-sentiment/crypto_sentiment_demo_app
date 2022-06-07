import React from "react";
import styles from "./HistoricalValues.module.scss";
import IndexLine from "./IndexLine";

function HistoricalValues({indexesForPeriods}) {
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
