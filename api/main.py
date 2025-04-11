from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/getdate")
def get_date():
    now = datetime.now().strftime("%A, %B %d %Y")
    return {"date": now}
