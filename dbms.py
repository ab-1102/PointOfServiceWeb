from database.connection import get_db_connection

def store_bill(bill):
    """Stores a new bill in the database."""

    pass

def categories():
    """Returns categories containing active products."""

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT category
                FROM public.inventory
                WHERE is_active = TRUE
                ORDER BY category;
            """)

            return [row[0] for row in cursor.fetchall()]


def products(category):
    """Returns active products belonging to a given category."""

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT name, id, category, price, stock, cost_price
                FROM public.inventory
                WHERE category = %s
                  AND is_active = TRUE
                ORDER BY name;
            """, (category,))

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

class Product:
    def __init__(self, name, id, category, sell_price, stock, cost_price):
        self.name = name
        self.id = id
        self.category = category
        self.sell_price = sell_price
        self.stock = stock
        self.cost_price = cost_price

class Bill:
    def __init__(self):
        self.products = []
        self.customer_name = ""
        self.customer_phone_number = 0

    def __len__(self):
        return len(self.products)

    def add(self, product, quantity = 1):
        for i in self.products:
            if i[0].id == product.id:
                i[1] = quantity
                break
        else:
            self.products.append([product, quantity])

    def product_names(self):
        names = []
        for i in self.products:
            names.append(i[0].name)
        return names

    def product_qty(self):
        qty = []
        for i in self.products:
            qty.append(i[1])
        return qty

    def product_price(self):
        price = []
        for i in self.products:
            price.append(i[0].sell_price * i[1])
        return price

    def total(self):
        total = 0
        for i in self.products:
            total += i[0].sell_price * i[1]
        return total

    def reset(self):
        self.products = []
