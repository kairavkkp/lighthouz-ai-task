import React, { useEffect, useState } from "react";

const OrderList = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOrders = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_BASE_URL}/orders`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setOrders(data);
    } catch (err) {
      setError(`Failed to fetch orders. Please try again later.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  if (loading)
    return <p style={{ textAlign: "center", padding: "20px" }}>Loading...</p>;
  if (error)
    return (
      <p style={{ textAlign: "center", color: "red", padding: "20px" }}>
        {error}
      </p>
    );

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Orders</h1>
      <div style={styles.orderList}>
        {orders.map(order =>
          <div key={order.order_id} style={styles.orderCard}>
            <div style={styles.gridContainer}>
              {/* Left Side */}
              <div style={styles.leftColumn}>
                <p style={styles.pTag}>
                  <strong>Order ID:</strong> {order.order_id}
                </p>
                <p style={styles.pTag}>
                  <strong>Purchase Order:</strong> {order.purchase_order}
                </p>
                <p style={styles.pTag}>
                  <strong>Supplier:</strong> {order.supplier.name}
                </p>
                <p style={styles.pTag}>
                  <strong>Buyer:</strong> {order.buyer.name}
                </p>
              </div>

              {/* Right Side */}
              <div style={styles.rightColumn}>
                <p style={styles.pTag}>
                  <strong>Order Date:</strong> {order.order_date}
                </p>
                <p style={styles.pTag}>
                  <strong>Exp. Delivery:</strong> {order.expected_delivery_date}
                </p>
                <p style={styles.pTag}>
                  <strong>Order Value:</strong> ${order.order_value}
                </p>
              </div>
            </div>

            {/* Bottom Section */}
            <div style={styles.bottomRow}>
              <p style={styles.pTag}>
                <strong>Order Status:</strong> {order.order_status}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "20px",
    fontFamily: "Arial, sans-serif"
  },
  heading: {
    fontSize: "2rem",
    fontWeight: "bold",
    marginBottom: "20px",
    textAlign: "left"
  },
  orderList: {
    display: "flex",
    flexDirection: "column",
    gap: "10px" // Less gap between cards
  },
  orderCard: {
    border: "1px solid #ddd", // Subtle border
    borderRadius: "6px", // Slight rounding
    padding: "10px", // Compact padding
    boxShadow: "0px 1px 3px rgba(0, 0, 0, 0.1)" // Light shadow
  },
  gridContainer: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr", // Two equal columns
    columnGap: "15px", // Smaller gap between columns
    rowGap: "8px" // Compact row spacing
  },
  leftColumn: {
    display: "flex",
    flexDirection: "column",
    gap: "6px" // Tighter spacing for compactness
  },
  rightColumn: {
    display: "flex",
    flexDirection: "column",
    gap: "6px" // Tighter spacing for compactness
  },
  bottomRow: {
    marginTop: "10px",
    borderTop: "1px solid #eee", // Subtle divider
    paddingTop: "8px",
    textAlign: "left"
  },
  pTag: {
    margin: "2px 0", // Reduced top and bottom margin
    lineHeight: "1.4" // Adjust line height for readability
  }
};

export default OrderList;
