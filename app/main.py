# app/main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, csv
from app.ml_model import predict_strength
from app.optimizer import get_best_suppliers
from app import database

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup_fill_suppliers():
    csv_path = os.getenv("SUPPLIERS_CSV", "data/suppliers.csv")
    suppliers_list = []
    if os.path.exists(csv_path):
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for k, v in row.items():
                    if k in ["cement_cost","slag_cost","flyash_cost","water_cost","delivery_time","reliability_score"]:
                        try:
                            row[k] = float(v)
                        except:
                            pass
                suppliers_list.append(row)
        database.insert_suppliers_if_empty(suppliers_list)

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    # On first load, don't show suppliers yet
    recent = database.get_recent_predictions()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": None,
        "recent": recent,
        "top_suppliers": []  # empty list
    })

@app.post("/predict", response_class=HTMLResponse)
async def post_predict(
    request: Request,
    cement: float = Form(...),
    slag: float = Form(...),
    flyash: float = Form(...),
    water: float = Form(...),
    superplasticizer: float = Form(...),
    coarseaggregate: float = Form(...),
    fineaggregate: float = Form(...),
    age: float = Form(...)
):
    # Predict strength
    features = [cement, slag, flyash, water, superplasticizer, coarseaggregate, fineaggregate, age]
    pred = predict_strength(features)

    # Save prediction in DB
    record = {"features": dict(zip(
        ["cement","slag","flyash","water","superplasticizer","coarseaggregate","fineaggregate","age"], features
    )), "predicted_csMPa": pred}
    database.save_prediction(record)

    # Now get supplier recommendations *based on predicted strength*
    top_suppliers = get_best_suppliers(predicted_strength=pred)
    recent = database.get_recent_predictions()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": round(pred, 2),
        "recent": recent,
        "top_suppliers": top_suppliers
    })
