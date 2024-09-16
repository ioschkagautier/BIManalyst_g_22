from collections import defaultdict
import ifcopenshell

# Function to check if the search number is in the level's name
def is_level_in_name(level_name, search_num):
    return search_num in level_name

# Open the IFC file
model = ifcopenshell.open('C:/Users/Lenovo/Desktop/CES_BLD_24_06_STR.ifc')  # Change to your location

# Retrieve all levels of type IfcBuildingStorey
levels = model.by_type('IfcBuildingStorey')

# Prompt the user to write the level they want to check
print('Please write the Level number you want to check (e.g., 2 for Level 2)')

# Get the user's input (e.g., "2")
desired_level_num = input()

# Find the specific level by checking if the number is in the level name
selected_level = None
for level in levels:
    if is_level_in_name(level.Name, desired_level_num):  # Check if the number is part of the level's name
        selected_level = level
        break

if selected_level is None:
    print(f"No level found containing '{desired_level_num}' in its name.")
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
        print(f'\nThere are {len(column_type_counts)} column types on the requested level.')
    elif len(column_type_counts) == 1:
        print("\nThere is a single column type on this level.")
    else:
        print("\nThere are no columns on this level.")