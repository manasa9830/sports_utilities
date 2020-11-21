from flask_restful import Resource,reqparse
from flask import jsonify
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token,jwt_required
from db import query
from resources.user import Users
from datetime import datetime,timedelta,date

class timetable(Resource):
    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('branch', type=str, required=True, help='branch Cannot be blank')
        parser.add_argument('year', type=int, required=True, help='year Cannot be blank')
        parser.add_argument('section', type=int, required=True, help='section Cannot be blank')
        data= parser.parse_args()
        data['year']=int(data['year'])
        data['section']=int(data['section'])
        section='section'+str(data['section'])
        try:
            return query(f"""Select {section} as time_table from timetable where branch=lower('{data['branch']}') and year={data['year']} and {section} is not Null""")
        except:
            return