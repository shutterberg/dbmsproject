from app import Vehicle_details,db
data=Vehicle_details(name = "novin",car_num = "ka19mc6110",fuel = "p",service_date="10/10/2020")
db.session.add(data)
db.session.commit()