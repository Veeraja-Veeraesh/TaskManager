#importing necessary modules
import tkinter as tk 
import tkinter.ttk as ttk
import tkinter.messagebox as popup
import time
import config as sql
import json

sNolist=[]      #contains the S.No of each event or task in time tables
timelist=[]     #contains the time alottment
eventlist=[]    #contains the events
detailsdict=dict()  #data stored like: {'btnobject1': {'sno': [], 'time': [], 'events': []}, 'btnobject2': {'sno': [], 'time': [], 'events': []} }
 

def updateglobalvalues(btnobj):
    '''Updates the global values to reflect any changes made to the data in a timetable'''

    global detailsdict, sNolist, timelist, eventlist

    sql.cursorobj.execute("SELECT * FROM timetableevents")
    for record in sql.cursorobj.fetchall():
        obj= record['btnobject']
        details=record['details'].replace("'",'"')
        detailsdict[obj]=json.loads(details) #deserializes the data in a mysql table to a python dictionary object

    sNolist=detailsdict[btnobj]['sno']
    timelist=detailsdict[btnobj]['time']
    eventlist=detailsdict[btnobj]['events']   



def addtaskbtnclick(btnobj, frame):
    '''Adds an event to the timetable when the "+Add Event" button is clicked'''
    
    global timelist,sNolist,detailsdict

    updateglobalvalues(btnobj)

    #a new window for adding the details of the event is created
    addeventframe=tk.Tk()
    addeventframe.title('Add event')
    addeventframe.resizable(False, False)
    addeventframe.geometry('300x300')

    #the labels in the window are created and placed on the window
    sNoLabel = tk.Label(addeventframe,text='S.No:')
    timelabel = tk.Label(addeventframe, text='Time span(24 hr):')
    eventlabel = tk.Label(addeventframe, text='Event:')
    sNoLabel.place(x=40,y=40)
    timelabel.place(x=40,y=100)
    eventlabel.place(x=40,y=160)

    #the entry fields are created and placed in the window
    e_sNo=tk.Entry(addeventframe)
    e_sNo.insert(0,"Enter S.No")
    e_sNo.place(x=140,y=42)

    e_time=tk.Entry(addeventframe)
    e_time.insert(0,"hh:mm-hh:mm")
    e_time.place(x=140,y=102)

    e_event=tk.Entry(addeventframe)
    e_event.insert(0,"Enter event or events")
    e_event.place(x=140,y=162)

    #the button to insert the task is created and placed
    insertaskbtn=ttk.Button(addeventframe,text='Add Event')
    insertaskbtn.place(x=120,y=240)

    
    def insertclick():
        '''Inserts the event onto the timetable window and database'''

        global sNolist,timelist, detailsdict

        #retrieving values from the entry fields in the add task window
        sNotext=e_sNo.get()  
        timetext=e_time.get()
        eventtext=e_event.get()

        #to make sure S.No, time and event are valid or not valid       
        try:
            if str(sNotext).isdigit()==False or int(sNotext)<=0:       #to make sure S.No entered is a POSITIVE INTEGER, otherwise throws an exception
                raise ValueError

            # to make sure the S.no, time, event input field is not empty or the default value
            if ((sNotext == '' or sNotext == ' ' or sNotext == 'Enter S.No') or 
            (timetext == '' or timetext == ' ' or timetext == 'hh:mm-hh:mm(24hr format)') or 
            (eventtext == '' or eventtext == ' ' or eventtext == 'Enter event or events')):
                raise ValueError

            if int(sNotext)>24: 
                popup.showinfo('Info', 'Sorry! Only 24 events are allowed.')
                addeventframe.destroy()
                frame.destroy()
                return

            if len(eventtext)>33:
                popup.showinfo('Info', 'Sorry! Only a maximum of 33 characters allowed.')
                addeventframe.destroy()
                frame.destroy()
                return


        except ValueError:
            popup.showwarning('Warning', 'Enter Valid Credentials. Your S.No/Time/Event fields have invalid values.')
        
        else:
            #2 steps:
            #first, to check if the time string entered by the user is of the right format, i.e HH:MM-HH:MM
            #second, to make sure that the beginning time is before the end time of that event, 
            #i.e 07:30-06:30 is an invalid time span

            start_time,_,end_time=timetext.partition('-')#splits the time string to 3 values[HH:MM,-,HH:MM)] and stores them in separate variables

            if start_time<end_time:               
                #to make sure format of time matches
                try:

                    start_time = time.strptime(start_time, "%H:%M")
                    end_time = time.strptime(end_time, "%H:%M")

                except Exception as error:
                    popup.showwarning('Warning', 'Enter the time(24 hr format) according to the right format-> HH:MM-HH:MM')
                    
                else:

                    #To update existing event                 
                    if int(sNotext) in sNolist:

                        index=sNolist.index(int(sNotext))
                        detailsdict[btnobj]['time'][index]=timetext
                        detailsdict[btnobj]['events'][index]=eventtext

                        sqlcommand = "UPDATE timetableevents SET btnobject=(%s), details=(%s) WHERE btnobject=(%s)"
                        sql.cursorobj.execute(sqlcommand, (btnobj, json.dumps(detailsdict[btnobj]), btnobj))
                        sql.mysqlobj.commit()

                        e_sNo.delete(0, tk.END)
                        e_sNo.insert(0, '')

                        e_time.delete(0, tk.END)
                        e_time.insert(0, '')

                        e_event.delete(0, tk.END)
                        e_event.insert(0, '')

                        popup.showinfo('Success', 'Your event was successfully updated as S.No was already present in your table.')
                        addeventframe.destroy()
                        frame.destroy()

                    #To add new event
                    else: 
                         
                        detailsdict[btnobj]['sno'].insert(int(sNotext)-1, int(sNotext))
                        detailsdict[btnobj]['time'].insert(int(sNotext)-1, timetext)
                        detailsdict[btnobj]['events'].insert(int(sNotext)-1, eventtext)

                        #the task is added onto the table in the remote database
                        sqlcommand="UPDATE timetableevents SET btnobject=(%s), details=(%s) WHERE btnobject=(%s)"
                        sql.cursorobj.execute(sqlcommand,(btnobj,json.dumps(detailsdict[btnobj]), btnobj))
                        sql.mysqlobj.commit()

                        #changing the input field back to normal, i.e blank
                        e_sNo.delete(0,tk.END)
                        e_sNo.insert(0,'')

                        e_time.delete(0,tk.END)
                        e_time.insert(0,'')

                        e_event.delete(0,tk.END)
                        e_event.insert(0,'')
                        
                        popup.showinfo('Success','Your event was successfully added.')
                        addeventframe.destroy()
                        frame.destroy()
            
            else:
                popup.showwarning('Warning', 'Start time is greater than end time')

        
    insertaskbtn.configure(command=insertclick)

    addeventframe.mainloop()



def deletetaskbtnclick(btnobj, frame):
    '''Delete an event as specified by user when the "X Delete Event" button is clicked '''

    global timelist, sNolist, eventlist, detailsdict    

    #retrieving the data from the remote database and storing it in the global variables
    updateglobalvalues(btnobj)

    #new window created to ask the user which event to delete
    deleventframe = tk.Tk()
    deleventframe.title('Delete event')
    deleventframe.resizable(False, False)
    deleventframe.geometry('300x300') 

    #labels, entry fields and buttons created and placed on the window
    sNoLabel = tk.Label(deleventframe, text='S.No:')
    sNoLabel.place(x=40, y=40)

    e_sNo = tk.Entry(deleventframe)
    e_sNo.insert(0, "Enter S.No")
    e_sNo.place(x=140, y=42)

    delbtn = tk.Button(deleventframe, text='Remove task')
    delbtn.place(x=120, y=240)


    
    def removeclick():
        '''Deletes specified event from table and database'''

        global sNolist, timelist, detailsdict

        #retrieving the S.No which the user gave as input
        sNotext=e_sNo.get()

        #to make sure that the entered S.No exists
        if int(sNotext) not in sNolist:
            popup.showerror('ERROR', 'S.No of event not present in time table.')
        else:

            #deletes event from database
            index = sNolist.index(int(sNotext))
            
            del detailsdict[btnobj]['sno'][index]
            del detailsdict[btnobj]['time'][index]
            del detailsdict[btnobj]['events'][index]
                                   
            sqlcommand = "UPDATE timetableevents SET btnobject=(%s), details=(%s) WHERE btnobject=(%s)"
            sql.cursorobj.execute(sqlcommand, (btnobj, json.dumps(detailsdict[btnobj]), btnobj))    #json.dumps used to serialize the data entered and store in the mysql database
            sql.mysqlobj.commit()

            #changes the input field to default
            e_sNo.delete(0,tk.END)
            e_sNo.insert(0,'')

            popup.showinfo('Success','Your event was successfully deleted')          
            deleventframe.destroy()

            frame.destroy()

    delbtn.configure(command=removeclick)

    deleventframe.mainloop()


def refreshbtnclick(btnobj, frame):
    '''Displays the stored values in the mysql database onto the tkinter window when the "O Refresh" button is clicked'''

    global sNolist, timelist, detailsdict

    updateglobalvalues(btnobj)
    #creating, styling, placing the labels
    sNoLabeltxt = tk.Label(frame, text='S.No', font=('Century Gothic', 16, 'bold'), fg='white', bg='#F0A500', width=10)
    timelabeltxt = tk.Label(frame, text='Time', font=('Century Gothic', 16, 'bold'), fg='white', bg='#F0A500', width=20)
    eventlabeltxt = tk.Label(frame, text='Event', font=('Century Gothic', 16, 'bold'), fg='white', bg='#F0A500', width=25)

    sNoLabeltxt.place(x=50, y=20)
    timelabeltxt.place(x=140, y=20)
    eventlabeltxt.place(x=360, y=20)

    for row in range(len(sNolist)):
        
        #displaying all the values as labels in the window
        sNoLabel = tk.Label(frame, text=str(sNolist[row]), font=('Century Gothic', 13), bg='#082032', fg='white')
        timelabel = tk.Label(frame, text=timelist[row], font=('Century Gothic', 13), bg='#082032', fg='white')
        eventlabel = tk.Label(frame, text=eventlist[row], font=('Century Gothic', 13), bg='#082032', fg='white')

        sNoLabel.place(x=100,y=row*25+70)
        timelabel.place(x=225,y=row*25+70)
        eventlabel.place(x=420,y=row*25+70)


def deleteallbtnclick(btnobj,frame):
    '''Deletes all events related to the current timetable when the "X Delete All X" button is clicked'''

    global sNolist, timelist, detailsdict

    confirmdelete = popup.askquestion('Delete All', 'Do you really want to Delete All Events?')
    if confirmdelete == 'yes':
        sNolist.clear()
        timelist.clear()
        eventlist.clear()

        detailsdict[btnobj]["sno"] = sNolist
        detailsdict[btnobj]["time"] = timelist
        detailsdict[btnobj]["event"] = eventlist

        sqlcommand = "UPDATE timetableevents SET btnobject=(%s), details=(%s) WHERE btnobject=(%s)"
        sql.cursorobj.execute(sqlcommand, (btnobj, json.dumps(detailsdict[btnobj]), btnobj))
        sql.mysqlobj.commit()
        frame.destroy()
        
    
    





