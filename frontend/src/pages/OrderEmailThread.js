import { Link, useParams } from "react-router-dom";
import React, { useCallback, useEffect, useState } from "react";

const OrderEmailThread = () => {
  const { orderId } = useParams(); // Get order_id from the URL
  const [emails, setEmails] = useState([]);
  const [orderDetails, setOrderDetails] = useState(null);
  const [loadingEmails, setLoadingEmails] = useState(true);
  const [loadingOrder, setLoadingOrder] = useState(true);
  const [errorEmails, setErrorEmails] = useState(null);
  const [errorOrder, setErrorOrder] = useState(null);

  const fetchOrderDetails = useCallback(
    async () => {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_API_BASE_URL}/orders/${orderId}`,
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
        setOrderDetails(data);
      } catch (err) {
        setErrorOrder(`Failed to fetch order details. Please try again later.`);
      } finally {
        setLoadingOrder(false);
      }
    },
    [orderId]
  );
  const fetchEmailThread = useCallback(
    async () => {
      try {
        const response = await fetch(
          `${process.env
            .REACT_APP_API_BASE_URL}/order-email-threads/${orderId}`,
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
        setEmails(data);
      } catch (err) {
        setErrorEmails(
          `Failed to fetch email threads. Please try again later.`
        );
      } finally {
        setLoadingEmails(false);
      }
    },
    [orderId]
  );

  useEffect(
    () => {
      fetchEmailThread();
      fetchOrderDetails();
    },
    [fetchEmailThread, fetchOrderDetails]
  );

  if (loadingEmails || loadingOrder)
    return <p style={{ textAlign: "center", padding: "20px" }}>Loading...</p>;
  if (errorOrder)
    return (
      <p style={{ textAlign: "center", color: "red", padding: "20px" }}>
        {errorOrder}
      </p>
    );

  if (errorEmails)
    return (
      <p style={{ textAlign: "center", color: "red", padding: "20px" }}>
        {errorEmails}
      </p>
    );

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Order Details</h1>
      {/* Order Details Section */}
      {orderDetails &&
        <div style={styles.orderCard}>
          <div style={styles.gridContainer}>
            {/* Left Side */}
            <div style={styles.leftColumn}>
              <p style={styles.pTag}>
                <strong>Order ID:</strong> {orderDetails.order_id}
              </p>
              <p style={styles.pTag}>
                <strong>Purchase Order:</strong> {orderDetails.purchase_order}
              </p>
              <p style={styles.pTag}>
                <strong>Supplier:</strong> {orderDetails.supplier.name}
              </p>
              <p style={styles.pTag}>
                <strong>Buyer:</strong> {orderDetails.buyer.name}
              </p>
            </div>

            {/* Right Side */}
            <div style={styles.rightColumn}>
              <p style={styles.pTag}>
                <strong>Order Date:</strong> {orderDetails.order_date}
              </p>
              <p style={styles.pTag}>
                <strong>Exp. Delivery:</strong>{" "}
                {orderDetails.expected_delivery_date}
              </p>
              <p style={styles.pTag}>
                <strong>Order Value:</strong> ${orderDetails.order_value}
              </p>
            </div>
          </div>
        </div>}
      <h1 style={styles.heading}>
        Email Threads for Order {orderId}
      </h1>
      <div style={styles.emailList}>
        {emails.map(email =>
          <div key={email.id} style={styles.emailCard}>
            <p>
              <strong>Subject:</strong> {email.subject}
            </p>
            <p>
              <strong>To:</strong> {email.to_email}
            </p>
            <p>
              <strong>From:</strong> {email.from_email}
            </p>
            <p>
              <strong>Timestamp:</strong> {email.timestamp}
            </p>
            <p>
              <strong>Email Summary:</strong> {email.email_summary}
            </p>
            <p>
              <strong>Order Status:</strong> {email.order_status}
            </p>
            <p>
              <strong>Attachments:</strong>{" "}
              {email.attachments && email.attachments.length > 0
                ? email.attachments.join(", ")
                : "No attachments"}
            </p>
          </div>
        )}
      </div>
      <Link to="/orders" style={styles.backLink}>
        Back to Orders
      </Link>
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
  emailList: {
    display: "flex",
    flexDirection: "column",
    gap: "15px"
  },
  emailCard: {
    border: "1px solid #ddd",
    borderRadius: "6px",
    padding: "10px",
    boxShadow: "0px 1px 3px rgba(0, 0, 0, 0.1)"
  },
  backLink: {
    display: "block",
    marginTop: "20px",
    textDecoration: "none",
    color: "#007BFF",
    fontWeight: "bold"
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

export default OrderEmailThread;
