from collections import defaultdict
import ifcopenshell

# Function to retrieve columns on a specific level based on level number
def get_columns_on_level(model, desired_level_num):
    # Convert desired_level_num to string to match level name format (e.g., "2" for "Level 2")
    desired_level_num = str(desired_level_num)

    # Retrieve all levels of type IfcBuildingStorey
    levels = model.by_type('IfcBuildingStorey')

    # Function to check if the search number is in the level's name
    def is_level_in_name(level_name, search_num):
        return search_num in level_name

    # Find the specific level by checking if the number is in the level name
    selected_level = None
    for level in levels:
        if is_level_in_name(level.Name, desired_level_num):  # Check if the number is part of the level's name
            selected_level = level
            break

    if selected_level is None:
        print(f"No level found containing '{desired_level_num}' in its name.")
        return None

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
    print(f"\nSummary of Columns by ObjectType on level {desired_level_num}:")
    for object_type, count in column_type_counts.items():
        print(f"{count} columns of type '{object_type}'")

    # Check if there are multiple types of columns or just a single one
    if len(column_type_counts) > 1:
        print(f'\nThere are {len(column_type_counts)} column types on the level {desired_level_num}.')
    elif len(column_type_counts) == 1:
        print(f"\nThere is a single column type on level {desired_level_num}.")
    else:
        print(f"\nThere are no columns on level {desired_level_num}.")