import { Link, useParams } from "react-router-dom";
import React, { useCallback, useEffect, useState } from "react";

const OrderEmailThread = () => {
  const { orderId } = useParams(); // Get order_id from the URL
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
        setError(`Failed to fetch email threads. Please try again later.`);
      } finally {
        setLoading(false);
      }
    },
    [orderId]
  );

  useEffect(
    () => {
      fetchEmailThread();
    },
    [fetchEmailThread]
  );

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
  }
};

export default OrderEmailThread;
