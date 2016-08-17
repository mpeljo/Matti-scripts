"""
Jonah's multiprocessing python script provided by Duncan Moore.
Draws upon a list and then feeds the list to the specified number of cores
when they are free via the pool method. Uses data in:
\\nas\cds\internal\internal\physiography\topographic_relief\elevation\data\statedatasets\nsw\BatemansBay0611\z56\2011\DEM\Grid\ASCII_GRID
"""

import arcpy
import os
import multiprocessing
import time
import sys
from osgeo import gdal, ogr, osr

# function that outputs a list of rasters in a folder or directory
def find_rasters(rasterDir, searchSubdirectories):
    print "counting rasters"
    if searchSubdirectories != True:
        rasterList = []
        arcpy.env.workspace = rasterDir
        arcpyrasterList = arcpy.ListRasters("")
        for raster in arcpyrasterList:
            rasterPath = os.path.join(rasterDir, raster)
            rasterList.append(rasterPath)
        msg = str(len(rasterList)), "rasters found"
        AddMsgAndPrint(msg)
    elif searchSubdirectories == True:
        def raster_in_workspace(workspace):
            arcpy.env.workspace = workspace
            for ras in arcpy.ListRasters("*"):
                yield os.path.join(workspace, ras)
            for ws in arcpy.ListWorkspaces():
                msg = "searching " + str(ws) + "..."
                AddMsgAndPrint(msg)
                for ras in raster_in_workspace(os.path.join(workspace, ws)):
                    yield ras
        rasterList = list(raster_in_workspace(rasterDir))
        msg = str(len(rasterList)) + " rasters found"
        AddMsgAndPrint(msg)
    return rasterList
    
def raster_attribute_list_gdal(rasterPath, i):
    rasterFile = gdal.Open(rasterPath)

    # find raster XY extent
    try:
        rasterExtent = rasterFile.GetGeoTransform()
        rasterCellsize = (rasterExtent[1] + abs(rasterExtent[5])) / 2
        rasterWidth = float(rasterFile.RasterXSize)
        rasterHeight = float(rasterFile.RasterYSize)
        rasterxMin = float(rasterExtent[0])
        rasterxMax = rasterxMin + (rasterWidth * rasterCellsize)
        rasteryMax = float(rasterExtent[3])
        rasteryMin = rasteryMax - (rasterHeight * rasterCellsize)

        # find other raster attributes
        rasterBand = rasterFile.RasterCount
        rasterDir = os.path.dirname(rasterPath)
        rasterFilename = os.path.basename(rasterPath)
        rasterFormat = rasterFile.GetDriver().LongName
        band = rasterFile.GetRasterBand(1)
        rasterpixelType = gdal.GetDataTypeName(band.DataType)
        rasterzMin = band.GetMinimum()
        rasterzMax = band.GetMaximum()

        # find raster projection information
        prj = rasterFile.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        rasterUnit = srs.GetLinearUnitsName()
        SRname = 'UNK' 
        if srs.IsProjected:
            SRname = srs.GetAttrValue('projcs')
            SRdatum = srs.GetAttrValue('datum')
            SRutmZone = srs.GetUTMZone()
        else:
            SRname = srs.GetAttrValue('geogcs')
            SRdatum = srs.GetAttrValue('datum')
            SRutmZone = 0
            
        # This is the ESRI method:
        # rasterSpatialReference = arcpy.Describe(rasterPath).spatialReference.exportToString()
        
        # look for *.rrd and *.ovr files
        pyramids = False
        pyramidTypes = [".rrd", ".ovr"]
        for pyrType in pyramidTypes:
            replaceExt = os.path.exists(rasterPath.split(os.extsep)[0] + pyrType)
            addtoExt = os.path.exists(rasterPath + pyrType)
            if replaceExt or addtoExt:
                pyramids = True

        # collect all raster attributes in a list
        rasterAttributes = [rasterDir, rasterFilename, rasterxMin, 
                            rasterxMax, rasteryMin, rasteryMax, 
                            rasterzMin, rasterzMax, rasterUnit, 
                            rasterFormat, rasterBand, rasterWidth, 
                            rasterHeight, rasterCellsize, 
                            rasterpixelType, pyramids, SRname,
                            SRdatum, SRutmZone, prj]

        # concatenate list of raster attributes
        rasterValues = []
        for attribute in rasterAttributes:
            rasterValues.append(str(attribute))

        # create dictionary with index as key and attribute list as value
        rasterDict = {}
        rasterDict[i] = rasterValues
        return rasterDict

    # clean up failed attempts to create shapefile and calculate fields
    except:
        msg = str(rasterPath) + " didn't work for some reason"
        print (msg)  

# function that handles messages
def AddMsgAndPrint(msg, severity=0):
    try:
        for string in msg.split('\n'):
            if severity == 0:
                arcpy.AddMessage(string)
            elif severity == 1:
                arcpy.AddWarning(string)
            elif severity == 2:
                arcpy.AddError(string)
    except:
        pass

# function that sends jobs for processing
def SendForProcessing(rasterList, cpu):

    # create a pool to be populated with jobs
    pool = multiprocessing.Pool(processes=cpu)
    jobs = []
    rasterDict = {}

    # send for processing
    for i in range(0, len(rasterList)):
        rasterPath = rasterList[i]
        jobs.append(pool.apply_async(raster_attribute_list_gdal, args=(rasterPath, i)))
    msg = "queued " + str(len(rasterList)) + " rasters for processing with " + str(cpu) + " CPUs"
    AddMsgAndPrint(msg)

    # build dictionary output
    counter = 1
    for i in range(0, len(jobs)):
        try:
            output = jobs[i].get()
            if output == None:
                pass
            else:
                rasterDict.update(output)
                msg = "queried raster " + str(counter) + " of " + str(len(jobs))
                AddMsgAndPrint(msg)
        except:
            pass
        counter += 1

    # cleanup objects
    del pool, jobs, output

    # return output
    return rasterDict

def Write_Dict_To_Shapefile_osgeo():
    
    shapePath = str(outputFolder) + os.sep + str(shapefileName)

    # Get driver
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # Create shapeData
    os.chdir(outputFolder)
    if os.path.exists(shapefileName): 
        driver.DeleteDataSource(shapePath)
    shapeData = driver.CreateDataSource(shapefileName)
    
    # Create spatialReference for output
    outputspatialRef = osr.SpatialReference()
    # determine if input has more than one spatialReference
    srList = []
    for entry in rasterDict:
        srList.append(rasterDict[entry][-1])
    if len(set(srList)) == 1:
        outputspatialRef.ImportFromWkt(srList[0])
    else:
        outputspatialRef.ImportFromEPSG(3112)

    # Create layer
    layer = shapeData.CreateLayer(shapePath, srs=outputspatialRef, geom_type=ogr.wkbPolygon)

    # add fields   
    fieldNames = ["Path", "Filename", "Xmin", "Xmax", "Ymin", "yMax",
                  "Zmin", "Zmax", "Unit", "Format", "Bands", "Width",
                  "Height", "Cellsize", "PixelType", "Pyramids", "ProjName",
                  "ProjDatum", "ProjZone", "SRS"]
    for n in range(0, len(fieldNames)):

        # add short text fields
        if fieldNames[n] in ["Filename", "Unit", "Format", "PixelType", "Pyramids"]:
            fieldstring = str(fieldNames[n])
            field_name = ogr.FieldDefn(fieldstring, ogr.OFTString)
            field_name.SetWidth(24)
            layer.CreateField(field_name)

        # add long text fields
        elif fieldNames[n] in ["Path", "ProjName", "ProjDatum"]:
            fieldstring = str(fieldNames[n])
            field_name = ogr.FieldDefn(fieldstring, ogr.OFTString)
            field_name.SetWidth(254)
            layer.CreateField(field_name)

        # add floating-point fields
        elif fieldNames[n] in ["Xmin", "Xmax", "Ymin", "yMax", "Zmin", "Zmax",
                               "Bands", "Width", "Height", "Cellsize",
                               "ProjZone"]:
            fieldstring = str(fieldNames[n])
            field_name = ogr.FieldDefn(fieldstring, ogr.OFTReal)
            field_name.SetWidth(24)
            layer.CreateField(field_name)

        # don' write the whole projection string
        elif fieldNames[n] in ["SRS"]:
            pass

    # process each raster
    counter = 1
    for entry in rasterDict:
        values = list(rasterDict[entry])

        # Create spatialReference for each raster
        inputspatialRef = osr.SpatialReference()
        inputspatialRef.ImportFromWkt(values[-1])
        
        # Create polygon object
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(float(values[2]), float(values[4]))
        ring.AddPoint(float(values[2]), float(values[5]))
        ring.AddPoint(float(values[3]), float(values[5]))
        ring.AddPoint(float(values[3]), float(values[4]))
        ring.AddPoint(float(values[2]), float(values[4]))
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        # project polygon object to output spatial reference
        coordTrans = osr.CoordinateTransformation(inputspatialRef, outputspatialRef)
        poly.Transform(coordTrans)
        
        # Create feature
        layerDefinition = layer.GetLayerDefn()
        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(poly)
        feature.SetFID(entry)

        # calculate fields
        for n in range(0, len(values)):
            if fieldNames[n] in ["SRS"]:
                pass
            else:
                field = fieldNames[n]
                value = values[n]
                feature.SetField(field, value)
            
        # Save feature
        layer.CreateFeature(feature)
        # Cleanup
        poly.Destroy()
        feature.Destroy()

        # report progress
        if counter % 50 == 0:
            msg = "added raster " + str(counter) + " of " + str(len(rasterDict))
            AddMsgAndPrint(msg)
        counter += 1
    
    # Cleanup
    shapeData.Destroy()
    # Return
    return shapePath

# this is the part of the script that initialises variables and calls the above functions
if __name__ == '__main__':
    startTime = time.time()

    # define variables
    rasterDir = sys.argv[1]
    #rasterDir = r'D:\Temp'
    outputFolder = rasterDir
    shapefileName = r'RasterIndex.shp'
    searchSubdirectories = True
    
    #set number of processors to half unless only 1 processor
    if int(os.environ["NUMBER_OF_PROCESSORS"]) == 1:
        cpu = 1
    else:
        cpu = max([1, int(os.environ["NUMBER_OF_PROCESSORS"]) / 2])

    # execute function to create list of rasters
    rasterList = find_rasters(rasterDir, searchSubdirectories)

    # execute multiprocessing function to create raster attribute dictionary
    rasterDict = SendForProcessing(rasterList, cpu)

    # execute shapefile construction function
    Write_Dict_To_Shapefile_osgeo()

    finishTime = time.time()
    processingTime = str(int(finishTime - startTime))
    msg = "finished in " + str(processingTime) + " seconds"
    AddMsgAndPrint(msg)
