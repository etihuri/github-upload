import urllib.request
from urllib.request import Request
from urllib.request import urlopen
from pyquery import PyQuery
import csv
import re
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl
import logging

def setLogger():
    logger = logging.getLogger('carSricpt_app')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('allLogs.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
def getPrevCarFromCsv():

    try:
        csvCarDict =[]
        csvCar = []
        with open('cars.csv','r') as file:
            csvCar  = csv.DictReader(file)
            for i in csvCar:
              csvCarDict.append(i)
        return csvCarDict
    except Exception as e:
        logger.error(e)

def getCarFromWebPage():

    try:
        req = Request('https://www.yad2.co.il/vehicles/cars?manufacturer=40,37&model=1625,279&year=2018--1&km=-1-80000&hand=-1-2&gearBox=1', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        pq = PyQuery(webpage)
        return pq
    except Exception as e:
        logger.error(e)


def getCarDiffFromCsvToWeb(pq,carDictFromCsv):
    try:
        newCarsList = []
        diffCarsUrlList = []
        websiteCars = pq(pq('div[item-id]'))
        for car in websiteCars:
            carPrice = (pq(car[0]).find(".price").text().split(" ")[0])
            isCarPriceNumraic = re.match("^[0-9,.]*$", carPrice)
            if(isCarPriceNumraic is None):
                carPrice = 0
            carId = (pq(car).attr("item-id"))
            newCarsList.append({"id":carId,"price" :carPrice,"url":"https://www.yad2.co.il/item/" + carId})
            if not any(d['id'] == carId for d in carDictFromCsv):
                diffCarsUrlList.append("https://www.yad2.co.il/item/" + carId)
            elif any(d['id'] == carId and d['price']!=str(carPrice) for d in carDictFromCsv):
                 diffCarsUrlList.append("https://www.yad2.co.il/item/" + carId)
        returnObj = dict()
        returnObj["newCarsList"] = newCarsList
        returnObj["diffCarsUrlList"] = diffCarsUrlList
        return returnObj
    except Exception as e:
        logger.error(e)

def writeNewDictToCsv(newCarsDict):
    try:
        keys = newCarsDict[0].keys()
        with open('cars.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(newCarsDict)
    except Exception as e:
        logger.error(e)



def sendAnEmail(message):
    try:
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        sender_email = "EtiNewCar2022@gmail.com"
        password ="Yad2NewCar"
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, "ehuri17@gmail.com", message.as_string())
        server.quit()
    except Exception as e:
        logger.error(e)
        
def sendDiffUrlByEmail(diffUrlList):
    try:
        message = MIMEMultipart('mixed')
        message.attach(MIMEText('\n'.join(diffUrlList),'plain'))
        sendAnEmail(message)
    except Exception as e:
        logger.error(e)
        
def main():
    try:
        pq = getCarFromWebPage();
        logger.info("read car from website successfully")
        carDictFromCsv = getPrevCarFromCsv();
        logger.info("read car from csv successfully")
        newCarData = getCarDiffFromCsvToWeb(pq,carDictFromCsv)
        writeNewDictToCsv(newCarData["newCarsList"])
        logger.info("write new cars to csv from website successfully")
        if len(newCarData["diffCarsUrlList"]) !=0:
            sendDiffUrlByEmail(newCarData["diffCarsUrlList"])
            logger.info("email send successfully")
        logger.info("Done")
                                         
    except Exception as e:
        logger.error("main")
if __name__ == '__main__':
    logger = setLogger()
    main()


