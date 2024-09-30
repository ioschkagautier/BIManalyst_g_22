import ifcopenshell
model = ifcopenshell.open('C:/Users/Lenovo/Desktop/CES_BLD_24_06_STR.ifc') #change to your location

slab = model.by_type('IfcSlab')
print(f"Slabs in model: {len(slab)}")