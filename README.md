# Data Analytics Portfolio  

Self-developed SQL training document and sample dashboards.  

---

## SQL Training Document  

This repository contains a self-developed **SQL Training Document**.  
It covers SQL fundamentals, queries, joins, functions, stored procedures, triggers, views, and integration with Visual Studio.  

📄 Files:  
- `SQL_Training_Document.pdf` → Full training material  

---

## Author  

**Burak Avacık**  
USMC Veteran | Industrial Engineer | Data & Business Analyst | Secret Clearance  

---

## Sample SQL Query  

```sql
-- Show all customers who live in San Francisco
SELECT CustomerID, FirstName, LastName, City
FROM Customers
WHERE City = 'San Francisco';
