from flask_restful import Resource,reqparse
from flask import jsonify
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token,jwt_required
from db import query
from resources.user import Users
from datetime import datetime,timedelta,date

class resourceDetails(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='resource_id Cannot be blank')
        data= parser.parse_args()
        try:
            return query(f"""Select * from resources where resource_id={data["id"]}""")
        except:
            return {"message": "There was an error connecting to resources table"}, 500

class incrementResourcesByValue(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='resource_id Cannot be blank')
        parser.add_argument('c', type=int, required=True, help='count Cannot be blank')
        data= parser.parse_args()
        try:
            query(f"""UPDATE resources  SET count=count+CAST({data["c"]} AS UNSIGNED) , resources_available=resources_available+CAST({data["c"]} AS UNSIGNED) where resource_id={data["id"]} """)
            return {"message":"changes are made to resources table","count":data["c"]}, 200
        except:
            return {"message": "There was an error connecting to resources table"}, 500

class decrementResourcesByValue(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='resource_id Cannot be blank')
        parser.add_argument('c', type=int, required=True, help='count Cannot be blank')
        data= parser.parse_args()
        try:
            query(f"""UPDATE resources  SET count=count-CAST({data["c"]} AS UNSIGNED) , resources_available=resources_available-CAST({data["c"]} AS UNSIGNED) where resource_id={data["id"]} and count>=CAST({data["c"]} AS UNSIGNED);""")
            return {"message":"changes are made to resources table"}, 200
        except:
            return {"message": "There was an error connecting to resources table"}, 500

class incrementResourcesByone(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='resource_id Cannot be blank')
        data= parser.parse_args()
        try:
            query(f"""UPDATE resources  SET resources_available=resources_available+1 where resource_id={data["id"]} and resources_available<count""")
            return {"message":"changes are made to resources table"}, 200

        except:
            return {"message": "There was an error connecting to resources table"}, 500

class decrementResourcesByone(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='resource_id Cannot be blank')
        data= parser.parse_args()
        try:
            query(f"""UPDATE resources  SET resources_available=resources_available-CAST(1 AS UNSIGNED) where resource_id={data["id"]} and resources_available>0""")
            return {"message":"changes are made to resources table"}, 200
        except:
            return {"message": "There was an error connecting to resources table while drecrement"}, 500

class issueResource(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='student_id Cannot be blank')
        #parser.add_argument('booking_time', type=str, required=True, help='booking_time Cannot be blank')
        data= parser.parse_args()
        now = datetime.now()
        now=now+timedelta(hours=5,minutes=30)
        current_time = now.strftime("%H:%M:%S")
        data["booking_time"]=str(current_time)
        try:
            result=query(f"""select * from bookingHistory2 where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status=CAST(0 AS UNSIGNED) """,return_json=False)
            log=query(f"""Select fine from students where id='{data["id"]}';""",return_json=False)
            if(log[0]['fine']>0):
                return {"message":"please clear the due"},200
            query(f"""UPDATE booking  SET status=2 where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status=0 """)
            ##query(f"""UPDATE booking  SET status=1,booking_time=time_format('{data["booking_time"]}',"%T") where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status<>1 """)
            ##except:
                ##query(f"""UPDATE booking  SET status=status+2 where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status=0 """)
                ##return {"message":"cancel your booking and try again"},200
            if(len(result)!=0):
                data["resc_id"]=result[0]['r_id']
                res1=query(f"""select * from resources  where resource_id={data["resc_id"]}""",return_json=False)
                if(res1[0]['resource_id']>0):
                    query(f"""UPDATE booking  SET status=CAST(1 AS UNSIGNED),booking_time=time_format('{data["booking_time"]}',"%T") where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status<>1 and  reservation_time='{result[0]['reservation_time']}' """)
                    query(f"""UPDATE resources  SET resources_available=resources_available-1 where resource_id={data["resc_id"]} and resources_available>0 """)
                    return {"message": "updated available resources"}, 200
                else:
                    return {"message": "Sorry there are no available resources"}, 200

            else:
                return {"message":"You didn't book any  resource"},404
        except:
            query(f"""UPDATE booking  SET status=status+2 where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status=0 """)
            return {"message": "There was an error connecting to booking table"}, 500

class acceptReturnedResource(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='student_id Cannot be blank')
        #parser.add_argument('return_time', type=str, required=True, help='return_time Cannot be blank')
        #parser.add_argument('return_day', type=str, required=True, help='return_day Cannot be blank')
        data= parser.parse_args()
        now = datetime.now()
        now=now+timedelta(hours=5,minutes=30)
        current_time = now.strftime("%H:%M:%S")
        #print(current_time)
        today = date.today()
        d1 = today.strftime("%Y-%m-%d")#check r_id - comparision with todays  date,instead take return time to check that and status=1
        data["return_time"]=str(current_time)
        data["return_day"]=str(d1)
        try:
            result=query(f"""select r_id from booking where user_id='{data["id"]}' and return_day is Null and status= CAST(1 AS UNSIGNED)""",return_json=False)
            data["resc_id"]=result[0]["r_id"]
            query(f"""UPDATE booking  SET return_time=time_format('{data["return_time"]}',"%T"),return_day=date_format('{data["return_day"]}',"%Y-%m-%d") where user_id='{data["id"]}' and return_day is Null and status=1""")
            query(f"""UPDATE resources  SET resources_available=resources_available+1 where resource_id={data["resc_id"]}""")
            res=query(f"""select * from bookingHistory2 where user_id='{data["id"]}' and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and time_to_sec(timediff(return_time,'16:20:00'))/60 >0""",return_json=False)
            res1=query(f"""select * from bookingHistory2 where user_id='{data["id"]}' and date_format(return_day,"%Y-%m-%d")<>date_format(day,"%Y-%m-%d") and date_format(return_day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") """,return_json=False)
            if(len(res)!=0 or len(res1)!=0):
                query(f"""UPDATE students  SET fine=50 where id='{data["id"]}'""")
                return {"message":"Fine has been added"},200
            else:
                return {"message": "updated available resources"}, 200
        except:
            return {"message": "There was an error connecting to resources table"}, 500

class rejectBooking(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='student_id Cannot be blank')
        data= parser.parse_args()
        try:
            query(f"""UPDATE booking  SET status=status+2 where user_id={data["id"]} and date_format(day,"%Y-%m-%d")=date_format(curdate(),"%Y-%m-%d") and status=0 """)
            return {"message": "updated status"}, 200
        except:
            return {"message": "There was an error connecting to booking table"}, 500


