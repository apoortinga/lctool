# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 14:47:06 2017

@author: SERVIRWK
"""

import ee
import logging

class environment(object):
    
    
    def __init__(self):
        """Initialize the environment."""   
         
        # Initialize the Earth Engine object, using the authentication credentials.
        ee.Initialize()
       
        # set dates
        self.startYear = 2003;
        self.endYear = 2004;
        self.startJulian = 1;
        self.endJulian = 366;        
        
        # set location 
        self.location = ee.Geometry.Polygon([[[103.294,17.923],[103.294,17.923],[106.453,17.923],[106.453,20.469],[103.2941,20.469],[103.294,17.923]]])
        
        #ee.Geometry.Polygon([[[103.91,20.02],[103.910,20.601],[103.1,20.601],[103.1325,20.002],[104.919,20.020]]]) #ee.Geometry.Point([105.809,21.074])
        
        # variable to filter cloud threshold
        self.metadataCloudCoverMax = 25
        
        # percentiles to filter for bad data
        self.lowPercentile = 1
        self.highPercentile = 99

        # whether to use imagecolletions
        self.useL4=True
        self.useL5=True
        self.useL7=True
        self.useL8=True

        # apply cloud masks
        self.maskSR = True
        self.maskCF = True
        
        self.bandNamesLandsat = ee.List(['blue','green','red','nir','swir1','swir2','cfmask'])
              
        # apply defringe
        self.defringe = True
        
        # pixel size
        self.pixSize = 30
        
        # user ID
        self.userID = "users/servirmekong/temp/"
        
        # define the landsat bands
        self.sensorBandDictLandsatSR = ee.Dictionary({'L8' : ee.List([1,2,3,4,5,6,7]),
                                                      'L7' : ee.List([0,1,2,3,4,5,6]),
                                                      'L5' : ee.List([0,1,2,3,4,5,6]),
                                                      'L4' : ee.List([0,1,2,3,4,5,6])})

        # threshold for defringing landsat5 and 7
        self.fringeCountThreshold = 279;                              

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
        # set the logfile
        logging.basicConfig(filename='model.log', filemode='w', level=logging.DEBUG)
        
        # Initialize the Earth Engine object, using the authentication credentials.
        ee.Initialize()
        
        # get the environment
        self.env = environment()
    
    def RunModel(self):
        """Run the SR model"""  
        
        logging.info('starting the model the model')
        
        # construct date objects
        startDate = ee.Date.fromYMD(self.env.startYear,1,1)
        endDate = ee.Date.fromYMD(self.env.endYear,1,1)    
        
        # get the images
        collection = self.GetLandsat(startDate,endDate,self.env.metadataCloudCoverMax)
        
       
        outputName = "testmask3_" + str(self.env.startYear)
        
        
        # calculate the percentiles
        
        #print percentiles.getInfo()
         
        #collection = collection.map(self.MaskPercentile) 
	img = ee.Image(collection.median())  
	self.ExportToAsset(img,outputName)         
        #print filteredCollection
        return  collection
        
          
    # Obtain Landsat image collections 
    def GetLandsat(self,startDate,endDate,metadataCloudCoverMax):
        """Get the Landsat imagery"""  
        
        logging.info('getting landsat images')

            
        # boolean to merge Landsat; when true is merges with another collection
        merge = False
        
        # landsat4 image collections 
        if self.env.useL4:        
            landsat4 =  ee.ImageCollection('LANDSAT/LT4_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat4 = landsat4.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            if self.env.defringe == True:
                 landsat4 =  landsat4.map(self.DefringeLandsat)
            if self.env.maskSR == True:
                landsat4 = landsat4.map(self.CloudMaskSR)
            if self.env.maskSR == True:
                landsat4 = landsat4.map(self.CloudMaskCF)
            if not merge:
			landsatCollection = landsat4.select(self.env.sensorBandDictLandsatSR.get('L4'),self.env.bandNamesLandsat)
			merge = True

        # landsat 5 image collections 
        if self.env.useL5:
            landsat5 =  ee.ImageCollection('LANDSAT/LT5_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat5 = landsat5.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            if self.env.defringe == True:
                 landsat5 =  landsat5.map(self.DefringeLandsat)
            if self.env.maskSR == True:
                landsat5 = landsat5.map(self.CloudMaskSR)
            if self.env.maskSR == True:
                landsat5 = landsat5.map(self.CloudMaskCF)
            if not merge:
			landsatCollection = landsat5
			merge = True
            else:
			landsatCollection = landsatCollection.merge(landsat5.select(self.env.sensorBandDictLandsatSR.get('L5'),self.env.bandNamesLandsat))
        
        # landsat 7 image collections  
        if self.env.useL7:
            landsat7 =  ee.ImageCollection('LANDSAT/LE7_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat7 = landsat7.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            if self.env.defringe == True:
                 landsat7 =  landsat7.map(self.DefringeLandsat)            
            if self.env.maskSR == True:
                landsat7 = landsat7.map(self.CloudMaskSR)
            if self.env.maskSR == True:
                landsat7 = landsat7.map(self.CloudMaskCF)
            if not merge:
			landsatCollection = landsat7
			merge = True
            else:
			landsatCollection = landsatCollection.merge(landsat7.select(self.env.sensorBandDictLandsatSR.get('L7'),self.env.bandNamesLandsat))

        # landsat8  image collections 				        
        if self.env.useL8:
            landsat8 =  ee.ImageCollection('LANDSAT/LC8_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
            landsat8 = landsat8.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            if self.env.defringe == True:
                 landsat8 =  landsat8.map(self.DefringeLandsat)    
            if self.env.maskSR == True:
                landsat8 = landsat8.map(self.CloudMaskCF)            
            if not merge:
			landsatCollection = landsat8
			merge = True
            else:
			landsatCollection = landsatCollection.merge(landsat8.select(self.env.sensorBandDictLandsatSR.get('L8'),self.env.bandNamesLandsat))            
       
        count = landsatCollection.size();
        
        logging.info('scaling images');
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
        cloudCoverMax = 40
        
        # get the images
        collection = self.GetLandsat(startDate,endDate,cloudCoverMax)

        # get upper and lower percentile
        collectionPercentile = collection.reduce(ee.Reducer.percentile([self.env.lowPercentile,self.env.highPercentile])) 
        
        logging.info('returning percentiles')
        
        return collectionPercentile

        
    def CloudMaskSR(self,img):
         """Apply cloud mask"""  
       
         logging.info('Applying SR mask')
        
         fmk = img.select("sr_cloud_qa").mask();
        
         logging.info('return mask')
         return img.updateMask(fmk) ## add .not
        
    def CloudMaskCF(self,img):
         """apply cf-mask Landsat"""  
        
         fmk = img.select("cfmask").lt(2)
         return img.updateMask(fmk)

    def ScaleLandsat(self,img):
        """Landast is scaled by factor 0.0001 """
        
        scaled = ee.Image(img).multiply(0.0001).copyProperties(img,['system:time_start']) 
        logging.info('return scaled image')
        return scaled

    def  DefringeLandsat(self,img):   
        """remove scanlines from landsat 4 and 7 """
        
        logging.info('removing scanlines')

        m = ee.Image(img).select("B1").mask().reduce(ee.Reducer.min())
        sum = m.reduceNeighborhood(ee.Reducer.sum(), self.env.k, 'kernel')
        sum = sum.gte(self.env.fringeCountThreshold)        
        img = img.mask(img.mask().add(sum)) # Check this
        return img
        
    def MaskPercentile(self,img):
	"""mask light and dark pixels """
	logging.info('mask light and dark areas')
	
	percentiles = self.CalculatePercentiles()
		
	upper = "blue_p" + str(int(self.env.highPercentile))
	lower = "blue_p" + str(int(self.env.lowPercentile))
        
        darkMask = img.gt(percentiles.select(lower))
	lightMask = img.lt(percentiles.select(upper))
	
	return img.updateMask(lightMask).updateMask(darkMask)
 
 
 
 
    def ExportToAsset(self,img,assetName):  
        """export to asset """
        
        outputName = self.env.userID + assetName
        logging.info('export image to asset: ' + str(outputName))   
        
            
        task_ordered = ee.batch.Export.image.toAsset(image=ee.Image(img), description="exportJob", assetId=outputName,region=self.env.location['coordinates'], maxPixels=1e13,scale=self.env.pixSize)
        
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
