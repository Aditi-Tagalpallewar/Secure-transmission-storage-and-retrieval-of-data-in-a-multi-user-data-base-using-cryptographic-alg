import cx_Oracle 
def getConnection():
    conn = cx_Oracle.connect("SHALMALI/Oracle#1@localhost:1521")
    return conn

def ifExists(name):
    conn = getConnection()
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM USERS WHERE name = '{name}'"
    cursor.execute(query) 
    for res in cursor:
        ret = res[0] # COUNT of users
    conn.commit()
    cursor.close()
    return ret

def fetchData(name):
    l = []
    conn = getConnection()
    cursor = conn.cursor()
    query = f"select * from USERS WHERE name = '{name}'"
    cursor.execute(query)
    for res in cursor:
        l.append(res[0]) # name
        l.append(res[1]) # salt
        l.append(res[2]) # key
    conn.commit()
    cursor.close()
    return l

def insert(name,salt,key):
    conn = getConnection()
    cursor = conn.cursor()
    query = f"insert into USERS values ('{name}','{salt}','{key}')"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    print("User Database updated.") 

def Store_in_Cloud(name, message, sharedkey, sign):
    conn = getConnection()
    cursor = conn.cursor()
    query = f"insert into DATABASE values ('{name}','{message}','{sharedkey}','{sign[0]}','{sign[1]}','{sign[2]}','{sign[3]}','{sign[4]}','{sign[5]}')"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    print("\nEncrypted data added to the Database successfully!")

def Retrieve_from_Cloud(name):
    l = [] 
    conn = getConnection() 
    cursor = conn.cursor()
    query = f"select * from DATABASE WHERE name = '{name}'"
    cursor.execute(query)
    for res in cursor:
        l.append(res)
    conn.commit()
    cursor.close()
    return l