from SQL import SQL

db = SQL()

tableName = "items"
primaryKey = "itemID"
primaryKeyValue = "12"
requiredRoleID = db.getData("SELECT requiredRoleID FROM items WHERE itemID = %s", (int(primaryKeyValue),))[0][0]
print(requiredRoleID)