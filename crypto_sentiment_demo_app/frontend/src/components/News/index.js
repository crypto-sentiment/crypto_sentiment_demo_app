import React from "react";
import styles from "./News.module.scss";
import NewsLine from "./NewsLine";

function News({lastNews}) {
  return (
    <div className={styles.indexCard}>
      <h2 className="ml-20">Latest News</h2>
      {lastNews.map((obj) => (
          <NewsLine news={obj.title} value={Math.round(100 * obj.positive)} />
        ))}
    </div>
  );
}

export default News;
