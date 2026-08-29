"""
Bilim Jangi — boshlang'ich savollar banki (1-bosqich: 60+ ta savol).
Har bir savol: text, option_a..d, correct_option (A/B/C/D), difficulty, category.

Admin panel orqali yangi savol qo'shish mumkin (keyingi bosqichda /admin/questions
bo'limi qo'shiladi). Bu ro'yxat ilova birinchi marta ishga tushganda (baza bo'sh
bo'lsa) avtomatik ma'lumotlar bazasiga yuklanadi.
"""

QUESTIONS: list[dict] = [
    # --- Geografiya ---
    {"text": "O'zbekiston poytaxti qaysi shahar?", "option_a": "Samarqand", "option_b": "Buxoro", "option_c": "Toshkent", "option_d": "Andijon", "correct_option": "C", "difficulty": "easy", "category": "geografiya"},
    {"text": "Dunyodagi eng katta okean qaysi?", "option_a": "Atlantika", "option_b": "Tinch okeani", "option_c": "Hind okeani", "option_d": "Shimoliy Muz okeani", "correct_option": "B", "difficulty": "easy", "category": "geografiya"},
    {"text": "Dunyodagi eng baland tog' cho'qqisi qaysi?", "option_a": "Elbrus", "option_b": "Kilimanjaro", "option_c": "Everest", "option_d": "Mont Blan", "correct_option": "C", "difficulty": "easy", "category": "geografiya"},
    {"text": "Rossiyaning poytaxti qaysi shahar?", "option_a": "Sankt-Peterburg", "option_b": "Moskva", "option_c": "Kazan", "option_d": "Novosibirsk", "correct_option": "B", "difficulty": "easy", "category": "geografiya"},
    {"text": "Afrikadagi eng uzun daryo qaysi?", "option_a": "Kongo", "option_b": "Niger", "option_c": "Nil", "option_d": "Zambezi", "correct_option": "C", "difficulty": "medium", "category": "geografiya"},
    {"text": "Yaponiyaning poytaxti qaysi?", "option_a": "Osaka", "option_b": "Kioto", "option_c": "Tokio", "option_d": "Yokohama", "correct_option": "C", "difficulty": "easy", "category": "geografiya"},
    {"text": "Dunyodagi eng kichik davlat qaysi?", "option_a": "Monako", "option_b": "Vatikan", "option_c": "San-Marino", "option_d": "Lixtenshteyn", "correct_option": "B", "difficulty": "medium", "category": "geografiya"},
    {"text": "Orol dengizi qaysi ikki davlat o'rtasida joylashgan?", "option_a": "Qozog'iston va O'zbekiston", "option_b": "Turkmaniston va Eron", "option_c": "Qirg'iziston va Tojikiston", "option_d": "Rossiya va Ukraina", "correct_option": "A", "difficulty": "medium", "category": "geografiya"},
    {"text": "Xitoyning poytaxti qaysi?", "option_a": "Shanxay", "option_b": "Pekin", "option_c": "Guanchjou", "option_d": "Shensen", "correct_option": "B", "difficulty": "easy", "category": "geografiya"},
    {"text": "Amerika qit'asini kim kashf etgan deb hisoblanadi?", "option_a": "Vasko da Gama", "option_b": "Ferdinand Magellan", "option_c": "Xristofor Kolumb", "option_d": "Marko Polo", "correct_option": "C", "difficulty": "medium", "category": "geografiya"},

    # --- Tarix ---
    {"text": "Amir Temur qaysi shaharda mausoleyga (Gur-Amir) dafn etilgan?", "option_a": "Buxoro", "option_b": "Samarqand", "option_c": "Shahrisabz", "option_d": "Toshkent", "correct_option": "B", "difficulty": "easy", "category": "tarix"},
    {"text": "Ikkinchi jahon urushi qaysi yilda tugagan?", "option_a": "1943", "option_b": "1944", "option_c": "1945", "option_d": "1946", "correct_option": "C", "difficulty": "easy", "category": "tarix"},
    {"text": "O'zbekiston mustaqillikni qaysi yilda qo'lga kiritgan?", "option_a": "1989", "option_b": "1990", "option_c": "1991", "option_d": "1992", "correct_option": "C", "difficulty": "easy", "category": "tarix"},
    {"text": "Buyuk Ipak yo'li asosan qaysi ikki qit'ani bog'lagan?", "option_a": "Osiyo va Yevropa", "option_b": "Afrika va Osiyo", "option_c": "Yevropa va Amerika", "option_d": "Osiyo va Avstraliya", "correct_option": "A", "difficulty": "medium", "category": "tarix"},
    {"text": "Mirzo Ulug'bek qaysi soha bilan mashhur bo'lgan?", "option_a": "Tibbiyot", "option_b": "Astronomiya", "option_c": "Arxitektura", "option_d": "Harbiy san'at", "correct_option": "B", "difficulty": "medium", "category": "tarix"},
    {"text": "Birinchi jahon urushi qaysi yilda boshlangan?", "option_a": "1912", "option_b": "1914", "option_c": "1916", "option_d": "1918", "correct_option": "B", "difficulty": "medium", "category": "tarix"},
    {"text": "Misr piramidalari asosan qaysi davrda qurilgan?", "option_a": "O'rta asrlar", "option_b": "Qadimgi davr", "option_c": "Antik davr", "option_d": "Yangi davr", "correct_option": "B", "difficulty": "medium", "category": "tarix"},

    # --- Fan va texnika ---
    {"text": "Suvning kimyoviy formulasi qanday?", "option_a": "CO2", "option_b": "H2O", "option_c": "O2", "option_d": "NaCl", "correct_option": "B", "difficulty": "easy", "category": "fan"},
    {"text": "Inson tanasida nechta suyak bor (kattalarda)?", "option_a": "186", "option_b": "206", "option_c": "226", "option_d": "246", "correct_option": "B", "difficulty": "medium", "category": "fan"},
    {"text": "Quyosh sistemasida nechta sayyora bor?", "option_a": "7", "option_b": "8", "option_c": "9", "option_d": "10", "correct_option": "B", "difficulty": "easy", "category": "fan"},
    {"text": "Yerga eng yaqin sayyora qaysi?", "option_a": "Mars", "option_b": "Venera", "option_c": "Merkuriy", "option_d": "Yupiter", "correct_option": "B", "difficulty": "medium", "category": "fan"},
    {"text": "Nisbiylik nazariyasini kim yaratgan?", "option_a": "Isaak Nyuton", "option_b": "Albert Eynshteyn", "option_c": "Galileo Galiley", "option_d": "Nikola Tesla", "correct_option": "B", "difficulty": "easy", "category": "fan"},
    {"text": "Inson qonining asosiy hujayrasi qaysi element tashiydi?", "option_a": "Kislorod", "option_b": "Azot", "option_c": "Vodorod", "option_d": "Uglerod", "correct_option": "A", "difficulty": "medium", "category": "fan"},
    {"text": "Kompyuter dasturlash tilida \"HTML\" nimani anglatadi?", "option_a": "HyperText Markup Language", "option_b": "HighText Machine Language", "option_c": "HyperTransfer Markup Language", "option_d": "Home Tool Markup Language", "correct_option": "A", "difficulty": "medium", "category": "fan"},
    {"text": "Yorug'lik tezligi taxminan qancha (km/s)?", "option_a": "150,000", "option_b": "300,000", "option_c": "450,000", "option_d": "600,000", "correct_option": "B", "difficulty": "hard", "category": "fan"},
    {"text": "DNK so'zi nimaning qisqartmasi?", "option_a": "Dezoksiribonuklein kislota", "option_b": "Digital Nucleic Acid", "option_c": "Dinamik Nuklein Aloqasi", "option_d": "Dezoksi Nuklein Aralashmasi", "correct_option": "A", "difficulty": "hard", "category": "fan"},

    # --- Sport ---
    {"text": "Futbolda bir jamoada nechta o'yinchi maydonda bo'ladi?", "option_a": "9", "option_b": "10", "option_c": "11", "option_d": "12", "correct_option": "C", "difficulty": "easy", "category": "sport"},
    {"text": "Olimpiya o'yinlari necha yilda bir marta o'tkaziladi?", "option_a": "2", "option_b": "3", "option_c": "4", "option_d": "5", "correct_option": "C", "difficulty": "easy", "category": "sport"},
    {"text": "Basketbolda bitta jamoada nechta o'yinchi maydonda bo'ladi?", "option_a": "4", "option_b": "5", "option_c": "6", "option_d": "7", "correct_option": "B", "difficulty": "easy", "category": "sport"},
    {"text": "2022-yilgi FIFA Jahon chempionati qaysi davlatda o'tkazilgan?", "option_a": "Rossiya", "option_b": "Qatar", "option_c": "AQSH", "option_d": "Braziliya", "correct_option": "B", "difficulty": "medium", "category": "sport"},
    {"text": "Sport gimnastikasi qaysi turdagi sportga kiradi?", "option_a": "Jamoaviy sport", "option_b": "Individual sport", "option_c": "Komanda sporti", "option_d": "Suv sporti", "correct_option": "B", "difficulty": "medium", "category": "sport"},

    # --- Adabiyot va san'at ---
    {"text": "\"O'tkan kunlar\" romanini kim yozgan?", "option_a": "Cho'lpon", "option_b": "Abdulla Qodiriy", "option_c": "Oybek", "option_d": "G'afur G'ulom", "correct_option": "B", "difficulty": "easy", "category": "adabiyot"},
    {"text": "Alisher Navoiy qaysi asrda yashagan?", "option_a": "XIII asr", "option_b": "XIV asr", "option_c": "XV asr", "option_d": "XVI asr", "correct_option": "C", "difficulty": "medium", "category": "adabiyot"},
    {"text": "\"Romeo va Julietta\" asarini kim yozgan?", "option_a": "Charlz Dikkens", "option_b": "Uilyam Shekspir", "option_c": "Lev Tolstoy", "option_d": "Viktor Gyugo", "correct_option": "B", "difficulty": "easy", "category": "adabiyot"},
    {"text": "Mona Liza rasmini kim chizgan?", "option_a": "Pablo Pikasso", "option_b": "Vinsent Van Gog", "option_c": "Leonardo da Vinchi", "option_d": "Mikelanjelo", "correct_option": "C", "difficulty": "easy", "category": "san'at"},
    {"text": "Alisher Navoiyning taxallusi nimani anglatadi?", "option_a": "Nido", "option_b": "Foniy", "option_c": "Hamdiy", "option_d": "Bedil", "correct_option": "B", "difficulty": "hard", "category": "adabiyot"},

    # --- Umumiy bilim ---
    {"text": "Bir yilda nechta oy bor?", "option_a": "10", "option_b": "11", "option_c": "12", "option_d": "13", "correct_option": "C", "difficulty": "easy", "category": "umumiy"},
    {"text": "Bir soatda nechta daqiqa bor?", "option_a": "50", "option_b": "60", "option_c": "70", "option_d": "80", "correct_option": "B", "difficulty": "easy", "category": "umumiy"},
    {"text": "Dunyoda eng ko'p gapiriladigan til qaysi?", "option_a": "Ingliz tili", "option_b": "Ispan tili", "option_c": "Xitoy tili (mandarin)", "option_d": "Arab tili", "correct_option": "C", "difficulty": "medium", "category": "umumiy"},
    {"text": "Birlashgan Millatlar Tashkiloti (BMT) qachon tashkil topgan?", "option_a": "1935", "option_b": "1945", "option_c": "1955", "option_d": "1965", "correct_option": "B", "difficulty": "hard", "category": "umumiy"},
    {"text": "Dunyoda eng ko'p oltin zaxirasiga ega davlat qaysi (odatda)?", "option_a": "Xitoy", "option_b": "Germaniya", "option_c": "AQSH", "option_d": "Rossiya", "correct_option": "C", "difficulty": "hard", "category": "umumiy"},
    {"text": "Piyoda yurish o'rtacha tezligi taxminan qancha (km/soat)?", "option_a": "1-2", "option_b": "5-6", "option_c": "10-12", "option_d": "15-18", "correct_option": "B", "difficulty": "medium", "category": "umumiy"},
    {"text": "Shaxmat taxtasida nechta katak bor?", "option_a": "32", "option_b": "48", "option_c": "64", "option_d": "100", "correct_option": "C", "difficulty": "easy", "category": "umumiy"},
    {"text": "Eng katta sut emizuvchi hayvon qaysi?", "option_a": "Fil", "option_b": "Ko'k kit", "option_c": "Jirafa", "option_d": "Bo'ri", "correct_option": "B", "difficulty": "easy", "category": "umumiy"},
    {"text": "Dunyodagi eng tez quruqlikdagi hayvon qaysi?", "option_a": "Sherlar", "option_b": "Gepard", "option_c": "Ot", "option_d": "Antilopa", "correct_option": "B", "difficulty": "easy", "category": "umumiy"},
    {"text": "Insonning eng katta organi qaysi?", "option_a": "Jigar", "option_b": "Miya", "option_c": "Teri", "option_d": "O'pka", "correct_option": "C", "difficulty": "medium", "category": "fan"},

    # --- O'zbekiston haqida ---
    {"text": "O'zbekistonda nechta viloyat bor (Qoraqalpog'iston va Toshkent shahridan tashqari)?", "option_a": "10", "option_b": "12", "option_c": "14", "option_d": "16", "correct_option": "B", "difficulty": "medium", "category": "ozbekiston"},
    {"text": "O'zbekistonning rasmiy valyutasi nima?", "option_a": "Tenge", "option_b": "Manat", "option_c": "So'm", "option_d": "Rubl", "correct_option": "C", "difficulty": "easy", "category": "ozbekiston"},
    {"text": "Registon maydoni qaysi shaharda joylashgan?", "option_a": "Buxoro", "option_b": "Xiva", "option_c": "Samarqand", "option_d": "Termiz", "correct_option": "C", "difficulty": "easy", "category": "ozbekiston"},
    {"text": "O'zbekiston bayrog'ida nechta rang bor?", "option_a": "2", "option_b": "3", "option_c": "4", "option_d": "5", "correct_option": "B", "difficulty": "easy", "category": "ozbekiston"},
    {"text": "Xiva shahridagi mashhur qadimiy qal'a nomi nima?", "option_a": "Ark", "option_b": "Ichan-Qal'a", "option_c": "Kaltaminor", "option_d": "Ko'hna Ark", "correct_option": "B", "difficulty": "medium", "category": "ozbekiston"},
    {"text": "O'zbekiston Respublikasi Konstitutsiyasi qaysi yilda qabul qilingan?", "option_a": "1991", "option_b": "1992", "option_c": "1993", "option_d": "1994", "correct_option": "B", "difficulty": "hard", "category": "ozbekiston"},

    # --- Texnologiya ---
    {"text": "Dunyodagi birinchi dasturlash tili sifatida ko'pincha qaysi til tilga olinadi?", "option_a": "Python", "option_b": "Fortran", "option_c": "Java", "option_d": "C++", "correct_option": "B", "difficulty": "hard", "category": "texnologiya"},
    {"text": "Telegram messenjerini kim yaratgan?", "option_a": "Mark Sukerberg", "option_b": "Pavel Durov", "option_c": "Bill Geyts", "option_d": "Elon Mask", "correct_option": "B", "difficulty": "easy", "category": "texnologiya"},
    {"text": "\"AI\" qisqartmasi nimani anglatadi?", "option_a": "Automatic Internet", "option_b": "Artificial Intelligence", "option_c": "Advanced Information", "option_d": "Applied Interface", "correct_option": "B", "difficulty": "easy", "category": "texnologiya"},
    {"text": "Birinchi iPhone qaysi yilda chiqarilgan?", "option_a": "2005", "option_b": "2007", "option_c": "2009", "option_d": "2011", "correct_option": "B", "difficulty": "medium", "category": "texnologiya"},
    {"text": "\"USB\" so'zi nimani anglatadi?", "option_a": "Universal Serial Bus", "option_b": "United System Board", "option_c": "Universal System Bus", "option_d": "Unified Serial Board", "correct_option": "A", "difficulty": "medium", "category": "texnologiya"},

    # --- Matematika ---
    {"text": "12 ning 25 foizi nechaga teng?", "option_a": "2", "option_b": "3", "option_c": "4", "option_d": "5", "correct_option": "B", "difficulty": "easy", "category": "matematika"},
    {"text": "π (pi) sonining taxminiy qiymati qancha?", "option_a": "3.12", "option_b": "3.14", "option_c": "3.16", "option_d": "3.18", "correct_option": "B", "difficulty": "easy", "category": "matematika"},
    {"text": "7 ning kvadrati nechaga teng?", "option_a": "14", "option_b": "42", "option_c": "49", "option_d": "56", "correct_option": "C", "difficulty": "easy", "category": "matematika"},
    {"text": "Uchburchakning ichki burchaklari yig'indisi necha darajaga teng?", "option_a": "90", "option_b": "180", "option_c": "270", "option_d": "360", "correct_option": "B", "difficulty": "medium", "category": "matematika"},
    {"text": "100 ning kvadrat ildizi nechaga teng?", "option_a": "5", "option_b": "10", "option_c": "20", "option_d": "50", "correct_option": "B", "difficulty": "easy", "category": "matematika"},

    # --- Din va falsafa (umumiy bilim doirasida, neytral) ---
    {"text": "Hijriy taqvim qaysi voqeadan boshlanadi?", "option_a": "Payg'ambarning tug'ilishi", "option_b": "Makkadan Madinaga hijrat", "option_c": "Qur'onning nozil bo'lishi", "option_d": "Makkaning fath etilishi", "correct_option": "B", "difficulty": "medium", "category": "umumiy"},
    {"text": "Bir hafta nechta kundan iborat?", "option_a": "5", "option_b": "6", "option_c": "7", "option_d": "8", "correct_option": "C", "difficulty": "easy", "category": "umumiy"},
]
