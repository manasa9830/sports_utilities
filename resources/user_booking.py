from flask_restful import Resource,reqparse
from flask import jsonify
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token,jwt_required
from db import query
from resources.user import Users
from datetime import date
class User_Bookings_log(Resource):
    @jwt_required
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='user_id Cannot be blank')
        data= parser.parse_args()
        #result=[]
        try:
            res= query(f"""Select * from bookingHistory2 where user_id='{data["id"]}'  and status<>CAST(2 AS UNSIGNED) and return_day is Null """,return_json=False)
            res1=query(f""" select resource_name from resources where resource_id={res[0]['r_id']} """,return_json=False)
            #log2= query(f"""Select * from bookingHistory2 where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=(date_format(curdate()-1,"%Y-%m-%d"))""",return_json=False)
            #if(len(log1)!=0):
                #result.append(log1)
            #if(len(log2)!=0):
                #result.append(log2)
            return jsonify({"booking_time":res[0]['booking_time'],
                            "day": res[0]['day'],
                            "r_id": res[0]['r_id'],
                            "resource_name":res1[0]['resource_name'],
                            "reservation_time": res[0]['reservation_time'],
                            "return_day": res[0]['return_day'],
                            "return_time": res[0]['return_time'],
                            "status": res[0]['status'],
                            "user_id": res[0]['user_id']})
        except:
            return {"message": "There was an error connecting to bookings table"}, 500

class UserBookingFine(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='user_id Cannot be blank')
        data= parser.parse_args()
        result=[]
        try:
            log = query(f"""select fine from students where id={data["id"]} and fine>0 """,return_json=False)
            if(len(log)==0):
                return {"message":"No Due"},200
            else:
                log1= query(f""" select * from bookingHistory2 where user_id={data["id"]} """,return_json=False)
                result.append(log1[-1])
                return jsonify(result)
        except:
            return {"message": "There was an error connecting to students table"}, 500

class allBookings(Resource):
    @jwt_required
    def get(self):
        try:
            return query(f"""Select * from bookingHistory2 where status<>2 order by day DESC;""")
        except:
            return {"message": "There was an error connecting to the booking table"}, 500


