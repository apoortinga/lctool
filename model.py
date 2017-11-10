# -*- coding: utf-8 -*-
"""
ExportLandsatSRComposite.py, SERVIR-Mekong (2017-07-30)

export landsat composites with gapfilling
________________________________________________________________________________


Usage
------

$ python  model.py {options}

{options} include:

--year (-y)      : required
                 : year to create the Landsat composite image for
                 : in format YYYY

--season (-s)    : season to create the Landsat composite image for
                 : seasons are set for the Mekong region and will need to be \
                 : changed for other geographic areas
                 : options are 'drycool', 'dryhot', or 'rainy'

--user (-u)      : user account used to create the composite
                 : changes the ~/.config/earthengine/credentials file
                 : dictionary is called to get credentials
                 : options are servirmekong, servir-mekong, ate, biplov .. default is servir-mekong

Example Usage
-------------

1) export surface reflectance composite for dryhot season of 2000 to assets:

  $ python model.py -y 2000 -s drycool -u Quyen

"""

import ee
import logging
import time
import math
from usercredentials import addUserCredentials
import argparse

class environment(object):
    
    
    def __init__(self):
        """Initialize the environment."""   
         
        # Initialize the Earth Engine object, using the authentication credentials.
		
        ee.Initialize()
       
	self.timeString = time.strftime("%Y%m%d_%H%M%S")

	# SEASONS:
	# '0': Dry Cool: Nov - Feb (305 - 59)
	# '1': Dry Hot: Mar - Apr (60 - 181)
	# '2': Rainy: May - Oct (182 - 304)
   
	startjulian = {'drycool':305,'dryhot':60,'rainy':182}
	endjulian = {'drycool':59,'dryhot':181,'rainy':304}
   
        # set dates
        self.startYear = int(args.year);
        self.endYear = int(args.year);
        self.startJulian = startjulian[args.season]
        self.endJulian = endjulian[args.season]
	
	if args.season == 'drycool':
	    self.startYear = int(args.year)-1
        
	self.NgheAn = [[103.876,18.552],[105.806,18.552],[105.806,19.999],[103.876,19.999],[103.876,18.552]]
      
        collectionName = "projects/servir-mekong/usgs_sr_composites/" + args.season 
        self.collection = ee.ImageCollection(collectionName)
	
	self.shadowSumBands = ['nir','swir1'];
	self.zScoreThresh = -0.8
	self.shadowSumThresh = 0.35;
	self.dilatePixels = 2
	
	#users/servirmekong/usgs_sr_composites/drycool
	self.outputName = args.season + str(self.startYear) + "_" + str(self.endYear)

        # variable to filter cloud threshold
        self.metadataCloudCoverMax = 40
        
        # threshold for landsatCloudScore
        self.cloudThreshold = 0
        
        # percentiles to filter for bad data
        self.lowPercentile = 5
        self.highPercentile = 85

        # whether to use imagecolletions
        self.useL4=True
        self.useL5=True
        self.useL7=True
	self.useL7scanline = False
        self.useL8=True

	# On May 31, 2003 the Scan Line Corrector (SLC) in the ETM+ instrument failed
	self.l7Failed = ee.Date.fromYMD(2003,5,31)

        # apply cloud masks
        self.maskSR = True

	self.tcInputBands =  ee.List(['blue','green','red','nir','swir1','swir2'])
	
        self.bandNamesLandsat = ee.List(['blue','green','red','nir','swir1','thermal','swir2','sr_atmos_opacity','pixel_qa','radsat_qa'])
       
	
	self.exportBands = ee.List(['blue','green','red','nir','swir1','thermal','swir2'])
	self.divideBands = ee.List(['blue','green','red','nir','swir1','swir2'])
        
	# apply defringe
        self.defringe = True
        
        # pixel size
        self.pixSize = 30
        
        # user ID
        #self.userID = "users/servirmekong/assemblage/"
        self.userID = "users/servirmekong/temp/4"
        #self.userID = "projects/servir-mekong/usgs_sr_composites/" + args.season + "/" 

       
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
        
	self.env.location = ee.Geometry.Polygon(self.env.NgheAn) #ee.Geometry.Polygon(geo)

	#self.env.location = ee.Geometry.Polygon([[104.716,18.615],[105.622,18.620],[105.540,19.451],[104.650,19.466],[104.716,18.615]])
	self.env.outputName = self.env.outputName + str(x) + str(y)
	 
        logging.info('starting the model the model')
        	
	print self.env.startJulian, self.env.endJulian
   
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
	fullCollection = self.returnCollection()  
	
	# Get some pixel-wise stats for the time series
	self.irStdDev = ee.Image(fullCollection.select(self.env.shadowSumBands).reduce(ee.Reducer.stdDev()))
	self.irMean = ee.ImageCollection(fullCollection.select(self.env.shadowSumBands)).mean()
	
	collection = collection.map(self.simpleTDOM2)


	# get upper and lower percentile
        self.percentile = fullCollection.reduce(ee.Reducer.percentile([self.env.lowPercentile,self.env.highPercentile])) 
	collection = collection.map(self.MaskPercentile) 
	img = ee.Image(collection.median())
	
	# mask all negative values
	mask = img.gt(0)
	img = ee.Image(img.updateMask(mask))
	

        count = collection.size();
        print('counted ' + str(count.getInfo()) +' images');    
	
	startDate = ee.Date.fromYMD(self.env.startYear-1,1,1)
        endDate = ee.Date.fromYMD(self.env.endYear-1,12,31)   
	
	#img = img.select(self.env.exportBands)

	img = self.addIndices(img)
	img = self.getTasseledCap(img,self.env.tcInputBands )
	img = self.addTCAngles(img)
		
	img = self.reScaleLandsat(img)

	
	
	previousAssemblage = ee.Image(self.env.collection.filterDate(startDate,endDate).mosaic())
	
	print previousAssemblage.bandNames().getInfo()

	
	img = ee.Image(img).unmask(previousAssemblage)
	print ee.Image(img).bandNames().getInfo()
	
	#for i in range(1,17,1):
	#    img = self.unmaskYears(img,i)    

	#for i in range(1,12,1):
	#    img = self.unmaskFutureYears(img,i)    
	

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
            if not merge:
		landsatCollection = landsat5.select(self.env.sensorBandDictLandsatSR.get('L5'),self.env.bandNamesLandsat)
		merge = True
            else:
		landsatCollection = landsatCollection.merge(landsat5.select(self.env.sensorBandDictLandsatSR.get('L5'),self.env.bandNamesLandsat))
	
        # landsat 7 image collections  
        if self.env.useL7:
            landsat7 =  ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filterDate(startDate,endDate).filterBounds(self.env.location)
	    if self.env.startYear == 2003 or  self.env.endYear == 2003:
		if self.env.useL7scanline == False:
		    landsat7 = landsat7.filterDate(startDate,self.env.l7Failed)
            landsat7 = landsat7.filterMetadata('CLOUD_COVER','less_than',metadataCloudCoverMax)
            landsat7 = landsat7.filter(ee.Filter.calendarRange(self.env.startJulian,self.env.endJulian))
            if landsat7.size().getInfo() > 0:
		if self.env.defringe == True:
		    landsat7 =  landsat7.map(self.DefringeLandsat)            
		if self.env.maskSR == True:
		    landsat7 = landsat7.map(self.CloudMaskSR)
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
       

    def returnCollection(self):
        """Calculate percentiles to filter imagery"""  
        
        logging.info('calculate percentiles')
        
        startDate = ee.Date.fromYMD(1984,1,1)
        endDate = ee.Date.fromYMD(2020,1,1)    
        cloudCoverMax = 30
        
        # get the images
        collection = self.GetLandsat(startDate,endDate,cloudCoverMax)
	
	return collection
       
    def CloudMaskSR(self,img):
         """apply cf-mask Landsat""" 
	 
	 QA = img.select("pixel_qa")
	 #mask = ee.Image(self.getQABits(QA,3, 5, 'internal_quality_flag')); 
	 #print mask
        
         return img.updateMask(QA.lt(112)).copyProperties(img)
         #return img.addBands(mask.select('internal_quality_flag'))

    def ScaleLandsat(self,img):
        """Landast is scaled by factor 0.0001 """
        
	thermal = ee.Image(img).select(ee.List(['thermal']))
        scaled = ee.Image(img).select(self.env.divideBands).multiply(0.0001)
	image = ee.Image(scaled.addBands(thermal))
    
	logging.info('return scaled image')
        return ee.Image(image.copyProperties(img))

    def reScaleLandsat(self,img):
        """Landast is scaled by factor 0.0001 """
        
	thermalBand = ee.List(['thermal'])
	thermal = ee.Image(img).select(thermalBand)
	
	otherBands = ee.Image(img).bandNames().removeAll(thermalBand)
        scaled = ee.Image(img).select(otherBands).divide(0.0001)
	
	image = ee.Image(scaled.addBands(thermal)).int16()
        logging.info('return scaled image')
        
	return image.copyProperties(img)

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


    def simpleTDOM2(self,img):
	""" Function for finding dark outliers in time series.
	Original concept written by Carson Stam and adapted by Ian Housman.
	Adds a band that is a mask of pixels that are dark, and dark outliers."""
 
	zScore = img.select(self.env.shadowSumBands).subtract(self.irMean).divide(self.irStdDev);
	irSum = img.select(self.env.shadowSumBands).reduce(ee.Reducer.sum());
	TDOMMask = zScore.lt(self.env.zScoreThresh).reduce(ee.Reducer.sum()).eq(2).And(irSum.lt(self.env.shadowSumThresh)).Not();
	TDOMMask = TDOMMask.focal_min(self.env.dilatePixels);
	
	return img.updateMask(TDOMMask);

    def ExportToAsset(self,img,assetName):  
        """export to asset """
        
        outputName = self.env.userID + assetName
        logging.info('export image to asset: ' + str(outputName))   
	
        startDate = ee.Date.fromYMD(self.env.startYear,1,1)
        endDate = ee.Date.fromYMD(self.env.endYear,12,31)    

	image = ee.Image(img).set({'system:time_start':startDate.millis(), \
				    'startyear':self.env.startYear, \
			            'endyear':self.env.endYear, \
			            'startJulian':self.env.startJulian, \
		                    'endJulian':self.env.endJulian,
				    'source':'USGS SR',\
				    'version':'1.0'}) 
	
        
        #task_ordered = ee.batch.Export.image.toAsset(image=ee.Image(img), description=str(self.env.timeString)+assetName, assetId=outputName,region=self.env.location['coordinates'], maxPixels=1e13,scale=self.env.pixSize)
        task_ordered = ee.batch.Export.image.toAsset(image=ee.Image(image), description=assetName, assetId=outputName,region=self.env.location['coordinates'], maxPixels=1e13,scale=self.env.pixSize)
        
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

    def unmaskFutureYears(self,img,year):
	""" Function to unmask nodata withpixels future year """
	
	print "unmasking for year " + str(self.env.startYear+year) 
	startDate = ee.Date.fromYMD(self.env.startYear+year,1,1)
	endDate = ee.Date.fromYMD(self.env.endYear+year,12,31)    
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

    def getTasseledCap(self,img,bands):
	"""Function to compute the Tasseled Cap transformation and return an image"""

        logging.info('get tasselcap for computed images')
	
	coefficients = ee.Array([
	    [0.3037, 0.2793, 0.4743, 0.5585, 0.5082, 0.1863],
	    [-0.2848, -0.2435, -0.5436, 0.7243, 0.0840, -0.1800],
	    [0.1509, 0.1973, 0.3279, 0.3406, -0.7112, -0.4572],
	    [-0.8242, 0.0849, 0.4392, -0.0580, 0.2012, -0.2768],
	    [-0.3280, 0.0549, 0.1075, 0.1855, -0.4357, 0.8085],
	    [0.1084, -0.9022, 0.4120, 0.0573, -0.0251, 0.0238]
	  ]);
	
	# Make an Array Image, with a 1-D Array per pixel.
	arrayImage1D = img.select(bands).toArray()
	
	# Make an Array Image with a 2-D Array per pixel, 6x1.
	arrayImage2D = arrayImage1D.toArray(1)
	
	componentsImage = ee.Image(coefficients).matrixMultiply(arrayImage2D).arrayProject([0]).arrayFlatten([['brightness', 'greenness', 'wetness', 'fourth', 'fifth', 'sixth']]).float();
  
	# Get a multi-band image with TC-named bands.
  	return img.addBands(componentsImage);


    def addTCAngles(self,img):
	""" Function to add Tasseled Cap angles and distances to an image.
	    Assumes image has bands: 'brightness', 'greenness', and 'wetness'."""
	
	logging.info('add tasseled cap angles')
	
	# Select brightness, greenness, and wetness bands	
	brightness = img.select('brightness');
	greenness = img.select('greenness');
	wetness = img.select('wetness');
  
	# Calculate Tasseled Cap angles and distances
	tcAngleBG = brightness.atan2(greenness).divide(math.pi).rename(['tcAngleBG']);
	tcAngleGW = greenness.atan2(wetness).divide(math.pi).rename(['tcAngleGW']);
	tcAngleBW = brightness.atan2(wetness).divide(math.pi).rename(['tcAngleBW']);
	tcDistBG = brightness.hypot(greenness).rename(['tcDistBG']);
	tcDistGW = greenness.hypot(wetness).rename(['tcDistGW']);
	tcDistBW = brightness.hypot(wetness).rename(['tcDistBW']);
	
	img = img.addBands(tcAngleBG).addBands(tcAngleGW).addBands(tcAngleBW).addBands(tcDistBG).addBands(tcDistGW).addBands(tcDistBW);
	return img;

class Primitives():
 
    def __init__(self):
        """Initialize the Surfrace Reflectance app."""  
        
        # import the log library
        import logging
	
	# get the environment
        self.env = environment()    
        
   
if __name__ == "__main__":
  
    # set argument parsing object
    parser = argparse.ArgumentParser(description="Create Landsat image composites using Google\
                                                  Earth Engine.")
   
    parser.add_argument('--year','-y', type=str,required=True,
                        help="Year to perform the ats correction and save to asset format in 'YYYY'")

    parser.add_argument('--season','-s', choices=['drycool','dryhot','rainy'],type=str,
                        help="Season to create composite for, these align with SERVIR-Mekong's seasonal composite times")

    parser.add_argument('--user','-u', type=str, default="servir-mekong",choices=['servir-mekong','servirmekong',"ate","biplov","quyen"],
			help="specify user account to run task")

    args = parser.parse_args() # get arguments  
  
    # user account to run task on
    userName = args.user
    year = args.year
    seasons = args.season
    
    # create a new file in ~/.config/earthengine/credentials with token of user
    addUserCredentials(userName)
    geom = ''    
    SurfaceReflectance().RunModel(geom,1,1)
    #SurfaceReflectance().makeTiles()
