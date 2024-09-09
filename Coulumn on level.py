import ifcopenshell
model = ifcopenshell.open('C:/Users/Lenovo/Desktop/CES_BLD_24_06_STR.ifc') #change to your location

#level = ('5')l

levels = model.by_type('IfcBuildingStorey') # this is the ifc object which we extract attributes from

for level in levels:
    name = level.Name  # Get the name of the storey (Extract the Name attribute)
    elevation = level.Elevation  # Get the elevation of the storey (Extract the Elevation attribute)
    print(f"Storey: {name}, Elevation: {elevation}")