from string import Template as Temp


card_html_with_score_ru = Temp("""
<b>$name</b>


$description

⏱ Режим работы - $working_hours $working_days

⭐️ Оценка - $average_score ($number_of_scores)

💵 Средний чек - $average_price  ₽""")


card_short_html = Temp("""
<b>$name</b>


$description

💵 Средний чек - $average_price  ₽""")


card_html_without_score_ru = Temp("""
<b>$name</b>


$description

⏱ Режим работы - $working_hours $working_days

💵 Средний чек - $average_price  ₽""")


card_html_with_score_en = Temp("""
<b>$name</b>


$description

⏱ Operating mode - $working_hours $working_days

⭐️ Rating - $average_score ($number_of_scores)

💵 Average check - $average_price  ₽""")


card_html_without_score_en = Temp("""
<b>$name</b>


$description

⏱ Operating mode - $working_hours $working_days

💵 Average check - $average_price  ₽""")


card_short_html_en = Temp("""
<b>$name</b>


$description

💵 Average check - $average_price  ₽""")
