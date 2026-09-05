from typing import List, Dict, Any

class OrderRanker:
    def rank_affected_orders(self, affected_orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks orders deterministically based on priority, risk level, promised date, and value.
        """
        priority_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        tier_map = {"Tier 1": 3, "Tier 2": 2, "Tier 3": 1}

        def sort_key(order):
            risk_score = priority_map.get(order.get("risk_level", "LOW"), 1) * 100
            prio_score = priority_map.get(order.get("priority", "Low").upper(), 1) * 10
            tier_score = tier_map.get(order.get("customer_tier", "Tier 3"), 1)
            # Earlier promised date gets higher rank
            date_score = order.get("promised_date", "9999-99-99")
            val_score = order.get("total_value", 0)

            return (-risk_score, -prio_score, -tier_score, date_score, -val_score)

        sorted_orders = sorted(affected_orders, key=sort_key)
        
        # Add rank index
        for idx, ord_item in enumerate(sorted_orders, start=1):
            ord_item["rank"] = idx

        return sorted_orders

order_ranker = OrderRanker()
