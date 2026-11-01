print('DBMS Module')

def store_bill(bill):
    pass

def categories():
    """
    Returns a list of categories available in the database.
    """
    # Placeholder for actual database query
    return ["Burgers", "Sandwiches", "Boba", "Shakes", "Cakes"]

def products(category):
    """
    Returns a list of products for a given category.
    """
    # Placeholder for actual database query
    cheese_burger = Product("Cheese Burger", 1, "Burgers", 10, 100, 5)
    classic_burger = Product("Classic Burger", 2, "Burgers", 10, 100, 5)
    veggie_burger = Product("Veggie Burger", 3, "Burgers", 11, 100, 6)
    club_sandwich = Product("Club Sandwich", 4, "Sandwiches", 8, 100, 3)
    grilled_cheese = Product("Grilled Cheese", 5, "Sandwiches", 7, 100, 2)
    chocolate_shake = Product("Chocolate Shake", 6, "Shakes", 8, 100, 3)
    vanilla_shake = Product("Vanilla Shake", 7, "Shakes", 8, 100, 3)
    strawberry_shake = Product("Strawberry Shake", 8, "Shakes", 8, 100, 3)
    mango_shake = Product("Mango Shake", 9, "Shakes", 8, 100, 3)
    banana_shake = Product("Banana Shake", 10, "Shakes", 8, 100, 3)
    coffee_shake = Product("Coffee Shake", 11, "Shakes", 8, 100, 3)

    if category == "Burgers":
        return [cheese_burger, classic_burger, veggie_burger]
    elif category == "Sandwiches":
        return [club_sandwich, grilled_cheese]
    elif category == "Shakes":
        return [chocolate_shake, vanilla_shake, strawberry_shake, mango_shake, banana_shake, coffee_shake]
    else:
        return []

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
