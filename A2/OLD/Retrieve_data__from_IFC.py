from collections import defaultdict
import ifcopenshell
import re


# Open the IFC file
ifc_file = ifcopenshell.open('C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc')


# Retrieve all IfcColumn elements
columns = ifc_file.by_type('IfcColumn')

# Print information about each column
#for column in columns:
    #print(f"Column ID: {column.id()}, Name: {column.Material}")




# Function to extract material from the type name
def extract_material_from_type_name(type_name):
    if 'Concrete' in type_name:
        return 'Concrete'
    if 'Timber' in type_name:
        return 'Timber'
    if 'Steel' in type_name:
        return 'Steel'
    # Add more conditions if there are other materials
    return 'Unknown'

# Function to extract dimensions from the type name
def extract_dimensions_from_type_name(type_name):
    match = re.search(r'(\d+)x(\d+)', type_name)
    if match:
        width = match.group(1)
        depth = match.group(2)
        return width, depth
    return 'N/A', 'N/A'

# Function to print specific attributes of an IfcColumn
def print_column_attributes(column):
    global_id = column.GlobalId
    type_name = column.ObjectType if hasattr(column, 'ObjectType') else 'N/A'
    material = extract_material_from_type_name(type_name)
    width, depth = extract_dimensions_from_type_name(type_name)
    volume = column.Volume if hasattr(column, 'Volume') else 'N/A'
    height = column.OverallHeight if hasattr(column, 'OverallHeight') else 'N/A'
    
    print(f"GlobalId: {global_id}")
    print(f"Material: {material}")
    print(f"Volume: {volume}")
    print(f"Height: {height}")
    print(f"Dimensions (Width x Depth): {width} x {depth}")
    print(f"Type: {type_name}")
    print('-' * 40)

# Print attributes for each column
for column in columns:
    print_column_attributes(column)

