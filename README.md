# data-analytics-portfolio
Self-developed SQL training document and sample dashboards
# SQL Training Document

This repository contains a self-developed **SQL Training Document**.  
It covers SQL fundamentals, queries, joins, functions, stored procedures, and integration with Visual Studio.  

📄 Files:  
- `SQL_Training_Document.pdf` → Full training material  

---

Author: **Burak Avacık**  
USMC Veteran | Industrial Engineer | Data & Business Analyst | Secret Clearance

-- Example 1: Create a simple Customers table
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    City VARCHAR(50),
    JoinDate DATE
);

-- Example 2: Insert sample data
INSERT INTO Customers (CustomerID, FirstName, LastName, City, JoinDate)
VALUES (1, 'John', 'Doe', 'San Francisco', '2023-01-15');

-- Example 3: Query data with filter and sorting
SELECT FirstName, LastName, City
FROM Customers
WHERE City = 'San Francisco'
ORDER BY JoinDate DESC;

-- Example 4: Aggregate query
SELECT City, COUNT(*) AS TotalCustomers
FROM Customers
GROUP BY City
ORDER BY TotalCustomers DESC;
