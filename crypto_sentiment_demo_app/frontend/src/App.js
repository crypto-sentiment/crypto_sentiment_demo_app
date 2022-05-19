import Manometer from "./components/Manometer";
import React from "react";
import Chart from "./components/Chart";
import HistoricalValues from "./components/HistoricalValues";
import News from "./components/News";

function App() {
  const [items, setItems] = React.useState([]);

  React.useEffect(() => {
    fetch("https://6267e06101dab900f1c65f2c.mockapi.io/indexes")
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setItems(json);
      });
  }, []);

  return (
    <div className="wrapper clear">
      <header className="d-flex flex-column">
        <div className="headerRectangle d-flex"></div>
        <div className="headerInfo d-flex align-center">
          <img width={60} height={60} src="/img/logo.png" alt="logo" />
          <h1>Cryptosentiment</h1>
        </div>
      </header>
      <div className="description d-flex flex-column mt-50">
        <div className="d-flex align-center">
          <img
            className="mr-15"
            width={60}
            height={30}
            src="/img/label.png"
            alt="label"
          />
          <h2>Crypto Sentiment Index</h2>
        </div>
        <p className="pr-15 pl-15">
          The Crypto Sentiment Index presents the emotions and sentiments of
          Bitcoin and other cryptocurrencies. The Crypto Sentiment Index varies
          in the range from 0 to 100, where a value of 0 means "Extreme
          Negative" while a value of 100 represents "Extreme Positive".
        </p>
      </div>
      <div className="indexCards d-flex flex-row justify-between mt-50">
        {items.map((item) => (
          <Manometer sentIndex={item.day_index} />
        ))}
        {items.map((item) => (
          <HistoricalValues indexesForPeriods={item.historical_values} />
        ))}
        {items.map((item) => (
          <News lastNews={item.last_news} />
        ))}
      </div>
      <div className="description d-flex flex-column mt-50">
        <div className="d-flex align-center">
          <img
            className="mr-15"
            width={60}
            height={30}
            src="/img/label.png"
            alt="label"
          />
          <h2>Crypto Sentiment Index Over Time</h2>
        </div>
        <p className="pr-15 pl-15">
          This is a plot of the Crypto Sentiment Index over time, where a value
          of 0 means "Extreme Negative" while a value of 100 represents "Extreme
          Positive".
        </p>
      </div>
      <div className="indexPlot d-flex justify-center">
        {items.map((item) => (
          <Chart chartData={item.graph} />
        ))}
      </div>
      <div className="basement d-flex flex-column mt-50">
        <div className="basementInfo align-center">
          <ul className="d-flex flex-raw align-center p-20 cu-p">
            <a href="https://github.com/crypto-sentiment">
              <img width={24} height={24} src="/img/git.png" alt="git" />
              <b>Crypto Sentiment Project</b>
            </a>
          </ul>
        </div>
        {/* <div className="basementRectangle d-flex"></div> */}
      </div>
    </div>
  );
}

export default App;
