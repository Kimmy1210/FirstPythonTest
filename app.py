# app.py
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# 数据库连接配置（请根据实际情况修改）
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'o7a@bj',
    'database': 'bank_db'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/deposit', methods=['POST'])
def deposit():
    """
    请求格式：
    POST /deposit
    JSON Body:
    {
      "account_id": 1,
      "amount": 100.00
    }
    """
    data = request.get_json()
    account_id = data.get("account_id")
    amount = data.get("amount", 0.0)

    if not account_id or amount <= 0:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 更新账户余额
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, account_id))
    conn.commit()

    # 查询更新后的余额
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return jsonify({"message": "Deposit successful", "new_balance": float(row[0])}), 200
    else:
        return jsonify({"error": "Account not found"}), 404

@app.route('/withdraw', methods=['POST'])
def withdraw():
    """
    请求格式：
    POST /withdraw
    JSON Body:
    {
      "account_id": 1,
      "amount": 50.00
    }
    """
    data = request.get_json()
    account_id = data.get("account_id")
    amount = data.get("amount", 0.0)

    if not account_id or amount <= 0:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查当前余额
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Account not found"}), 404

    current_balance = float(row[0])
    if current_balance < amount:
        cursor.close()
        conn.close()
        return jsonify({"error": "Insufficient funds"}), 400

    # 更新余额
    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, account_id))
    conn.commit()

    # 查询更新后的余额
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
    updated_balance_row = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({"message": "Withdraw successful", "new_balance": float(updated_balance_row[0])}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
