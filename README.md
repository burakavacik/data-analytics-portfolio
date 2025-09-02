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

-- Example 6: Subquery to find customers with above-average order amount
SELECT FirstName, LastName
FROM Customers c
WHERE CustomerID IN (
    SELECT CustomerID
    FROM Orders
    GROUP BY CustomerID
    HAVING AVG(Amount) > (SELECT AVG(Amount) FROM Orders)
);

-- Example 7: Create a Stored Procedure
CREATE PROCEDURE GetCustomerOrders @CustID INT
AS
BEGIN
    SELECT o.OrderID, o.OrderDate, o.Amount
    FROM Orders o
    WHERE o.CustomerID = @CustID;
END;

-- Example 8: Simple Trigger to log order insert
CREATE TABLE OrderLog (
    LogID INT IDENTITY PRIMARY KEY,
    OrderID INT,
    LogDate DATETIME DEFAULT GETDATE()
);

CREATE TRIGGER trg_AfterOrderInsert
ON Orders
AFTER INSERT
AS
BEGIN
    INSERT INTO OrderLog (OrderID)
    SELECT OrderID FROM inserted;
END;

## Sample Dashboards

![Sales Dashboard](dashboards/sales_dashboard.png)  
*Example Power BI dashboard showing sales trends by month and region*


