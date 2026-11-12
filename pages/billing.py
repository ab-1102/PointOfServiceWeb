import streamlit as st
import main

if "customer_name" not in st.session_state:
    st.session_state.customer_name = "hgfd"
if "customer_phone_number" not in st.session_state:
    st.session_state.customer_phone_number = "76543"

st.set_page_config(layout="wide")

productSelectionPanel, cartPanel = st.columns([6,4])

with productSelectionPanel:
    categorises = main.categories() #----------------------------------- DBMS
    tabs = st.tabs(categorises)
    for tabI, tab in enumerate(tabs):
        category = categorises[tabI]
        with tab:
            products = main.products(category) #------------------------ DBMS
            numCols = 3
            proI = 0
            cols = st.columns(numCols)
            for proI in range(0 , len(products), numCols):
                for colI, col in enumerate(cols):
                    with col:
                        if st.button(products[proI].name,
                                  use_container_width=True):
                            main.add_to_bill(products[proI], 1)
                    proI += 1
                    if proI == len(products):
                        break

containerHeight = 40
with cartPanel:
    st.session_state.customer_name  = st.text_input(label="Customer Name",label_visibility="hidden",placeholder="Customer Name",key="customerName",value="")
    st.session_state.customer_phone_number = st.text_input(label="Mobile Number",label_visibility="hidden",placeholder="Mobile Number",key="mobileNumber",value="",type="phone")

    st.divider()

    item_col, qty_col, price_col = st.columns([3, 1, 1])
    with item_col:
        item_names = main.currentBill.product_names()
        for i in item_names:
            with st.container(width=400 , height=containerHeight, horizontal_alignment="left", vertical_alignment="center"):
                st.text(i)

    with qty_col:

        item_qty = main.currentBill.product_qty()
        for i, qty in enumerate(item_qty):
            with st.container(width=100, height=containerHeight, horizontal_alignment="center", vertical_alignment="center"):
                num =  st.number_input(
                    label='QTY',
                    label_visibility="collapsed",
                    value=qty,
                    min_value=1,
                    step=1,
                    format="%d",
                    key=f"qty_{i}")
            if num is not None:
                product = main.currentBill.products[i][0]
                main.add_to_bill(product, num)

    with price_col:
        item_prices = main.currentBill.product_price()
        for i in item_prices:
            with st.container(width=100, height=containerHeight, horizontal_alignment="center", vertical_alignment="center"):
                st.write(f"₹{i}")

    st.divider()

    st.subheader(f"Total: ₹{main.currentBill.total()}")

    if st.button("Checkout",use_container_width=True) and main.currentBill.total() != 0:
        if st.session_state.customer_name != "" and st.session_state.customer_phone_number != "" and len(st.session_state.customer_phone_number) == 10:
            main.finish_bill(st.session_state.customer_name, st.session_state.customer_phone_number)
            st.session_state.customer_name = ""
            st.session_state.customer_phone_number = ""
            st.toast("Bill completed successfully!", duration=2, icon="✅")
            st.rerun()

        else:
            st.toast("Check Name/Phone Number", icon="⚠️")