# app/ml_model.py
import joblib
import numpy as np
import os

MODEL_PATH = os.getenv("MODEL_PATH", "models/concrete_strength_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

def predict_strength(features):
    """
    features: list or 1D-array of 8 numbers in order:
    [cement, slag, flyash, water, superplasticizer, coarseaggregate, fineaggregate, age]
    returns float prediction
    """
    arr = np.array(features).reshape(1, -1)
    pred = model.predict(arr)
    return float(pred[0])
