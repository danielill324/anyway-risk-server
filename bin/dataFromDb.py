from __future__ import division
# BH
import sqlite3
import web
import numpy as np
from math import fabs

from urllib2 import Request, urlopen, URLError, HTTPError
import json

from math import gamma, factorial
from decimal import Decimal

alpha = float(0.00130)
beta = float(0.0018)

        
        
def inSquare(lat, lng, latLms, lngLms):
    latLms=float(latLms)
    lngLms=float(lngLms)
    if latLms >=lat and latLms<(lat+alpha):
        if(lngLms>=lng and lngLms<(lng+beta)):
            return True
    return False


class DbFunc():

#connect to anyway server
    def __init__(self):
        self.conn = sqlite3.connect('Squares.db')
        self.c=self.conn.cursor()

    def screenColor(self,ne_Lat, ne_Lng, sw_lat, sw_Lng):
        ne_Lat=float(ne_Lat)+alpha
        ne_Lng=float(ne_Lng)+beta
        sw_lat=float(sw_lat)-alpha
        sw_Lng=float(sw_Lng)-beta
        allData=[]
        i=0
        for rec in self.c.execute('''SELECT * FROM squares WHERE ((lat BETWEEN ? AND ?) AND (long BETWEEN ? AND ?)) ''',(sw_lat, ne_Lat, sw_Lng, ne_Lng)):
            data = {}
            data['id']=i
            data['lat']=rec[1]
            data['lng']=rec[2]
            data['color']=rec[3]
            i+=1
            #print(data)
            allData.append(data)
            
        return json.dumps(allData)

        
    def find_square(self,latL,longL):
        for rec in self.c.execute('SELECT * FROM squares'):
            if inSquare(rec[1], rec[2],latL,longL) == True:
                color=int(rec[3])
                if(color>=0 and color<=30):
                    return 1
                else:
                    return -1
        return -1
        
              
    def getAcc(self, lat,lng, alpha, beta):
        try:
            url='http://www.anyway.co.il/markers'
            ne_lat=str(lat)
            ne_lng=str(lng)
            sw_lat=str(lat-alpha)
            sw_lng=str (lng-beta)
            ask='ne_lat='+ne_lat+'&ne_lng='+ne_lng+'&sw_lat='+sw_lat+'&sw_lng='+sw_lng+'&zoom=17&thin_markers=false&start_date=1104537600&end_date=1735689600&show_fatal=1&show_severe=1&show_light=&approx=1&accurate=0&show_markers=1&show_discussions=1&show_urban=3&show_intersection=3&show_lane=3&show_day=7&show_holiday=0&show_time=24&start_time=25&end_time=25&weather=0&road=0&separation=0&surface=0&acctype=0&controlmeasure=0&district=0&case_type=0'
            req = Request(url+'?'+ask)
            arr=[0,0,0,0,0,0,0,0,0,0,0,0,0]
            try:    
                response = json.loads(urlopen(req).read())
            except HTTPError as e:
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
            except URLError as e:
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            else:
            #print response
                for each in response[u'markers']:
                    try:
                    #print each['latitude'],each[u'longitude'],each[u'created'][0:4],each[u'severity']
                        severity=str(each[u'severity'])
                        year=int(each[u'created'][2:4])
                        if(severity == "2"):
                            if year > 10:
                                arr[year-5]+=2
                            else:
                                arr[year-5]+=1
                        else:
                            if year > 10:
                                arr[year-5]+=1
                    except KeyError: pass
                return arr
        except:
            return [0]


    def calc(self, acc):
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
    def getColor(self,p):
        maxH = 85
        if p == -1:
            return 235 #blue color 
        p=1-p
        H=(maxH*p)/3
        return int(round(H,0))


    

#################################
