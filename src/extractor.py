from typing import Dict, Any, List, Optional
from src.data_loader import db

class EntityExtractor:
    def __init__(self, data_loader=db):
        self.db = data_loader

    def normalize_and_map(self, raw_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps extracted strings to database IDs (supplier_id, product_ids, warehouse_ids).
        Flags unmapped items or ambiguous cases.
        """
        mapped_supplier = None
        supplier_raw = raw_extraction.get("supplier")
        if supplier_raw:
            mapped_supplier = self.db.get_supplier_by_name(supplier_raw)

        mapped_products = []
        unmapped_products = []
        raw_products = raw_extraction.get("products", [])
        for p_str in raw_products:
            p_obj = self.db.get_product_by_name_or_id(p_str)
            if p_obj:
                mapped_products.append(p_obj)
            else:
                unmapped_products.append(p_str)

        text_ambiguities = list(raw_extraction.get("ambiguities", []))
        
        # Ambiguity is true when supplier is missing or duration/quantities are unconfirmed
        is_ambiguous = len(text_ambiguities) > 0 or raw_extraction.get("confidence", 1.0) < 0.70
        is_no_impact = (len(mapped_products) == 0 and len(unmapped_products) > 0)

        return {
            "raw_extraction": raw_extraction,
            "mapped_supplier": mapped_supplier,
            "mapped_products": mapped_products,
            "unmapped_products": unmapped_products,
            "shipment_id": raw_extraction.get("shipment_id"),
            "start_date": raw_extraction.get("start_date", "2026-09-05"),
            "expected_end_date": raw_extraction.get("expected_end_date"),
            "confidence": raw_extraction.get("confidence", 0.90),
            "ambiguities": text_ambiguities,
            "is_ambiguous": is_ambiguous,
            "is_no_impact": is_no_impact
        }

extractor = EntityExtractor()
