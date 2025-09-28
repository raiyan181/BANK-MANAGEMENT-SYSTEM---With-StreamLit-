import json
import random
import string
from pathlib import Path
import streamlit as st


class Bank:
    database = 'data.json'
    data = []

    # Load database
    try:
        if Path(database).exists():
            with open(database, "r") as fs:
                data = json.load(fs)
        else:
            data = []
    except Exception as error:
        st.error(f'Error: {error}')
        data = []

    @staticmethod
    def __randomGenerate():
        alpha = random.choices(string.ascii_uppercase, k=3)
        num = random.choices(string.digits, k=3)
        special = random.choices('£$%^&*@!', k=1)
        acc_id = alpha + num + special
        random.shuffle(acc_id)
        return "".join(acc_id)

    @classmethod
    def __update(cls):
        with open(cls.database, 'w') as fs:
            json.dump(cls.data, fs, indent=4)

    @classmethod
    def __find_user(cls, acc_no, pin):
        return [u for u in cls.data if u['Account.No'] == acc_no and u['pin'] == pin]

    # --- Features ---
    def createAccount(self, name, age, email, pin):
        if age < 18 or len(str(pin)) != 4:
            return False, "❌ Account cannot be created (Age <18 or invalid PIN)"
        info = {
            'name': name,
            'age': age,
            'email': email,
            'pin': pin,
            'Account.No': Bank.__randomGenerate(),
            'Balance': 0
        }
        Bank.data.append(info)
        Bank.__update()
        return True, info

    def depositMoney(self, acc_no, pin, amount):
        user = Bank.__find_user(acc_no, pin)
        if not user:
            return False, "❌ Account not found"
        if amount <= 0 or amount > 10000:
            return False, "❌ Deposit must be between 1 and 10000"
        user[0]['Balance'] += amount
        Bank.__update()
        return True, user[0]

    def withdrawMoney(self, acc_no, pin, amount):
        user = Bank.__find_user(acc_no, pin)
        if not user:
            return False, "❌ Account not found"
        if amount <= 0 or amount > 10000:
            return False, "❌ Withdraw must be between 1 and 10000"
        if user[0]['Balance'] < amount:
            return False, "❌ Insufficient balance"
        user[0]['Balance'] -= amount
        Bank.__update()
        return True, user[0]

    def accountDetails(self, acc_no, pin):
        user = Bank.__find_user(acc_no, pin)
        if not user:
            return False, "❌ Account not found"
        return True, user[0]

    def updateDetails(self, acc_no, pin, name=None, email=None, new_pin=None):
        user = Bank.__find_user(acc_no, pin)
        if not user:
            return False, "❌ Account not found"
        user = user[0]
        if name: user['name'] = name
        if email: user['email'] = email
        if new_pin: user['pin'] = new_pin
        Bank.__update()
        return True, user

    def accountDelete(self, acc_no, pin):
        user = Bank.__find_user(acc_no, pin)
        if not user:
            return False, "❌ Account not found"
        Bank.data.remove(user[0])
        Bank.__update()
        return True, "✅ Account deleted successfully"


# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Bank Management System", layout="centered")
st.title("🏦 Bank Management System")

bank = Bank()

menu = st.sidebar.selectbox("Choose Other", [
    "Create Account", "Deposit Money", "Withdraw Money",
    "Account Details", "Update Details", "Delete Account"
])

if menu == "Create Account":
    with st.form("create_account"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, step=1)
        email = st.text_input("Email")
        pin = st.number_input("PIN (4 digits)", min_value=1000, max_value=9999, step=1)
        submit = st.form_submit_button("Create Account")
    if submit:
        success, result = bank.createAccount(name, age, email, pin)
        if success:
            st.success("Account Created Successfully!")
            st.json(result)
        else:
            st.error(result)

elif menu == "Deposit Money":
    with st.form("deposit"):
        acc_no = st.text_input("Account Number")
        pin = st.number_input("PIN", min_value=1000, max_value=9999, step=1)
        amount = st.number_input("Amount", min_value=1, step=1)
        submit = st.form_submit_button("Deposit")
    if submit:
        success, result = bank.depositMoney(acc_no, pin, amount)
        if success:
            st.success("Deposit Successful")
            st.json(result)
        else:
            st.error(result)

elif menu == "Withdraw Money":
    with st.form("withdraw"):
        acc_no = st.text_input("Account Number")
        pin = st.number_input("PIN", min_value=1000, max_value=9999, step=1)
        amount = st.number_input("Amount", min_value=1, step=1)
        submit = st.form_submit_button("Withdraw")
    if submit:
        success, result = bank.withdrawMoney(acc_no, pin, amount)
        if success:
            st.success("Withdrawal Successful")
            st.json(result)
        else:
            st.error(result)

elif menu == "Account Details":
    with st.form("details"):
        acc_no = st.text_input("Account Number")
        pin = st.number_input("PIN", min_value=1000, max_value=9999, step=1)
        submit = st.form_submit_button("Get Details")
    if submit:
        success, result = bank.accountDetails(acc_no, pin)
        if success:
            st.json(result)
        else:
            st.error(result)

elif menu == "Update Details":
    with st.form("update"):
        acc_no = st.text_input("Account Number")
        pin = st.number_input("PIN", min_value=1000, max_value=9999, step=1)
        new_name = st.text_input("New Name (leave blank if no change)")
        new_email = st.text_input("New Email (leave blank if no change)")
        new_pin = st.text_input("New PIN (leave blank if no change)")
        submit = st.form_submit_button("Update")
    if submit:
        new_pin = int(new_pin) if new_pin else None
        success, result = bank.updateDetails(acc_no, pin, new_name or None, new_email or None, new_pin)
        if success:
            st.success("Account Updated")
            st.json(result)
        else:
            st.error(result)

elif menu == "Delete Account":
    with st.form("delete"):
        acc_no = st.text_input("Account Number")
        pin = st.number_input("PIN", min_value=1000, max_value=9999, step=1)
        submit = st.form_submit_button("Delete")
    if submit:
        success, result = bank.accountDelete(acc_no, pin)
        if success:
            st.success(result)
        else:
            st.error(result)

st.markdown(
    """
    <style>
    .footer {
        position: relative;
        bottom: 0;
        width: 100%;
        background-color: none;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #555;
        
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display: none;}
        footer {visibility: hidden;}
    }
    </style>
    <div class="footer">
        -- ©2025 all rights reserved by <b>E H S A N</b>. --
    </div>
    """,
    unsafe_allow_html=True
)