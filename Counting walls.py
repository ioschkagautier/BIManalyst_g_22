import ifcopenshell
model = ifcopenshell.open('C:/Users/Lenovo/Desktop/CES_BLD_24_06_STR.ifc') #change to your location

walls = model.by_type('IfcWall')
print(f"Walls in model: {len(walls)}")