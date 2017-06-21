# -*- coding: utf-8 -*-
#import sys
#print(sys.version)
#import pip
#installed_packages = pip.get_installed_distributions()
#installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
#     for i in installed_packages])
#print(installed_packages_list)
import vtk

#help(vtk.vtkRectilinearGridReader())
#%gui qt
rectGridReader = vtk.vtkRectilinearGridReader()
rectGridReader.SetFileName("data/jet4_0.500.vtk")
# do not forget to call "Update()" at the end of the reader
rectGridReader.Update()
rectGridOutline = vtk.vtkRectilinearGridOutlineFilter()
rectGridOutline.SetInputData(rectGridReader.GetOutput())

# New vtkRectilinearGridGeometryFilter() goes here:
plane = vtk.vtkRectilinearGridGeometryFilter()
plane.SetInputData(rectGridReader.GetOutput())
plane.SetExtent(0, 128,0,150 , 0, 128) 

rectGridOutlineMapper = vtk.vtkPolyDataMapper()
rectGridOutlineMapper.SetInputConnection(rectGridOutline.GetOutputPort())

rectGridGeomMapper = vtk.vtkPolyDataMapper()
rectGridGeomMapper.SetInputConnection(plane.GetOutputPort())

outlineActor = vtk.vtkActor()
outlineActor.SetMapper(rectGridOutlineMapper)
outlineActor.GetProperty().SetRepresentationToWireframe()
outlineActor.GetProperty().SetColor(1, 1, 0.9)

gridGeomActor = vtk.vtkActor()
gridGeomActor.SetMapper(rectGridGeomMapper)
#gridGeomActor.GetProperty().SetRepresentationToWireframe()
gridGeomActor.GetProperty().SetColor(0.9, 0.6, 0.6)
# Find out how to visualize this as a wireframe 
#renderer = vtk.vtkRenderer()
#renderer.SetBackground(1, 1, 1)
#renderer.AddActor(outlineActor)
#renderer.AddActor(gridGeomActor)
#renderer.ResetCamera()

#renderWindow = vtk.vtkRenderWindow()
#renderWindow.AddRenderer(renderer)
#renderWindow.SetSize(700, 700)
#renderer.GetActiveCamera().Elevation(60.0)
#renderer.GetActiveCamera().Azimuth(30.0)
#renderer.GetActiveCamera().Zoom(1.0)
#renderWindow.Render()

#iren = vtk.vtkRenderWindowInteractor()
#iren.SetRenderWindow(renderWindow)
#iren.Start()
# Play with the options you get for setting up actor properties (color, opacity, etc.)
magnitudeCalcFilter = vtk.vtkArrayCalculator()
magnitudeCalcFilter.SetInputConnection(rectGridReader.GetOutputPort())
magnitudeCalcFilter.AddVectorArrayName('vectors')
# Set up here the array that is going to be used for the computation ('vectors')
magnitudeCalcFilter.SetResultArrayName('magnitude')
magnitudeCalcFilter.SetFunction("mag(vectors)")
# Set up here the function that calculates the magnitude of a vector
magnitudeCalcFilter.Update()

#Inspect the output of the calculator using the IPython console to verify the result
#Extract the data from the result of the vtkCalculator
points = vtk.vtkPoints()
grid = magnitudeCalcFilter.GetOutput()
grid.GetPoints(points)
scalars = grid.GetPointData().GetArray('magnitude')

#Create an unstructured grid that will contain the points and scalars data
ugrid = vtk.vtkUnstructuredGrid()
ugrid.SetPoints(points)
ugrid.GetPointData().SetScalars(scalars)

#Populate the cells in the unstructured grid using the output of the vtkCalculator
for i in range (0, grid.GetNumberOfCells()):
    cell = grid.GetCell(i)
    ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
lut2 = vtk.vtkLookupTable()
lut2.SetNumberOfColors(10)
lut2.SetHueRange(1, 0)
lut2.SetVectorModeToMagnitude()
lut2.Build()
#There are too many points, let's filter the points
subset = vtk.vtkMaskPoints()
subset.SetOnRatio(10)
subset.RandomModeOn()
subset.SetInputData(ugrid)

#Make a vtkPolyData with a vertex on each point.
pointsGlyph = vtk.vtkVertexGlyphFilter()
pointsGlyph.SetInputConnection(subset.GetOutputPort())
#pointsGlyph.SetInputData(ugrid)
pointsGlyph.Update()

plane = vtk.vtkRectilinearGridGeometryFilter()
plane.SetInputData(pointsGlyph.GetOutput())
plane.SetExtent(0, 128,0,150 , 0, 128) 
plane.Update()

pointsMapper = vtk.vtkPolyDataMapper()
pointsMapper.SetInputConnection(pointsGlyph.GetOutputPort())
pointsMapper.SetLookupTable(lut2)
pointsMapper.SetScalarModeToUsePointData()

pointsActor = vtk.vtkActor()
pointsActor.SetMapper(pointsMapper)
pointsActor.GetProperty().SetOpacity(1)

scalarRange = ugrid.GetPointData().GetScalars().GetRange()
lut = vtk.vtkLookupTable()
lut.SetNumberOfColors(256)
lut.SetHueRange(0.667, 0.3)
lut.SetVectorModeToMagnitude()
lut.Build()

isoFilter = vtk.vtkContourFilter()
isoFilter.SetInputData(ugrid)
isoFilter.GenerateValues(3, scalarRange)

isoMapper = vtk.vtkPolyDataMapper()
isoMapper.SetInputConnection(isoFilter.GetOutputPort())
isoMapper.SetLookupTable(lut)

isoActor = vtk.vtkActor()
isoActor.SetMapper(isoMapper)
isoActor.GetProperty().SetOpacity(1)

scalarRange = ugrid.GetPointData().GetScalars().GetRange()

isoFilter2 = vtk.vtkContourFilter()
isoFilter2.SetInputData(ugrid)
isoFilter2.GenerateValues(10, scalarRange)

isoMapper2 = vtk.vtkPolyDataMapper()
isoMapper2.SetInputConnection(isoFilter2.GetOutputPort())
isoMapper2.SetLookupTable(lut2)

isoActor2 = vtk.vtkActor()
isoActor2.SetMapper(isoMapper2)
isoActor2.GetProperty().SetOpacity(0.1)



hh = vtk.vtkHedgeHog()
hh.SetInputConnection(subset.GetOutputPort())
hh.SetScaleFactor(0.001)

hhm = vtk.vtkPolyDataMapper()
hhm.SetInputConnection(hh.GetOutputPort())
hhm.SetLookupTable(lut)
hhm.SetScalarVisibility(True)
hhm.SetScalarModeToUsePointFieldData()
hhm.SelectColorArray('vectors')
hhm.SetScalarRange((grid.GetPointData().GetVectors().GetRange(-1)))

hhActor = vtk.vtkActor()
hhActor.SetMapper(hhm)

#Option 1: Default vtk render window
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.6, 0.6, 0.6)
renderer.AddActor(outlineActor)
renderer.AddActor(isoActor)
renderer.AddActor(isoActor2)
#renderer.AddActor(gridGeomActor)
renderer.AddActor(pointsActor)
renderer.ResetCamera()

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(2000, 2000)
renderWindow.Render()

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renderWindow)
iren.Start()
