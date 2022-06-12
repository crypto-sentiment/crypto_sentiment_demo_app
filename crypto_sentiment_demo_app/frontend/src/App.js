import Manometer from "./components/Manometer";
import React from "react";
import Chart from "./components/Chart";
import HistoricalValues from "./components/HistoricalValues";
import News from "./components/News";



function App() {
  const host = process.env.REACT_APP_HOST
  const [latest_news_items, setLatestNewsItems] = React.useState([]);
  const [average_last_hours, setAverageLastHours] = React.useState([]);
  const [average_per_days, setAveragePerDays] = React.useState([]);

  var date = new Date();
  var lastweek = new Date(date.getFullYear(), date.getMonth(), date.getDate() - 7).toISOString().slice(0, 10);
  var today = date.toISOString().slice(0, 10);

  React.useEffect(() => {
    fetch(
      `${host}:8002/news/top_k_news_titles?k=4`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        },
      }
    )
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setLatestNewsItems(json);
      });
  }, []);

  console.log(latest_news_items);

  React.useEffect(() => {
    fetch(
      `${host}:8002/positive_score/average_last_hours`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      },
      // body: JSON.stringify({
      //   "k": 4,
      // }),
    })
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setAverageLastHours(json);
      });
  }, []);

  console.log(average_last_hours);

  React.useEffect(() => {
    fetch(`${host}:8002/positive_score/average_per_days?` + new URLSearchParams({
      "start_date": lastweek,
      "end_date": today
    }), {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      },
    })
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setAveragePerDays(json);
      });
  }, []);

  console.log(average_per_days);

  React.useEffect(() => {
    fetch("/positive_score/average_last_hours", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setAverageLastHours(json);
      });
  }, []);

  console.log(average_last_hours);

  React.useEffect(() => {
    fetch("/positive_score/average_per_days?" + new URLSearchParams({
            "start_date": lastweek,
            "end_date": today
}), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setAveragePerDays(json);
      });
  }, []);

  console.log(average_per_days);

  return (
    <div className="wrapper clear">
      <header className="d-flex flex-column">
        <div className="headerRectangle d-flex"></div>
        <div className="headerInfo d-flex align-center">
          <img
            className="ml-15 mr-15"
            width={60}
            height={60}
            src="/img/logo.png"
            alt="logo"
          />
          <h1>Cryptosentiment</h1>
        </div>
      </header>
      <div className="description d-flex flex-column mt-50">
        <div className="d-flex align-center">
          <h2 className="ml-20">Crypto Sentiment Index</h2>
        </div>
        <p className="pr-15 pl-20">
          The Crypto Sentiment Index presents the emotions and sentiments of
          Bitcoin and other cryptocurrencies. It ranges from 0 to 100, with 0
          meaning totally negative, and 100 meaning clearly positive.
        </p>
      </div>
      <div className="indexCards d-flex flex-row justify-between mt-50">
        {items.map((average_last_hours) => (
          <Manometer sentIndex={average_last_hours} />
        ))}
        {items.map((item) => (
          <HistoricalValues indexesForPeriods={item.historical_values} />
        ))}
        {items.map((item) => (
          <News lastNews={latest_news_items} />
        ))}
      </div>
      <div className="description d-flex flex-column mt-50">
        <div className="d-flex align-center">
          <h2 className="ml-20">Crypto Sentiment Index Over Time</h2>
        </div>
        <p className="pr-15 pl-20">
          This is a plot of the Crypto Sentiment Index over time, with 0 meaning
          totally negative, and 100 meaning clearly positive.
        </p>
      </div>
      <div className="indexPlot d-flex justify-center">
        {items.map((item) => (
          <Chart chartData={average_per_days} />
        ))}
      </div>
      <div className="basement d-flex mt-50">
        <div className="basementInfo d-flex flex-column pt-20">
          <ul className="basementInfoItem cu-p ">
            <a
              className="d-flex flex-raw align-center"
              href="https://github.com/crypto-sentiment"
            >
              <img
                width={26}
                height={26}
                src="/img/github_white.svg"
                alt="git"
              />
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
            <b>Acknowledgements:</b>
            <ul className="Acknowledgements">
              <li>
                We thank Nikita Zakharov and Yekaterina Kryukova for their
                contributions
              </li>
              <li>
                We are grateful to
                <a className="cu-p mr-5  ml-5" href="https://hostkey.ru/">
                  Hostkey
                </a>
                and
                <a className="cu-p mr-5  ml-5" href="https://dstack.ai/">
                  dstack.ai
                </a>
                for providing computational resources
              </li>
            </ul>
          </li>
        </div>
      </div>
    </div>
  );
}

export default App;
