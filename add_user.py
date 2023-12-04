from run import db, User,app, bcrypt
user_list = [["Garnacho",'garnacho@hcmut.edu.vn',"123"],
             ["Bell",'bell@hcmut.edu.vn',"123"],
            ]
def create_User(user_list):
    for user in user_list:
        hashed_password = bcrypt.generate_password_hash(user[2]).decode('utf-8')
        new_user = User(username=user[0], email=user[1], password=hashed_password) 
        with app.app_context():
            db.session.add(new_user) 
            db.session.commit()
#create_User(user_list)

    
with app.app_context():
    all_user = User.query.all()
    user = User.query.filter_by(username="Shan").first()
    print(user.password)
    


# with app.app_context():
#     db.drop_all()


# with app.app_context():
#     all_user = User.query.all()
#     for user in all_user:
#         db.session.delete(user)
#         db.session.commit()
#     print(all_user)
    