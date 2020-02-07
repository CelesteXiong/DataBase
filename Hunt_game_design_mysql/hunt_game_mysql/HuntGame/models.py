from HuntGame import db,login_manager
from flask_login import UserMixin
# reload the user from userID stored in the session
# need attributes:
# - authenticated
# - active
# - anonymous
# method: getID
@login_manager.user_loader
def load_user(user_id):
    return Characters.query.get(int(user_id))


class Characters(db.Model, UserMixin):
    def get_id(self):
        # login_user calls get_id on the user instance
        # UserMixin provides a get_id method that returns the id attribute
        return self.cid
    cid = db.Column(db.Integer, primary_key=True, nullable=False)
    cname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    money = db.Column(db.Float, nullable=False, default=0)
    treasure = db.relationship("Treasures",
                               cascade="save-update, delete, merge",
                               backref="character",
                               lazy=True)

    def __repr__(self):
        return f"Characters('cid:{self.cid}','password:{self.password}','cname:{self.cname}','money:{self.money}',\n {self.treasure})"


class Treasures(db.Model):
    tid = db.Column(db.Integer, primary_key=True, nullable=False)
    tname = db.Column(db.String(255), nullable=False)
    luck_score = db.Column(db.Integer, default=0)
    competence_score = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0)
    on_sale = db.Column(db.Boolean, default=False)
    on_dress = db.Column(db.Boolean, default=False)
    cid = db.Column(db.Integer, db.ForeignKey('characters.cid'), default=None)


    def __repr__(self):
        return f"Treasure: 'tid:{self.tid}','tname: {self.tname}','price: {self.price}',\n 'luck_score:{self.luck_score}','competence_score:{self.competence_score}," \
               f"\n 'on_sale: {self.on_sale}','on_dress: {self.on_dress}'" \
               f"\n 'cid: {self.cid}"
