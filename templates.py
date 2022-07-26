from string import Template as Temp


card_html_with_score = Temp("""
<b>$name</b>


$description

⏱ Режим работы - $working_hours $working_days

⭐️ Оценка - $average_score ($number_of_scores)

💵 Средний чек - $average_price  ₽""")


card_short_html = Temp("""
<b>$name</b>


$description

💵 Средний чек - $average_price  ₽""")


card_html_without_score = Temp("""
<b>$name</b>


$description

⏱ Режим работы - $working_hours $working_days

💵 Средний чек - $average_price  ₽""")