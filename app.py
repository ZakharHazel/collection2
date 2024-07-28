import os
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from werkzeug.utils import secure_filename

upload_folder = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
Mobility(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD'] = upload_folder
db = SQLAlchemy(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Category(db.Model):
    # Таблица с категориями
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_category = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(30), nullable=False)


class Collection(db.Model):
    # Таблица с экземпляроми коллекции
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(50), nullable=True)
    Category = db.Column(db.Integer, nullable=False)
    Year = db.Column(db.Integer, nullable=False)


@app.route('/')
def index():
    return redirect('/collection/category/0')


@app.route('/collection/category/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}collection.html")
def folder(template, id):
    # Страница редактирования экземпляра коллекции
    if request.method == 'POST':
        if request.form['action'] == 'return':
            if id==0:
                return redirect('/collection/category/0')
            else:
                cat = Category.query.filter_by(id=id).first()
                iid = cat.parent_category
                return redirect('/collection/category/' + str(iid))
    else:
        iidd= id
        way='/'
        while iidd!=0:
            catt = Category.query.filter_by(id=iidd).first()
            oway = catt.name
            way = '/' +oway +  way
            iidd = catt.parent_category
        coll = Collection.query.filter_by(Category=id).all()
        cat = Category.query.filter_by(parent_category=id).all()
        return render_template(template, coll=coll, cat=cat, id=id, way=way)







@app.route('/collection/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}collect.html")
def update_collection(template, id):
    # Страница редактирования экземпляра коллекции
    coll = Collection.query.filter_by(id=id).first()
    idd = coll.Category
    if request.method == 'POST':
        if request.form['action'] == 'update':
            try:
                file = request.files['img']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD'], filename))
                coll.image = filename
            except:
                pass
            coll.Year = request.form['Year']
            coll.Name = request.form['Name']
            try:
                db.session.commit()
                return redirect('/collection/category/' + str(idd))
            except:
                return redirect('/collection/' + str(id))

        if request.form['action'] == 'return':
            return redirect('/collection/category/' + str(idd))
    else:
        return render_template(template, coll=coll)


@app.route('/collection/add/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}add_collection.html")
def add_collection(template, id):
    # Страница для добавления нового экземпляра
    if request.method == 'POST':
        if request.form['action'] == 'add':
            try:
                file = request.files['img']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD'], filename))
            except:
                filename = 'Base.jpg'
            upload = Collection(image=filename, Category=id, Year=request.form['Year'], Name=request.form['Name'])
            try:
                db.session.add(upload)
                db.session.commit()
                return redirect('/collection/category/' + str(id))
            except:
                pass
        return redirect('/collection/category/' + str(id))
    else:
        return render_template(template, id=id)


@app.route('/collection/delete/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}delete_collection.html")
def delete_collection(template, id):
    # Страница добавления новой категории
    if request.method == 'POST':
        Coll = Collection.query.filter_by(id=id).first()
        idd = Coll.Category
        if request.form['action'] == 'yes':
            try:
                os.remove('static/uploads/' + Coll.image)
                db.session.delete(Coll)
                db.session.commit()
                return redirect('/collection/category/'+ str(idd))
            except:
                return redirect('/collection/delete/'+ str(id))
        if request.form['action'] == 'no':
            return redirect('/collection/category/' + str(idd))
    else:
        return render_template(template)


@app.route('/collection/move/<int:iddd>/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}move_collection.html")
def move_collection(template, id, iddd):
    coll = Collection.query.filter_by(id=iddd).first()
    iid = coll.Category
    if request.method == 'POST':
        if request.form['action'] == 'return':
            if id==0:
                return redirect('/collection/move/'+ str(iddd)+ '/0')
            else:
                cat = Category.query.filter_by(id=id).first()
                iiid = cat.parent_category
                return redirect('/collection/move/'+ str(iddd)+ '/' + str(iiid))
        if request.form['action'] == 'cancel':
            return redirect('/collection/category/' + str(iid))
            pass
        if request.form['action'] == 'save':
            coll.Category=id
            try:
                db.session.commit()
                return redirect('/collection/category/' + str(id))
            except:
                return redirect('/collection/move/'+ str(iddd)+ '/' + str(iid))
            pass
    else:
        iidd= id
        way='/'
        while iidd!=0:
            catt = Category.query.filter_by(id=iidd).first()
            oway = catt.name
            way = '/' +oway +  way
            iidd = catt.parent_category
        coll = Collection.query.filter_by(Category=id).all()
        cat = Category.query.filter_by(parent_category=id).all()
        return render_template(template, coll=coll, cat=cat, id=id, way=way, iddd=iddd)




@app.route('/category/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}category.html")
def update_category(template, id):
    # Страница редактирования экземпляра коллекции

    cat = Category.query.filter_by(id=id).first()
    idd = cat.parent_category
    if request.method == 'POST':
        if request.form['action'] == 'update':
            cat.name = request.form['Name']
            try:
                db.session.commit()
                return redirect('/collection/category/' + str(idd))
            except:
                return redirect('/category/' + str(id))

        if request.form['action'] == 'return':
            return redirect('/collection/category/' + str(idd))
    else:
        return render_template(template, cat=cat)


@app.route('/collection/category/add/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}add_category.html")
def add_category(template, id):
    # Страница добавления новой категории
    if request.method == 'POST':
        if request.form['action'] == 'add':
            Cat = Category(name=request.form['cat_name'], parent_category=id)
            try:
                db.session.add(Cat)
                db.session.commit()
                return redirect('/collection/category/'+ str(id))
            except:
                return redirect('/collection/category/'+ str(id))
    else:
        return render_template(template)

@app.route('/collection/category/delete/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}delete_category.html")
def delete_category(template, id):
    # Страница добавления новой категории
    if request.method == 'POST':
        Cat = Category.query.filter_by(id=id).first()
        idd = Cat.parent_category
        if request.form['action'] == 'yes':
            try:
                db.session.delete(Cat)
                db.session.commit()
                return redirect('/collection/category/'+ str(idd))
            except:
                return redirect('/collection/category/delete/'+ str(idd))
        if request.form['action'] == 'no':
            return redirect('/collection/category/' + str(idd))
    else:
        return render_template(template)


@app.route('/collection/category/move/<int:iddd>/<int:id>', methods=['POST', 'GET'])
@mobile_template("{mobile/}move_category.html")
def move_category(template, id, iddd):
    cat = Category.query.filter_by(id=iddd).first()
    iid = cat.parent_category
    if request.method == 'POST':
        if request.form['action'] == 'return':
            if id==0:
                return redirect('/collection/category/move/'+ str(iddd)+ '/0')
            else:
                catt = Category.query.filter_by(id=id).first()
                iiid = catt.parent_category
                return redirect('/collection/category/move/'+ str(iddd)+ '/' + str(iiid))
        if request.form['action'] == 'cancel':
            return redirect('/collection/category/' + str(iid))
            pass
        if request.form['action'] == 'save':
            cat.parent_category=id
            try:
                db.session.commit()
                return redirect('/collection/category/' + str(id))
            except:
                return redirect('/collection/category/move/'+ str(iddd)+ '/' + str(iid))
            pass
    else:
        iidd= id
        way='/'
        while iidd!=0:
            catt = Category.query.filter_by(id=iidd).first()
            oway = catt.name
            way = '/' +oway +  way
            iidd = catt.parent_category
        ccat = Category.query.filter_by(parent_category=id).all()
        return render_template(template, cat=ccat, id=id, way=way, iddd=iddd)


if __name__ == '__main__':
    app.run()
