SELECT tick FROM 
company comp
LEFT JOIN
money_values val ON val.id_comp = comp.id
WHERE calendar_date = '2019-12-31' AND id_lines = 1;