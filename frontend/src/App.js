import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import OrderEmailThread from "./pages/OrderEmailThread";
import OrderList from "./pages/OrderList";
import React from "react";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/orders" element={<OrderList />} />
        <Route path="/orders/:orderId" element={<OrderEmailThread />} />
      </Routes>
    </Router>
  );
};

export default App;
