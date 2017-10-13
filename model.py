# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 14:47:06 2017

@author: SERVIRWK
"""

import ee
import logging
import time

class environment(object):
    
    
    def __init__(self):
        """Initialize the environment."""   
         
        # Initialize the Earth Engine object, using the authentication credentials.
        ee.Initialize()
       
	self.timeString = time.strftime("%Y%m%d_%H%M%S")

	# SEASONS:
	# '0': Dry Cool: Nov - Feb (305 - 59)
	# '1': Dry Hot: Mar - Apr (60 - 120)
	# '2': Rainy: May - Oct (121 - 304)
       
        # set dates
        self.startYear = 2004;
        self.endYear = 2004;
        self.startJulian =60;
        self.endJulian = 120;        
        
	
	# Rainy
	# dry hot
	# dry cool
	
        # set location 
        self.location = ee.Geometry.Polygon([[[103.294,17.923],[103.294,17.923],[106.453,17.923],[106.453,20.469],[103.2941,20.469],[103.294,17.923]]])
        
        self.location = ee.Geometry.Polygon([[[106.321,20.802],[106.210,20.258],[106.457,20.207],[106.501,20.735],[106.321,20.802]]]) #ee.Geometry.Point([105.809,21.074])
        self.location = ee.Geometry.Polygon([[[100.810546875,15.199386048559994],[100.87646484375,14.008696370634672],[103.24951171875,13.645986814875332],[103.99658203125,16.172472808397515],[101.62353515625,16.97274101999902],[100.810546875,15.199386048559994]]]) #ee.Geometry.Point([105.809,21.074])
        #self.location = ee.Geometry.Polygon([[[104.16021199975899,19.23975872471158],[103.96228285797224,18.329898276316065],[104.93086921942609,18.304353250936266],[105.02779295134292,18.819239142504617],[104.81347339419835,19.213817182344677],[104.16021199975899,19.23975872471158]]]) #ee.Geometry.Point([105.809,21.074])
        
        # variable to filter cloud threshold
        self.metadataCloudCoverMax = 100
        
        # threshold for landsatCloudScore
        self.cloudThreshold = 0
        
        # percentiles to filter for bad data
        self.lowPercentile = 5
        self.highPercentile = 95

        # whether to use imagecolletions
        self.useL4=True
        self.useL5=True
        self.useL7=True
        self.useL8=True

        # apply cloud masks
        self.maskSR = True
        self.maskCF = False
        self.cloudScore = False
	
        self.bandNamesLandsat = ee.List(['blue','green','red','nir','swir1','swir2','sr_atmos_opacity','pixel_qa','radsat_qa'])
              
        # apply defringe
        self.defringe = True
        
        # pixel size
        self.pixSize = 30
        
        # user ID
        self.userID = "users/servirmekong/temp/"
        
        # define the landsat bands
        self.sensorBandDictLandsatSR = ee.Dictionary({'L8' : ee.List([1,2,3,4,5,6,7,8,9]),
                                                      'L7' : ee.List([0,1,2,3,4,6,7,9,10]),
                                                      'L5' : ee.List([0,1,2,3,4,6,7,9,10]),
                                                      'L4' : ee.List([0,1,2,3,4,6,7,9,10])})

        # threshold for defringing landsat5 and 7
        self.fringeCountThreshold = 279

	#band for TDOM
	self.shadowSumBands = ['nir','swir1']
	self.dilatePixels = 5;
	self.cloudHeights = ee.List.sequence(200,5000,500);
	self.zScoreThresh = -0.8;
	self.shadowSumThresh = 0.35;


        self.k = ee.Kernel.fixed(41, 41, 
                                [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]);
        
        
        
class SurfaceReflectance():
    
    def __init__(self):
        """Initialize the Surfrace Reflectance app."""  
        
        # import the log library
        
        import logging
	
	# get the environment
        self.env = environment()
  
        # set the logfile
        logging.basicConfig(filename=str(self.env.timeString) + 'model.log', filemode='w', level=logging.DEBUG)
                
    
    def RunModel(self):
        """Run the SR model"""  
        
        logging.info('starting the model the model')
        
        # construct date objects
        startDate = ee.Date.fromYMD(self.env.startYear,1,1)
        endDate = ee.Date.fromYMD(self.env.endYear,12,31)    
        
	logging.info('startDate = ' + str(startDate.getInfo()))
	logging.info('endDatDate = ' + str(startDate.getInfo()))
	logging.info('Cloudcover filter = ' + str(self.env.metadataCloudCoverMax))	
	
        # get the images
        collection = self.GetLandsat(startDate,endDate,self.env.metadataCloudCoverMax)
               
        outputName = "testmask_Percentile_" + str(self.env.startYear)
                
        # calculate the percentiles
        
        #print percentiles.getInfo()
	#self.percentile = ee.Image(self.CalculatePercentiles())  
        
	#collection = collection.map(self.MaskPercentile) 

	# Get some pixel-wise stats for the time series
	#self.irStdDev = collection.select(self.env.shadowSumBands).reduce(ee.Reducer.stdDev());
	#self.irMean = collection.select(self.env.shadowSumBands).mean();
	
	#collection = collection.map(self.simpleTDOM)
	#collection = collection.map(self.cloudProject)
	
	
        count = collection.size();
        print('counted ' + str(count.getInfo()) +' images');    
    
	img = ee.Image(collection.median())  
	
	#print(img)

	self.ExportToAsset(img,outputName)         
       
        return collection
        
          
    # Obtain Landsat image collections 
    def GetLandsat(self,startDate,endDate,metadataCloudCoverMax):
        """Get the Landsat imagery"""  
        
        logging.info('getting landsat images')

            
        # boolean to merge Landsat; when true is merges with another collection
        merge = False

        # landsat4 image collections 
        if self.env.useL4:        
            landsat4 =  ee.ImageCollection('LANDSAT/LT04/C01/T1_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat4 = landsat4.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            landsat4 = landsat4.filter(ee.Filter.calendarRange(self.env.startJulian,self.env.endJulian))
            if self.env.defringe == True:
                 landsat4 =  landsat4.map(self.DefringeLandsat)
            if self.env.maskSR == True:
                landsat4 = landsat4.map(self.CloudMaskSR)
            if self.env.maskSR == True:
                landsat4 = landsat4.map(self.radSat)
                landsat4 = landsat4.map(self.maskHaze)
            if not merge:
		landsatCollection = landsat4.select(self.env.sensorBandDictLandsatSR.get('L4'),self.env.bandNamesLandsat)
		merge = True

        # landsat 5 image collections 
        if self.env.useL5:
            landsat5 =  ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat5 = landsat5.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            landsat5 = landsat5.filter(ee.Filter.calendarRange(self.env.startJulian,self.env.endJulian))
            if self.env.defringe == True:
                 landsat5 =  landsat5.map(self.DefringeLandsat)
            if self.env.maskSR == True:
                landsat5 = landsat5.map(self.CloudMaskSR)
            if self.env.maskSR == True:
                landsat5 = landsat5.map(self.radSat)
                landsat5 = landsat5.map(self.maskHaze)
            if not merge:
		landsatCollection = landsat5
		merge = True
            else:
		landsatCollection = landsatCollection.merge(landsat5.select(self.env.sensorBandDictLandsatSR.get('L5'),self.env.bandNamesLandsat))

        # landsat 7 image collections  
        if self.env.useL7:
            landsat7 =  ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat7 = landsat7.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            landsat7 = landsat7.filter(ee.Filter.calendarRange(self.env.startJulian,self.env.endJulian))
            if self.env.defringe == True:
		landsat7 =  landsat7.map(self.DefringeLandsat)            
            if self.env.maskSR == True:
		landsat7 = landsat7.map(self.CloudMaskSR)
            if self.env.maskSR == True:
                landsat7 = landsat7.map(self.radSat)
                landsat7 = landsat7.map(self.maskHaze)
            if not merge:
		landsatCollection = landsat7
	    	merge = True
            else:
		landsatCollection = landsatCollection.merge(landsat7.select(self.env.sensorBandDictLandsatSR.get('L7'),self.env.bandNamesLandsat))

        # landsat8  image collections 				        
        if self.env.useL8:
            landsat8 =  ee.ImageCollection('LANDSAT/LC8_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat8 = landsat8.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            landsat8 = landsat8.filter(ee.Filter.calendarRange(self.env.startJulian,self.env.endJulian))
            if self.env.defringe == True:
                 landsat8 =  landsat8.map(self.DefringeLandsat)    
            #if self.env.maskSR == True:
            #    landsat8 = landsat8.map(self.maskHaze)            
            if not merge:
		landsatCollection = landsat8
		merge = True
            else:
		landsatCollection = landsatCollection.merge(landsat8.select(self.env.sensorBandDictLandsatSR.get('L8'),self.env.bandNamesLandsat))            
       
        count = landsatCollection.size();

        
        landsatCollection = landsatCollection.map(self.ScaleLandsat)
        

	if self.env.cloudScore == True:
	    landsatCollection = landsatCollection.map(self.landsatCloudScore)
	
       
        logging.info('counted ' + str(count.getInfo()) +' images');           
        logging.info('returning imagecollection')

        # return the image collection           
        return ee.ImageCollection(landsatCollection)
        

    def CalculatePercentiles(self):
        """Calculate percentiles to filter imagery"""  
        
        logging.info('calculate percentiles')
        
        startDate = ee.Date.fromYMD(1984,1,1)
        endDate = ee.Date.fromYMD(2020,1,1)    
        cloudCoverMax = 30
        
        # get the images
        collection = self.GetLandsat(startDate,endDate,cloudCoverMax)

        # get upper and lower percentile
        collectionPercentile = collection.reduce(ee.Reducer.percentile([self.env.lowPercentile,self.env.highPercentile])) 
        
        logging.info('returning percentiles')
        
        return ee.Image(collectionPercentile)

    def maskHaze(self,img):
         """Apply cloud mask"""  
       
         logging.info('Applying SR mask')
        
         fmk = img.select("sr_atmos_opacity").multiply(0.001).lt(0.30)
         logging.info('return mask')
         return img.updateMask(fmk).copyProperties(img)
        
    def CloudMaskCF(self,img):
         """Apply cloud mask"""  
       
         logging.info('Applying SR mask')
        
         fmk = img.select("sr_cloud_qa").mask();
        
         logging.info('return mask')
         return img.updateMask(fmk.neq(0)).copyProperties(img) ## add .not? # changed to neq
  
    def radSat(self,img):
         """apply cf-mask Landsat""" 
	 
	 mask = img.select("radsat_qa").eq(0)
	        
         return img.updateMask(mask).copyProperties(img)
        
    def CloudMaskSR(self,img):
         """apply cf-mask Landsat""" 
	 
	 QA = img.select("pixel_qa")
	 #mask = ee.Image(self.getQABits(QA,3, 5, 'internal_quality_flag')); 
	 #print mask
        
         return img.updateMask(QA.eq(66)).copyProperties(img)
         #return img.addBands(mask.select('internal_quality_flag'))

    def ScaleLandsat(self,img):
        """Landast is scaled by factor 0.0001 """
        
        scaled = ee.Image(img).multiply(0.0001).copyProperties(img,['system:time_start']) 
        logging.info('return scaled image')
        return scaled.copyProperties(img)

    # helper function to extract the QA bits
    def getQABits(self,image, start, end, newName):
	# Compute the bits we need to extract.
	pattern = 0;
	for i in range(start,end,1):
	    pattern += 2^i
	    # Return a single band image of the extracted QA bits, giving the banda new name.
	
	return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)

    def DefringeLandsat(self,img):   
        """remove scanlines from landsat 4 and 7 """
        
        logging.info('removing scanlines')

        m = ee.Image(img).mask().reduce(ee.Reducer.min())
        sum = m.reduceNeighborhood(ee.Reducer.sum(), self.env.k, 'kernel')
        mask = sum.gte(self.env.fringeCountThreshold)        
        #img = img.mask(img.mask().add(sum)) 
        return img.updateMask(mask)
        
    def MaskPercentile(self,img):
	"""mask light and dark pixels """
	logging.info('mask light and dark areas')
	
	# GEE adds _p_percentile to bandname
	upper = str(int(self.env.highPercentile))
	lower = str(int(self.env.lowPercentile))
	
	# we dont want to include the mask
	selectedBandNamesLandsat = ee.List(['blue'])#,'green','red','nir','swir1','swir2'])

	# get the upper and lower band
	bandsUpper = ee.List(['blue_p'+ upper ])#+ upper,'green_p'+ upper,'red_p'+ upper,'nir_p'+ upper,'swir1_p'+ upper,'swir2_p'+ upper])
	bandsLower = ee.List(['blue_p' + lower])#+ lower,'green_p'+ lower,'red_p'+ lower,'nir_p'+ lower,'swir1_p'+ lower,'swir2_p'+ lower])

	percentilesUp = self.percentile.select(bandsUpper,selectedBandNamesLandsat )
	percentilesLow = self.percentile.select(bandsLower,selectedBandNamesLandsat )
	
	imgToMask = img.select(selectedBandNamesLandsat)
			 
	darkMask = ee.Image(imgToMask.lt(percentilesLow).reduce(ee.Reducer.sum())).eq(0)
	lightMask = ee.Image(imgToMask.gt(percentilesUp).reduce(ee.Reducer.sum())).eq(0)
	    
	return img.updateMask(lightMask).updateMask(darkMask).copyProperties(img)


    def simpleTDOM(self,img):
	
	#Mask out dark dark outliers
        zScore = img.select(self.env.shadowSumBands).subtract(self.irMean).divide(self.irStdDev)
        irSum = img.select(self.env.shadowSumBands).reduce(ee.Reducer.sum())
	TDOMMask = zScore.lt(self.env.zScoreThresh).reduce(ee.Reducer.sum()).eq(2).And(irSum.lt(self.env.shadowSumThresh)).Not()
	TDOMMask = ee.Image(TDOMMask.focal_min(self.env.dilatePixels)).rename(['TDOMMask'])
	
	return img.addBands(TDOMMask)
  


 
    def landsatCloudScore(self,img):
	""" Compute a cloud score and adds a band that represents the cloud mask.  
	This expects the input image to have the common band names: 
	["red", "blue", etc], so it can work across sensors. """

	logging.info('running landsatCloudscore = ' + str(self.env.cloudThreshold))
	
	img = ee.Image(img)
      
	# Compute several indicators of cloudiness and take the minimum of them.
        # Clouds are reasonably bright in the blue band.
	
	thresholds  = [0.07, 0.3]
	score = ee.Image(img.select("blue").subtract(thresholds[0])).divide(thresholds[1] - thresholds[0])
 
	thresholds  = [0.2, 0.8]
	image = img.select("blue").add(img.select("red")).add(img.select("green"))
        # Clouds are reasonably bright in all visible bands.
        score = score.min(ee.Image(image.subtract(thresholds[0])).divide(thresholds[1] - thresholds[0]))
	#self.rescale(image, 'red', [0.2, 0.8]));
   
	thresholds  = [0.3, 0.8]
        image = ee.Image(img.select('nir').add(img.select('swir1')).add(img.select('swir2')))
        # Clouds are reasonably bright in all infrared bands.
        score = score.min(ee.Image(image.subtract(thresholds[0])).divide(thresholds[1] - thresholds[0]))
	

        # edit Ate cfmask uses therman band to detect clouds
        # Clouds are reasonably cool in temperature.
        #score = score.min(rescale(img,'img.temp', [300, 290]));

        # However, clouds are not snow.
        #ndsi = ee.Image(img).normalizedDifference(['green', 'swir1']);
        #score =  score.min(self.rescale(ndsi, 'img', [0.8, 0.6])).multiply(100).byte();
        score = score.lt(self.env.cloudThreshold);   
		
        return img.updateMask(score) ;
 
    
    def cloudProject(self,img):
	""" Function for wrapping cloud and shadow masking together.
	    Assumes image has cloud mask band called "cloudMask" and a TDOM mask called  "TDOMMask".
	    function cloudProject(img,shadowSumThresh,dilatePixels,cloudHeights,
	    azimuthField,zenithField)
	"""
	
	#Get the cloud mask
	cloud = img.select('sr_cloud_qa').lt(0.0002);
	cloud = cloud.focal_max(self.env.dilatePixels);
	cloud = cloud.updateMask(cloud);
      
	# Get TDOM mask
	TDOMMask = img.select(['TDOMMask']).Not();
      
	# Project the shadow finding pixels inside the TDOM mask that are dark and 
	# inside the expected area given the solar geometry
	# Find dark pixels
	darkPixels = img.select(['nir','swir1','swir2']).reduce(ee.Reducer.sum()).lt(self.env.shadowSumThresh)
      
	# Get scale of image
	nominalScale = cloud.projection().nominalScale();

	# Find where cloud shadows should be based on solar geometry
	# Convert to radians
	meanAzimuth = img.get('solar_azimuth_angle');
	meanZenith = img.get('solar_zenith_angle');
        
	azR = ee.Number(meanAzimuth).multiply(3.14).divide(180.0).add(ee.Number(0.5).multiply(3.14 ));
        zenR = ee.Number(0.5).multiply(3.14).subtract(ee.Number(meanZenith).multiply(3.14).divide(180.0));
      
	def cloudHeight(cloudHeight):
	    cloudHeight = ee.Number(cloudHeight);
	    shadowCastedDistance = zenR.tan().multiply(cloudHeight); #Distance shadow is cast
	    x = azR.cos().multiply(shadowCastedDistance).divide(nominalScale).round() #X distance of shadow
	    y = azR.sin().multiply(shadowCastedDistance).divide(nominalScale).round() #Y distance of shadow
	    return cloud.changeProj(cloud.projection(), cloud.projection().translate(x, y));
      
	# Find the shadows
	shadows = self.env.cloudHeights.map(cloudHeight)

        shadow = ee.ImageCollection.fromImages(shadows).max();
     
	# Create shadow mask
	shadow = shadow.updateMask(cloud.mask().Not());
	shadow = shadow.focal_max(self.env.dilatePixels);
	shadow = shadow.updateMask(darkPixels.And(TDOMMask));

	# Combine the cloud and shadow masks
	combinedMask = cloud.mask().Or(shadow.mask()).neq(0);
      
	# Update the image's mask and return the image
	img = img.updateMask(combinedMask);
	img = img.addBands(combinedMask.rename(['cloudShadowMask']));
		
	return img;


 
    def ExportToAsset(self,img,assetName):  
        """export to asset """
        
        outputName = self.env.userID + str(self.env.timeString) + assetName
        logging.info('export image to asset: ' + str(outputName))   
	
	img = img.multiply(10000).int16()

                    
        task_ordered = ee.batch.Export.image.toAsset(image=ee.Image(img), description=str(self.env.timeString)+"_exportJob", assetId=outputName,region=self.env.location['coordinates'], maxPixels=1e13,scale=self.env.pixSize)
        
        # start task
        task_ordered.start()
    
        
        
col = SurfaceReflectance().RunModel()
   
count = col.size();
print('Count: ', count.getInfo());

image = ee.Image(col.first())



#print(image)
# create the vizualization parameters
viz = {'min':0.0, 'max':2000, 'bands':["B3","B2","B1"]};
# Print the information for an image asset.


#import ee.mapclient

# display the map
#ee.mapclient.addToMap(ee.Image(image),viz)
