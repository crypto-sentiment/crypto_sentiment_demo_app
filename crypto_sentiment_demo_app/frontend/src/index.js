import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.scss';
import 'macro-css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
const cors = require("cors");
App.use(cors());

root.render(
  // <React.StrictMode>
    <App />
  // </React.StrictMode>
);
