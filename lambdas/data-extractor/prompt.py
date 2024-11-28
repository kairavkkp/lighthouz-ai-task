PROMPT = """
Assume that you have an email with order details coming from a Supplier.
I want you extract following things for me and in specific JSON format, mind that
I'll be using json.loads() in python to load it up as a dictionary, so no extra things should
be a part of the response.

Following are the set of keys:
order_status: Based on the content inside the Email body or Invoice, infer the order status in a few lines.
email_summary: Summary of the email based on the subject and body
invoice_id: ID of the Invoice
order_id: ID of the Order
purchase_order: Purchase Order Number for the invoice and order
supplier.name: Supplier's Name
supplier.email: Supplier's email
supplier.phone: Supplier's Phone
supplier.address: Supplier's Address
buyer.name: buyer's Name
buyer.email: buyer's email
buyer.phone: buyer's Phone
buyer.address: buyer's Address
order_date: Date of the Order
expected_delivery_date: Date of Expected Delivery
order_value: Order Value in float
line_items: Array of line items, where each object can have the following keys if present:
    item_name: Name of the item
    item_code: Code of the item
    quantity: Itm quantity
    price_per_unit: Price per Unit
    total_price: Total Price


So, these many attributes are expected in the response. Make sure that if something is not present, 
count it as None, but don't skip any attribute.
Again, no extra characters just the string that can be loaded up as Dictionary.
"""
