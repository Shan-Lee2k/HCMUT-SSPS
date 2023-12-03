from run import db, User,app
user_list = [["Garnacho",'garnacho@hcmut.edu.vn',"123"],
             ["Bell",'bell@hcmut.edu.vn',"123"],]
def create_User(user_list):
    for user in user_list:
        new_user = User(username=user[0], email=user[1], password=user[2]) 
        with app.app_context():
            db.session.add(new_user) 
            db.session.commit()
# create_User(user_list)
with app.app_context():
    all_user = User.query.all()
    print(all_user)
        



    