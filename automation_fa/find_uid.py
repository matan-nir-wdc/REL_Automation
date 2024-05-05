import pyodbc


def search_in_clear(server, database, username, password, query):
    try:
        print("Search in CLEAR")
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password
        )
        cursor = conn.cursor()
        cursor.execute("USE [REL]")
        cursor.execute(query)
        results = cursor.fetchall()
        if not results:
            print("result not found")
        else:
            for row in results:
                print(f"UID : {row[1]}")
                print(f"Sticker ID : {row[2]}")
        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"Error executing SQL query: {e}")


def search_in_star(server, database, username, password, query):
    try:
        print("Search in STAR")
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password
        )
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        if not results:
            print("result not found")
        else:
            for row in results:
                print(f"UID : {row[1]}")
                print(f"Sticker ID : {row[2]}")
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print(f"Error executing SQL query: {e}")


if __name__ == "__main__":
    print('Enter 1 for sticker or 2 for UID:')
    ans = input()
    print('Enter your search:')
    id = input()
    server = '10.24.8.170'
    server_oberon = 'ULS-DP-SQLCDW'
    database = 'master'
    username = 'rel_user'
    password = 'reluser!123'
    if ans == "1":
        query_clear = f"SELECT * FROM dwh.uidsticker where StickerId like '{id}'"
        query_oberon = f"SELECT * FROM [Input_Management].[dwh].[UidSticker] where StickerId like '{id}'"
    else:
        query_clear = f" SELECT * FROM dwh.uidsticker where uid like '%{id}%'"
        query_oberon = f"SELECT * FROM [Input_Management].[dwh].[UidSticker] where Uid like '%{id}%'"
    search_in_clear(server, database, username, password, query_clear)
    search_in_star(server_oberon, database, username, password, query_oberon)
