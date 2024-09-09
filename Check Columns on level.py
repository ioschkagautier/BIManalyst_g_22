#Introduction: Type the desired Level name in the console when asked to do so in this format: Level 4

from collections import defaultdict
import ifcopenshell
model = ifcopenshell.open('C:/Users/Lenovo/Desktop/CES_BLD_24_06_STR.ifc') #change to your location

levels = model.by_type('IfcBuildingStorey') # this is the ifc object which we extract attributes from, # Retrieve all levels of type IfcBuildingStorey

print('Please write the Level you want to check')

# Example: Retrieve level by its Name attribute
desired_level_name = input() #input level Name: Level 2 # Specify the level name you want to retrieve

# Find the specific level
selected_level = None
for level in levels:
    if level.Name == desired_level_name:  # or use level.GlobalId == "SomeId"
        selected_level = level
        break


if selected_level is None:
    print(f"No level found with name {desired_level_name}.")
else:
    # Retrieve all elements on the specific level
    elements_on_level = [rel.RelatedElements for rel in selected_level.ContainsElements]
    
    # Flatten the list of elements
    elements_on_level = [item for sublist in elements_on_level for item in sublist]
    
    # Filter only IfcColumn elements
    columns_on_level = [element for element in elements_on_level if element.is_a("IfcColumn")]
    
    # Dictionary to store counts of columns by their ObjectType
    column_type_counts = defaultdict(int)

    # Extract ObjectType for each column and count types
    for column in columns_on_level:
        object_type = column.ObjectType if column.ObjectType else "Undefined"  # Handle None or undefined ObjectType
        column_type_counts[object_type] += 1

    # Print the summary of column ObjectTypes and their counts
    print("\nSummary of Columns by ObjectType on Level:")
    for object_type, count in column_type_counts.items():
        print(f"{count} columns of type '{object_type}'")

  # Check if there are multiple types of columns or just a single one
    if len(column_type_counts) > 1:
        print("\nThere are multiple column types on this level.")
    elif len(column_type_counts) == 1:
        print("\nThere is a single column type on this level.")
    else:
        print("\nThere are no columns on this level.")
