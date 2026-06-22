import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Budget Tracker", layout="centered")
st.title("Budget Tracker")

# ======ADD A TRANSACTION ========
st.header("Add a Transaction")

with st.form("add_transaction_form"):
    type_ = st.selectbox("Type", ["income", "expense"])
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    description = st.text_input("Description (optional)")
    date = st.date_input("Date")

    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        if not category.strip():
            st.warning("Please enter a category before submitting.")
        else:
            response = requests.post(
                f"{API_BASE_URL}/transactions",
                json={
                    "type": type_,
                    "category": category,
                    "amount": amount,
                    "description": description,
                    "date": str(date),
                },
            )
            if response.status_code == 200:
                st.success("Transaction added")
            else:
                st.error(f"Error: {response.text}")
 

#-------ALL TRANSACTION -------

st.header("All Transactions")
response = requests.get(f"{API_BASE_URL}/transactions")

if response.status_code == 200:
    transactions = response.json()
    if transactions:
        st.dataframe(transactions, use_container_width=True)
    else:
        st.info("No transactions yet.")
else:
    st.error("Could not load Transactions.")

#====DELETE=====

st.subheader("Delete a Transaction")
delete_id = st.number_input("Enter Transaction ID to delete", min_value=1, key="delete_id")

if st.button("Delete Transaction"):
    delete_response = requests.delete(f"{API_BASE_URL}/transactions/{int(delete_id)}")
    if delete_response.status_code == 200:
        st.success(f"Transaction {int(delete_id)} deleted!")
        st.rerun()
    elif delete_response.status_code == 404:
        st.warning(f"Transaction {int(delete_id)} not found.")
    else:
        st.error(f"Error: {delete_response.text}")

#=====UPDATE======

st.subheader("Update a Transaction")

update_id = st.number_input("Enter Transaction ID to update", min_value=1, step=1, key="update_id")

with st.form("update_transaction_form"):
    update_type = st.selectbox("Type", ["income", "expense"], key="update_type")
    update_category = st.text_input("Category", key="update_category")
    update_amount = st.number_input("Amount", min_value=0.0, step=0.01, key="update_amount")
    update_description = st.text_input("Description (optional)", key="update_description")
    update_date = st.date_input("Date", key="update_date")

    update_submitted = st.form_submit_button("Update Transaction")

    if update_submitted:
        if not update_category.strip():
            st.warning("Please enter a category before submitting.")
        else:
            update_response = requests.put(
                f"{API_BASE_URL}/transactions/{int(update_id)}",
                json={
                    "type": update_type,
                    "category": update_category,
                    "amount": update_amount,
                    "description": update_description,
                    "date": str(update_date),
                },
            )
            if update_response.status_code == 200:
                st.success(f"Transaction {int(update_id)} updated!")
                st.rerun()
            elif update_response.status_code == 404:
                st.warning(f"Transaction {int(update_id)} not found.")
            else:
                st.error(f"Error: {update_response.text}")

#======SHOW THE SUMMARY =========

st.header("Summary")

summary_response = requests.get(f"{API_BASE_URL}/summary")

if summary_response.status_code == 200:
    summary = summary_response.json()
    opening = summary['opening_balance']
    income = summary["total_income"]
    expense = summary["total_expense"]
    closing = summary["closing_balance"]
    

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Opening Balance", f"RM{opening:.2f}")
    col2.metric("Total Income", f"RM{income:.2f}")
    col3.metric("Total Expense", f"RM{expense:.2f}")
    col4.metric("Closing Balance", f"RM{closing:.2f}")
    
else:
    st.error("Could not land summary.")






