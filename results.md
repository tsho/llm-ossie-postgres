# Demo Results

## Configuration

| Item | Value |
|------|-------|
| LLM Provider | Snowflake Cortex (REST API) |
| Model | `llama3.1-70b` |
| Database | PostgreSQL 17.7 (Homebrew, aarch64-apple-darwin) |
| Semantic Model | Apache Ossie `retail_model.yaml` |
| Date | 2026-07-14 |

## Results

### Question 1: "What is the total sales revenue for June?"

| | Without Ossie | With Ossie |
|--|--|--|
| SQL | `SELECT SUM(ss_ext_sales_price) FROM store_sales INNER JOIN date_dim ON store_sales.ss_sold_date_sk = date_dim.d_date_sk WHERE date_dim.d_month_name = 'June'` | `SELECT SUM(T2.ss_ext_sales_price) FROM date_dim AS T1 INNER JOIN store_sales AS T2 ON T1.d_date_sk = T2.ss_sold_date_sk WHERE T1.d_month_name = 'June'` |
| Result | 1160.73 | 1160.73 |
| Correct? | Yes | Yes |
| Notes | Both used the correct column (`ss_ext_sales_price`) and joined to `date_dim`. The LLM inferred the join from foreign key constraints in the DDL. |

### Question 2: "Show me sales by brand."

| | Without Ossie | With Ossie |
|--|--|--|
| SQL | `SELECT i.i_brand, SUM(ss.ss_ext_sales_price) AS total_sales FROM item i JOIN store_sales ss ON i.i_item_sk = ss.ss_item_sk GROUP BY i.i_brand` | `SELECT T2.i_brand, SUM(T1.ss_ext_sales_price) FROM store_sales AS T1 INNER JOIN item AS T2 ON T1.ss_item_sk = T2.i_item_sk GROUP BY T2.i_brand` |
| Result | 8 brands, correct values | 8 brands, correct values |
| Correct? | Yes | Yes |
| Notes | Both correctly joined `store_sales` to `item` and grouped by brand. The foreign key constraint in DDL was sufficient for this case. |

### Question 3: "What is the customer lifetime value?"

| | Without Ossie | With Ossie |
|--|--|--|
| SQL | `SELECT SUM(ss_ext_sales_price) FROM store_sales` | `SELECT SUM(T1.ss_ext_sales_price) / COUNT(DISTINCT T1.ss_customer_sk) FROM store_sales AS T1` |
| Result | **2693.37** | **538.67** |
| Correct? | **No** — returns total revenue, not per-customer value | **Yes** — uses the metric definition from Ossie |
| Notes | Without Ossie, the LLM has no definition of "customer lifetime value" and falls back to a simple sum. With Ossie, the `customer_lifetime_value` metric is defined as `SUM(ss_ext_sales_price) / COUNT(DISTINCT ss_customer_sk)`, which the LLM correctly applies. |

## Summary

| Question | Without Ossie | With Ossie | Improvement |
|----------|:---:|:---:|:---:|
| Total sales for June | Correct | Correct | - |
| Sales by brand | Correct | Correct | - |
| Customer LTV | **Wrong** (total, not per-customer) | **Correct** | Ossie metric definition |

### Key Takeaway

For simple queries where DDL foreign keys provide sufficient context (Q1, Q2), Ossie adds no difference. However, for **business-specific calculations** like Customer Lifetime Value (Q3), the Ossie semantic model's `metrics` definitions are essential for the LLM to generate correct SQL. Without explicit metric definitions, the LLM cannot distinguish "total revenue" from "revenue per customer."

### Ossie Features That Made the Difference

- **`metrics.customer_lifetime_value`** — Pre-defined formula: `SUM(ss_ext_sales_price) / COUNT(DISTINCT ss_customer_sk)`
- **`ai_context.instructions`** — Clarifies that "sales" means `ss_ext_sales_price`, not `ss_sales_price`
- **`ai_context.synonyms`** — Maps business terms ("CLV", "LTV") to the correct metric
