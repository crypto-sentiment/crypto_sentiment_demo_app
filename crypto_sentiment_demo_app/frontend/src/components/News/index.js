import React from "react";
import styles from "./News.module.scss";
import NewsLine from "./NewsLine";

function News({lastNews}) {
  return (
    <div className={styles.indexCard}>
      <h2 className="ml-20">Last News</h2>
      {lastNews.map((obj) => (
          <NewsLine news={obj.news} value={obj.value} />
        ))}
    </div>
  );
}

export default News;
