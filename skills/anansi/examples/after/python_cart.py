from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Item:
    sku: str
    price: Decimal
    qty: int = 1


@dataclass
class Cart:
    items: list = field(default_factory=list)
    coupon: str = None

    def add(self, item):
        for existing in self.items:
            if existing.sku == item.sku:
                # Matching SKUs share a row; the incoming quantity joins the existing one.
                existing.qty += item.qty
                return
        self.items.append(item)

    def total(self):
        # Decimal keeps price arithmetic out of binary floating-point.
        subtotal = sum((i.price * i.qty for i in self.items), Decimal("0"))
        if self.coupon == "WELCOME10":
            # Apply the exact 10% discount before quantizing the final total to cents.
            subtotal = subtotal * Decimal("0.90")
        return subtotal.quantize(Decimal("0.01"))
