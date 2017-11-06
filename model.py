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
        self.startYear = 2001;
        self.endYear = 2001;
        self.startJulian = 182
        self.endJulian = 304
        
	self.outputName = "rainy_" + str(self.startYear) + "_" + str(self.endYear)
	# Rainy
	# dry hot
	# dry cool
	
        # variable to filter cloud threshold
        self.metadataCloudCoverMax = 40
        
        # threshold for landsatCloudScore
        self.cloudThreshold = 0
        
        # percentiles to filter for bad data
        self.lowPercentile = 8
        self.highPercentile = 66

        # whether to use imagecolletions
        self.useL4=True
        self.useL5=True
        self.useL7=False
        self.useL8=True

        # apply cloud masks
        self.maskSR = True
        self.maskCF = False
        self.cloudScore = False
	
        self.bandNamesLandsat = ee.List(['blue','green','red','nir','swir1','thermal','swir2','sr_atmos_opacity','pixel_qa','radsat_qa'])
	
	self.exportBands = ee.List(['blue','green','red','nir','swir1','thermal','swir2'])
        
	# apply defringe
        self.defringe = True
        
        # pixel size
        self.pixSize = 30
        
        # user ID
        #self.userID = "users/servirmekong/assemblage/"
        self.userID = "projects/servir-mekong/temp/"
        
        # define the landsat bands
        self.sensorBandDictLandsatSR = ee.Dictionary({'L8' : ee.List([1,2,3,4,5,6,7,8,9]),
                                                      'L7' : ee.List([0,1,2,3,4,5,6,7,9,10]),
                                                      'L5' : ee.List([0,1,2,3,4,5,6,7,9,10]),
                                                      'L4' : ee.List([0,1,2,3,4,5,6,7,9,10])})

        # threshold for defringing landsat5 and 7
        self.fringeCountThreshold = 279

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
                
    
    def RunModel(self,geo,x,y):
        """Run the SR model"""  
        
	self.env.location = ee.Geometry.Polygon(geo)
	self.env.outputName = self.env.outputName + str(x) + str(y)
	 
        logging.info('starting the model the model')
        
        # construct date objects
        startDate = ee.Date.fromYMD(self.env.startYear,1,1)
        endDate = ee.Date.fromYMD(self.env.endYear,12,31)    
        
	logging.info('startDate = ' + str(startDate.getInfo()))
	logging.info('endDatDate = ' + str(startDate.getInfo()))
	logging.info('Cloudcover filter = ' + str(self.env.metadataCloudCoverMax))	
	
        # get the images
        collection = self.GetLandsat(startDate,endDate,self.env.metadataCloudCoverMax)
        	
        # calculate the percentiles
        
        #print percentiles.getInfo()
	self.percentile = ee.Image(self.CalculatePercentiles())  
	
	#print self.percentile.bandNames()
        
	collection = collection.map(self.MaskPercentile) 
	img = ee.Image(collection.median())
	mask = img.gt(0)
	img = ee.Image(img.updateMask(mask))


        count = collection.size();
        print('counted ' + str(count.getInfo()) +' images');    
	
	for i in range(1,16,1):
	    img = self.unmaskYears(img,i)    

	self.ExportToAsset(img,self.env.outputName)         

        
          
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
            #if self.env.maskSR == True:
            #    landsat4 = landsat4.map(self.radSat)
            #    landsat4 = landsat4.map(self.maskHaze)
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
            #if self.env.maskSR == True:
            #    landsat5 = landsat5.map(self.radSat)
            #    landsat5 = landsat5.map(self.maskHaze)
            if not merge:
		landsatCollection = landsat5.select(self.env.sensorBandDictLandsatSR.get('L5'),self.env.bandNamesLandsat)
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
            #if self.env.maskSR == True:
            #    landsat7 = landsat7.map(self.radSat)
            #    landsat7 = landsat7.map(self.maskHaze)
            if not merge:
		landsatCollection = landsat7.select(self.env.sensorBandDictLandsatSR.get('L7'),self.env.bandNamesLandsat)
	    	merge = True
            else:
		landsatCollection = landsatCollection.merge(landsat7.select(self.env.sensorBandDictLandsatSR.get('L7'),self.env.bandNamesLandsat))
	"""
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
		landsatCollection = landsat8.select(self.env.sensorBandDictLandsatSR.get('L8'),self.env.bandNamesLandsat)
		merge = True
            else:
		landsatCollection = landsatCollection.merge(landsat8.select(self.env.sensorBandDictLandsatSR.get('L8'),self.env.bandNamesLandsat))            
        """
        count = landsatCollection.size();

        landsatCollection = landsatCollection.map(self.ScaleLandsat)        
       
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
	#print collectionPercentile.bandNames().getInfo()
        logging.info('returning percentiles')
        
        return ee.Image(collectionPercentile)
       
    def CloudMaskSR(self,img):
         """apply cf-mask Landsat""" 
	 
	 QA = img.select("pixel_qa")
	 #mask = ee.Image(self.getQABits(QA,3, 5, 'internal_quality_flag')); 
	 #print mask
        
         return img.updateMask(QA.lt(112)).copyProperties(img)
         #return img.addBands(mask.select('internal_quality_flag'))

    def ScaleLandsat(self,img):
        """Landast is scaled by factor 0.0001 """
        
        scaled = ee.Image(img).multiply(0.0001).copyProperties(img,['system:time_start']) 
        logging.info('return scaled image')
        return scaled.copyProperties(img)


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
	selectedBandNamesLandsat =['blue','green','red','nir'] #,'swir1','swir2']

	for b in selectedBandNamesLandsat:
	    
	    selectedBand = ee.List([b])

	    # get the upper and lower band
	    bandsUpper = ee.List([str(b)+ '_p'+ upper])#+ upper,'green_p'+ upper,'red_p'+ upper,'nir_p'+ upper,'swir1_p'+ upper,'swir2_p'+ upper])
	    bandsLower = ee.List([str(b)+ '_p' + lower])#+ lower,'green_p'+ lower,'red_p'+ lower,'nir_p'+ lower,'swir1_p'+ lower,'swir2_p'+ lower])
	    #print bandsUpper

	    percentilesUp = self.percentile.select(bandsUpper,selectedBand  )
	    percentilesLow = self.percentile.select(bandsLower,selectedBand )
	    
	    #print percentilesUp
	    imgToMask = img.select(selectedBand)
			     
	    darkMask = ee.Image(imgToMask.lt(percentilesLow).reduce(ee.Reducer.sum())).eq(0)
	    lightMask = ee.Image(imgToMask.gt(percentilesUp).reduce(ee.Reducer.sum())).eq(0)
	    
	    img = ee.Image(img.updateMask(lightMask).updateMask(darkMask).copyProperties(img))
	    
	return img


    def ExportToAsset(self,img,assetName):  
        """export to asset """
        
        outputName = self.env.userID + assetName
        logging.info('export image to asset: ' + str(outputName))   
	
	print outputName
	img = img.multiply(10000).int16().select(self.env.exportBands)
                    
        #task_ordered = ee.batch.Export.image.toAsset(image=ee.Image(img), description=str(self.env.timeString)+assetName, assetId=outputName,region=self.env.location['coordinates'], maxPixels=1e13,scale=self.env.pixSize)
        task_ordered = ee.batch.Export.image.toAsset(image=ee.Image(img), description=assetName, assetId=outputName,region=self.env.location['coordinates'], maxPixels=1e13,scale=self.env.pixSize)
        
        # start task
        task_ordered.start()
    
    def addIndices(self,img):
	""" Function to add common (and less common) spectral indices to an image.
	    Includes the Normalized Difference Spectral Vector from (Angiuli and Trianni, 2014) """

	#Add Normalized Difference Spectral Vector (NDSV)
        img = img.addBands(img.normalizedDifference(['blue','green']).rename(['ND_blue_green']));
	img = img.addBands(img.normalizedDifference(['blue','red']).rename(['ND_blue_red']));
	img = img.addBands(img.normalizedDifference(['blue','nir']).rename(['ND_blue_nir']));
	img = img.addBands(img.normalizedDifference(['blue','swir1']).rename(['ND_blue_swir1']));
	img = img.addBands(img.normalizedDifference(['blue','swir2']).rename(['ND_blue_swir2']));

	img = img.addBands(img.normalizedDifference(['green','red']).rename(['ND_green_red']));
	img = img.addBands(img.normalizedDifference(['green','nir']).rename(['ND_green_nir']));  # NDWBI
	img = img.addBands(img.normalizedDifference(['green','swir1']).rename(['ND_green_swir1']));  # NDSI, MNDWI
	img = img.addBands(img.normalizedDifference(['green','swir2']).rename(['ND_green_swir2']));

	img = img.addBands(img.normalizedDifference(['red','swir1']).rename(['ND_red_swir1']));
	img = img.addBands(img.normalizedDifference(['red','swir2']).rename(['ND_red_swir2']));

	img = img.addBands(img.normalizedDifference(['nir','red']).rename(['ND_nir_red']));  # NDVI
	img = img.addBands(img.normalizedDifference(['nir','swir1']).rename(['ND_nir_swir1']));  # NDWI, LSWI, -NDBI
	img = img.addBands(img.normalizedDifference(['nir','swir2']).rename(['ND_nir_swir2']));  # NBR, MNDVI

	img = img.addBands(img.normalizedDifference(['swir1','swir2']).rename(['ND_swir1_swir2']));
  
	# Add ratios
	img = img.addBands(img.select('swir1').divide(img.select('nir')).rename(['R_swir1_nir']));  # ratio 5/4
	img = img.addBands(img.select('red').divide(img.select('swir1')).rename(['R_red_swir1']));  # ratio 3/5

	#Add Enhanced Vegetation Index (EVI)
	evi = img.expression(
	    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
	      'NIR': img.select('nir'),
	      'RED': img.select('red'),
	      'BLUE': img.select('blue')
	  }).float();
	
	img = img.addBands(evi.rename(['EVI']));
	  
	# Add Soil Adjust Vegetation Index (SAVI)
	# using L = 0.5;
	savi = img.expression(
	    '(NIR - RED) * (1 + 0.5)/(NIR + RED + 0.5)', {
	      'NIR': img.select('nir'),
	      'RED': img.select('red')
	  }).float();
	img = img.addBands(savi.rename(['SAVI']));
	  
	# Add Index-Based Built-Up Index (IBI)
	ibi_a = img.expression(
	    '2*SWIR1/(SWIR1 + NIR)', {
	      'SWIR1': img.select('swir1'),
	      'NIR': img.select('nir')
	    }).rename(['IBI_A']);
	
	ibi_b = img.expression(
	    '(NIR/(NIR + RED)) + (GREEN/(GREEN + SWIR1))', {
	      'NIR': img.select('nir'),
	      'RED': img.select('red'),
	      'GREEN': img.select('green'),
	      'SWIR1': img.select('swir1')
	    }).rename(['IBI_B']);
	
	ibi_a = ibi_a.addBands(ibi_b);
	ibi = ibi_a.normalizedDifference(['IBI_A','IBI_B']);
	img = img.addBands(ibi.rename(['IBI']));
	  
	return img;       


    def unmaskYears(self,img,year):
	""" Function to unmask nodata withpixels previous year """
	
	print "unmasking for year " + str(self.env.startYear-year) 
	startDate = ee.Date.fromYMD(self.env.startYear-year,1,1)
	endDate = ee.Date.fromYMD(self.env.endYear-year,12,31)    
	prev = self.GetLandsat(startDate,endDate,self.env.metadataCloudCoverMax)
	if prev.size().getInfo() > 0:
	    prev = prev.map(self.MaskPercentile) 
	    previmg = ee.Image(prev.median())
	    previmg = previmg.mask(previmg.gt(0))
	    img = img.unmask(previmg)
	
	
	return ee.Image(img)


    def makeTiles(self):
	# set bounds
	xmin = 91.979254;
	xmax = 114.664186;
	ymin = 5.429208;
	ymax = 28.728774;

	# number of rows and columns
	n = 2;

	for  i in range(0, n, 1):
	    for j in range(0, n,1):	# x, y distance of one block
		xs = (xmax - xmin) / n
		ys = (ymax - ymin) / n
		
		xl = xmin + i * xs;
		xr = xmin + (i+1) * xs;
		
		yt = ymin + (j*ys);
		yb = ymin + (j+1)*ys;
		geom =   [[xl, yt], [xl, yb], [xr, yb], [xr, yt]];

		col = SurfaceReflectance().RunModel(geom,i,j)

        
   
if __name__ == "__main__":
   SurfaceReflectance().makeTiles()
