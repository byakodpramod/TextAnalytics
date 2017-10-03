#!/usr/bin/python
import PyPDF2
import re
import urllib.request
import os
import sqlite3

def fetchincidents():
     
    URL = "http://normanpd.normanok.gov/content/daily-activity"
    website = urllib.request.urlopen(URL)
    html = website.read()
    links = re.findall(r'/filebrowser_download/657/\d{4}-\d{2}-\d{2}%\d\d?Daily%\d{2}Incident%\d{2}Summary.pdf',str(html))
    for k in range(len(links)):
        links[k]="http://normanpd.normanok.gov"+links[k]
    return links


def extractincidents():
    str_obj = []
    txt_file = open("incidents.txt","w")
    links = fetchincidents()
    for link in links:
        resp = urllib.request.urlretrieve(link,'test.pdf')
        pdf_reader = PyPDF2.PdfFileReader(open("test.pdf", 'rb'))
        pdf_pages = pdf_reader.getNumPages()
        for i in range(0,pdf_pages):
            page_obj = pdf_reader.getPage(i)
            for line in page_obj.extractText().splitlines():
                txt_file.write(line+"\n")
   
    os.system("sed -i '/^Daily Incident Summary (Public)$/d' incidents.txt")
    os.system("sed -i '/^NORMAN POLICE DEPARTMENT$/d' incidents.txt")
    os.system("sed -i '/^Date \/ Time$/d' incidents.txt")
    os.system("sed -i '/^Incident Number$/d' incidents.txt")
    os.system("sed -i '/^Location$/d' incidents.txt")
    os.system("sed -i '/^Nature$/d' incidents.txt")
    os.system("sed -i '/Incident ORI/d' incidents.txt")
    
    inci_file = open("incidents.txt", "r")
   
    for line in inci_file:
        str_obj.append(line.rstrip('\n'))
    return str_obj


def createdb():
    conn = sqlite3.connect('normanpd.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE incidents
             (id integer,number text,date_time text,location text,nature text,ORI text)''')
    conn.commit()
    conn.close()

def populatedb(incidents):
    conn = sqlite3.connect('normanpd.db')
    c = conn.cursor()
    i = 0;
    j = 0;
    cnt=0;
    while j < (len(incidents) - 5):
          if re.match('OK0140200', incidents[j+4]) or re.match('1400.', incidents[j+4]) or re.match('EMSSTAT', incidents[j+4]):
             c.execute("INSERT INTO incidents VALUES ('%d','%s','%s','%s','%s','%s')" %((i+1),incidents[j],incidents[j+1],incidents[j+2],incidents[j+3],incidents[j+4]))
             i = i+1
             j=j+5

          elif re.match('OK0140200', incidents[j+2]) or re.match('1400.', incidents[j+2]) or re.match('EMSSTAT', incidents[j+2]):
               c.execute("INSERT INTO incidents VALUES ('%d','%s','%s','%s','%s','%s')" %((i+1),incidents[j],incidents[j+1],' ',' ',incidents[j+2]))
               i = i+1
               j=j+8

          elif re.match('\d\d?/\d\d?/\d\d\d\d\s\d\d?:\d\d', incidents[j]) and re.match('\d\d?/\d\d?/\d\d\d\d\s\d\d?:\d\d', incidents[j+1]):
               c.execute("INSERT INTO incidents VALUES ('%d','%s','%s','%s','%s','%s')" %((i+1),incidents[j+1],incidents[j+2],incidents[j+3],incidents[j+4],incidents[j+5]))
               i = i+1
               j=j+6

          else:
              c.execute("INSERT INTO incidents VALUES ('%d','%s','%s','%s','%s','%s')" %((i+1),incidents[j],incidents[j+1],incidents[j+2]+incidents[j+3],incidents[j+4],incidents[j+5]))
              i = i+1
              j=j+6
    c.execute("SELECT * FROM incidents")
    #for row in c:
         #print(row)
    conn.commit()
    conn.close()

def status(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM incidents;")
    num_rows = c.fetchall()
    print("\nTotal number of rows in the table is %d" %(num_rows[0]))
    print("\n5 random rows from the table Incidents")
    print("---------------------------------------")
    c.execute("SELECT * FROM incidents ORDER BY random() LIMIT 5")
    for r in c:
        print(r)
    conn.commit()
    conn.close()
