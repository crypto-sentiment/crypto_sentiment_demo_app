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
          <img className="ml-15 mr-15" width={60} height={60} src="/img/logo.png" alt="logo" />
          <h1>Cryptosentiment</h1>
        </div>
      </header>
      <div className="description d-flex flex-column mt-50">
        <div className="d-flex align-center">
          <h2 className="ml-20">Crypto Sentiment Index</h2>
        </div>
        <p className="pr-15 pl-20">
          The Crypto Sentiment Index presents the emotions and sentiments of
          Bitcoin and other cryptocurrencies. It ranges from 0 to 100, with 0 meaning totally negative, and 100 meaning clearly positive.
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
          <h2 className="ml-20">Crypto Sentiment Index Over Time</h2>
        </div>
        <p className="pr-15 pl-20">
          This is a plot of the Crypto Sentiment Index over time, with 0 meaning totally negative, and 100 meaning clearly positive.
        </p>
      </div>
      <div className="indexPlot d-flex justify-center">
        {items.map((item) => (
          <Chart chartData={item.graph} />
        ))}
      </div>
      <div className="basement d-flex mt-50">
        <div className="basementInfo d-flex flex-column pt-20">
          <ul className="basementInfoItem cu-p ">
            <a className="d-flex flex-raw align-center" href="https://github.com/crypto-sentiment">
              <img width={26} height={26} src="/img/github_white.svg" alt="git" />
              <b>Crypto Sentiment Project</b>
            </a>
          </ul>
          <li className="basementInfoItem d-flex flex-raw">
            <p className="authorsHeader">Authors</p>
            <a className="cu-p" href="https://github.com/Yorko">
              <p>Yury Kashnitsky</p>
            </a>
            <a className="cu-p" href="https://github.com/Arsenaut">
              <p>Arseniy Glotov</p>
            </a>
            <a className="cu-p" href="https://github.com/aleksandrinvictor">
              <p>Victor Aleksandrin</p>
            </a>
            <a className="cu-p" href="https://github.com/LinkaG">
              <p>Zalina Rusinova</p>
            </a>
          </li>
          <li className="basementInfoItem mb-20">
            <p>We express our gratitude to Nikita Zaharov and Ekaterina Kryukova for the help in the project</p>
          </li>


        </div>
      </div>
    </div>
  );
}

export default App;
