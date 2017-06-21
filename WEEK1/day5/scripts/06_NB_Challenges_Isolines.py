import vtk

# Read the file (to test that it was written correctly)
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName("../data/challenge_2.vti")
reader.Update()
print(reader.GetOutput())
# Convert the image to a polydata
imageDataGeometryFilter = vtk.vtkImageDataGeometryFilter()
imageDataGeometryFilter.SetInputConnection(reader.GetOutputPort())
imageDataGeometryFilter.Update()

scalarRange = reader.GetOutput().GetPointData().GetScalars().GetRange(-1)
contoursFilter = vtk.vtkContourFilter()
contoursFilter.SetInputConnection(imageDataGeometryFilter.GetOutputPort())
contoursFilter.GenerateValues(6, scalarRange)

contoursMapper = vtk.vtkPolyDataMapper()
contoursMapper.SetInputConnection(contoursFilter.GetOutputPort())
contoursMapper.SetColorModeToMapScalars()
contoursMapper.ScalarVisibilityOn()
contoursMapper.SelectColorArray("JPEGImage")
contoursMapper.SetScalarRange(scalarRange)

contoursActor = vtk.vtkActor()
contoursActor.SetMapper(contoursMapper)

actor = vtk.vtkActor()
actor.SetMapper(contoursMapper)
 
# Setup rendering
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(1,1,1)
renderer.ResetCamera()
 
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
 
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
 
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.Start()

