from dataclasses import dataclass
import re

ALLOWED_COLUMNS = {
    "store_week": {
        "store_id", "week_start", "region", "sales", "orders", "promo_spend", "ads_spend"
    }
}
ALLOWED_TABLES = set(ALLOWED_COLUMNS)

@dataclass(frozen=True)
class SchemaItem:
    name: str
    description: str
    synonyms: tuple[str, ...] = ()

CATALOG = [
    SchemaItem("store_week", "Weekly store-level commercial performance fact table.", ("store", "weekly", "store performance")),
    SchemaItem("sales", "Gross sales/revenue amount for the store-week.", ("revenue", "sales")),
    SchemaItem("orders", "Number of customer orders for the store-week.", ("order count", "orders")),
    SchemaItem("promo_spend", "Spend attributable to promotions for the store-week.", ("promotion", "promo", "discount")),
    SchemaItem("ads_spend", "Paid advertising spend for the store-week.", ("advertising", "ads", "marketing spend")),
    SchemaItem("store_id", "Unique store identifier.", ("store", "location")),
    SchemaItem("region", "Commercial region containing the store.", ("geography", "area")),
    SchemaItem("week_start", "ISO date representing the first day of the reporting week.", ("week", "date")),
]

SCHEMA_TEXT = """TABLE store_week (
  store_id TEXT NOT NULL,
  week_start TEXT NOT NULL, -- ISO date YYYY-MM-DD
  region TEXT NOT NULL,
  sales REAL NOT NULL,
  orders INTEGER NOT NULL,
  promo_spend REAL NOT NULL,
  ads_spend REAL NOT NULL
)

Business definitions:
- sales: commercial sales/revenue amount for a store-week.
- orders: number of orders in the store-week.
- promo_spend: promotion spend.
- ads_spend: paid advertising spend.
- week_start: first day of the reporting week.
"""

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))

def retrieve_schema(question: str, top_k: int = 6) -> dict:
    q = _tokens(question)
    scored = []
    for item in CATALOG:
        haystack = _tokens(" ".join((item.name, item.description, *item.synonyms)))
        score = len(q & haystack)
        scored.append((score, item))
    scored.sort(key=lambda x: (-x[0], x[1].name))
    selected = [item for score, item in scored if score > 0][:top_k]
    if not selected:
        selected = CATALOG[:top_k]
    selected_names = {x.name for x in selected}
    columns = [c for c in ALLOWED_COLUMNS["store_week"] if c in selected_names]
    if "store_week" in selected_names or not columns:
        columns = sorted(ALLOWED_COLUMNS["store_week"])
    return {
        "table": "store_week",
        "columns": columns,
        "items": [
            {"name": x.name, "description": x.description, "synonyms": list(x.synonyms)}
            for x in selected
        ],
        "context": SCHEMA_TEXT,
    }
