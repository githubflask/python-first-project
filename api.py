
from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from sqlalchemy.orm.exc import UnmappedClassError, UnmappedInstanceError
from flask_jwt_extended import JWTManager, jwt_required , create_access_token
from flask_mail import Mail, Message
 

app = Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\narendra\\Desktop\\planet.db'
# 'C:\\\' + os.path.join(basedir,'planet.db')
app.config['JWT_SECRET_KEY'] = 'super_secret'
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
db =SQLAlchemy(app)
ma =Marshmallow(app)
jwt = JWTManager(app)


# @app.cli.command('/db_create')
@app.route('/db_create')
def db_create():
    db.create_all()
    return "database created!"


@app.route('/db_drop')
def db_drop():
    db.drop_all()
    return "database droped!"



# @app.cli.command('/db_seed')
@app.route('/db_seed')
def db_seed():
    mercury = planet(planet_name = 'mercury',
                     planet_type = 'class D',
                     home_start = 'sol',
                     mass = '23.43e4',
                     radius = '34.65',
                     distance = '34.65e6')
    
    
    venus = planet(planet_name = 'venus',
                     planet_type = 'class K',
                     home_start = 'sol',
                     mass = '19.43e4',
                     radius = '54.65',
                     distance = '90.65e6')


    earth = planet(planet_name = 'earth',
                        planet_type = 'class M',
                        home_start = 'sol',
                        mass = '15.43e4',
                        radius = '24.65',
                        distance = '90.65e6')

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)
    db.session.commit()


    test_user = User(first_name = 'swathi',
                      last_name = 'boddu',
                      email = 'swath gmail',
                      password = 'password')

    db.session.add(test_user)
    db.session.commit() 
    return "database seeded!"                                    



@app.route('/hi')
def hello():
    return 'Hello Swathi!'

@app.route('/bi')
def bye():
    
        return jsonify(message= 'Bye Bye Swathi!',
                       msg='hi swathi',
                       warning='do not use'),200

@app.route('/not_found')
def no():

        return jsonify(message = "not found "),500




@app.route('/parameters/<name>/<age>')
def parameters():
     name= request.args.get('name')
     age= int(request.args.get('age'))
     if age < 18:
        return jsonify("sorry"  + name + " , you are not old enough")
     else:
        return jsonify("welcome"  + name +  " , you are old enough")



@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name : str,age : int):
    if age < 18:
        return jsonify(message="sorry"   + name + ",you are not old enough")
    else:
        return jsonify(message="welcome"    + name + ",you are old enough")    


@app.route('/planets',methods=['GET'])
def planets():
    planets_list = planet.query.all()
    result = planet_schema.dump(planets_list)
    return jsonify (result.data)



@app.route('/register',methods = ['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify("that email alredy exists."),409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name = first_name, last_name= last_name, password= password, email= email)
        db.session.add(user)
        db.session.commit()
        return jsonify(message = "user created successfully."),201


@app.route('/login',methods=['POST'])
# @jwt_required
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.json['email']
        password = request.json['password']

    test = User.query.filter_by(email = email , password = password).first()
    if test:
        access_token = create_access_token(identify = email)
        return jsonify(meaasge='login successed',access_token = access_token)
    else:
        return jsonify(message = 'bad email or password'),401



@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("your planetary API password is " + user.password,
                      sender="admin@planetary-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email)
    else:
        return jsonify(message="That email doesn't exist"), 401





# DB Models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer,primary_key= True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    password = Column(String)


class planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer,primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_start = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','first_name','last_name','email','password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id','planet_name','planet_type','home_star','mass','radius','distance')



user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)



if __name__ == '__main__':
    app.run()



