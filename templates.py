from string import Template as Temp


card_html_with_score_ru = Temp("""
<b>$name</b>


$description

⏱ Режим работы - $working_hours

⭐️ Оценка - $average_score ($number_of_scores)

💵 Средний чек - $average_price  ₽

$address""")


card_short_html = Temp("""
<b>$name</b>


$description

💵 Средний чек - $average_price  ₽

$address""")


card_html_without_score_ru = Temp("""
<b>$name</b>


$description

⏱ Режим работы - $working_hours

💵 Средний чек - $average_price  ₽

$address""")


card_html_with_score_en = Temp("""
<b>$name</b>


$description

⏱ Operating mode - $working_hours

⭐️ Rating - $average_score ($number_of_scores)

💵 Average check - $average_price  ₽

$address_en""")


card_html_without_score_en = Temp("""
<b>$name</b>


$description

⏱ Operating mode - $working_hours

💵 Average check - $average_price  ₽

$address_en""")


card_short_html_en = Temp("""
<b>$name</b>


$description

💵 Average check - $average_price  ₽

$address_en""")


card_for_moderator = Temp("""
<b>id</b> - $id

<b>$name</b>


$description

⏱ Режим работы - $working_hours

💵 Средний чек - $average_price  ₽

$address

$phone

Категория - $types

Владелец - $owner
""")
