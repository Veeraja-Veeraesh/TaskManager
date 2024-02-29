import sys
import pymysql
import tkinter as tk
import tkinter.messagebox as popup


try:
    mysqlobj = pymysql.connect(host='db4free.net',
                            port=3306,
                            user='planner202122',
                            password='YBv2VEPTM3',
                            db='planner202122',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)


    cursorobj = mysqlobj.cursor()
    cursorobj.execute('USE planner202122')

except Exception as e:
    tk.Tk().withdraw() #hides the extra tkinter root window created when popup is executed
    popup.showerror('ERROR', 'Could not connect to database: sql6462301')
    sys.exit()         #to stop execution if connection not established
