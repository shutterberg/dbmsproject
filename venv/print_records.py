from app import Vehicle_details,User
user=User.query.all()
for person in user:
    print("User id :",person.id)
    print("Name :",person.username)
    print("car_num: ",person.password_hash)