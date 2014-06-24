import sys
import random
import smtplib
import email.utils
from email.mime.text import MIMEText
from datetime import datetime
from functools import wraps
from werkzeug import check_password_hash, generate_password_hash, secure_filename
from flask import Flask, g, url_for, redirect, flash, render_template, session, _app_ctx_stack, request

from B2C import db, app
from models import User, Comment, Item, Address, Order, Directory, TopDirectory, Admin, CreditRequirement


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['user_id']).first()


@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_user_id(email=None):
    return User.query.filter_by(email=email).first()


@app.route("/")
def index():
    return render_template("web/home.html", top_dir = TopDirectory.query.all())

#do the real search stuff
def _search(keyword = None, cate_id = None, price_level = 0, discount_level = 0):
    assert keyword

    price_map = {
        0:{"lower_bound": 0, "upper_bound": sys.maxint},
        1:{"lower_bound": 0, "upper_bound": 10},
        2:{"lower_bound": 10, "upper_bound": 30},
        3:{"lower_bound": 30, "upper_bound": 50},
        4:{"lower_bound": 50, "upper_bound": 100},
        5:{"lower_bound": 100, "upper_bound": sys.maxint}
    }

    discount_map = {
        0:{"lower_bound": 0, "upper_bound": 1.0},
        1:{"lower_bound": 0, "upper_bound": 0.3},
        2:{"lower_bound": 0.3, "upper_bound": 0.5},
        3:{"lower_bound": 0.5, "upper_bound": 0.7},
        4:{"lower_bound": 0.7, "upper_bound": 1.0}
    }

    items = Item.query.filter(Item.item_name == keyword,
        Item.price >= price_map[price_level]['lower_bound'],
        Item.price < price_map[price_level]['upper_bound'],
        Item.discount >= discount_map[discount_level]['lower_bound'],
        Item.discount < discount_map[discount_level]['upper_bound']).all()

    if cate_id:
        for i in items:
            if i.cate_id != cate_id:
                del i
    return items

@app.route('/item_search', methods = ['GET', 'POST'])
def item_search():
    cate_id = None
    if request.method == 'POST':
        if request.form['cate_id'] != '':
            cate_id = request.form['cate_id']
        items = _search(request.form['keyword'], cate_id, int(request.form['price_level']), int(request.form['discount_level']))
        return render_template('web/item_search_list.html', items = items)
    return render_template('web/item_search.html', top_dir = TopDirectory.query.all())

@app.route('/item_info/<int:id>')
def item_info(id):
    return render_template('web/item_info.html', item = Item.query.filter_by(id = id).first())

# Address related functions
@app.route("/add_address", methods=['GET'])
@login_required
def add_address():
    # Query database for address entries
    address_list = Address.query.filter_by(user_id=session['user_id'])
    return render_template('web/address_daohang.html', address_list=address_list)

@app.route("/do_add_address", methods=['POST'])
def do_add_address():
    rc_name = request.form['name']
    addr_name = request.form['address']
    phone = request.form['phone']
    zipcode = request.form['postcode']
    is_local = True and request.form['province'] == '1' or False

    a = Address(rc_name, addr_name, phone, zipcode, is_local=is_local)
    db.session.add(a)
    g.user.address.append(a)
    db.session.commit()
    return redirect("/add_address")

@app.route("/do_update_address", methods=['POST'])
def do_update_address():
    rc_name = request.form['name']
    addr_name = request.form['address']
    phone = request.form['phone']
    zipcode = request.form['postcode']
    is_local = True and request.form['province'] == '1' or False

    a = Address.query.get(request.form['id'])
    a.reciver_name = rc_name
    a.address_name = addr_name
    a.phone = phone
    a.zipcode = zipcode
    a.is_local = is_local
    db.session.commit()
    return redirect('/add_address')

@app.route("/edit_address", methods=['GET'])
@login_required
def edit_address():
    address_id = request.args.get('id')
    if not address_id:
        return redirect('add_address')
    address = Address.query.filter_by(id=address_id).first()

    return render_template('web/address_edit.html', address=address)

@app.route("/delete_address")
@login_required
def delete_address():
    address_id = request.args.get('id')

    a = Address.query.get(address_id)
    db.session.delete(a)
    db.session.commit()

    # Query database for all address entries
    return redirect(url_for('add_address'))

# User register, login and logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user is None:
            error = 'Invalid email address'
        elif not check_password_hash(user.pw_hash,
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('web/login.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif get_user_id(request.form['email']) is not None:
            error = 'The email is already taken'
        else:
            user = User(request.form['username'], request.form[
                        'email'], generate_password_hash(request.form['password']))
            db.session.add(user)
            db.session.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('web/register.html', error=error)

# User profile and password related functions
@app.route("/edit_profile", methods=['GET'])
@login_required
def edit_profie():
    return render_template('web/user_edit.html')

@app.route("/do_edit_profile", methods=['POST'])
def do_edit_profile():
    if not check_password_hash(g.user.pw_hash, request.form['passwordold']):
        flash("Origin password incorrect!")
        return redirect('edit_profile')
    # nickname not none then change it
    if request.form['name'] != "":
        g.user.username = request.form['name']
    g.user.pw_hash = generate_password_hash(request.form['passwordnew'])
    db.session.commit()
    flash("Success!")
    return redirect('/edit_profile')

@app.route("/find_password", methods=['GET'])
def find_password():
    return render_template('web/pwd_find.html')

@app.route('/do_find_password', methods=['POST'])
def do_find_password():
    email_address = request.form['email']
    new_password = str(random.randint(100000, 999999))
    g.user.pw_hash = generate_password_hash(new_password)
    send_email(email_address, "Retrive Password", "Your new password is " + new_password)
    flash("Mail sent!")

    return redirect('/find_password')

def send_email(to_email_address, subject, text):
    msg = MIMEText(text)
    msg['To'] = email.utils.formataddr(('User', to_email_address))
    msg['From'] = email.utils.formataddr(('B2C', 'author@example.com'))
    msg['Subject'] = subject

    server = smtplib.SMTP("219.217.227.32", 25)
    server.set_debuglevel(True) # show communication with the server
    server.ehlo()
    server.login("b1123710410@ssmail.hit.edu.cn", "BENKE")
    try:
        server.sendmail('b1123710410@ssmail.hit.edu.cn', [to_email_address], msg.as_string())
       
    finally:
        server.quit()

@app.route("/query_credit")
@login_required
def query_credit():
    return render_template("web/credit_query.html")

# Manager user credit settings(Really? WTF?!)
@app.route("/manage_user", methods=['GET', 'POST'])
def manage_user():
    credit_req = CreditRequirement.query.get(0)
    
    return render_template('back/user_admin.html', credit_req=credit_req)

@app.route("/do_manage_user", methods=['POST'])
def do_manage_user():
    credit_req = CreditRequirement.query.get(0)
    if request.form['userlevel'] == '1':
        credit_req.normal = request.form['credit']
        credit_req.normal_percent = request.form['ratio']
    elif request.form['userlevel'] == '2':
        credit_req.silver = request.form['credit']
        credit_req.silver_percent = request.form['ratio']
    elif request.form['userlevel'] == '3':
        credit_req.gold = request.form['credit']
        credit_req.gold_percent = request.form['ratio']
    elif request.form['userlevel'] == '4':
        credit_req.pt = request.form['credit']
        credit_req.pt_percent = request.form['ratio']
    db.session.commit()
    return redirect('/manage_user')

# fuck fuck fuck ...............................


@app.route('/edit_dir', methods=['GET', 'POST'])
def edit_dir():
    error = None

    if request.method == 'POST':
        if 'remove' in request.form:
            if request.form['cate']:
                a = TopDirectory.query.filter_by(id = request.form['cate']).first()
                db.session.delete(a)
                db.session.commit()
                return redirect(url_for('edit_dir'))
            assert request.form['kid_cate']
            a = Directory.query.filter_by(id = request.form['kid_cate']).first()
            db.session.delete(a)
            db.session.commit()
            return redirect(url_for('edit_dir'))
            
        if request.form['cate']:
            a = TopDirectory.query.filter_by(id = request.form['cate']).first()
            return redirect(url_for('add_dir', origin_info_set = a.as_dict(), top = True))
        a = Directory.query.filter_by(id = request.form['kid_cate']).first()
        return redirect(url_for('add_dir', origin_info_set = a.as_dict()))
        
        #return redirect(url_for("index"))
    return render_template('back/category_list.html', error=error,top_level=TopDirectory.query.all(), count=0)

@app.route('/add_dir', methods=['POST', 'GET'])
def add_dir(origin_info_set='{}', top = False):
    if request.method == 'POST':
        top_level = False
        '''
        file = request.files['file']
        path = ''
        if file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
        '''
        if 'origin_info_set' in request.args:
            o = eval(request.args['origin_info_set'])
            if 'top' in request.args:
                a = TopDirectory.query.filter_by(id = o['id']).first()
            else:
                a = Directory.query.filter_by(id = o['id']).first()

            a.dir_name = request.form['name']
            a.description = request.form['description']
            db.session.commit()
            return redirect(url_for('edit_dir'))

        path = ''
        if request.form['parent'] == '':
            d = TopDirectory(request.form['name'], request.form['description'],
                             path)
            db.session.add(d)
        else:
            d = Directory(request.form['name'], request.form['description'],
                          path, int(request.form['parent']))
            parents = TopDirectory.query.filter_by(
                id=request.form['parent']).first()
            db.session.add(d)
            parents.kids.append(d)

        db.session.commit()
        return redirect(url_for("edit_dir")) 

    if 'origin_info_set' in request.args:
        origin_info_set = request.args['origin_info_set']
    return render_template('/back/category_edit.html', origin_info_set=eval(origin_info_set), top_level=TopDirectory.query.all())


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/item_list/<int:cate_id>')
def item_list(cate_id):
    items = Item.query.filter_by(cate_id = cate_id).all()
    return render_template("back/item_list.html", items = items, cate_id = cate_id)

@app.route('/add_item', methods = ['POST'])
def add_item():
    a = Item(request.form['name'], request.form['description'], request.form['price'], request.form['discount'], request.form['storage'], request.form['cate_id'])
    cate = Directory.query.filter_by(id = request.form['cate_id']).first()
    cate.items.append(a)
    db.session.add(a)
    db.session.commit()
    return redirect(url_for('item_list', cate_id = request.form['cate_id']))

@app.route('/edit_item/<int:id>', methods = ['GET', 'POST'])
def edit_item(id):
    if request.method == 'POST':
        i = Item.query.filter_by(id = id).first()
        i.item_name = request.form['name']
        i.price = request.form['price']
        i.description = request.form['desc']
        i.discount = request.form['discount']
        i.count = request.form['count']
        db.session.commit()
        return redirect(url_for('item_list', cate_id = i.cate_id))
    i = Item.query.filter_by(id = id).first()
    return render_template('back/item_edit.html', item = i)

@app.route('/remove_item/<int:id>', methods = ['GET'])
def remove_item(id):
    assert request.method == 'GET'
    i = Item.query.filter_by(id = id).first()
    cate_id = i.cate_id
    db.session.delete(i)
    db.session.commit()
    return redirect(url_for('item_list', cate_id = cate_id))

@app.route('/comment_list/<int:id>', methods = ['GET'])
@login_required
def comment_list(id):
    comments = Comment.query.filter_by(item_id = id).all()
    for comment in comments:
        user = User.query.filter_by(id = comment.user_id).first()
        comment.__dict__['user'] = user
    return render_template('web/comment_list.html', comments = comments)

@app.route('/add_comment/<int:id>', methods = ['POST', 'GET'])
@login_required
def add_comment(id):
    if request.method == 'POST':
        date = datetime.now()
        comment = Comment(request.form['like'],'',request.form['desc'], date, id, g.user.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('comment_list', id = id))
    return render_template('web/comment_add.html')
    

