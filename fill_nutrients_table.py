import sqlite3

db = sqlite3.connect("gwf.db")

db.execute("INSERT INTO nutrients (fdcNumber, name) VALUES (?, ?)", (208, "calories"))
db.execute("INSERT INTO nutrients (fdcNumber, name) VALUES (?, ?)", (204, "total fat"))
db.execute("INSERT INTO nutrients (fdcNumber, name) VALUES (?, ?)", (307, "sodium"))
db.execute("INSERT INTO nutrients (fdcNumber, name) VALUES (?, ?)", (291, "fiber"))
db.execute("INSERT INTO nutrients (fdcNumber, name) VALUES (?, ?)", (209, "starch"))
db.execute("INSERT INTO nutrients (fdcNumber, name) VALUES (?, ?)", (203, "protein"))

db.commit()
db.close()
