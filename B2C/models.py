from B2C import db

order_item_re = db.Table('order_items',
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column(
                             'item_id', db.Integer, db.ForeignKey('item.id')),
                         db.Column(
                             'order_id', db.Integer, db.ForeignKey('order.id'))
                         )

user_collection_re = db.Table('collection', 
    db.Column('id', db.Integer, primary_key = True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('date', db.DateTime)
    )


class User(db.Model):

    """docstring for User"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False)
    email = db.Column(db.String(80), unique=True)
    pw_hash = db.Column(db.Text)
    register_date = db.Column(db.DateTime)

    consumption = db.Column(db.Float)
    points = db.Column(db.Integer)

    # user -> address
    address = db.relationship('Address', backref='user', lazy='dynamic')

    # order
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref = 'user', lazy = 'dynamic')
    collections = db.relationship('Item', secondary=user_collection_re, backref=db.backref('user', lazy='dynamic'))

    def __init__(self, username, email, pw_hash, register_date, consumption=0, points=0):
        self.username = username
        self.email = email
        self.pw_hash = pw_hash
        self.register_date = register_date
        self.points = 0
        self.consumption = 0

    def __repr__(self):
        return '<User %r>' % self.username


class Address(db.Model):

    """docstring for Address"""
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    reciver_name = db.Column(db.String(180), unique=False)
    address_name = db.Column(db.String(180), unique=False)
    phone = db.Column(db.String(20), unique=False)
    zipcode = db.Column(db.String(40))
    is_local = db.Column(db.Boolean)

    # user -> address
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # order

    def __init__(self, reciver_name, address_name, phone, zipcode, is_local=False):
        self.reciver_name = reciver_name
        self.address_name = address_name
        self.phone = phone
        self.zipcode = zipcode
        self.is_local = is_local

    def __repr__(self):
        return '<Address %r>' % self.reciver_name


class Order(db.Model):

    """docstring for Order"""
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    status = db.Column(db.Integer)  # 0:wait for pay 1:pay 2:done
    deliver_method = db.Column(db.Integer)  # 0: 1:
    is_confirm = db.Column(db.Boolean)
    points = db.Column(db.Integer)
    total = db.Column(db.Float)
    count = db.Column(db.String(10000))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    items = db.relationship(
        'Item', secondary=order_item_re, backref=db.backref('orders', lazy='dynamic'))

    def __init__(self, date, user_id, address_id, total, points = 0, status=0, deliver_method=0, is_confirm = False, count = '0'):
        
        self.date = date
        self.user_id = user_id
        self.address_id = address_id
        self.status = status
        self.points = points
        self.deliver_method = deliver_method
        self.is_confirm = is_confirm
        self.total = total
        self.count = count


class Item(db.Model):

    """docstring for Item"""
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String, unique=False)
    description = db.Column(db.Text, unique = False)
    image = db.Column(db.Text)  # file path
    price = db.Column(db.Float)
    discount = db.Column(db.Float)
    count = db.Column(db.Integer)
    sales = db.Column(db.Integer)

    comments = db.relationship('Comment', backref='item', lazy='dynamic')

    cate_id = db.Column(db.Integer, db.ForeignKey('directory.id'))

    def __init__(self, item_name, description, price, discount=1.0, count=0, cate_id = 0, sales=0, image = ''):
        self.item_name = item_name
        self.description = description
        self.price = price
        self.discount = discount
        self.count = count
        self.sales = sales
        self.cate_id = cate_id
        self.image = image


    def consume(self, num=0):
        self.count = self.count - num

    def __repr__(self):
        return '<Item %r>' % self.item_name


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Integer)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, rate, title, content, date, item_id, user_id):
        self.rate = rate
        self.title = title
        self.content = content
        self.item_id = item_id
        self.date = date
        self.user_id = user_id

    def __repr__(self):
        return '<Commment %r>' % self.title


class Directory(db.Model):
    __tablename__ = 'directory'
    id = db.Column(db.Integer, primary_key=True)
    dir_name = db.Column(db.String(80))
    description = db.Column(db.Text)
    image_path = db.Column(db.String(100))

    parent_id = db.Column(db.Integer, db.ForeignKey('top_dir.id'))

    items = db.relationship('Item', backref='directory', lazy='dynamic')

    def __init__(self, dir_name, description='', image_path='', parent_id=None):
        self.dir_name = dir_name
        self.description = description
        self.image_path = image_path
        self.parents_id = parent_id

    def __repr__(self):
        return '<Directory %r>' %self.dir_name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TopDirectory(db.Model):
    __tablename__ = 'top_dir'
    id = db.Column(db.Integer, primary_key=True)
    dir_name = db.Column(db.String(80))
    description = db.Column(db.String(100))
    image_path = db.Column(db.String(100))

    kids = db.relationship('Directory', backref='user', lazy='dynamic')

    def __init__(self, dir_name, description='', image_path=''):
        self.dir_name = dir_name
        self.description = description
        self.image_path = image_path

    def __repr__(self):
        return '<TopDirectory %r>' %self.dir_name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100))
    pw_hash = db.Column(db.Text)

    def __init__(self, admin_name, pw_hash):
        self.admin_name = admin_name
        self.pw_hash = pw_hash

    def __repr__(self):
        pass
        
        
class CreditRequirement(db.Model):
	__tablename__ = 'credit_limit'
	id = db.Column(db.Integer, primary_key = True)
	normal = db.Column(db.Integer)
	silver = db.Column(db.Integer)
	gold = db.Column(db.Integer)
	pt = db.Column(db.Integer)

	normal_percent = db.Column(db.Integer)
	silver_percent = db.Column(db.Integer)
	gold_percent = db.Column(db.Integer)
	pt_percent = db.Column(db.Integer)
	
	def __init__(self, normal, silver, gold, pt, normal_percent, silver_percent, gold_percent, pt_percent):
		self.normal = normal
		self.silver = silver
		self.gold = gold
		self.pt = pt
		self.normal_percent = normal_percent
		self.silver_percent = silver_percent
		self.gold_percent = gold_percent
		self.pt_percent = pt_percent

	def __repr__(self):
		pass
