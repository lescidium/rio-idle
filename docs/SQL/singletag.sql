SELECT tick, tag, calendar_date, value
FROM company comp
LEFT JOIN
money_values val ON val.id_comp = comp.id
LEFT JOIN
statement_lines lin ON lin.id = val.id_lines
LEFT JOIN
line_order ord ON ord.id_statement_line = val.id_lines
LEFT JOIN
statement_titles tit ON tit.id = ord.id_statement_type
WHERE tick = 'AAPL' AND lin.tag = 'revenues'
ORDER BY tit.id, calendar_date DESC, ord.order