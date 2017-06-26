import vtk

#------------READER ----------------------
rectGridReader = vtk.vtkXMLImageDataReader()
rectGridReader.SetFileName("../data/wind_image.vti")
rectGridReader.Update()
#------------END READER ------------------
print(rectGridReader.GetOutput())
#------------ FILTER: CALCULATE VECTOR MAGNITUDE ----------------------
magnitudeCalcFilter = vtk.vtkArrayCalculator()
magnitudeCalcFilter.SetInputConnection(rectGridReader.GetOutputPort())
magnitudeCalcFilter.AddVectorArrayName('wind_velocity')
magnitudeCalcFilter.SetResultArrayName('magnitude')
magnitudeCalcFilter.SetFunction("mag(wind_velocity)")
magnitudeCalcFilter.Update()
#------------END CALCULATE VECTOR MAGNITUDE ----------------------

#------------FILTER: RECTILINEAR GRID TO IMAGE DATA-----------
bounds = magnitudeCalcFilter.GetOutput().GetBounds()
dimensions = magnitudeCalcFilter.GetOutput().GetDimensions()
origin = (bounds[0], bounds[2], bounds[4])
spacing = ( (bounds[1]-bounds[0])/dimensions[0], 
            (bounds[3]-bounds[2])/dimensions[1],
            (bounds[5]-bounds[4])/dimensions[2])

imageData = vtk.vtkImageData()
imageData.SetOrigin(origin)
imageData.SetDimensions(dimensions)
imageData.SetSpacing(spacing)

probeFilter = vtk.vtkProbeFilter()
probeFilter.SetInputData(imageData)
probeFilter.SetSourceData(magnitudeCalcFilter.GetOutput())
probeFilter.Update()

imageData2 = probeFilter.GetImageDataOutput()
#------------END RECTILINEAR GRID TO IMAGE DATA-----------

##------------FILTER, MAPPER, AND ACTOR: VOLUME RENDERING -------------------

# Create transfer mapping scalar value to opacity
opacityTransferFunction = vtk.vtkPiecewiseFunction()
def funcColor(d,n):
    return 1-((d-n)/10)
# Create transfer mapping scalar value to color
colorTransferFunction = vtk.vtkColorTransferFunction()
for x in range(0,500):
    d = x/10
    print(d)
    opacityTransferFunction.AddPoint(d, d/500)
    if(d <= 10):
        colorTransferFunction.AddRGBPoint(d,0.0, 0.0, funcColor(d,0))
    elif (d <= 20):
        colorTransferFunction.AddRGBPoint(d, 0.0, funcColor(d,10), 1.0)
    elif(d<=30):
        colorTransferFunction.AddRGBPoint(d,0.0, funcColor(d,20), 0.0)
    elif(d<=40):
        colorTransferFunction.AddRGBPoint(d,1.0, funcColor(d,30), 0.0)
    elif (d <= 50):
        colorTransferFunction.AddRGBPoint(d, funcColor(d,40), 0.0, 0.0)




# The property describes how the data will look
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.ShadeOff()
volumeProperty.SetInterpolationTypeToLinear()


# The mapper / ray cast function know how to render the data
#volumeMapper = vtk.vtkProjectedTetrahedraMapper()
#volumeMapper = vtk.vtkUnstructuredGridVolumeZSweepMapper()
volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
#volumeMapper = vtk.vtkUnstructuredGridVolumeRayCastMapper()
volumeMapper.SetInputData(imageData2)

# The volume holds the mapper and the property and
# can be used to position/orient the volume
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

##------------END VOLUME RENDERING ----------------------

#---------RENDERER, RENDER WINDOW, AND INTERACTOR ----------
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.5, 0.5, 0.5)
renderer.AddVolume(volume)
renderer.ResetCamera()

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(500, 500)
renderWindow.Render()

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renderWindow)
iren.Start()
#---------END RENDERER, RENDER WINDOW, AND INTERACTOR -------