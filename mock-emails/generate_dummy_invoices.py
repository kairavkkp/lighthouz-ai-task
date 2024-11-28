import random
import json
from faker import Faker
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os
from textwrap import wrap

# Initialize Faker
fake = Faker()


def generate_dummy_invoice():
    # Generate random invoice data
    line_items = generate_line_items(random.randint(2, 6))
    order_value = sum(item["total_price"] for item in line_items)  # Sum of line item totals

    invoice = {
        "invoice_id": f"INV-{random.randint(1000, 9999)}",
        "order_id": f"ORD-{random.randint(1000, 9999)}",
        "purchase_order": f"PO-{random.randint(1000, 9999)}",
        "supplier": {
            "name": fake.company(),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
        },
        "buyer": {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
        },
        "order_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
        "expected_delivery_date": (datetime.now() + timedelta(days=random.randint(5, 15))).strftime("%Y-%m-%d"),
        "order_value": round(order_value, 2),  # Fixed calculation
        "line_items": line_items,
    }
    return invoice


def generate_line_items(count):
    # Generate random line items
    line_items = []
    for _ in range(count):
        item = {
            "item_name": fake.word().capitalize(),
            "item_code": f"IT-{random.randint(100, 999)}",
            "quantity": random.randint(1, 10),
            "price_per_unit": round(random.uniform(10, 500), 2),
            "total_price": 0,  # Calculated below
        }
        item["total_price"] = round(item["quantity"] * item["price_per_unit"], 2)
        line_items.append(item)
    return line_items


def save_invoice_as_pdf(invoice, output_dir="invoices_pdf"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{invoice['invoice_id']}.pdf")
    pdf = canvas.Canvas(filename, pagesize=letter)

    # Header
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, "INVOICE")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 730, f"Invoice ID: {invoice['invoice_id']}")
    pdf.drawString(50, 710, f"Order ID: {invoice['order_id']}")
    pdf.drawString(50, 690, f"Purchase Order: {invoice['purchase_order']}")

    pdf.drawString(400, 730, f"Order Date: {invoice['order_date']}")
    pdf.drawString(400, 710, f"Exp. Delivery: {invoice['expected_delivery_date']}")

    # Supplier and Buyer Details
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 670, "Supplier Information")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 650, f"Name: {invoice['supplier']['name']}")
    pdf.drawString(50, 635, f"Email: {invoice['supplier']['email']}")
    pdf.drawString(50, 620, f"Phone: {invoice['supplier']['phone']}")
    render_multiline_text(pdf, 50, 605, f"Address: {invoice['supplier']['address']}", 30)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(300, 670, "Buyer Information")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(300, 650, f"Name: {invoice['buyer']['name']}")
    pdf.drawString(300, 635, f"Email: {invoice['buyer']['email']}")
    pdf.drawString(300, 620, f"Phone: {invoice['buyer']['phone']}")
    render_multiline_text(pdf, 300, 605, f"Address: {invoice['buyer']['address']}", 30)

    # Line Items Table
    table_data = [["Item Name", "Item Code", "Quantity", "Price/Unit", "Total Price"]]
    for item in invoice["line_items"]:
        table_data.append(
            [
                item["item_name"],
                item["item_code"],
                item["quantity"],
                f"${item['price_per_unit']:.2f}",
                f"${item['total_price']:.2f}",
            ]
        )

    table = Table(table_data, colWidths=[120, 80, 80, 100, 100])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    # Render table
    table.wrapOn(pdf, 50, 400)
    table.drawOn(pdf, 50, 400)

    # Footer
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 370, f"Total Order Value: ${invoice['order_value']:.2f}")

    pdf.save()
    print(f"Saved PDF: {filename}")


def render_multiline_text(pdf, x, y, text, max_width):
    """
    Render multiline text on a PDF canvas.
    :param pdf: PDF canvas object.
    :param x: X-coordinate for the text.
    :param y: Starting Y-coordinate for the text.
    :param text: The full text to render.
    :param max_width: Maximum width in characters for each line.
    """
    lines = wrap(text, max_width)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= 15  # Move to the next line (adjust line spacing as needed)


def generate_invoices(count=10):
    invoices = [generate_dummy_invoice() for _ in range(count)]
    return invoices


def save_invoices_to_file(invoices, filename="dummy_invoices.json"):
    with open(filename, "w") as f:
        json.dump(invoices, f, indent=4)
    print(f"Saved {len(invoices)} invoices to {filename}")


if __name__ == "__main__":
    # Generate and save dummy invoices
    invoice_count = int(input("Enter the number of invoices to generate: "))
    dummy_invoices = generate_invoices(invoice_count)

    # Save as JSON
    save_invoices_to_file(dummy_invoices)

    # Save each invoice as PDF
    for invoice in dummy_invoices:
        save_invoice_as_pdf(invoice)
