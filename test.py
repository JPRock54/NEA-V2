from SQL import SQL


db = SQL()
roles = "roles"
query = db.getData("SELECT * FROM", (roles))
print(query)