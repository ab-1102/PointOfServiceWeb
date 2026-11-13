import pages.connection as connection

import dbms
# DBMS Wrapper
def categories():
    return dbms.categories()
def products(category):
    return dbms.products(category)

# Bill Maker
currentBill = dbms.Bill()
def add_to_bill(product, quantity = 1):
    global currentBill
    currentBill.add(product, quantity)

def finish_bill(customer_name, mobile_number):
    currentBill.customer_name = customer_name
    currentBill.customer_phone_number = mobile_number
    dbms.store_bill(currentBill)
    bill = currentBill.products
    data = [bill, customer_name, mobile_number]
    connection.send_to_local(data)
    currentBill.reset()

def reset_bill():
    global currentBill
    currentBill.reset()

