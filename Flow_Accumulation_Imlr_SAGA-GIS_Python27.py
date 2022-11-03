#! /usr/bin/env python

#_________________________________________
# Initialize the environment...

import os
from datetime import datetime

nSteps = 10          #number of Interpolation steps
SaveResultingGrids = False

gridsPath = 'E:/Conference2020/!!!!!SAGA_GIS_Imlr_Project_v.1.1/50m_grids_Surfer'
bottomGrid = gridsPath + os.sep + 'paleosurface_A_3D_outline.grd'
topGrid = gridsPath + os.sep + 'T3-T_50m_3D_outline_Surfer.grd'


if os.name == 'nt': # Windows
    if os.getenv('SAGA_PATH') is None: # in case you did not define a 'SAGA_PATH' environment variable pointing to your SAGA installation directory
        os.environ['SAGA_PATH'] = 'E:/Conference2020/!!!SAGA_gis_program/saga-7.8.0_src/saga-gis/bin'
    os.environ['PATH'     ] = os.environ['SAGA_PATH'] + os.sep +    ';' + os.environ['PATH']
    os.environ['PATH'     ] = os.environ['SAGA_PATH'] + os.sep + 'dll;' + os.environ['PATH']
    os.environ['PROJ_LIB' ] = os.environ['SAGA_PATH'] + os.sep + 'dll' + os.sep + 'proj-data'
    os.environ['GDAL-DATA'] = os.environ['SAGA_PATH'] + os.sep + 'dll' + os.sep + 'gdal-data'
    Dir_Tools = os.environ['SAGA_PATH'] + os.sep + 'tools'
else:               # Linux
    Dir_Tools = 'E:/Conference2020/!!!SAGA_gis_program/saga-7.8.0_src/saga-gis/bin/tools' # you might have to adjust this path to your system

import sys, saga_api


#_________________________________________
# Load the tools...
saga_api.SG_Get_History_Depth()        # History will not be created

saga_api.SG_UI_Msg_Lock(True) # avoid too much noise
saga_api.SG_Get_Tool_Library_Manager().Add_Directory(Dir_Tools, False)
if os.getenv('SAGA_TLB') is not None:
    saga_api.SG_Get_Tool_Library_Manager().Add_Directory(os.environ['SAGA_TLB'], False)
saga_api.SG_UI_Msg_Lock(False)

#_________________________________________
# Print versions and number of loaded tools...

print('Python - Version ' + sys.version)
print(saga_api.SAGA_API_Get_Version())
print('number of loaded libraries: ' + str(saga_api.SG_Get_Tool_Library_Manager().Get_Count()))
print()

#_________________________________________
##########################################
def GridCalculus(botGrd, topGrd, Step, Tool):
    #_____________________________________
    # Provide your input dataset(s), here -as example- load a dataset from file.
    # Using SAGA's central data manager instance for such jobs is an easy way to go...

    '''
    Data = saga_api.SG_Get_Data_Manager().Add(File)
    if Data == None or Data.is_Valid() == False:
        print('Failed to load dataset [' + File + ']')
        return False
    '''
    # bGrid = saga_api.SG_Get_Data_Manager().Add(botGrd)
    # tGrid = saga_api.SG_Get_Data_Manager().Add(topGrd)
    if botGrd == None or botGrd.is_Valid() == False or topGrd == None or topGrd.is_Valid() == False:
        print('Failed to load dataset [' + botGrd + '] or [' + topGrd + ']')
        return False

    #_____________________________________
    # Create a new instance of tool 'Grid Calculator'
    # Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    if Tool == None:
        print('Failed to create tool: Grid Calculator')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    formula = 'g1 + ' + str(Step) + ' * (g2 - g1)'
    print(formula)

    Tool.Set_Parameter('FORMULA', formula)          #'g1+0.162*(g2-g1)'
    #Tool.Set_Parameter('NAME', 'Calculation [(g1 - g2) / (g1 + g2)]')
    #Tool.Set_Parameter('FNAME', True)
    #Tool.Set_Parameter('USE_NODATA', False)
    Tool.Set_Parameter('TYPE', '4 byte floating point number')
    Tool.Get_Parameter('GRIDS').asGridList().Add_Item(botGrd)
    Tool.Get_Parameter('GRIDS').asGridList().Add_Item(topGrd)
    #Tool.Get_Parameter('GRIDS').asList().Add_Item(bGrid)

    #Tool.Get_Parameter('XGRIDS').asList().Add_Item('Grid input list, optional')


    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:
    Path = 'E:/Conference2020/!!!!!SAGA_GIS_Imlr_Project_v.1.1/SavedGrids/' + datetime.now().strftime('%Y-%m-%d_%H-%M') + '_GridCalculus_' + str(Step) + '.sg-grd-z'

    # Data = Tool.Get_Parameter('RESULT').asDataObject()
    gridCalculated = Tool.Get_Parameter('RESULT').asGrid()
    if SaveResultingGrids:
        gridCalculated.Save(Path)

    if Step == 1:
        #_____________________________________
        # remove this tool instance, if you don't need it anymore
        saga_api.SG_Get_Tool_Library_Manager().Delete_Tool(Tool)

        # job is done, free memory resources
        # saga_api.SG_Get_Data_Manager().Delete_All()

    return gridCalculated


#_________________________________________
##########################################
def FillSinks_Planchon(grid, Step, Tool):

    #_____________________________________
    # Create a new instance of tool 'Fill Sinks (Planchon/Darboux, 2001)'
    # Tool = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('ta_preprocessor', '3')
    if Tool == None:
        print('Failed to create tool: Fill Sinks (Planchon/Darboux, 2001)')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('DEM', grid)
    Tool.Set_Parameter('MINSLOPE', 0.010000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    #_____________________________________
    # Save results to file:
    Path = 'E:/Conference2020/!!!!!SAGA_GIS_Imlr_Project_v.1.1/SavedFillSinksGrids/' + datetime.now().strftime(
        '%Y-%m-%d_%H-%M') + '_FillSinks_' + str(Step) + '.sg-grd-z'

    gridFilledSinks = Tool.Get_Parameter('RESULT').asGrid()
    if SaveResultingGrids:
        gridFilledSinks.Save(Path)

    if Step == 1:
        #_____________________________________
        # remove this tool instance, if you don't need it anymore
        saga_api.SG_Get_Tool_Library_Manager().Delete_Tool(Tool)

        # job is done, free memory resources
        # saga_api.SG_Get_Data_Manager().Delete_All()


    return gridFilledSinks


#_________________________________________
##########################################
def TerrainMapView(grid, Step, Tool):

    if Tool == None:
        print('Failed to create tool: Terrain Map View')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('DEM', grid)
    Tool.Set_Parameter('SHADE', saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('METHOD', 'Topography')
    Tool.Set_Parameter('CONTOUR_LINES', False)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    # _____________________________________
    # Save results to file:
    Path = 'E:/Conference2020/!!!!!SAGA_GIS_Imlr_Project_v.1.1/SavedShadeGrids/' + datetime.now().strftime(
        '%Y-%m-%d_%H-%M') + '_ShadeGrid_' + str(Step) + '.sg-grd-z'

    gridShade = Tool.Get_Parameter('SHADE').asGrid()
    if SaveResultingGrids:
        gridShade.Save(Path)

    if Step == 1:
        # _____________________________________
        # remove this tool instance, if you don't need it anymore
        saga_api.SG_Get_Tool_Library_Manager().Delete_Tool(Tool)

        # job is done, free memory resources
        # saga_api.SG_Get_Data_Manager().Delete_All()

    return gridShade


#_________________________________________
##########################################
def FlowAccumulTopDown(grid, Step, Tool):

    #_____________________________________

    if Tool == None:
        print('Failed to create tool: Flow Accumulation (Top-Down)')
        return False

    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('ELEVATION', grid)
    Tool.Set_Parameter('STEP', 1)
    Tool.Set_Parameter('FLOW_UNIT', 'cell area')
    Tool.Set_Parameter('METHOD', 'Multiple Flow Direction')
    Tool.Set_Parameter('LINEAR_DO', False)
    Tool.Set_Parameter('CONVERGENCE', 1.100000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    # Save results to file:
    Path = 'E:/Conference2020/!!!!!SAGA_GIS_Imlr_Project_v.1.1/SavedFlowGrids/' + datetime.now().strftime(
        '%Y-%m-%d_%H-%M') + '_FlowGrids_' + str(Step) + '.sg-grd-z'

    flowGrid = Tool.Get_Parameter('FLOW').asGrid()
    if SaveResultingGrids:
        flowGrid.Save(Path)

    '''
    Data = Tool.Get_Parameter('VAL_MEAN').asDataObject()
    Data.Save(Path + Data.Get_Name() + '.sg-grd-z')

    Data = Tool.Get_Parameter('ACCU_TOTAL').asDataObject()
    Data.Save(Path + Data.Get_Name() + '.sg-grd-z')

    Data = Tool.Get_Parameter('ACCU_LEFT').asDataObject()
    Data.Save(Path + Data.Get_Name() + '.sg-grd-z')

    Data = Tool.Get_Parameter('ACCU_RIGHT').asDataObject()
    Data.Save(Path + Data.Get_Name() + '.sg-grd-z')

    Data = Tool.Get_Parameter('FLOW_LENGTH').asDataObject()
    Data.Save(Path + Data.Get_Name() + '.sg-grd-z')

    Data = Tool.Get_Parameter('WEIGHT_LOSS').asDataObject()
    Data.Save(Path + Data.Get_Name() + '.sg-grd-z')
    '''

    if Step == 1:
        #_____________________________________
        # remove this tool instance, if you don't need it anymore
        saga_api.SG_Get_Tool_Library_Manager().Delete_Tool(Tool)

        # job is done, free memory resources
        # saga_api.SG_Get_Data_Manager().Delete_All()

    return flowGrid


def ExportImages(fileName, flowGrid, shadeGrid, Step, Tool):


    if Tool == None:
        print('Failed to create tool: Export Image (bmp, jpg, pcx, png, tif)')
        return False

    Path = 'E:/Conference2020/!!!!!SAGA_GIS_Imlr_Project_v.1.1/ImagesFlowAccumulation/' + fileName + '_' + datetime.now().strftime(
        '%Y-%m-%d_%H-%M') + '_' + str(Step) + '.png'


    Tool.Get_Parameters().Reset_Grid_System()

    Tool.Set_Parameter('GRID', flowGrid)
    Tool.Set_Parameter('SHADE', shadeGrid)
    Tool.Set_Parameter('FILE', Path)
    # Tool.Set_Parameter('FILE_KML', False)
    Tool.Set_Parameter('NO_DATA', True)
    Tool.Set_Parameter('COLOURING', 'histogram stretch to standard deviation')
    Tool.Set_Parameter('GRADUATED', True)
    Tool.Set_Parameter('STDDEV', 2.000000)
    Tool.Set_Parameter('LINEAR.MIN', 0.000000)
    Tool.Set_Parameter('LINEAR.MAX', 100.000000)
    Tool.Set_Parameter('STRETCH.MIN', 0.000000)
    Tool.Set_Parameter('STRETCH.MAX', 100.000000)
    Tool.Set_Parameter('SCALE_MODE', 'increasing geometrical intervals')
    Tool.Set_Parameter('SCALE_LOG', 10.000000)
    # Tool.Set_Parameter('LUT', saga_api.SG_Create_Table('table.txt'))
    Tool.Set_Parameter('SHADE_TRANS', 85.000000)
    Tool.Set_Parameter('SHADE_COLOURING', 'Standard Deviation')
    Tool.Set_Parameter('SHADE_BRIGHT.MIN', 0.000000)
    Tool.Set_Parameter('SHADE_BRIGHT.MAX', 100.000000)
    Tool.Set_Parameter('SHADE_STDDEV', 2.000000)

    print('Executing tool: ' + Tool.Get_Name().c_str())
    if Tool.Execute() == False:
        print('failed')
        return False
    print('okay')

    if Step == 1:
        # _____________________________________
        # remove this tool instance, if you don't need it anymore
        saga_api.SG_Get_Tool_Library_Manager().Delete_Tool(Tool)

    return True


#_________________________________________
##########################################
if __name__ == '__main__':
    print('Usage: %s <in: filename>')
    print('This is a simple template for using a SAGA tool through Python.')
    print('Please edit the script to make it work properly before using it!')

    #____________________________________
    bGrid = saga_api.SG_Get_Data_Manager().Add(bottomGrid)
    tGrid = saga_api.SG_Get_Data_Manager().Add(topGrid)
    ToolGridCalculus = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_calculus', '1')
    ToolFillSinksPlanchon = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('ta_preprocessor', '3')
    # Create a new instance of tool 'Terrain Map View'
    ToolShade = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('grid_visualisation', '8')
    # Create a new instance of tool 'Flow Accumulation (Top-Down)'
    ToolTopDown = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('ta_hydrology', '0')
    # Create a new instance of tool 'Export Image (bmp, jpg, pcx, png, tif)'
    ToolExport = saga_api.SG_Get_Tool_Library_Manager().Create_Tool('io_grid_image', '0')

    nSteps = 1 + nSteps
    iStep = 1
    while iStep <= nSteps:
        currentStep = float(iStep) / float(nSteps)
        calculatedGrid = GridCalculus(bGrid, tGrid, currentStep, ToolGridCalculus)                       # Calculating new grid
        filledGrid = FillSinks_Planchon(calculatedGrid, currentStep, ToolFillSinksPlanchon)              # and fill depressions
        shadeGrid = TerrainMapView(filledGrid, currentStep, ToolShade)
        flowGrid = FlowAccumulTopDown(filledGrid, currentStep, ToolTopDown)
        ExportImages('A-T3_FlowAccumulation', flowGrid, shadeGrid, currentStep, ToolExport)
        iStep += 1
    saga_api.SG_Get_Data_Manager().Delete_All()
    sys.exit()

