import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import OrderList from "./pages/OrderList";
import React from "react";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/orders" element={<OrderList />} />
      </Routes>
    </Router>
  );
};

export default App;
