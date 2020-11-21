from flask_restful import Resource,reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token,jwt_required
from db import query
from flask import jsonify,url_for,request

class User():
    def __init__(self,id,name,batch,password):
        self.id=id
        self.name=name
        self.batch=batch
        self.password=password

    @classmethod
    def getUserById(cls,id):
        result=query(f"""SELECT id,name,branch,password FROM students WHERE id='{id}'""",return_json=False)
        if len(result)>0: return User(result[0]['id'],result[0]['name'],result[0]['branch'],result[0]['password'])
        return None

class UserRegister(Resource):
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id',type=str,required=True,help="ID cannot be  blank!")
        parser.add_argument('name',type=str,required=True,help="username cannot be  blank!")
        parser.add_argument('mail_id',type=str,required=True,help="mail_id cannot be left blank!")
        parser.add_argument('branch',type=str,required=True,help="branch cannot be left blank!")
        parser.add_argument('password',type=str,required=True,help="Password cannot be  blank!")
        data=parser.parse_args()
        if User.getUserById(data['id']):
            return {"message": "A user with that id already exists"}, 400
        try:
            query(f"""INSERT INTO students(id,name,branch,password)
                                  VALUES('{data['id']}','{data['name']}','{data['mail_id']}','{data['branch']}','{data['password']}')""")
        except:
            return {"message": "An error occurred while registering."}, 500
        return {"message": "User created successfully."}, 201


class UserLogin(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('id',type=str,required=True,help="ID cannot be blank.")
    parser.add_argument('password',type=str,required=True,help="Password cannot be blank.")
    def post(self):
        data=self.parser.parse_args()
        user=User.getUserById(data['id'])
        if user and safe_str_cmp(user.password,data['password']):
            access_token=create_access_token(identity=user.id,expires_delta=False)
            return {'access_token':access_token},200
        return {"message":"Invalid Credentials!"}, 401

class changePassword(Resource):
    @jwt_required
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='user_id Cannot be blank')
        parser.add_argument('password',type=str,required=True,help="Password cannot be blank.")
        parser.add_argument('new_password',type=str,required=True,help="new Password cannot be blank.")
        data= parser.parse_args()
        try:
            res = query(f"""Select * from students where id='{data["id"]}' """,return_json=False)
            if(res[0]['password']==data['password']):
                if(res[0]['password']!=data['new_password']):
                    query(f""" update students set password='{data['new_password']}' where id='{data['id']}';""")
                    return {"message":"password changed !"},200
                else:
                    return {"message":"old password and new are same,cannot update !"},200
            else:
                return {"message":"enter the correct password"},401
        except:
            return {"message": "There was an error connecting to user table"}, 400

class Users(Resource):
    @jwt_required
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='user_id Cannot be blank')
        data= parser.parse_args()
        try:
            res = query(f"""Select * from students where id={data["id"]}""",return_json=False)
            if(len(res)!=0):
                return jsonify({"id": res[0]['id'],
                                "name":res[0]['name'],
                                "branch":res[0]['branch'],
                                "password":res[0]['password'],
                                "fine":res[0]['fine']})
        except:
            return {"message": "There was an error connecting to user table"}, 500

class bookResource(Resource):
    @jwt_required
    def post(self):
        parser=reqparse.RequestParser() #cannot book even if he doesnot return any resource have to add that
        parser.add_argument('id',type=str,required=True,help="ID cannot be  blank!")
        parser.add_argument('name',type=str,required=True,help="resource_name cannot be  blank!")
        parser.add_argument('day',type=str,required=True,help="date cannot be left blank!")
        parser.add_argument('reservation_time',type=str,required=True,help="reservation_time  cannot be  blank!")
        data=parser.parse_args()
        res=query(f"""select fine from students where id='{data["id"]}';""",return_json=False)
        if(res[0]['fine']>0):
            return {"message":"You can't book the resource until your due is cleared"},400
        log=query(f"""select resource_id,resources_available from resources where resource_name='{data["name"]}';""",return_json=False)
        result=query(f"""select * from booking where user_id='{data["id"]}' and return_day is Null and status= CAST(1 AS UNSIGNED)""",return_json=False)
        log1=query(f"""select * from bookingHistory2 where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status<>2 """,return_json=False)
        log2=query(f""" select date_format('{data['day']}',"%Y-%m-%d")=curdate() as dif; """,return_json=False)
        c=log2[0]['dif']
        d=len(result)
        if(len(log)!=0 and len(log1)==0 and c==1 and d==0 and log[0]['resources_available']>0):
            try:
                query(f"""INSERT INTO booking(user_id,r_id,day,reservation_time,status) 
                        VALUES('{data['id']}',CAST({log[0]['resource_id']} as UNSIGNED),date_format('{data['day']}',"%Y-%m-%d"),time_format('{data['reservation_time']}',"%T"),0);""")

                return {"message": "Booking is successful."}, 201
            except:
                return {"message": "An error occurred while booking."}, 400
        else:
            return {"message": "Resource is not available for you now,try to book after some time or return the issued resources."}, 400

'''class forgot_password():
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id',type=str,required=True,help="id  cannot be  blank!")
        data=parser.parse_args()
        res=query(f"""select email from students where id='{data["id"]}';""",return_json=False)
        email =res[0]['email']
        token = s.dumps(email, salt='email-confirm')

        msg = Message('Confirm Email', sender='sportsresources.cbit@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return {"message":"mail has been sent to reset password"},200'''
