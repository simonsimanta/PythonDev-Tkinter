import urllib
import sqlite3
import json
import time
import codecs
from Tkinter import *
import webbrowser
import os


try:
    os.remove('where.js')
    os.remove('geodata.sqlite')
except OSError:
    pass

f=open('where.html','w')

html= """<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>A Map of Information</title>
    <link href="http://google-developers.appspot.com/maps/documentation/javascript/examples/default.css" rel="stylesheet">

    <!-- If you are in China, you may need to use theis site for the Google Maps code
    <script src="http://maps.google.cn/maps/api/js" type="text/javascript"></script> -->
   <!--<script src="http://maps.googleapis.com/maps/api/js?sensor=false"></script>-->
   <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyA1HUGH5gOh298F7R_MWVtnJziFlH8wQUg&callback=initMap"
    async defer>
      
    </script>

    <script src="http://google-maps-utility-library-v3.googlecode.com/svn/trunk/markerclusterer/src/markerclusterer_compiled.js"></script>
    <script src="where.js"></script>
    <script>

      function initialize() {
        alert("To see the title of a marker, hover over the marker but don't click.");
        var myLatlng = new google.maps.LatLng(20.5937,78.9629)
        var mapOptions = {
          zoom: 5,
          center: myLatlng,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

        i = 0;
        var markers = [];
        for ( pos in myData ) {
            i = i + 1;
            var row = myData[pos];
		    window.console && console.log(row);
            // if ( i < 3 ) { alert(row); }
            var newLatlng = new google.maps.LatLng(row[0], row[1]);
            var marker = new google.maps.Marker({
                position: newLatlng,
                map: map,
                title: row[2]
            });
            markers.push(marker);
        }
      }
    </script>
  </head>
  <body onload="initialize()">
<div id="map_canvas" style="height: 500px"></div>
<p><b>About this Map</b></p>
<p>
This is a python project on google maps API.
</p>
</body>
</html>
"""

f.write(html)
f.close()

def delete_sqljs():
    conn = sqlite3.connect('geodata.sqlite')
    cur = conn.cursor()

    cur.execute('''DROP TABLE Locations''')
    try:
        os.remove("where.js")
    except OSError:
        pass
    

def datadump():
    line = str(Entry.get(search))
    address = line.strip()
    serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"

    scontext = None

    conn = sqlite3.connect('geodata.sqlite')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

    url = serviceurl + urllib.urlencode({"sensor": "false", "address": address})
    uh = urllib.urlopen(url, context=scontext)
    data = uh.read()

    cur.execute('''INSERT INTO Locations (address, geodata) VALUES ( ?, ? )''', (buffer(address), buffer(data)))
    conn.commit()
    time.sleep(1)
def data_dump(event):
    datadump()
    

def j_load():
    conn = sqlite3.connect('geodata.sqlite')
    cur = conn.cursor()

    cur.execute('SELECT * FROM Locations')
    fhand = codecs.open('where.js','w', "utf-8")
    fhand.write("myData = [\n")

    count=0
    for row in cur:
        data = str(row[1])
        try: js = json.loads(str(data))
        except: continue

        if not('status' in js and js['status'] == 'OK') : continue

        lat = js["results"][0]["geometry"]["location"]["lat"]
        lng = js["results"][0]["geometry"]["location"]["lng"]
        if lat == 0 or lng == 0 : continue
        where = js['results'][0]['formatted_address']
        where = where.replace("'","")
        try :

            count = count + 1
            if count > 1 : fhand.write(",\n")
            output = "["+str(lat)+","+str(lng)+", '"+where+"']"
            fhand.write(output)
        except:
            continue
    fhand.write("\n];\n")
    screen0.delete("1.0", END)
    screen0.insert(END, lat)
    screen1.delete("1.0", END)
    screen1.insert(END, lng)
    screen2.delete("1.0", END)
    screen2.insert(END, where)
    cur.close()
    fhand.close()
def open():
    webbrowser.open('file://' + os.path.realpath("where.html"))

root=Tk()

root.title('Google_maps_Api by-SsS')

#left
labelframe = LabelFrame(root, text=" ")
labelframe.pack(side=LEFT,fill="both",expand="yes")
#left_top
tframe = LabelFrame(labelframe, text="Input Data")
tframe.pack(side=TOP,fill="both", expand="yes")

left_u = Label(tframe, text="To clear previous searches",bg="#3890DA",fg="#fff",width =38)
left_u.grid(row=0,column=0,ipadx=8,ipady=6,padx=8,pady=4)

button_u=Button(tframe, text="Click here",bg="#DA4C36", fg="#fff", command=delete_sqljs,width =16)
button_u.grid(row=0,column=1,ipadx=8,ipady=3,padx=1,pady=4)

left_b = Label(tframe, text="Enter text to search",bg="#3890DA",fg="#fff",width =60)
left_b.grid(row=1,columnspan=2,ipadx=8,ipady=6,padx=8,pady=4)

search=Entry(tframe ,bd=2,bg="#e0e0eb",width = 70)
search.grid(row=2,columnspan=2,ipadx=8,ipady=6,padx=8,pady=4)

button_b=Button(tframe, text="Search",bg="#DA4C36", fg="#fff", command=datadump,width =20)
button_b.grid(row=3,columnspan=2,ipadx=8,ipady=3,padx=8,pady=4)
search.bind('<Return>', data_dump)

#left_bottom
bframe = LabelFrame(labelframe, text="Extracted Data")
bframe.pack(side=BOTTOM,fill="both", expand="yes")

button=Button(bframe, text="Load data",bg="#DA4C36", fg="#fff", command=j_load, width =20)
button.grid(row=0,columnspan=2,ipadx=8,ipady=3,padx=8,pady=4)

lat = Label(bframe, text="Latitude",bg="#54AA59",fg="#fff",width =20)
lat.grid(row=1,column=0,ipadx=8,ipady=6,padx=8,pady=4)
screen0=Text(bframe, height=1, width =30, bd=5)
screen0.grid(row=1,column=1,ipadx=8,ipady=6,padx=8,pady=4)

lon = Label(bframe, text="Longitude",bg="#54AA59",fg="#fff",width =20)
lon.grid(row=2,column=0,ipadx=8,ipady=6,padx=8,pady=4)
screen1=Text(bframe, height=1, width =30, bd=5)
screen1.grid(row=2,column=1,ipadx=8,ipady=6,padx=8,pady=4)

add = Label(bframe, text="Address",bg="#DEE64C",fg="#fff",width =20)
add.grid(row=3,column=0,ipadx=8,ipady=6,padx=8,pady=4)
screen2=Text(bframe, height=1, width =30, bd=5)
screen2.grid(row=3,column=1,ipadx=8,ipady=6,padx=8,pady=4)


#right
lframe = LabelFrame(root, text=" ")
lframe.pack(side=RIGHT,fill="both",expand="yes")


imgPath = r"google.gif"
photo = PhotoImage(file = imgPath)
label = Label(lframe,image = photo)
label.image = photo # keep a reference!
label.grid(row=0,column=0)

button=Button(lframe, text="Open Map In Browser",height=3, width =30, bg="#DA4C36", fg="#fff",command=open)
button.grid(row=2,column=0,ipadx=8,ipady=3,padx=8,pady=4)

root.mainloop()

