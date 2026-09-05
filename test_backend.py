import sys
from src.data_loader import db
from src.gemini_client import gemini_client
from src.extractor import extractor
from src.impact_engine import impact_engine
from src.ranking import order_ranker
from src.recommender import recommender
from src.evidence import evidence_engine

def safe_print(msg: str):
    """Encodes unicode string safely for Windows console printing"""
    print(msg.encode('ascii', errors='replace').decode('ascii'))

def run_tests():
    print("--- 1. Testing Data Loader ---")
    summary = db.get_all_summary()
    print("Dataset summary:", summary)
    assert summary["suppliers_count"] == 3
    assert summary["products_count"] == 4
    assert summary["orders_count"] == 9
    print("[OK] DataLoader passed!")

    print("\n--- 2. Testing Case 1 (Normal Disruption) ---")
    case1_text = "ABC Components has stopped production for P-101 Motor Controller until 18 Sept due to equipment failure."
    ext1 = gemini_client.extract_disruption_entities(case1_text)
    mapped1 = extractor.normalize_and_map(ext1)
    impact1 = impact_engine.calculate_impact(mapped1)
    impact1["affected_orders"] = order_ranker.rank_affected_orders(impact1["affected_orders"])
    recs1 = recommender.generate_options_matrix(impact1)

    print(f"Case 1 Status: {impact1['status']}")
    print(f"Affected Orders Count: {impact1['affected_orders_count']}")
    safe_print(f"Recommended Action: {recs1['recommendation_title']}")
    assert impact1["status"] == "IMPACT_DETECTED"
    assert impact1["affected_orders_count"] == 7
    print("[OK] Case 1 passed!")

    print("\n--- 3. Testing Case 2 (Difficult / Ambiguous Disruption) ---")
    case2_text = "We're having some production issues with the controller line at our plant. Some deliveries could potentially be impacted next week."
    ext2 = gemini_client.extract_disruption_entities(case2_text)
    mapped2 = extractor.normalize_and_map(ext2)
    impact2 = impact_engine.calculate_impact(mapped2)

    print(f"Case 2 Status: {impact2['status']}")
    print(f"Ambiguities: {impact2['ambiguities']}")
    assert impact2["status"] == "AMBIGUOUS_NOTICE"
    print("[OK] Case 2 passed!")

    print("\n--- 4. Testing Case 3 (No Impact Disruption) ---")
    case3_text = "ABC Components has temporarily stopped production of Product P999 due to scheduled facility maintenance."
    ext3 = gemini_client.extract_disruption_entities(case3_text)
    mapped3 = extractor.normalize_and_map(ext3)
    impact3 = impact_engine.calculate_impact(mapped3)

    print(f"Case 3 Status: {impact3['status']}")
    print(f"Affected Orders Count: {impact3['affected_orders_count']}")
    assert impact3["status"] == "NO_CURRENT_IMPACT"
    assert impact3["affected_orders_count"] == 0
    print("[OK] Case 3 passed!")

    print("\n--- 5. Testing Evidence Tracing Engine ---")
    ev1 = evidence_engine.get_evidence_detail("INV-WH01-P101")
    print("Evidence INV-WH01-P101:", ev1["data"])
    assert ev1["verification_status"] == "VERIFIED_FROM_SOURCE_CSV"

    ev2 = evidence_engine.get_evidence_detail("ORDER-O1001")
    print("Evidence ORDER-O1001:", ev2["data"])
    assert ev2["verification_status"] == "VERIFIED_FROM_SOURCE_CSV"
    print("[OK] Evidence Engine passed!")

    print("\n==========================================")
    print("SUCCESS: ALL BACKEND UNIT TESTS PASSED!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
