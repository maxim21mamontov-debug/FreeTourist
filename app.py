import sqlite3
import math
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "oopt.db"

def init_db():
    """Создает базу данных и наполняет ее реальными примерами ООПТ."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oopt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            base_price INTEGER NOT NULL,
            free_categories TEXT NOT NULL,
            discount_50_categories TEXT NOT NULL,
            required_docs TEXT NOT NULL,
            payment_url TEXT,
            contact_email TEXT,
            manual_instruction TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            radius_km REAL NOT NULL,
            mchs_status TEXT NOT NULL,
            mchs_note TEXT NOT NULL,
            mchs_source_url TEXT,
            park_news_url TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM oopt")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            (
                "Национальный парк «Куршская коса»",
                "Калининградская область",
                400,
                "Дети до 18 лет, пенсионеры, инвалиды, многодетные семьи, жители Калининградской области",
                "Нет (для льготников бесплатно)",
                "Паспорт РФ, документ подтверждающий льготу (если применимо). Если на авто — СТС.",
                "https://park-kosa.ru",
                None,
                None,
                55.1636, 20.8617, 25.0,
                "open",
                "По данным МЧС по Калининградской области, ограничений на посещение нет. Соблюдайте правила пожарной безопасности.",
                "https://mchs.gov.ru",
                "https://park-kosa.ru"
            ),
            (
                "Кавказский государственный природный биосферный заповедник",
                "Краснодарский край / Республика Адыгея",
                300,
                "Дети дошкольного и школьного возраста, пенсионеры, инвалиды I и II групп, местные жители",
                "Студенты очной формы обучения",
                "Паспорт РФ, маршрутный лист (выбирается при оформлении), полис ОМС.",
                "https://kavkazzapoved.ru",
                None,
                None,
                43.8344, 40.3883, 45.0,
                "warning",
                "Внимание! По сводкам МЧС в горных районах возможна лавинная опасность или закрытие отдельных маршрутов. Уточняйте статус тропы перед выходом.",
                "https://mchs.gov.ru",
                "https://kavkazzapoved.ru"
            ),
            (
                "Кроноцкий государственный заповедник (Долина гейзеров)",
                "Камчатский край",
                1200,
                "Дети до 12 лет, местные жители Камчатского края (по квотам)",
                "Пенсионеры, школьники от 12 до 18 лет",
                "Паспорт РФ, заявка на посещение, медицинская страховка, разрешение на ввоз/вывоз оборудования (если есть).",
                None,
                "tourism@kronoki.ru",
                "1. Заполните форму ниже, чтобы автоматически сформировать текст заявки.\n2. Нажмите «Скопировать текст заявки» и отправьте его на почту отдела туризма заповедника (tourism@kronoki.ru) минимум за 10 рабочих дней до поездки.\n3. Дождитесь ответного письма с договором и квитанцией на оплату.",
                54.4306, 160.1394, 60.0,
                "open",
                "По данным МЧС Камчатского края, вулканическая и погодная обстановка в норме. Посещение строго в составе организованных групп.",
                "https://mchs.gov.ru",
                "https://kronoki.ru"
            ),
            (
                "Национальный парк «Таганай»",
                "Челябинская область",
                300,
                "Дети дошкольного и школьного возраста, пенсионеры, инвалиды, многодетные семьи, жители г. Златоуст и пгт. Магнитка",
                "Нет (для льготников оформление бесплатного разрешения)",
                "Паспорт РФ, документ подтверждающий льготу или местную регистрацию.",
                "https://taganay.org",
                None,
                None,
                55.2667, 59.8167, 20.0,
                "open",
                "По данным МЧС по Челябинской области, тропы открыты. В горной зоне возможны резкие перепады температуры и ветра.",
                "https://mchs.gov.ru",
                "https://taganay.org"
            ),
            (
                "Национальный парк «Приэльбрусье»",
                "Кабардино-Балкарская Республика",
                200,
                "Дети до 18 лет, пенсионеры, инвалиды, ветераны, жители Кабардино-Балкарии",
                "Нет (для льготников бесплатно при предъявлении документов)",
                "Паспорт РФ (при восхождении выше 3800 м требуется отдельное разрешение за 300 руб. и регистрация в МЧС).",
                "https://resort-elbrus.ru",
                None,
                None,
                43.2667, 42.5500, 35.0,
                "warning",
                "Внимание! Высокогорный район. По сводкам МЧС по КБР регулярно объявляется лавинная опасность и штормовые предупреждения.",
                "https://mchs.gov.ru",
                "https://xn--80ab2abvfcfr1gj.xn--p1ai"
            )
        ]
        cursor.executemany('''
            INSERT INTO oopt (name, region, base_price, free_categories, discount_50_categories, 
            required_docs, payment_url, contact_email, manual_instruction, lat, lon, radius_km, 
            mchs_status, mchs_note, mchs_source_url, park_news_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
        conn.commit()
    conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/oopt", methods=["GET"])
def get_oopt():
    query = request.args.get("q", "").lower()
    oopt_id = request.args.get("id", "")
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM oopt")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if oopt_id:
        rows = [r for r in rows if str(r["id"]) == str(oopt_id)]
    elif query:
        rows = [r for r in rows if query in r["name"].lower() or query in r["region"].lower()]
    return jsonify(rows)

@app.route("/api/check-location", methods=["POST"])
def check_location():
    data = request.json
    user_lat = data.get("lat")
    user_lon = data.get("lon")
    
    if user_lat is None or user_lon is None:
        return jsonify({"error": "Нет координат"}), 400

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM oopt")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    nearby = []
    for r in rows:
        dist = haversine(user_lat, user_lon, r["lat"], r["lon"])
        if dist <= r["radius_km"]:
            nearby.append({
                "name": r["name"],
                "distance_km": round(dist, 1),
                "payment_url": r["payment_url"]
            })
            
    return jsonify({"in_oopt": len(nearby) > 0, "zones": nearby})

init_db()

if __name__ == "__main__":
    app.run(debug=True)