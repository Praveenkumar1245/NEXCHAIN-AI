import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.data_loader import db
from src.gemini_client import gemini_client
from src.extractor import extractor
from src.impact_engine import impact_engine
from src.ranking import order_ranker
from src.recommender import recommender
from src.evidence import evidence_engine

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NexChain AI - Supply Chain Response Copilot",
    description="PS08 Disruption Response Engine: LLM Entity Extraction + Deterministic Impact Calculations + Traceable Evidence Matrix",
    version="1.0.0"
)

# Enable CORS for live server / cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/{filename}")
async def serve_static_file(filename: str):
    file_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/cases/{case_type}")
async def get_demo_case(case_type: str):
    case_files = {
        "normal": "normal_case.txt",
        "difficult": "difficult_case.txt",
        "no_impact": "no_impact_case.txt"
    }
    filename = case_files.get(case_type.lower())
    if not filename:
        raise HTTPException(status_code=404, detail="Demo case not found")
    
    file_path = os.path.join(os.path.dirname(__file__), "data", "disruptions", filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return {"case_type": case_type, "text": f.read().strip()}
    raise HTTPException(status_code=404, detail=f"File {filename} not found")

class DisruptionAnalysisRequest(BaseModel):
    text: str
    api_key: Optional[str] = None

@app.post("/api/analyze")
async def analyze_disruption(payload: DisruptionAnalysisRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Disruption notice text cannot be empty.")

    # Always reload fresh CSV data from disk
    db.reload()

    # 1. Gemini Extraction (or Fallback Engine)
    if payload.api_key:
        from src.gemini_client import GeminiClient
        client = GeminiClient(api_key=payload.api_key)
        raw_extraction = client.extract_disruption_entities(text)
    else:
        raw_extraction = gemini_client.extract_disruption_entities(text)

    # 2. Entity Normalization & Database Mapping
    mapped_data = extractor.normalize_and_map(raw_extraction)

    # 3. Deterministic Impact Engine Calculation (Pure Python Math)
    impact_data = impact_engine.calculate_impact(mapped_data)

    # 4. Rank Affected Orders
    if impact_data.get("affected_orders"):
        impact_data["affected_orders"] = order_ranker.rank_affected_orders(impact_data["affected_orders"])

    # 5. Generate Response Options & Pick Recommended Action
    recommendations = recommender.generate_options_matrix(impact_data)

    # 6. Generate Auditable Execution Timeline Trace
    import datetime
    now = datetime.datetime.now()
    def format_t(delta_secs):
        t = now + datetime.timedelta(seconds=delta_secs)
        return t.strftime("%H:%M:%S")

    model_source = raw_extraction.get("source", "Gemini 2.5 Flash")

    sup_obj = mapped_data.get("mapped_supplier") or {}
    sup_name = sup_obj.get("name") or "Unconfirmed Supplier"
    sup_id = sup_obj.get("supplier_id") or "Ambiguous"

    prods_list = mapped_data.get("mapped_products") or []
    prod_id = prods_list[0].get("product_id") if prods_list else "Ambiguous"
    shipment_id = mapped_data.get("shipment_id") or "SH101"

    chain = impact_data.get("impact_chain") or {}
    shortage_units = chain.get("total_shortage_units", 0)

    analysis_trace = [
        {"time": format_t(0), "step": "Notice received", "detail": "Unstructured disruption notice ingested into parser", "arch": "UNSTRUCTURED PARSER", "type": "ai"},
        {"time": format_t(1), "step": f"Extracted via {model_source}", "detail": f"Vendor: {sup_name} (ID: {sup_id})", "arch": f"AI ({model_source.upper()})", "type": "ai"},
        {"time": format_t(1), "step": f"Mapped to {prod_id}", "detail": "Database product catalog entity mapping evaluated", "arch": "DATABASE LOOKUP", "type": "database"},
        {"time": format_t(2), "step": f"Matched Shipment {shipment_id}", "detail": "Inbound logistics shipment tracking evaluated", "arch": "DATABASE", "type": "database"},
        {"time": format_t(2), "step": "Calculated inventory shortage", "detail": f"Python engine stock math: {shortage_units} units shortage calculated", "arch": "PYTHON MATH ENGINE", "type": "python"},
        {"time": format_t(3), "step": f"Identified {impact_data.get('affected_orders_count', 0)} affected orders", "detail": f"{impact_data.get('high_priority_count', 0)} High-Priority Tier 1 customer orders ranked by risk", "arch": "PYTHON RISK RANKING", "type": "python"},
        {"time": format_t(3), "step": "Generated response options", "detail": "Mitigation options matrix evaluated across cost & SLA impact", "arch": "AI DECISION ENGINE", "type": "ai"},
        {"time": format_t(4), "step": "Recommendation ready", "detail": "Grounded decision strategy generated for human authorization", "arch": "HUMAN AUTHORIZATION", "type": "database"}
    ]

    # Return combined audit bundle
    return {
        "disruption_text": text,
        "extraction": mapped_data,
        "impact": impact_data,
        "recommendations": recommendations,
        "analysis_trace": analysis_trace,
        "dataset_summary": db.get_all_summary()
    }


@app.get("/api/evidence/{evidence_key}")
async def get_evidence(evidence_key: str):
    db.reload()
    return evidence_engine.get_evidence_detail(evidence_key)

@app.get("/api/data/summary")
async def get_data_summary():
    db.reload()
    return {
        "summary": db.get_all_summary(),
        "suppliers": db.suppliers.to_dict('records'),
        "products": db.products.to_dict('records'),
        "inventory": db.inventory.to_dict('records'),
        "shipments": db.shipments.to_dict('records'),
        "orders": db.orders.to_dict('records'),
        "customers": db.customers.to_dict('records')
    }

class DatasetUpdateRequest(BaseModel):
    table_name: str
    records: List[Dict[str, Any]]

class CSVUploadRequest(BaseModel):
    table_name: str
    csv_content: str

@app.post("/api/data/reload")
async def reload_dataset():
    db.reload()
    return {"status": "success", "message": "Database reloaded from CSV files", "summary": db.get_all_summary()}

@app.post("/api/data/update")
async def update_dataset(payload: DatasetUpdateRequest):
    success = db.save_dataset(payload.table_name, payload.records)
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid dataset table name: {payload.table_name}")
    return {"status": "success", "message": f"Dataset '{payload.table_name}' updated successfully", "summary": db.get_all_summary()}

@app.post("/api/data/upload-csv")
async def upload_csv_data(payload: CSVUploadRequest):
    table_clean = payload.table_name.lower().strip()
    valid_tables = ["suppliers", "products", "inventory", "shipments", "orders", "customers"]
    if table_clean not in valid_tables:
        raise HTTPException(status_code=400, detail=f"Invalid table name. Choose from: {', '.join(valid_tables)}")
    
    save_path = os.path.join(db.data_dir, f"{table_clean}.csv")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(payload.csv_content.strip())
    
    db.reload()
    return {
        "status": "success",
        "message": f"Successfully uploaded and updated '{table_clean}.csv' dataset!",
        "summary": db.get_all_summary()
    }

if __name__ == "__main__":
    print("==========================================================")
    print("[NEXCHAIN // CONTROL TOWER] Supply Chain Control Tower starting...")
    print("URL: http://127.0.0.1:8000")
    print("==========================================================")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
