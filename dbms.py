
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

from psycopg.types.json import Jsonb

from database.connection import get_db_connection


# --------------------------------------------------
# BILL NUMBER GENERATION
# --------------------------------------------------

def _encode_letters(number):
    """Convert a positive integer into Excel-style letters."""

    result = ""

    while number > 0:
        number -= 1
        result = chr(65 + (number % 26)) + result
        number //= 26

    return result


def _decode_letters(letters):
    """Convert Excel-style letters into a positive integer."""

    result = 0

    for char in letters:
        result = result * 26 + ord(char) - 64

    return result


def _encode_bill_number(date_prefix, sequence):
    """Generate the suffix for a daily bill sequence."""

    if sequence < 1:
        raise ValueError("Invalid bill sequence.")

    if sequence <= 9999:
        suffix = f"{sequence:04d}"
    else:
        overflow = sequence - 10000
        letters = _encode_letters((overflow // 10000) + 1)
        counter = overflow % 10000
        suffix = f"{letters}{counter:04d}"

    return date_prefix + suffix


def _decode_bill_number(bill_number, date_prefix):
    """Extract the numerical sequence from a bill number."""

    suffix = bill_number[len(date_prefix):]

    if len(suffix) < 4 or not suffix[-4:].isdigit():
        raise ValueError(f"Invalid existing bill number: {bill_number}")

    letters = suffix[:-4]
    counter = int(suffix[-4:])

    if not letters:
        return counter

    if not letters.isalpha() or not letters.isupper():
        raise ValueError(f"Invalid existing bill number: {bill_number}")

    letter_value = _decode_letters(letters)

    return 10000 + (letter_value - 1) * 10000 + counter


def _next_bill_number(cursor, bill_date):
    """Generate the next bill number safely for a given date."""

    date_prefix = bill_date.strftime("%d%m%Y")
    date_key = int(bill_date.strftime("%Y%m%d"))

    # Serialize bill-number generation for this date.
    cursor.execute(
        "SELECT pg_advisory_xact_lock(%s, %s);",
        (15012026, date_key)
    )

    cursor.execute(
        """
        SELECT bill_number
        FROM public.bills
        WHERE bill_number LIKE %s;
        """,
        (date_prefix + "%",)
    )

    existing_numbers = cursor.fetchall()

    highest_sequence = 0

    for row in existing_numbers:
        sequence = _decode_bill_number(row[0], date_prefix)
        highest_sequence = max(highest_sequence, sequence)

    return _encode_bill_number(
        date_prefix,
        highest_sequence + 1
    )


# --------------------------------------------------
# BILL STORAGE
# --------------------------------------------------

def store_bill(bill):
    """Validate and store a bill, updating inventory atomically."""

    if not bill.products:
        raise ValueError("Cannot store an empty bill.")

    if not bill.payment_method:
        raise ValueError("Payment method is required.")

    # Aggregate quantities by product ID.
    quantities = {}

    for product, quantity in bill.products:

        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity <= 0
        ):
            raise ValueError(
                f"Invalid quantity for {product.name}."
            )

        quantities[product.id] = (
            quantities.get(product.id, 0) + quantity
        )

    product_ids = sorted(quantities.keys())

    # Use Indian local date for bill numbering.
    bill_date = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).date()

    with get_db_connection() as conn:
        with conn.cursor() as cursor:

            # Lock inventory rows to prevent concurrent
            # transactions from selling the same stock.
            cursor.execute(
                """
                SELECT id, name, price, cost_price, stock,
                       category, is_active
                FROM public.inventory
                WHERE id = ANY(%s)
                ORDER BY id
                FOR UPDATE;
                """,
                (product_ids,)
            )

            rows = cursor.fetchall()

            inventory = {
                row[0]: row for row in rows
            }

            if len(inventory) != len(product_ids):
                raise ValueError(
                    "One or more products no longer exist."
                )

            subtotal = Decimal("0.00")
            bill_items = []

            # Validate stock and calculate using database prices.
            for product_id in product_ids:

                row = inventory[product_id]

                (
                    db_id,
                    name,
                    price,
                    cost_price,
                    stock,
                    category,
                    is_active
                ) = row

                quantity = quantities[product_id]

                if not is_active:
                    raise ValueError(
                        f"{name} is no longer active."
                    )

                if stock < quantity:
                    raise ValueError(
                        f"Insufficient stock for {name}. "
                        f"Available: {stock}, requested: {quantity}."
                    )

                price = Decimal(str(price))
                cost_price = Decimal(str(cost_price))

                line_total = price * quantity
                subtotal += line_total

                bill_items.append({
                    "product_id": db_id,
                    "name": name,
                    "category": category,
                    "quantity": quantity,
                    "unit_price": float(price),
                    "cost_price_at_sale": float(cost_price),
                    "line_total": float(line_total)
                })

            subtotal = subtotal.quantize(Decimal("0.01"))
            total = subtotal

            # Generate the bill number inside this transaction.
            bill_number = _next_bill_number(
                cursor,
                bill_date
            )

            customer_name = bill.customer_name or None

            phone = bill.customer_phone_number
            customer_number = (
                str(phone) if phone not in (None, "", 0) else None
            )

            payment_status = (
                bill.payment_status or "Unpaid"
            )

            # Create the immutable bill snapshot.
            bill_content = {
                "schema_version": 1,
                "bill_number": bill_number,
                "customer": {
                    "name": customer_name,
                    "phone": customer_number
                },
                "items": bill_items,
                "subtotal": float(subtotal),
                "total": float(total),
                "payment_method": bill.payment_method,
                "payment_status": payment_status
            }

            # Deduct inventory.
            for product_id in product_ids:

                quantity = quantities[product_id]

                cursor.execute(
                    """
                    UPDATE public.inventory
                    SET stock = stock - %s
                    WHERE id = %s
                      AND stock >= %s;
                    """,
                    (quantity, product_id, quantity)
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "Inventory update failed."
                    )

            # Insert bill.
            cursor.execute(
                """
                INSERT INTO public.bills (
                    bill_number,
                    customer_name,
                    customer_number,
                    subtotal,
                    total,
                    payment_method,
                    status,
                    bill_content
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    bill_number,
                    customer_name,
                    customer_number,
                    subtotal,
                    total,
                    bill.payment_method,
                    payment_status,
                    Jsonb(bill_content)
                )
            )

            bill_id = cursor.fetchone()[0]

    # The transaction has committed successfully here.
    return {
        "id": bill_id,
        "bill_number": bill_number,
        "subtotal": subtotal,
        "total": total,
        "status": payment_status
    }


# --------------------------------------------------
# INVENTORY READ OPERATIONS
# --------------------------------------------------

def categories():
    """Returns categories containing active products."""

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT category
                FROM public.inventory
                WHERE is_active = TRUE
                ORDER BY category;
                """
            )

            return [row[0] for row in cursor.fetchall()]


def products(category):
    """Returns active products belonging to a given category."""

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT name, id, category, price, stock, cost_price
                FROM public.inventory
                WHERE category = %s
                  AND is_active = TRUE
                ORDER BY name;
                """,
                (category,)
            )

            rows = cursor.fetchall()

            return [
                Product(
                    name=row[0],
                    id=row[1],
                    category=row[2],
                    sell_price=row[3],
                    stock=row[4],
                    cost_price=row[5]
                )
                for row in rows
            ]


# --------------------------------------------------
# PRODUCT CLASS
# --------------------------------------------------

class Product:

    def __init__(
        self,
        name,
        id,
        category,
        sell_price,
        stock,
        cost_price
    ):
        self.name = name
        self.id = id
        self.category = category
        self.sell_price = sell_price
        self.stock = stock
        self.cost_price = cost_price


# --------------------------------------------------
# BILL CLASS
# --------------------------------------------------

class Bill:

    def __init__(self):
        self.products = []
        self.customer_name = ""
        self.customer_phone_number = ""
        self.payment_method = "Pay"
        self.payment_status = "Unpaid"

    def __len__(self):
        return len(self.products)

    def add(self, product, quantity=1):

        for item in self.products:
            if item[0].id == product.id:
                item[1] = quantity
                break
        else:
            self.products.append([product, quantity])

    def product_names(self):
        return [item[0].name for item in self.products]

    def product_qty(self):
        return [item[1] for item in self.products]

    def product_price(self):
        return [
            item[0].sell_price * item[1]
            for item in self.products
        ]

    def total(self):
        return sum(self.product_price())

    def reset(self):
        self.products = []

    def bill_data_for_print(self):
        data = []
        for item in self.products:
            #row= [name,qty,price]
            row = [item[0].name, item[1], float(item[0].sell_price*item[1])]
            data.append(row)
        return data