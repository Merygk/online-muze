from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

app = Flask(__name__)
app.secret_key = "gizli_anahtar"  # Oturumlar için gereklidir

# Veritabanı ayarı
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kullanicilar.db"
db = SQLAlchemy(app)

# Kullanıcı modeli
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(100), unique=True, nullable=False)
    sifre = db.Column(db.String(100), nullable=False)

# Ana sayfa
@app.route("/")
def index():
    return render_template("index.html", kullanici=session.get("kullanici"))


@app.route('/favori/<int:eser_id>', methods=['POST'])
def favori_toggle(eser_id):
    if 'username' not in session:
        return jsonify({'durum': 'hata', 'mesaj': 'Giriş yapmalısınız.'}), 401
    
    favoriler = session.get('favoriler', [])
    
    if eser_id in favoriler:
        favoriler.remove(eser_id)
        durum = 'çıkarıldı'
    else:
        favoriler.append(eser_id)
        durum = 'eklendi'
    
    session['favoriler'] = favoriler
    return jsonify({'durum': durum})

# Kayıt sayfası
@app.route("/kayit", methods=["GET", "POST"])
def kayit():
    if request.method == "POST":
        kullanici_adi = request.form["kullanici_adi"]
        sifre = request.form["sifre"]

        # Aynı kullanıcı adı daha önce alınmış mı?
        mevcut_kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
        if mevcut_kullanici:
            return "Bu kullanıcı adı zaten var."

        # Yeni kullanıcıyı kaydet
        yeni_kullanici = Kullanici(kullanici_adi=kullanici_adi, sifre=sifre)
        db.session.add(yeni_kullanici)
        db.session.commit()
        return redirect("/giris")

    return render_template("kayit.html")

# Giriş sayfası
@app.route("/giris", methods=["GET", "POST"])
def giris():
    if request.method == "POST":
        kullanici_adi = request.form["kullanici_adi"]
        sifre = request.form["sifre"]

        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi, sifre=sifre).first()
        if kullanici:
            session["kullanici"] = kullanici_adi
            if 'favoriler' not in session:
                session['favoriler'] = []
            return redirect("/")
        else:
            return "Kullanıcı adı veya şifre yanlış"

    # Eğer GET isteği ise (formu göster)
    return render_template("giris.html")

# Çıkış
@app.route("/cikis")
def cikis():
    session.pop("kullanici", None)
    return redirect("/")

@app.route("/muze")
def muze():
    return render_template("muze.html")

@app.route("/muze/1")
def ankara_muzesi():
    return render_template("ankara-muzesi.html")

@app.route("/muze/2")
def modern_sanat_muzesi():
    return render_template("modern-sanat-muzesi.html")

    # Hakkımızda sayfası
@app.route("/hakkimizda")
def hakkimizda():
    return render_template("hakkimizda.html")

# Veritabanını oluştur ve uygulamayı başlat
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    