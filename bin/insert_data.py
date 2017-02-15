from __future__ import division
import csv
import time
from math import gamma, factorial
import csv
import pyproj
import sqlite3

class ItmToWGS84(object):
    def __init__(self):
        # initializing WGS84 (epsg: 4326) and Israeli TM Grid (epsg: 2039) projections.
        # for more info: http://spatialreference.org/ref/epsg/<epsg_num>/
        self.wgs84 = pyproj.Proj(init='epsg:4326')
        self.itm = pyproj.Proj(init='epsg:2039')

    def convert(self, x, y):
        """
        converts ITM to WGS84 coordinates
        :type x: float
        :type y: float
        :rtype: tuple
        :return: (long,lat)
        """
        longitude, latitude = pyproj.transform(self.itm, self.wgs84, x, y)
        return longitude, latitude


def find_square(latL,longL):
    for rec in c.execute('SELECT * FROM squares'):
        if inSquare(rec[1], rec[2],latL,longL) == True:
            return rec[0] ,rec[4]
    return -1

def inSquare(lat, lng, latLms, lngLms):
#    print lat,lng,latLms,lngLms
    if latLms >lat and latLms<=(lat+alpha):
        if(lngLms>=lng and lngLms<=lng+beta):
            return True
    return False

def calc(acc):

    n = len(acc)
    xn = sum(acc)
    if (n == 0 or xn == 0):
        return 0
    try:
        mean = xn/n
        s = 0
        for xi in acc:
            s += (pow((xi-mean), 2))
        variance = s/n
        alpha_c = (variance - mean) / (pow(mean, 2))
        alpha1 = pow(alpha_c, -1)
        alpha_lambda = alpha_c*mean
        first = gamma(xn + alpha1) / (factorial(xn) * gamma(alpha1))
        second = pow((alpha_lambda/(alpha_lambda+1)),xn)
        third = pow((1/(1+alpha_lambda)),alpha1)
        probability = first*second*third
        return probability
    except:
        return -1

#color of probability
def getColor(p):
    if p == -1:
        return 235 #blue color
    H=p*1050
    if H>85:
        return 235
    return int(round(H,0))

alpha = 0.0013
beta = 0.0018
#create connection to DB
conn = sqlite3.connect('SquaresWith2014.db')
#connect ti DB via c
c = conn.cursor()



convertor = ItmToWGS84()


fileName ='H20131161AccData'

localTime = time.asctime(time.localtime(time.time()))
print "Local current time", localTime
csv_file = fileName+'.csv'
firstLine = True
i=1
with open(fileName+'.csv') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        if firstLine or row[0]=="":
            firstLine = False
            continue
        try:
            yearS = row[14]
            severity = row[22]
            x =float(row[47])
            y =float(row[48])
            lg,lt = convertor.convert(x,y)
            update_id, accS =find_square(lt,lg)
            if accS == str([0]):
                accS = str([0,0,0,0,0,0,0,0,0,0,0,0,0])
            accT= str(accS).replace(" ","")
            accT= accT[1:len(accT)-1]
            accT= map(int, accT.split(','))
            year = int(yearS[2:4])
            numAcc=accT[year-5]
            if severity == '3' and year >10:
                accT[year-5]= numAcc +2
            elif severity == '3' or (severity == '2' and year >= 10):
                accT[year-5]= numAcc +1
            p=calc(accT)
            col=getColor(p)
            SaccL = str(accT)
            if update_id != -1 and severity != '1':
                c.execute('''UPDATE squares SET acc = ? , H = ? WHERE id = ? ''',(SaccL,col,update_id))
            if i%100==0:
                print i
                conn.commit()
                localTime = time.asctime(time.localtime(time.time()))
                print "Local current time", localTime
            i+=1
        except:
            print "here"
            continue
conn.commit()
conn.close()
localTime = time.asctime(time.localtime(time.time()))
print "Local current time", localTime
print "end!"
