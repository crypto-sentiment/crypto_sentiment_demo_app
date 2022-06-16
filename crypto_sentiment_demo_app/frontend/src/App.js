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
  const [yesterday_data, setYesterdayData] = React.useState([]);
  const [last_week_data, setLastWeekData] = React.useState([]);
  const [last_month_data, setLastMonthData] = React.useState([]);

  var date = new Date();
  var today = date.toISOString().slice(0, 10);
  var yesterday = new Date(date.getFullYear(), date.getMonth(), date.getDate() - 1).toISOString().slice(0, 10);
  var lastweek = new Date(date.getFullYear(), date.getMonth(), date.getDate() - 7).toISOString().slice(0, 10);
  var lastmonth = new Date(date.getFullYear(), date.getMonth(), date.getDate() - 30).toISOString().slice(0, 10);

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

  React.useEffect(() => {
    fetch(
      `${host}:8002/positive_score/average_last_hours?n=4`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      },
    })
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setAverageLastHours(json);
      });
  }, []);

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

  React.useEffect(() => {
    fetch(`${host}:8002/positive_score/average_for_period?` + new URLSearchParams({
      "start_date": yesterday,
      "end_date": yesterday
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
        setYesterdayData(json);
      });
  }, []);

  React.useEffect(() => {
    fetch(`${host}:8002/positive_score/average_for_period?` + new URLSearchParams({
      "start_date": lastweek,
      "end_date": lastweek
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
        setLastWeekData(json);
      });
  }, []);

  React.useEffect(() => {
    fetch(`${host}:8002/positive_score/average_for_period?` + new URLSearchParams({
      "start_date": lastmonth,
      "end_date": lastmonth
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
        setLastMonthData(json);
      });
  }, []);

  const dataForPlot = average_per_days.sort((a, b) => {
    return new Date(a.pub_date).getTime() -
      new Date(b.pub_date).getTime()
  }).map(item => ({ ...item, avg_positive: Math.round(100 * item.avg_positive) }));

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
          <h1>Cryptobarometer</h1>
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
        <Manometer sentIndex={average_last_hours * 100} />
        <HistoricalValues
          yesteyday_value={yesterday_data}
          last_week_value={last_week_data}
          last_month_value={last_month_data}
        />
        <News lastNews={latest_news_items} />
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
        <Chart chartData={dataForPlot} />
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
