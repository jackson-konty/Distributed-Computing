from msilib.schema import Error
import sqlite3 as sql



# It creates a class called Result that has three attributes: key, value, and size.
class Result:
    def __init__(self,key,value):
        self.key = key
        self.value = value
        self.size = len(bytes(value,encoding = "utf-8"))
    def toString(self)->str:
        return f"KEY {self.key}\n\rVALUE {self.value}\n\rSIZE {self.size}\n\rEND"


# It creates a database file and a table in it if they don't exist, and then it can add key-value
# pairs to the table and retrieve values from the table.
class KVstore:
    
    def __init__(self,db_file = r"kv.db"):
        '''If the database file doesn't exist, create it and create a table in it. If the database file does
        exist, open it and check if the table exists. If the table doesn't exist, create it.
        
        Parameters
        ----------
        db_file, optional
            The name of the database file.
        
        '''

        self.table = False
        self.db_file = db_file
        try:
            self.connection = sql.connect(self.db_file)
        except Error as e:
            print(e)
        if(self.connection):
            try:  
                curr = self.connection.cursor()
                table = """ CREATE TABLE IF NOT EXISTS data (
                    key VARCHAR(255) PRIMARY KEY,
                    value CHAR(25) NOT NULL,
                    timestamp INT
                    ); """
                curr.execute(table)
                self.table = True
            except (sql.Error, sql.Warning) as e:
                print(e)

    def addPair(self,key,value,timestamp) -> bool:
        '''If the connection and table are valid, insert the key, value, and timestamp into the table. If the
        insert fails, update the value if the timestamp is newer than the existing timestamp.
        
        Parameters
        ----------
        key
            The key of the pair.
        value
            The value to be stored in the database.
        timestamp
            The timestamp of the data.
        
        Returns
        -------
            A boolean value.
        
        '''

        if self.connection and self.table:
            query = "INSERT INTO data(key,value,timestamp) VALUES(?,?,?)"
            cur = self.connection.cursor()
            try:
                cur.execute(query,(key,value,timestamp))
                self.connection.commit()
                cur.close()
                return True
            except (sql.Error, sql.Warning):
                try:
                    query = "UPDATE data set value = ? where key = ? and timestamp < ?"
                    cur.execute(query,(value,key,timestamp))
                    self.connection.commit()
                    cur.close()
                    return True
                except (sql.Error, sql.Warning):
                    cur.close()
                    return False

    def getValue(self,key):
        '''It takes a key, and returns a Result object containing the key and the value associated with the key
        
        Parameters
        ----------
        key
            The key to search for
        
        Returns
        -------
            A Result object
        
        '''
        if self.connection and self.table:
            cur = self.connection.cursor()
            query = "SELECT value FROM data WHERE key= ?"
            value = cur.execute(query,(key,)).fetchone()
            cur.close()
            if value:
                res = Result(key,value[0])
                return res
        return None


    



