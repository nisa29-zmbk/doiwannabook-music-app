from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
DATABASE_URL = "postgresql://neondb_owner:npg_sIjLreHN58PA@ep-divine-bread-a56wh69j-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgre
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "degistirecegiz_birazdan"


# =========================================
# VERİTABANI
# =========================================

def veritabani_olustur():

  conn = psycopg2.connect(DATABASE_URL)

    # KULLANICILAR
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL
        )
    """)

    # KİTAPLAR
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kitaplar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT NOT NULL,
            kitap_adi TEXT NOT NULL,
            yazar TEXT NOT NULL
        )
    """)

    # NOTLAR
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT NOT NULL,
            kitap_adi TEXT NOT NULL,
            not_metni TEXT NOT NULL
        )
    """)

    # MÜZİKLER
    conn.execute("""
        CREATE TABLE IF NOT EXISTS muzikler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT NOT NULL,
            sarki_adi TEXT NOT NULL,
            sanatci TEXT NOT NULL
        )
    """)

    # KALPLER
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kalpler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT NOT NULL,
            sarki_adi TEXT NOT NULL,
            sanatci TEXT NOT NULL,
            neden TEXT NOT NULL
        )
    """)

    # SOHBETLER
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sohbetler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT NOT NULL,
            mesaj TEXT NOT NULL
        )
    """)

    # TÜM CEVAPLAR
    conn.execute("""
        CREATE TABLE IF NOT EXISTS yanitlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bolum TEXT NOT NULL,
            hedef_id INTEGER NOT NULL,
            kullanici_adi TEXT NOT NULL,
            cevap TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================
# ANA SAYFA
# =========================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================
# KAYIT
# =========================================

@app.route("/kayit", methods=["GET", "POST"])
def kayit():

    if request.method == "POST":

        kullanici_adi = request.form["kullanici_adi"]
        sifre = request.form["sifre"]

        conn = sqlite3.connect("kullanicilar.db")

        try:

            conn.execute(
                """
                INSERT INTO kullanicilar
                (kullanici_adi, sifre)
                VALUES (?, ?)
                """,
                (
                    kullanici_adi,
                    generate_password_hash(sifre)
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Bu kullanıcı adı zaten kullanılıyor."

        conn.close()

        return redirect(url_for("giris"))

    return render_template("kayit.html")


# =========================================
# GİRİŞ
# =========================================

@app.route("/giris", methods=["GET", "POST"])
def giris():

    if request.method == "POST":

        kullanici_adi = request.form["kullanici_adi"]
        sifre = request.form["sifre"]

        conn = sqlite3.connect("kullanicilar.db")

        kullanici = conn.execute(
            """
            SELECT *
            FROM kullanicilar
            WHERE kullanici_adi = ?
            """,
            (kullanici_adi,)
        ).fetchone()

        conn.close()

        if kullanici and check_password_hash(kullanici[2], sifre):

            session["kullanici_adi"] = kullanici_adi

            return redirect(url_for("index"))

        return "Kullanıcı adı veya şifre yanlış."

    return render_template("giris.html")


# =========================================
# ÇIKIŞ
# =========================================

@app.route("/cikis")
def cikis():

    session.pop("kullanici_adi", None)

    return redirect(url_for("index"))


# =========================================
# KİTAP
# =========================================

@app.route("/kitap", methods=["GET", "POST"])
def kitap():

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    if request.method == "POST":

        kitap_adi = request.form["kitap_adi"]
        yazar = request.form["yazar"]

        conn = sqlite3.connect("kullanicilar.db")

        conn.execute(
            """
            INSERT INTO kitaplar
            (kullanici_adi, kitap_adi, yazar)
            VALUES (?, ?, ?)
            """,
            (
                session["kullanici_adi"],
                kitap_adi,
                yazar
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("kitap"))

    conn = sqlite3.connect("kullanicilar.db")

    kitaplar = conn.execute(
        """
        SELECT id, kitap_adi, yazar, kullanici_adi
        FROM kitaplar
        ORDER BY id DESC
        """
    ).fetchall()

    cevaplar = conn.execute(
        """
        SELECT id, hedef_id, cevap, kullanici_adi
        FROM yanitlar
        WHERE bolum = 'kitap'
        ORDER BY id ASC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "kitap.html",
        kitaplar=kitaplar,
        cevaplar=cevaplar
    )


# KİTAP DÜZENLE

@app.route("/kitap_duzenle/<int:kitap_id>", methods=["GET", "POST"])
def kitap_duzenle(kitap_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    kitap = conn.execute(
        """
        SELECT id, kitap_adi, yazar, kullanici_adi
        FROM kitaplar
        WHERE id = ?
        """,
        (kitap_id,)
    ).fetchone()

    if not kitap or kitap[3] != session["kullanici_adi"]:
        conn.close()
        return "Bu kitabı düzenleme yetkin yok."

    if request.method == "POST":

        kitap_adi = request.form["kitap_adi"]
        yazar = request.form["yazar"]

        conn.execute(
            """
            UPDATE kitaplar
            SET kitap_adi = ?, yazar = ?
            WHERE id = ?
            AND kullanici_adi = ?
            """,
            (
                kitap_adi,
                yazar,
                kitap_id,
                session["kullanici_adi"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("kitap"))

    conn.close()

    return render_template(
        "kitap_duzenle.html",
        kitap=kitap
    )


# KİTAP SİL

@app.route("/kitap_sil/<int:kitap_id>", methods=["POST"])
def kitap_sil(kitap_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    conn.execute(
        """
        DELETE FROM yanitlar
        WHERE bolum = 'kitap'
        AND hedef_id = ?
        """,
        (kitap_id,)
    )

    conn.execute(
        """
        DELETE FROM kitaplar
        WHERE id = ?
        AND kullanici_adi = ?
        """,
        (
            kitap_id,
            session["kullanici_adi"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("kitap"))


# =========================================
# NOT
# =========================================

@app.route("/not", methods=["GET", "POST"])
def notlar():

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    if request.method == "POST":

        kitap_adi = request.form["kitap_adi"]
        not_metni = request.form["not_metni"]

        conn = sqlite3.connect("kullanicilar.db")

        conn.execute(
            """
            INSERT INTO notlar
            (kullanici_adi, kitap_adi, not_metni)
            VALUES (?, ?, ?)
            """,
            (
                session["kullanici_adi"],
                kitap_adi,
                not_metni
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("notlar"))

    conn = sqlite3.connect("kullanicilar.db")

    notlar = conn.execute(
        """
        SELECT id, kitap_adi, not_metni, kullanici_adi
        FROM notlar
        ORDER BY id DESC
        """
    ).fetchall()

    cevaplar = conn.execute(
        """
        SELECT id, hedef_id, cevap, kullanici_adi
        FROM yanitlar
        WHERE bolum = 'not'
        ORDER BY id ASC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "not.html",
        notlar=notlar,
        cevaplar=cevaplar
    )


# NOT DÜZENLE

@app.route("/not_duzenle/<int:not_id>", methods=["GET", "POST"])
def not_duzenle(not_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    not_item = conn.execute(
        """
        SELECT id, kitap_adi, not_metni, kullanici_adi
        FROM notlar
        WHERE id = ?
        """,
        (not_id,)
    ).fetchone()

    if not not_item or not_item[3] != session["kullanici_adi"]:
        conn.close()
        return "Bu notu düzenleme yetkin yok."

    if request.method == "POST":

        kitap_adi = request.form["kitap_adi"]
        not_metni = request.form["not_metni"]

        conn.execute(
            """
            UPDATE notlar
            SET kitap_adi = ?, not_metni = ?
            WHERE id = ?
            AND kullanici_adi = ?
            """,
            (
                kitap_adi,
                not_metni,
                not_id,
                session["kullanici_adi"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("notlar"))

    conn.close()

    return render_template(
        "not_duzenle.html",
        not_item=not_item
    )


# NOT SİL

@app.route("/not_sil/<int:not_id>", methods=["POST"])
def not_sil(not_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    conn.execute(
        """
        DELETE FROM yanitlar
        WHERE bolum = 'not'
        AND hedef_id = ?
        """,
        (not_id,)
    )

    conn.execute(
        """
        DELETE FROM notlar
        WHERE id = ?
        AND kullanici_adi = ?
        """,
        (
            not_id,
            session["kullanici_adi"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("notlar"))


# =========================================
# MÜZİK
# =========================================

@app.route("/muzik", methods=["GET", "POST"])
def muzik():

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    if request.method == "POST":

        sarki_adi = request.form["sarki_adi"]
        sanatci = request.form["sanatci"]

        conn = sqlite3.connect("kullanicilar.db")

        conn.execute(
            """
            INSERT INTO muzikler
            (kullanici_adi, sarki_adi, sanatci)
            VALUES (?, ?, ?)
            """,
            (
                session["kullanici_adi"],
                sarki_adi,
                sanatci
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("muzik"))

    conn = sqlite3.connect("kullanicilar.db")

    muzikler = conn.execute(
        """
        SELECT id, sarki_adi, sanatci, kullanici_adi
        FROM muzikler
        ORDER BY id DESC
        """
    ).fetchall()

    cevaplar = conn.execute(
        """
        SELECT id, hedef_id, cevap, kullanici_adi
        FROM yanitlar
        WHERE bolum = 'muzik'
        ORDER BY id ASC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "muzik.html",
        muzikler=muzikler,
        cevaplar=cevaplar
    )


# MÜZİK DÜZENLE

@app.route("/muzik_duzenle/<int:muzik_id>", methods=["GET", "POST"])
def muzik_duzenle(muzik_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    muzik = conn.execute(
        """
        SELECT id, sarki_adi, sanatci, kullanici_adi
        FROM muzikler
        WHERE id = ?
        """,
        (muzik_id,)
    ).fetchone()

    if not muzik or muzik[3] != session["kullanici_adi"]:
        conn.close()
        return "Bu şarkıyı düzenleme yetkin yok."

    if request.method == "POST":

        sarki_adi = request.form["sarki_adi"]
        sanatci = request.form["sanatci"]

        conn.execute(
            """
            UPDATE muzikler
            SET sarki_adi = ?, sanatci = ?
            WHERE id = ?
            AND kullanici_adi = ?
            """,
            (
                sarki_adi,
                sanatci,
                muzik_id,
                session["kullanici_adi"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("muzik"))

    conn.close()

    return render_template(
        "muzik_duzenle.html",
        muzik=muzik
    )


# MÜZİK SİL

@app.route("/muzik_sil/<int:muzik_id>", methods=["POST"])
def muzik_sil(muzik_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    conn.execute(
        """
        DELETE FROM yanitlar
        WHERE bolum = 'muzik'
        AND hedef_id = ?
        """,
        (muzik_id,)
    )

    conn.execute(
        """
        DELETE FROM muzikler
        WHERE id = ?
        AND kullanici_adi = ?
        """,
        (
            muzik_id,
            session["kullanici_adi"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("muzik"))


# =========================================
# KALP
# =========================================

@app.route("/kalp", methods=["GET", "POST"])
def kalp():

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    if request.method == "POST":

        sarki_adi = request.form["sarki_adi"]
        sanatci = request.form["sanatci"]
        neden = request.form["neden"]

        conn = sqlite3.connect("kullanicilar.db")

        conn.execute(
            """
            INSERT INTO kalpler
            (kullanici_adi, sarki_adi, sanatci, neden)
            VALUES (?, ?, ?, ?)
            """,
            (
                session["kullanici_adi"],
                sarki_adi,
                sanatci,
                neden
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("kalp"))

    conn = sqlite3.connect("kullanicilar.db")

    kalpler = conn.execute(
        """
        SELECT id, sarki_adi, sanatci, neden, kullanici_adi
        FROM kalpler
        ORDER BY id DESC
        """
    ).fetchall()

    cevaplar = conn.execute(
        """
        SELECT id, hedef_id, cevap, kullanici_adi
        FROM yanitlar
        WHERE bolum = 'kalp'
        ORDER BY id ASC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "kalp.html",
        kalpler=kalpler,
        cevaplar=cevaplar
    )


# KALP DÜZENLE

@app.route("/kalp_duzenle/<int:kalp_id>", methods=["GET", "POST"])
def kalp_duzenle(kalp_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    kalp_item = conn.execute(
        """
        SELECT id, sarki_adi, sanatci, neden, kullanici_adi
        FROM kalpler
        WHERE id = ?
        """,
        (kalp_id,)
    ).fetchone()

    if not kalp_item or kalp_item[4] != session["kullanici_adi"]:
        conn.close()
        return "Bu paylaşımı düzenleme yetkin yok."

    if request.method == "POST":

        sarki_adi = request.form["sarki_adi"]
        sanatci = request.form["sanatci"]
        neden = request.form["neden"]

        conn.execute(
            """
            UPDATE kalpler
            SET sarki_adi = ?, sanatci = ?, neden = ?
            WHERE id = ?
            AND kullanici_adi = ?
            """,
            (
                sarki_adi,
                sanatci,
                neden,
                kalp_id,
                session["kullanici_adi"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("kalp"))

    conn.close()

    return render_template(
        "kalp_duzenle.html",
        kalp=kalp_item
    )


# KALP SİL

@app.route("/kalp_sil/<int:kalp_id>", methods=["POST"])
def kalp_sil(kalp_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    conn.execute(
        """
        DELETE FROM yanitlar
        WHERE bolum = 'kalp'
        AND hedef_id = ?
        """,
        (kalp_id,)
    )

    conn.execute(
        """
        DELETE FROM kalpler
        WHERE id = ?
        AND kullanici_adi = ?
        """,
        (
            kalp_id,
            session["kullanici_adi"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("kalp"))


# =========================================
# SOHBET
# =========================================

@app.route("/sohbet", methods=["GET", "POST"])
def sohbet():

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    if request.method == "POST":

        mesaj = request.form["mesaj"]

        conn = sqlite3.connect("kullanicilar.db")

        conn.execute(
            """
            INSERT INTO sohbetler
            (kullanici_adi, mesaj)
            VALUES (?, ?)
            """,
            (
                session["kullanici_adi"],
                mesaj
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("sohbet"))

    conn = sqlite3.connect("kullanicilar.db")

    sohbetler = conn.execute(
        """
        SELECT id, mesaj, kullanici_adi
        FROM sohbetler
        ORDER BY id DESC
        """
    ).fetchall()

    cevaplar = conn.execute(
        """
        SELECT id, hedef_id, cevap, kullanici_adi
        FROM yanitlar
        WHERE bolum = 'sohbet'
        ORDER BY id ASC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "sohbet.html",
        sohbetler=sohbetler,
        cevaplar=cevaplar
    )


# =========================================
# GENEL CEVAP VER
# =========================================

@app.route("/cevap/<bolum>/<int:hedef_id>", methods=["POST"])
def cevap_ver(bolum, hedef_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    izinli_bolumler = [
        "kitap",
        "not",
        "muzik",
        "kalp",
        "sohbet"
    ]

    if bolum not in izinli_bolumler:
        return "Geçersiz bölüm."

    cevap = request.form["cevap"]

    conn = sqlite3.connect("kullanicilar.db")

    conn.execute(
        """
        INSERT INTO yanitlar
        (bolum, hedef_id, kullanici_adi, cevap)
        VALUES (?, ?, ?, ?)
        """,
        (
            bolum,
            hedef_id,
            session["kullanici_adi"],
            cevap
        )
    )

    conn.commit()
    conn.close()

    if bolum == "kitap":
        return redirect(url_for("kitap"))

    if bolum == "not":
        return redirect(url_for("notlar"))

    if bolum == "muzik":
        return redirect(url_for("muzik"))

    if bolum == "kalp":
        return redirect(url_for("kalp"))

    return redirect(url_for("sohbet"))


# =========================================
# CEVAP DÜZENLE
# =========================================

@app.route("/cevap_duzenle/<int:cevap_id>", methods=["POST"])
def cevap_duzenle(cevap_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    yeni_cevap = request.form["cevap"]

    conn = sqlite3.connect("kullanicilar.db")

    cevap = conn.execute(
        """
        SELECT bolum
        FROM yanitlar
        WHERE id = ?
        AND kullanici_adi = ?
        """,
        (
            cevap_id,
            session["kullanici_adi"]
        )
    ).fetchone()

    if cevap:

        conn.execute(
            """
            UPDATE yanitlar
            SET cevap = ?
            WHERE id = ?
            AND kullanici_adi = ?
            """,
            (
                yeni_cevap,
                cevap_id,
                session["kullanici_adi"]
            )
        )

        conn.commit()

    conn.close()

    if cevap:

        if cevap[0] == "kitap":
            return redirect(url_for("kitap"))

        if cevap[0] == "not":
            return redirect(url_for("notlar"))

        if cevap[0] == "muzik":
            return redirect(url_for("muzik"))

        if cevap[0] == "kalp":
            return redirect(url_for("kalp"))

        return redirect(url_for("sohbet"))

    return redirect(url_for("index"))


# =========================================
# CEVAP SİL
# =========================================

@app.route("/cevap_sil/<int:cevap_id>", methods=["POST"])
def cevap_sil(cevap_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    cevap = conn.execute(
        """
        SELECT bolum
        FROM yanitlar
        WHERE id = ?
        AND kullanici_adi = ?
        """,
        (
            cevap_id,
            session["kullanici_adi"]
        )
    ).fetchone()

    if cevap:

        conn.execute(
            """
            DELETE FROM yanitlar
            WHERE id = ?
            AND kullanici_adi = ?
            """,
            (
                cevap_id,
                session["kullanici_adi"]
            )
        )

        conn.commit()

    conn.close()

    if cevap:

        if cevap[0] == "kitap":
            return redirect(url_for("kitap"))

        if cevap[0] == "not":
            return redirect(url_for("notlar"))

        if cevap[0] == "muzik":
            return redirect(url_for("muzik"))

        if cevap[0] == "kalp":
            return redirect(url_for("kalp"))

        return redirect(url_for("sohbet"))

    return redirect(url_for("index"))


# =========================================
# SOHBET MESAJI DÜZENLE
# =========================================

@app.route("/sohbet_duzenle/<int:sohbet_id>", methods=["POST"])
def sohbet_duzenle(sohbet_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    mesaj = request.form["mesaj"]

    conn = sqlite3.connect("kullanicilar.db")

    conn.execute(
        """
        UPDATE sohbetler
        SET mesaj = ?
        WHERE id = ?
        AND kullanici_adi = ?
        """,
        (
            mesaj,
            sohbet_id,
            session["kullanici_adi"]
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("sohbet"))


# =========================================
# SOHBET MESAJI SİL
# =========================================

@app.route("/sohbet_sil/<int:sohbet_id>", methods=["POST"])
def sohbet_sil(sohbet_id):

    if "kullanici_adi" not in session:
        return redirect(url_for("giris"))

    conn = sqlite3.connect("kullanicilar.db")

    mesaj = conn.execute(
        """
        SELECT kullanici_adi
        FROM sohbetler
        WHERE id = ?
        """,
        (sohbet_id,)
    ).fetchone()

    if mesaj and mesaj[0] == session["kullanici_adi"]:

        conn.execute(
            """
            DELETE FROM yanitlar
            WHERE bolum = 'sohbet'
            AND hedef_id = ?
            """,
            (sohbet_id,)
        )

        conn.execute(
            """
            DELETE FROM sohbetler
            WHERE id = ?
            """,
            (sohbet_id,)
        )

        conn.commit()

    conn.close()

    return redirect(url_for("sohbet"))


# =========================================
# UYGULAMAYI BAŞLAT
# =========================================

if __name__ == "__main__":

    veritabani_olustur()

    app.run(debug=True)
