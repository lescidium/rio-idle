SELECT comp.ticker
FROM money_values val
LEFT JOIN 
company comp ON comp.id = val.id_company
WHERE id_lines = 0 AND YEAR(filing_date) = 2019;