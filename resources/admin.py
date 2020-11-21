from flask_restful import Resource,reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token,jwt_required
from db import query
from resources.user import User
class Admin(Resource):
    def __init__(self,id,name,password):
        self.id=id
        self.name=name
        self.password=password
    
    @classmethod
    def getAdminById(cls,id):
        result=query(f"""SELECT admin_id,name,password FROM admin WHERE admin_id={id}""",return_json=False)
        if len(result)>0: return Admin(result[0]['admin_id'],result[0]['name'],result[0]['password'])
        return None


class AdminLogin(Resource):
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id',type=int,required=True,help="ID cannot be blank.")
        parser.add_argument('name',type=str,required=True,help="Name cannot be blank.")
        parser.add_argument('password',type=str,required=True,help="Password cannot be blank.")
        data=parser.parse_args()
        admin=Admin.getAdminById(data['id'])
        if admin and safe_str_cmp(admin.password,data['password']) and safe_str_cmp(admin.name, data['name']):
            access_token=create_access_token(identity=admin.id,expires_delta=False)
            return {'access_token':access_token},200
        else:
            return {"access_token":"Invalid credentials"},401
        return {'message':'Error'}

          
class resource_(Resource):
    def __init__(self, id, name, count, resources_available):
        self.id=id
        self.name=name
        self.count=count
        self.resources_available=resources_available

    @classmethod
    def getResourceById(cls,id):
        result=query(f"""SELECT * from resources WHERE resource_id={id}""",return_json=False)
        if len(result)>0: 
            return resource_(result[0]['resource_id'],result[0]['resource_name'],result[0]['count'],result[0]['resources_available'])
        return None
    
    @classmethod
    def getResourceByName(cls,name):
        result=query(f"""SELECT * from resources WHERE lower(resource_name)=lower("{name}")""",return_json=False)
        if len(result)>0: 
            return resource_(result[0]['resource_id'],result[0]['resource_name'],result[0]['count'],result[0]['resources_available'])
        return None


class Resourcespresent(Resource):
    @jwt_required
    def get(self):
        try:
            return query(f"""Select * from resources""")
        except:
            return {"message": "There was an error connecting to the resource table"}, 500

class AddExtraResource(Resource):
    def post(self):
        parser=reqparse.RequestParser()
        #parser.add_argument('id',type=int,required=True,help="ID cannot be blank.")
        parser.add_argument('name',type=str,required=True,help="Name cannot be blank.")
        parser.add_argument('count',type=int,required=True,help="Count cannot be blank")
        data=parser.parse_args()
        res=resource_.getResourceByName(data['name'])
        try:
            if res:
                return {"message": "Coudnt add resource because it already exists"}, 401
            else:
                query(f"""INSERT into resources(resource_name,count,resources_available) values('{data["name"]}', CAST({data["count"]} as UNSIGNED) ,CAST({data["count"]} as UNSIGNED))""")
        except:
            return {"message": "Coudnt add resource"}, 401


class DeleteResource(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('id',type=int,required=True,help="ID cannot be blank.")
    def get(self):
        data=self.parser.parse_args()
        r=resource_.getResourceById(data['id'])
        try:
            if r:
                query(f"""DELETE from resources WHERE resource_id= {data["id"]} """)
            else:
                return {"message": "Coudn't delete resource because it doesn't exist"}, 401
        except:
            return {"message": "Coudnt delete resource"}, 500

class admin_change_password(Resource):
    @jwt_required
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='user_id Cannot be blank')
        parser.add_argument('password',type=str,required=True,help="Password cannot be blank.")
        parser.add_argument('new_password',type=str,required=True,help="new Password cannot be blank.")
        data= parser.parse_args()
        try:
            res = query(f"""Select * from admin where admin_id={data["id"]} """,return_json=False)
            if(res[0]['password']==data['password']):
                if(res[0]['password']!=data['new_password']):
                    query(f""" update admin set password='{data['new_password']}' where admin_id={data['id']};""")
                    return {"message":"password changed !"},200
                else:
                    return {"message":"old password and new are same,cannot update !"},200
            else:
                return {"message":"enter the correct password"},200
        except:
            return {"message": "There was an error connecting to admin table"}, 400