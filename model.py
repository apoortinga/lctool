# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 14:47:06 2017

@author: SERVIRWK
"""

import ee
import logging

class environment(object):
    
    
    def __init__(self):
          
        # set the logfile
              
        # Initialize the Earth Engine object, using the authentication credentials.
        ee.Initialize()
    
        # set dates
        self.startYear = 2000;
        self.endYear = 2001;
        self.startJulian = 60;
        self.endJulian = 181;        
        
        # set location 
        self.location = ee.Geometry.Point([105.59,18.93])
        
        # variable to filter cloud threshold
        self.metadataCloudCoverMax = 25
        
        # percentiles to filter for bad data
        self.lowPercentile = 15.9
        self.highPercentile = 84.1

        # whether to use imagecolletions
        self.useL4=True
        self.useL5=True
        self.useL7=True
        self.useL8=True

        self.maskSR = True;
        self.maskCF = True;
        
        # define the landsat bands
        self.sensorBandDictLandsatSR = ee.Dictionary({'L8' : ee.List([1,2,3,4,5,6,7]),
                                                      'L7' : ee.List([0,1,2,3,4,5,6]),
                                                      'L5' : ee.List([0,1,2,3,4,5,6]),
                                                      'L4' : ee.List([0,1,2,3,4,5,6])})

        # threshold for defringing landsat5 and 7
        self.fringeCountThreshold = 279;                              


class landCoverTool():
    
    def __init__(self):
        import logging
        # set the logfile
        logging.basicConfig(filename='model.log', filemode='w', level=logging.DEBUG)
        
        # Initialize the Earth Engine object, using the authentication credentials.
        ee.Initialize()
        
        # get the environment
        self.env = environment()
    
    # run the model
    def runModel(self):
        
        logging.info('running the model')
        
        collection = self.getLandsat()
        
        percentiles = self.calculatePercentiles(collection)
        
        filteredCollection = self.filterTime(collection) 
        
        filteredCollection = self.filterBounds(collection) 
            
                
        print filteredCollection
        return  filteredCollection
        
          
    # Obtain Landsat image collections 
    def getLandsat(self):
        
        logging.info('getting landsat images')
        
        collection = []
        
        # landsat image collections 
        if self.env.useL4:        
            landsat4 =  ee.ImageCollection('LANDSAT/LT4_SR')
            if self.env.maskSR == True:
                landsat4 = landsat4.map(self.cloudMaskSR)
            if self.env.maskSR == True:
                landsat4 = landsat4.map(self.cloudMaskCF)
            collection.append(landsat4)

        if self.env.useL5:
            landsat5 =  ee.ImageCollection('LANDSAT/LT5_SR')
            if self.env.maskSR == True:
                landsat5 = landsat5.map(self.cloudMaskSR)
            if self.env.maskSR == True:
                landsat5 = landsat5.map(self.cloudMaskCF)
            collection.append(landsat5)
        
        if self.env.useL7:
            landsat7 =  ee.ImageCollection('LANDSAT/LT7_SR')
            if self.env.maskSR == True:
                landsat7 = landsat7.map(self.cloudMaskSR)
            if self.env.maskSR == True:
                landsat7 = landsat7.map(self.cloudMaskCF)
            collection.append(landsat7)
        
        if self.env.useL8:
            landsat8 =  ee.ImageCollection('LANDSAT/LC8_SR')
            if self.env.maskSR == True:
                landsat8 = landsat8.map(self.cloudMaskCF)            
            
            collection.append(landsat8)
        
        # get first item and put it into image collection
        landsatCollection = ee.ImageCollection(collection[0])    
        
        # merge into one collection
        for i in range(1,len(collection),1):
            logging.info('Adding' + str(i))
            landsatCollection.merge(collection[i])
    
        logging.info('returning imagecollection')
            
        return landsatCollection
        

    def calculatePercentiles(self,collection):
        
        logging.info('calculate percentiles')
        
        # get upper and lower percentile
        collectionPercentile = collection.reduce(ee.Reducer.percentile([self.env.lowPercentile,self.env.highPercentile])) 
        
        logging.info('returning percentiles')
        return collectionPercentile
        
        
    # apply filter for period
    def filterTime(self,collection):
        
        logging.info('Filter for time')
        
        # construct date objects
        startDate = ee.Date.fromYMD(self.env.startYear,1,1)
        endDate = ee.Date.fromYMD(self.env.endYear,1,1)
        
        # filter for year
        filteredCollection = collection.filterDate(startDate,endDate).filter(ee.Filter.calendarRange(self.env.startJulian,self.env.endJulian))
        
        logging.info('return filtered collection')
        return  filteredCollection
        
    # apply filter for area
    def filterBounds(self,collection):
        
        logging.info('Filter for location')
                       
        # filter for year
        filteredCollection = collection.filterBounds(self.env.location)
        
        logging.info('return filtered collection')
        return  filteredCollection
        
    def cloudMaskSR(self,img):
        
        logging.info('Applying SR mask')
        
        # get cloud mask
        fmk = img.select("sr_cloud_qa").mask();
        
        logging.info('return mask')
        return img.updateMask(fmk) ## add .not
        
    def cloudMaskCF(self,img):
        fmk = img.select("cfmask").lt(2)
        return img.updateMask(fmk)

        
        
        
col = landCoverTool().runModel()
   
        
image = ee.Image(col.median())
# create the vizualization parameters
viz = {'min':0.0, 'max':2000, 'bands':"B3,B2,B1"};


from PIL import Image, ImageTk
import ee.mapclient
# display the map
ee.mapclient.addToMap(image,viz, "mymap")
