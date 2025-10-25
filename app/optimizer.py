# app/optimizer.py
from app.database import get_all_suppliers

def compute_supplier_score(supplier, predicted_strength=None):
    """
    Compute a supplier score based on:
    - total cost (lower is better)
    - reliability (higher is better)
    - delivery time (lower is better)
    - predicted strength (affects weighting)
    """

    # Extract key fields
    cost_fields = [k for k in supplier.keys() if k.endswith("_cost")]
    total_cost = sum(float(supplier.get(k, 0)) for k in cost_fields)
    reliability = float(supplier.get("reliability_score", 0))
    delivery = float(supplier.get("delivery_time", 0))

    # Default weights
    weights = {"cost": 0.5, "reliability": 0.4, "delivery": 0.1}

    # Adjust weights based on predicted strength (simulate AI-driven optimization)
    if predicted_strength:
        if predicted_strength > 40:
            # High strength → prioritize reliability more
            weights = {"cost": 0.3, "reliability": 0.6, "delivery": 0.1}
        elif predicted_strength < 25:
            # Low strength → prioritize cost (cheaper materials)
            weights = {"cost": 0.7, "reliability": 0.2, "delivery": 0.1}

    # Normalize scores (higher is better)
    cost_score = 1 / (1 + total_cost)
    delivery_score = 1 / (1 + delivery)
    reliability_score = reliability

    # Weighted total
    final_score = (
        weights["cost"] * cost_score
        + weights["reliability"] * reliability_score
        + weights["delivery"] * delivery_score
    )

    return final_score, total_cost


def get_best_suppliers(predicted_strength=None, top_n=3):
    """Return top N suppliers ranked by computed score."""
    suppliers = get_all_suppliers()
    scored = []

    for s in suppliers:
        score, total_cost = compute_supplier_score(s, predicted_strength)
        scored.append({
            "supplier_id": s["supplier_id"],
            "score": round(score, 4),
            "total_cost": round(total_cost, 2),
            "delivery_time": s["delivery_time"],
            "reliability_score": s["reliability_score"]
        })

    # Sort by score descending
    sorted_list = sorted(scored, key=lambda x: x["score"], reverse=True)
    return sorted_list[:top_n]
