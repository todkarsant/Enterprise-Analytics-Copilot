import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx


def _extract_json_object(text: str) -> dict:
    """Parse a JSON object from an LLM response, tolerating fenced/extra text."""
    text = (text or "").strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    # Strip markdown fences if the model returned them.
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    # Recover the first balanced JSON object.
    start = cleaned.find("{")
    if start >= 0:
        depth = 0
        in_string = False
        escaped = False
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = cleaned[start:i + 1]
                    try:
                        obj = json.loads(candidate)
                        if isinstance(obj, dict):
                            return obj
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"LLM did not return a valid JSON object: {text[:500]}")

@dataclass
class LLMResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = "unknown"

class LLMProvider(ABC):
    @abstractmethod
    def generate_sql(self, question: str, schema: str, repair_reason: str | None = None) -> LLMResult: ...

    @abstractmethod
    def summarize(self, question: str, columns: list[str], rows: list[list]) -> LLMResult: ...

class MockProvider(LLMProvider):
    def generate_sql(self, question: str, schema: str, repair_reason: str | None = None) -> LLMResult:
        q = question.lower()
        if "highest revenue" in q or "top stores" in q or "highest sales" in q:
            sql = "SELECT store_id, SUM(sales) AS total_sales FROM store_week GROUP BY store_id ORDER BY total_sales DESC LIMIT 10"
        elif "sales by region" in q or "revenue by region" in q:
            sql = "SELECT region, SUM(sales) AS total_sales FROM store_week GROUP BY region ORDER BY total_sales DESC"
        elif "average promo spend" in q:
            sql = "SELECT region, AVG(promo_spend) AS avg_promo_spend FROM store_week GROUP BY region ORDER BY avg_promo_spend DESC"
        elif "highest orders" in q and "january" in q:
            sql = "SELECT store_id, SUM(orders) AS total_orders FROM store_week WHERE week_start >= '2026-01-01' AND week_start < '2026-02-01' GROUP BY store_id ORDER BY total_orders DESC LIMIT 1"
        elif "total sales" in q and "last month" in q:
            sql = """SELECT SUM(sales) AS total_sales
FROM store_week
WHERE week_start >= date((SELECT MAX(week_start) FROM store_week), 'start of month', '-1 month')
  AND week_start < date((SELECT MAX(week_start) FROM store_week), 'start of month')"""
        elif "monthly sales" in q:
            sql = "SELECT substr(week_start, 1, 7) AS month, region, SUM(sales) AS total_sales FROM store_week GROUP BY month, region ORDER BY month, total_sales DESC"
        elif "ads spend" in q:
            sql = "SELECT region, SUM(ads_spend) AS total_ads_spend FROM store_week GROUP BY region ORDER BY total_ads_spend DESC"
        else:
            raise ValueError("Mock provider has no deterministic template for this question. Use LLM_PROVIDER=ollama or azure_openai for general NL2SQL.")
        return LLMResult(sql, 0, 0, "mock")

    def summarize(self, question: str, columns: list[str], rows: list[list]) -> LLMResult:
        if not rows:
            return LLMResult("The query returned no rows.", model="mock")
        if "store_id" in columns and "total_sales" in columns:
            i1, i2 = columns.index("store_id"), columns.index("total_sales")
            return LLMResult(f"The top store by revenue is {rows[0][i1]} with {rows[0][i2]:,.2f} in total sales.", model="mock")
        if "region" in columns and "total_sales" in columns:
            return LLMResult(f"The query returned regional sales for {len(rows)} region-level result(s).", model="mock")
        return LLMResult(f"The query returned {len(rows)} row(s).", model="mock")

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 120):
        self.url = base_url.rstrip("/") + "/api/chat"
        self.model = model
        self.timeout = timeout_seconds

    def _chat(self, prompt: str) -> LLMResult:
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False, "format": "json", "options": {"temperature": 0}}
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.url, json=payload)
            response.raise_for_status()
            data = response.json()
        return LLMResult(
            text=data["message"]["content"],
            input_tokens=int(data.get("prompt_eval_count") or 0),
            output_tokens=int(data.get("eval_count") or 0),
            model=data.get("model", self.model),
        )

    def generate_sql(self, question: str, schema: str, repair_reason: str | None = None) -> LLMResult:
        repair = f"Previous validation error: {repair_reason}\nFix it." if repair_reason else ""
        prompt = f"""You are a senior analytics SQL engineer generating SQLite SQL for a production analytics system.
Generate exactly one read-only SELECT statement.

Rules:
1. Use only the supplied schema and its columns.
2. Never mutate data; no INSERT, UPDATE, DELETE, DDL, PRAGMA, or multiple statements.
3. Return ONLY a JSON object with exactly one key: sql.
4. The sql value must be a valid SQLite SELECT statement.
5. For relative dates such as last month, use the latest date available in the dataset as the reference point, not the current calendar date.
6. week_start is stored as ISO text YYYY-MM-DD.
7. For the previous complete month, use SQLite expressions such as date((SELECT MAX(week_start) FROM store_week), 'start of month', '-1 month').
8. The current dataset has one analytical table: store_week. Prefer a direct aggregation over this table.
9. Do NOT self-join store_week. Do NOT create derived-table aliases such as T1/T2 unless the supplied schema explicitly requires a multi-table join.
10. For "highest sales", "top stores by sales", or equivalent, use SUM(sales), GROUP BY store_id, ORDER BY the aggregate alias DESC, and LIMIT 10.
11. Do not reference a table alias that is not defined in the same SELECT.
12. Do not put explanations or markdown in the response.

{repair}
Schema:
{schema}
Question:
{question}"""
        result = self._chat(prompt)
        obj = _extract_json_object(result.text)
        result.text = obj["sql"]
        return result

    def summarize(self, question: str, columns: list[str], rows: list[list]) -> LLMResult:
        prompt = f"""Answer using only the supplied SQL result. Do not invent facts. Return JSON {{\"answer\": \"...\"}}.
Question: {question}\nColumns: {columns}\nRows: {rows}"""
        result = self._chat(prompt)
        obj = _extract_json_object(result.text)
        result.text = obj["answer"]
        return result

class AzureOpenAIProvider(LLMProvider):
    def __init__(self, endpoint: str, api_key: str, api_version: str, deployment: str):
        if not all((endpoint, api_key, api_version, deployment)):
            raise ValueError("Azure OpenAI requires endpoint, API key, API version and deployment.")
        from openai import AzureOpenAI
        self.client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)
        self.deployment = deployment

    def _chat(self, prompt: str) -> LLMResult:
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "system", "content": "You are a precise analytics AI engineer."}, {"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        usage = response.usage
        return LLMResult(
            text=response.choices[0].message.content or "{}",
            input_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
            model=self.deployment,
        )

    def generate_sql(self, question: str, schema: str, repair_reason: str | None = None) -> LLMResult:
        repair = f"Previous validation error: {repair_reason}. Correct it." if repair_reason else ""
        result = self._chat(f"Generate one read-only SQLite SELECT. Use only this schema. Return JSON with key sql. {repair}\nSchema:\n{schema}\nQuestion:\n{question}")
        result.text = json.loads(result.text)["sql"]
        return result

    def summarize(self, question: str, columns: list[str], rows: list[list]) -> LLMResult:
        result = self._chat(f"Answer using only the result. Return JSON with key answer. Question={question}; columns={columns}; rows={rows}")
        result.text = json.loads(result.text)["answer"]
        return result
