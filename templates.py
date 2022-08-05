from string import Template as Temp


card_html_with_score_ru = Temp("""
$tags
<b>$name</b>

$description
$stars $average_score ($number_of_scores)
⏱ $working_hours
💵 $average_price
📍 $address""")


card_short_html = Temp("""
$tags
<b>$name</b>

$description
💵 $average_price
📍 $address""")


card_short_html_score = Temp("""
$tags
<b>$name</b>

$description
$stars $average_score ($number_of_scores)
💵 $average_price
📍 $address""")


card_html_without_score_ru = Temp("""
$tags
<b>$name</b>

$description
⏱ $working_hours
💵 $average_price
📍 $address""")


card_html_with_score_en = Temp("""
$tags
<b>$name</b>

$description
$stars $average_score ($number_of_scores)
⏱ $working_hours
💵  $average_price
📍 $address_en""")


card_html_without_score_en = Temp("""
$tags
<b>$name</b>

$description
⏱ $working_hours
💵 $average_price
📍 $address_en""")


card_short_html_en = Temp("""
$tags
<b>$name</b>

$description
💵 $average_price
📍 $address_en""")


card_short_html_en_score = Temp("""
$tags
<b>$name</b>

$description
$stars $average_score ($number_of_scores)
💵 $average_price
📍 $address_en""")


card_for_moderator = Temp("""
<b>id</b> - $id

<b>$name</b>


$description

⏱ Режим работы - $working_hours

💵 Средний чек - $average_price  ₽

📍 $address

$phone

Категория - $types

Владелец - $owner
""")


post_template = Temp("""
<b>$header</b>
$text
""")


channel_template_with_score = Temp("""
$tags
<b>$name</b>

$description
$stars $average_score ($number_of_scores)
⏱ $working_hours
💵 $average_price
📍 $address
"""
)


channel_template_without_score = Temp("""
$tags
<b>$name</b>

$description
⏱ $working_hours
💵 $average_price
📍 $address
""")


channel_template_with_score_en = Temp("""
$tags
<b>$name</b>

$description
$stars $average_score ($number_of_scores)
⏱ $working_hours
💵 $average_price
📍 $address
"""
)


channel_template_without_score_en = Temp("""
$tags
<b>$name</b>

$description
⏱ $working_hours
💵 $average_price
📍 $address
""")

