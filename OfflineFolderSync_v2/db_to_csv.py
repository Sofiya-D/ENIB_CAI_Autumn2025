
import sqlite3
import csv
import os

if __name__ == "__main__" :

    db_name="test.db"
    table_name="test"

    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_name = os.path.join(script_dir, db_name)

    connect=sqlite3.connect(db_name)
    connect.row_factory=sqlite3.Row
    cursor=connect.cursor()
    path = os.path.join(script_dir,table_name)
    f = open(str(path+'.csv'), 'w')
    query="SELECT * from "+table_name
    results=cursor.execute(query)
    columns=[]
    for result in results.description :
        columns.append(result[0])
    with f:
        writer = csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        for result in results :
            string =""
            for i in range (len(columns)) :
                string=string + "columns ["+str(i)+"]:"+"result[columns["+str(i)+"]],"
            print(eval("{"+string+"}"))
            writer.writerow (eval("{"+string+"}"))        
    connect.commit()
