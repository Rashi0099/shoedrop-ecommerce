from io import BytesIO

from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    """
    Renders a Django template to a raw PDF byte string using xhtml2pdf.

    The template must be a standalone HTML document (no {% extends %}).
    Returns the raw bytes on success, or None on failure.
    """
    template = get_template(template_src)
    html = template.render(context_dict)

    buffer = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), buffer)

    if not pdf.err:
        return buffer.getvalue()

    return None

from decimal import Decimal

def calculate_item_refund_amount(order, item):
    """
    Calculates the exact refund amount for a single order item.
    It adds 18% GST to the item's total, and subtracts the proportional coupon discount
    applied to the overall order.
    """
    original_subtotal = sum(float(i.total) for i in order.items.all())
    if original_subtotal <= 0:
        return Decimal('0.00')
    
    item_ratio = float(item.total) / original_subtotal
    refund_amount = (float(item.total) * 1.18) - (item_ratio * float(order.coupon_discount))
    
    if refund_amount < 0:
        refund_amount = 0
        
    return Decimal(str(round(refund_amount, 2)))
