from flask import Flask,jsonify,url_for,request
import pymysql
from flask_restful import Api,Resource 
from flask_cors import CORS,cross_origin
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from db import query
from resources.user import *
from resources.user_cancel import *
from resources.admin import *
from resources.user_booking import *
from resources.resource import *
from resources.booking_log import *
from resources.timetable import *

app= Flask(__name__)
api=Api(app)
CORS(app,allow_headers=["Content-Type","Authorization","Access-Control-Allow-Credentials"],supports_credentials=True)
app.config['PROPAGATE_EXCEPTIONS']=True
app.config['PREFERRED_URL_SCHEME']='https'
app.config['JWT_SECRET_KEY']='sportsresourceapikey'
api= Api(app)
jwt = JWTManager(app)
app.config.from_pyfile('config.cfg')
mail = Mail(app)
s = URLSafeTimedSerializer('Thisisasecretkey!')

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error': 'authorization_required',
        "description": "Request does not contain an access token."
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'invalid_token',
        'message': 'Signature verification failed.'
    }), 401


api.add_resource(UserRegister,'/register')
api.add_resource(UserLogin,'/login')
api.add_resource(AdminLogin, '/AdminLogin')
api.add_resource(Resourcespresent, '/ResourcesPresent')
api.add_resource(User_Bookings_log,'/userBookingslog')
api.add_resource(UserBookingFine,'/userDue')
api.add_resource(cancelBooking,'/cancelBooking')
api.add_resource(resourceDetails,'/resourceDetails')
api.add_resource(incrementResourcesByone,'/incrementByOne')
api.add_resource(incrementResourcesByValue,'/incrementByValue')
api.add_resource(decrementResourcesByone,'/decrementByOne')
api.add_resource(decrementResourcesByValue,'/decrementByValue')
api.add_resource(issueResource,'/issueResource')
api.add_resource(acceptReturnedResource,'/acceptResource')
#api.add_resource(bookingHistory2,'/bookingHistory2')
api.add_resource(issuedBookings,'/issuedBookings')
api.add_resource(blockedUsers,'/blockedUsers')
api.add_resource(unblockUser,'/unblockUser')
api.add_resource(blockUser,'/blockUser')
api.add_resource(bookResource,'/bookResource')
api.add_resource(bookingRequests,'/bookingRequests')
api.add_resource(rejectBooking,'/rejectBooking')
api.add_resource(returnedHistory,'/returnedHistory')
api.add_resource(notreturnedHistory,'/notreturnedHistory')
api.add_resource(notreturnedToday,'/notreturnedToday')
api.add_resource(allBookings,'/allBookings')
api.add_resource(AddExtraResource, '/AddExtraResource')
api.add_resource(DeleteResource, '/DeleteResource')
api.add_resource(check,'/check')
api.add_resource(Users,'/users')
api.add_resource(changePassword,'/changePassword')
api.add_resource(timetable,'/timetable')
api.add_resource(admin_change_password,'/admin_change_password')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return '<form action="/" method="POST"><input name="email"><input type="submit"></form>'

    email = request.form['email']
    token = s.dumps(email, salt='email-confirm')

    msg = Message('Confirm Email', sender='sportsresources.cbit@gmail.com', recipients=[email])

    link = url_for('confirm_email', token=token, _external=True)

    msg.body = 'Your link is {}'.format(link)

    mail.send(msg)

    return '<h1>The email you entered is {}. The token is {}</h1>'.format(email, token)

@app.route('/forgot_password', methods=['GET'])
def forgot_password():
    global id
    parser=reqparse.RequestParser()
    parser.add_argument('id',type=str,required=True,help="id  cannot be  blank!")
    data=parser.parse_args()
    admin_id=int(data['id'])
    res1=query(f"""select email from students where id='{data["id"]}';""",return_json=False)
    res2=query(f"""select email from admin where admin_id={admin_id};""",return_json=False)
    if(len(res1)!=0):
        email =res1[0]['email']
        id=data["id"]
        token = s.dumps(email, salt='email-confirm')

        msg = Message('Confirm Email', sender='sportsresources.cbit@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return {"message":"mail has been sent to reset password"},200
    elif(len(res2)!=0):
        email =res2[0]['email']
        id=admin_id
        token = s.dumps(email, salt='email-confirm')

        msg = Message('Confirm Email', sender='sportsresources.cbit@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return {"message":"mail has been sent to reset password"},200


@app.route('/confirm_email/<token>',methods=['GET', 'POST'])
def confirm_email(token):
    try:
        if request.method == 'GET':
            email = s.loads(token, salt='email-confirm', max_age=3600)
            return '<center><h1 style="color:blue">SPORTS RESOURCES BOOKING APPLICATION</h1><br><br><h1 style="font-family:verdana">Change Password!</h1><br><br><form action="/confirm_email/<token>" method="POST"><input type="password" placeholder="password" name="password" required class="form-control my-2"><br><br><input type="password" placeholder="confirm_password" name="confirm_password" required class="form-control my-2"><br><br><input class="btn col-6 text-black font-weight-bold" type="submit"style="background-color:  #2bb321; font-size: 18px;"></center></form>'
        if request.method == 'POST':
            p1=request.form['password']
            p2=request.form['confirm_password']
            if(p1==p2 and type(id)==str):
                query(f""" update students set password='{p1}' where id='{id}' """)
                return '<h1>Updated Password !</h1>'
            elif(p1==p2 and type(id)==int):
                query(f""" update admin set password='{p1}' where admin_id={id} """)
                return '<h1>Updated Password !</h1>'
            
            else:
                return '<h1>Password is not updated</h1>'
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'


@app.route('/update_password')
def update_password():
    p1=request.form['password']
    p2=request.form['confirm_password']
    if(p1==p2):
        query(f""" update students set password={p1} where id={id} """)
        return '<h1>Updated Password</h1>'
    else:
        return '<h1>Password is not updated</h1>'

if __name__=='__main__':
    app.run(port="5000",debug=True)
