from flask_restful import Resource,reqparse
from flask import jsonify
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token,jwt_required
from db import query
from resources.user import Users
from datetime import date,datetime,timedelta

class cancelBooking(Resource):
    @jwt_required
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='user_id Cannot be blank')
        data= parser.parse_args()
        now = datetime.now()
        now=now+timedelta(hours=5,minutes=30)
        current_time = now.strftime("%H:%M:%S")
        current_time=str(current_time)
        data['current_time']=current_time
        try:
            log1=query(f"""Select * from bookingHistory2 where user_id='{data["id"]}' and time_to_sec(timediff('{data['current_time']}',reservation_time))/60 <=20 and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status=0 """,return_json=False)
            
            if(len(log1)==0):
                return {"message": "Can't Cancel your booking request"}, 400
            else:
                query(f"""UPDATE booking set status=CAST(2 AS UNSIGNED) where user_id='{data["id"]}' and  date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status<>1""")
                return {"message": "cancelled!"}, 200
        except:
            return {"message": "Cannot connect to the bookings table"}, 500

class check(Resource):
    def get(self):
        try:
            now = datetime.now()
            now=now+timedelta(hours=5,minutes=30)
            current_time = now.strftime("%H:%M:%S")
            return {"message":current_time},200
        except:
            return {"m":"failed"},500
