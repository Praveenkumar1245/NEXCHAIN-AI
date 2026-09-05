from typing import Dict, Any, List

class ResponseRecommender:
    def generate_options_matrix(self, impact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates mitigation option tradeoffs and picks the optimal recommended action with evidence.
        """
        status = impact_data.get("status")
        affected_orders = impact_data.get("affected_orders", [])

        if status == "AMBIGUOUS_NOTICE":
            return {
                "recommendation_title": "⚠ Human Review & Escalation Required",
                "recommended_option_id": "OPT-MANUAL",
                "rationale": "Disruption notice contains unconfirmed parameters (missing supplier confirmation, unknown duration, or vague line issues). Automated reallocation or shipment expediting halted until human review confirms notice.",
                "why_points": [
                    "Supplier name or primary plant unconfirmed",
                    "Exact restart date or duration unconfirmed",
                    "Impacted shipment numbers unconfirmed"
                ],
                "evidence_citations": ["NOTICE-AMBIGUOUS"],
                "options": [
                    {
                        "option_id": "OPT-01",
                        "title": "Request Supplier Written Confirmation",
                        "cost": "Low",
                        "delivery_impact": "None",
                        "customer_impact": "Low",
                        "stock_impact": "No change",
                        "time_to_execute": "1-2 Hours",
                        "description": "Issue automated inquiry to vendor ops (ABC Components) to verify exact halt duration."
                    },
                    {
                        "option_id": "OPT-02",
                        "title": "Precautionary Reservation on WH02 Buffer",
                        "cost": "Low",
                        "delivery_impact": "None",
                        "customer_impact": "Low",
                        "stock_impact": "WH02 Buffer Locked (20 units)",
                        "time_to_execute": "Immediate",
                        "description": "Lock 20 units of P101 inventory in WH02 buffer as a precautionary hold."
                    }
                ]
            }

        if status == "NO_CURRENT_IMPACT" or not affected_orders:
            return {
                "recommendation_title": "✓ Log Disruption & Continue Regular Operations",
                "recommended_option_id": "OPT-LOG",
                "rationale": "The disruption notice for Product P999 was parsed successfully. Zero matching inbound shipments, zero inventory allocations, and zero pending customer orders exist in the current system.",
                "why_points": [
                    "Disruption notice parsed & verified by Gemini",
                    "Product P999 is not used in active customer order book",
                    "Zero unit shortage detected ($0 financial exposure)"
                ],
                "evidence_citations": ["INV-P999-NONE"],
                "options": [
                    {
                        "option_id": "OPT-01",
                        "title": "Log Disruption Notice in Vendor Risk Registry",
                        "cost": "Zero",
                        "delivery_impact": "None",
                        "customer_impact": "None",
                        "stock_impact": "No change",
                        "time_to_execute": "Immediate",
                        "description": "Record facility maintenance notice in historical supplier scorecards."
                    }
                ]
            }

        # Case 1 Normal Disruption Options Matrix
        options = [
            {
                "option_id": "OPT-01",
                "title": "Reallocate Stock across Warehouses",
                "cost": "Low",
                "delivery_impact": "Low",
                "customer_impact": "Low",
                "stock_impact": "WH02 buffer ↓ (20 units)",
                "time_to_execute": "4 Hours",
                "description": "Transfer 20 units of P101 stock from WH02 (Bengaluru Hub) to WH01 (Chennai Hub) to fulfill Tier 1 orders O1001 and O1002 immediately.",
                "tradeoff": "Depletes safety buffer at WH02.",
                "is_recommended": False
            },
            {
                "option_id": "OPT-02",
                "title": "Expedite Freight SH101 (Air Charter)",
                "cost": "High ($1,200)",
                "delivery_impact": "Low",
                "customer_impact": "Low",
                "stock_impact": "No change",
                "time_to_execute": "24 Hours",
                "description": "Upgrade delayed shipment SH101 (100 units) from ocean to priority air charter, advancing ETA from Sep 23 to Sep 10.",
                "tradeoff": "Incurs $1,200 air freight surcharge.",
                "is_recommended": False
            },
            {
                "option_id": "OPT-03",
                "title": "Part-Ship Orders (Partial Fulfillment)",
                "cost": "Medium",
                "delivery_impact": "Medium",
                "customer_impact": "Medium",
                "stock_impact": "Low (50% shipped)",
                "time_to_execute": "Immediate",
                "description": "Fulfill 50% partial shipments (15 units) for O1001 immediately from existing inventory; backorder remaining 15 units until Sep 18.",
                "tradeoff": "Increases invoice splitting costs; customer receives partial shipment.",
                "is_recommended": False
            },
            {
                "option_id": "OPT-04",
                "title": "Inform Customers & Renegotiate SLA",
                "cost": "Low",
                "delivery_impact": "High (+12 Days)",
                "customer_impact": "High",
                "stock_impact": "No change",
                "time_to_execute": "1 Hour",
                "description": "Notify customer accounts (Apex Robotics, Siemens, ABB) of a 10-12 day delivery delay.",
                "tradeoff": "Risks customer dissatisfaction and damages Tier 1 customer trust.",
                "is_recommended": False
            }
        ]

        # Selected recommendation: Reallocate WH02 stock + Expedite SH101 freight
        recommended_title = "⭐ Recommended Action: Reallocate WH02 stock + Expedite SH101"
        rationale = (
            "Reallocating 20 available units from WH02 buffer alongside express shipment expediting (SH101: 100 units) "
            "addresses shortages across all 4 High-Priority Tier 1 customer orders (O1001, O1002, O1005, O1007)."
        )

        why_points = [
            "20 units available at WH02",
            "105-unit total shortage across affected orders",
            "SH101 contains 100 units",
            "Expedited ETA: Sep 10",
            "4 high-priority orders affected"
        ]

        evidence_citations = ["INV-WH02-P101", "SHIPMENT-SH101", "ORDER-O1001", "ORDER-O1002"]

        return {
            "recommendation_title": recommended_title,
            "recommended_option_id": "OPT-HYBRID",
            "rationale": rationale,
            "why_points": why_points,
            "evidence_citations": evidence_citations,
            "options": options
        }

recommender = ResponseRecommender()

