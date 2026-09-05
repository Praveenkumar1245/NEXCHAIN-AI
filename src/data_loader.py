import os
import pandas as pd
from typing import Dict, List, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

class DataLoader:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.reload()

    def reload(self):
        self.suppliers = pd.read_csv(os.path.join(self.data_dir, "suppliers.csv"))
        self.products = pd.read_csv(os.path.join(self.data_dir, "products.csv"))
        self.inventory = pd.read_csv(os.path.join(self.data_dir, "inventory.csv"))
        self.shipments = pd.read_csv(os.path.join(self.data_dir, "shipments.csv"))
        self.orders = pd.read_csv(os.path.join(self.data_dir, "orders.csv"))
        self.customers = pd.read_csv(os.path.join(self.data_dir, "customers.csv"))

    def get_supplier_by_id(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        res = self.suppliers[self.suppliers['supplier_id'].str.upper() == supplier_id.upper()]
        return res.iloc[0].to_dict() if not res.empty else None

    def get_supplier_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        name_clean = name.lower().strip()
        for _, row in self.suppliers.iterrows():
            if name_clean in row['name'].lower() or row['name'].lower() in name_clean:
                return row.to_dict()
        return None

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        clean_id = product_id.replace("-", "").replace(" ", "").upper()
        for _, row in self.products.iterrows():
            curr_id = str(row['product_id']).replace("-", "").replace(" ", "").upper()
            if curr_id == clean_id:
                return row.to_dict()
        return None

    def get_product_by_name_or_id(self, term: str) -> Optional[Dict[str, Any]]:
        p_by_id = self.get_product_by_id(term)
        if p_by_id:
            return p_by_id
        term_clean = term.lower().strip()
        for _, row in self.products.iterrows():
            if term_clean in row['name'].lower() or row['name'].lower() in term_clean:
                return row.to_dict()
        return None

    def get_inventory_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        res = self.inventory[self.inventory['product_id'].str.upper() == product_id.upper()]
        return res.to_dict('records')

    def get_shipments_for_supplier(self, supplier_id: str) -> List[Dict[str, Any]]:
        res = self.shipments[self.shipments['supplier_id'].str.upper() == supplier_id.upper()]
        return res.to_dict('records')

    def get_shipments_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        res = self.shipments[self.shipments['product_id'].str.upper() == product_id.upper()]
        return res.to_dict('records')

    def get_orders_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        res = self.orders[self.orders['product_id'].str.upper() == product_id.upper()]
        # Merge customer name
        records = []
        for _, row in res.iterrows():
            item = row.to_dict()
            cust = self.customers[self.customers['customer_id'] == item['customer_id']]
            if not cust.empty:
                item['customer_name'] = cust.iloc[0]['name']
                item['customer_tier'] = cust.iloc[0]['tier']
            records.append(item)
        return records

    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        res = self.customers[self.customers['customer_id'].str.upper() == customer_id.upper()]
        return res.iloc[0].to_dict() if not res.empty else None

    def get_all_summary(self) -> Dict[str, Any]:
        return {
            "suppliers_count": len(self.suppliers),
            "products_count": len(self.products),
            "inventory_records": len(self.inventory),
            "shipments_count": len(self.shipments),
            "orders_count": len(self.orders),
            "total_order_value": int(self.orders['total_value'].sum())
        }

db = DataLoader()
