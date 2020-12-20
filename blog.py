from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from passlib.hash import sha256_crypt
from flask_pymongo import PyMongo
from functools import wraps
import datetime
import json
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "yb-blog"
app.config["MONGO_URI"] = "mongodb+srv://kaanmuratayvaz:24813236@cluster0.aa8dl.mongodb.net/test?retryWrites=true&w=majority"
mongo = PyMongo(app)
db_operations = mongo.db.test
db_makale = mongo.db.makaleler


# kullanıcı giriş decoratoru
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "loggin_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Lütfen giriş yapınız.", "danger")
            return redirect(url_for('login'))
    return decorated_function


@ app.route("/about")
def about():
    return render_template("about.html")


@app.route("/dashboard")
@login_required
def dashboard():
    myquery = {"yazar": session['username']}
    makaleler = db_makale.find(myquery)
    output = [
        {
            '_id': makale['_id'],
            'baslik': makale['baslik'],
            'icerik': makale['icerik'],
            'time':makale['time'],
            'yazar':makale['yazar'],
            'kategori':makale['kategori']
        } for makale in makaleler]
    return render_template("dashboard.html", output=output)


@app.route('/addarticle', methods=['GET', 'POST'])
@login_required
def addarticle():
    if request.method == 'POST':
        yazi_baslik = request.form['yazi_baslik']
        yazi_kat = request.form['kategori_id']
        yaz_icerik = request.form['yazi_icerik']
        yaz_tanitim = request.form['yazi_icerik'][:100]
        print(yazi_baslik)
        print(yazi_kat)
        print(yaz_icerik)
        new_article = {"baslik": yazi_baslik, "kategori": yazi_kat, "icerik": yaz_icerik,'tanitim':yaz_tanitim,
                       "time": datetime.datetime.now(), "yazar": session['username']}
        db_makale.insert_one(new_article)
        flash("Başarıyla makale kayıt edildi.", "success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html")


@app.route('/article/<string:id>')
def article(id):
    myquery = {"_id": ObjectId(id)}
    makaleler = db_makale.find(myquery)
    output = [
        {
            '_id': makale['_id'],
            'baslik': makale['baslik'],
            'icerik': makale['icerik'],
            'time':makale['time'],
            'yazar':makale['yazar'],
            'kategori':makale['kategori']
        } for makale in makaleler]
    return render_template("article.html", output=output)


@app.route('/makaleguncelle/<string:id>')
@login_required
def makaleguncelle(id):
    myquery = {"_id": ObjectId(id)}
    makaleler = db_makale.find(myquery)
    output = [
        {
            '_id': makale['_id'],
            'baslik': makale['baslik'],
            'icerik': makale['icerik'],
            'time':makale['time'],
            'yazar':makale['yazar'],
            'kategori':makale['kategori']
        } for makale in makaleler]
    return render_template("makaleguncelle.html", output=output)


@app.route('/delete/<string:id>')
@login_required
def delete(id):
    myquery = {"_id": ObjectId(id)}
    db_makale.delete_one(myquery)
    return redirect(url_for('dashboard'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        existing_username = db_operations.find_one({'username': username})
        existing_email = db_operations.find_one({'email': email})
        if existing_username is None:
            if existing_email is None:
                if password == confirm_password:
                    password = sha256_crypt.encrypt(request.form['password'])
                    new_user = {"username": username,
                                "password": password, "email": email, "name": name}
                    db_operations.insert_one(new_user)
                    flash("Başarıyla kayıt oldunuz.", "success")
                    return redirect(url_for('login'))
                else:
                    flash("Girdiğiniz parolalar uyuşmuyor.", "danger")
                    return render_template('register.html')
            else:
                flash("Email mevcut.", "danger")
                return render_template('register.html')

        else:
            flash("Kullanıcı adı mevcut.", "danger")
            return render_template('register.html')
    else:
        return render_template('register.html')


@ app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_user = db_operations.find_one({'username': username})
        if login_user:
            if username == login_user['username']:
                if sha256_crypt.verify(password, login_user['password']):
                    flash("Giriş Başarıyla Gerçekleştirildi!", "success")
                    session['loggin_in'] = True
                    session['username'] = username
                    return redirect(url_for("index"))
                else:
                    flash("Parolanız geçersiz.", "danger")
        else:
            flash("Kullanıcı adınız geçersiz.", "danger")
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = request.form['search']
        print(data.upper())
        print(data.lower())
        myquery = {"baslik": {"$regex": '^'+data.lower()}}
        myquery2 = {"baslik": {"$regex": '^'+data.upper()}}
        makaleler = db_makale.find(myquery)
        makaleler1 = db_makale.find(myquery2)
        output = [
            {
                '_id': makale['_id'],
            } for makale in makaleler]
        output1 = [
            {
                '_id': makale['_id'],
            } for makale in makaleler1]
        print(output)
        print(output1)
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    makaleler = db_makale.find()
    output = [
    {
        '_id': makale['_id'],
        'baslik': makale['baslik'],
        'icerik': makale['icerik'],
        'time':makale['time'],
        'yazar':makale['yazar'],
        'tanitim':makale['tanitim'],
        'kategori':makale['kategori']
    } for makale in makaleler]
    print(output)
    return render_template('index.html', output=output)


@ app.route('/oku', methods=['GET', 'POST'])
def oku():
    users = db_operations.find()
    output = [{'name': user['name'], 'username': user['username']}
              for user in users]
    print(output)
    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)
