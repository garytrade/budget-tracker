from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import init_db, get_connection

app = FastAPI(title="Budget Tracker API")

@app.on_event("startup")
def startup():
    init_db()

class TransactionIn(BaseModel):
    type: str  #In or out
    category: str  #food,rent, grocery
    amount: float
    description: str = ""
    date: str

#-----POST------
@app.post("/transactions")
def create_transaction(transaction: TransactionIn):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO transactions ( type, category, amount, description, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.description,
                transaction.date,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        return {"id": new_id, "message": "Transaction created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

#-----GET-----

@app.get("/transactions")
def list_transactions(category: str = None, type: str = None):
    conn = get_connection()
    try:
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []        
        
        if category:
            query += " AND category = ?"
            params.append(category)
           
        if type:
            query += " AND type = ?"
            params.append(type)

        query += "ORDER BY id DESC"

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

#------PUT------

@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, transaction: TransactionIn):
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM transactionsn WHERE id =?", (transaction_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Transaction not found")
        conn.execute(
            """
            UPDATE transactions
            SET type = ?, category = ?, amount = ?, description = ?, date = ?,
            WHERE id = ?
            """,
            (
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.description,
                transaction.date,
                transaction_id,
            ),
        )
        conn.commit()
        return {"message": "Transaction updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()


#-----DELETE-------
@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        conn.execute("DELETE FROM transaction WHERE id = ?", (transaction_id,))
        conn.commit()
        return {"message": "Transaction deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        conn.close()

#----opening balance-----
class OpeningBalanceIn(BaseModel):
    opening_balance: float

@app.put("/settings/opening-balance")
def update_opening_balance(payload: OpeningBalanceIn):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE settings SET opening_balance = ? WHERE id = 1",
            (payload.opening_balance,),
        )
        conn.commit()
        return {"message": "Opening balance updated", "opening_balance": payload.opening_balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        conn.close()   

#-----GET ( SUMMARY)
@app.get("/summary")
def get_summary():
    conn = get_connection()
    try:
        setting_row = conn.execute(
            "SELECT opening_balance FROM settings WHERE id = 1"
        ).fetchone()
        opening_balance = setting_row["opening_balance"]
        
        income_row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as total FROM transactions WHERE type = 'income'"
        ).fetchone()
        expense_row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) as total FROM transactions WHERE type = 'expense'"
        ).fetchone()

        total_income = income_row["total"]
        total_expense = expense_row["total"]
        closing_balance = opening_balance + total_income - total_expense

        return {
            "opening balance": opening_balance,
            "total_income": total_income,
            "total_expense": total_expense,
            "closing_balance": closing_balance,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()




        

    
    



        

    
