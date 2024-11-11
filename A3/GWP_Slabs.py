
#---------------Please intall in the command prompt before use---------------------------------------------------

'pip install ifcopenshell xlwings specklepy'

#---------------Imports-------------------------------------------------------------------------------------------

#Ifc part
import re
import ifcopenshell
import ifcopenshell.geom
#Excel part
import xlwings as xw
#Speckle part
from specklepy.api.client import SpeckleClient
from specklepy.objects.geometry import Mesh
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send

#--------------Please provide File paths and speckle data----------------------------------------------------------------

ifc_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc'
Excel_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/A2/LCA_Advanced_BIM_to_Python_slabs.xlsx'
personal_access_token = "e84c64a17e9103569a55ccb97e2f00526982240229"  # Replace this with your actual personal speckle access token (PAT)
stream_id = "2a3df00e3e"  # Your specified speckle stream ID
host = "app.speckle.systems" # Specify the correct server host (e.g., app.speckle.systems as default for viewer)

#-------------Parameters-------------------------------------------------------------------------------------------------

# Concrete strength for missing data
concrete_strength = " C25/30"  #C20/25 and C30/35 are also available, otherwise Excelfile needs to be updated in Data section
# Reinforcement densities
reinforcement_density_slab = 150  # kg/m³ for slabs, can be modified to any needs

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------






#-----------Not yours to worry about from here on!!! unless you wish to further understand and or improve the code:)---------------------------------------------------------------------------------


#------------------------------------Retrieve Slab Data from Ifc File---------------------------------------------------------------------
# Open the IFC file 
ifc_file = ifcopenshell.open(ifc_file_path)

# Function to extract material from the type name
def extract_material_from_type_name(type_name):
    if 'Concrete' in type_name:
        return 'Concrete'
    if 'Timber' in type_name:
        return 'Timber'
    if 'Steel' in type_name:
        return 'Steel'
    return 'Unknown'

# Function to extract thickness from type name
def extract_thickness_from_type_name(type_name):
    match = re.search(r'(\d+)mm', type_name)
    if match:
        return int(match.group(1))
    return None

# Process slabs and aggregate types/materials/dimensions
def process_slabs(slabs):
    slab_info_dict = {}

    for slab in slabs:
        try:
            # Get type name and material
            type_name = slab.ObjectType if hasattr(slab, 'ObjectType') else 'N/A'
            material = extract_material_from_type_name(type_name)
            
            # Skip slabs with unknown material
            if material == 'Unknown':
                continue
            
            # Append concrete strength
            material += concrete_strength

            # Extract thickness from type name
            thickness = extract_thickness_from_type_name(type_name)
            if thickness is None:
                continue  # Skip if no thickness is found

            # Convert thickness to meters and round height
            height = round(thickness / 1000, 3)  # Thickness in meters

            # Calculate volume (per m²) and round it to 5 digits
            volume = round(1 * 1 * height, 5)

            # Create a key for the slab
            key = (type_name, material, height)

            # Update count and volume in the dictionary
            if key in slab_info_dict:
                slab_info_dict[key]['count'] += 1
            else:
                slab_info_dict[key] = {
                    'count': 1,
                    'volume': volume,
                    'height': height,
                }

        except Exception as e:
            print(f"Error processing slab {type_name}: {e}")

    return slab_info_dict


#------------Add reinforcement data based on assumed parameter-------------------------------------------------------------------------

def add_reinforcement_info(info_dict):
    reinforcement_info = {}

    for (type_name, material, height), data in info_dict.items():
        if 'Concrete' in material:
            # Calculate reinforcement volume (in kg) based on element type
            reinforcement_volume = data['volume'] * reinforcement_density_slab

            # Create a new entry for reinforcement
            reinforcement_key = (type_name + '_Reinforcement', 'Reinforcement', height)
            
            # Check if the reinforcement type is already in the dictionary
            if reinforcement_key not in reinforcement_info:
                reinforcement_info[reinforcement_key] = {
                    'count': 1,  # Count is always 1 for reinforcement
                    'volume': round(reinforcement_volume,4)
                }

    # Merge reinforcement info into the original dictionary
    info_dict.update(reinforcement_info)
    return info_dict


#..............................................Excel...........................................................---------------------

# Write data to Excel Input sheet and update the sheet
def write_data_to_excel(info_dict, sheet):
    start_row = 14  # Start writing at row 14
    for row_index, ((type_name, material, height), data) in enumerate(info_dict.items(), start=start_row):
        # Include height in the type name for the Excel sheet
        sheet.range(f'A{row_index}').value = f"{type_name} - {material} (Height: {height}m)"  # Column A
        sheet.range(f'B{row_index}').value = material  # Column B
        sheet.range(f'D{row_index}').value = data['volume']  # Column D
        
        # Set count to 1 for reinforcement, otherwise use the original count
        count_value = 1 if 'Reinforcement' in type_name else data['count']
        sheet.range(f'E{row_index}').value = count_value  # Column E


# Retrieve GWP data from Excel for each type and print individually
def retrieve_gwp_from_excel(sheet, start_row, end_row):
    gwp_dict = {}

    # Read GWP values from column J, starting at row 14
    gwp_values = sheet.range(f'J{start_row}:J{end_row}').value  # Adjust range as necessary
    element_names = sheet.range(f'A{start_row}:A{end_row}').value  # Corresponding element names (types)

    # Store GWP in a dictionary
    for element_name, gwp in zip(element_names, gwp_values):
        if element_name:
            gwp_dict[element_name] = gwp

    return gwp_dict



#------------------------------------------------------------Call functions for Ifc to Excel part-------------------------------------------------------
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

# Retrieve all IfcSlab elements
slabs = ifc_file.by_type('IfcSlab')

# Process slabs and aggregate results
slab_info_dict = process_slabs(slabs)

# Add reinforcement information for concrete slabs
slab_info_dict = add_reinforcement_info(slab_info_dict)

# Open the workbook with xlwings
wb = xw.Book(Excel_file_path)

# Select the 'Input' sheet to write the data
input_sheet = wb.sheets['Input']

# Write data to the Input sheet
write_data_to_excel(slab_info_dict, input_sheet)

# Refresh and calculate the Excel file
wb.app.calculate()

# Save the Excel file
wb.save()

# Select the 'RESULTS' sheet to read GWP data
results_sheet = wb.sheets['RESULTS']

# Retrieve GWP data from Excel and match it with the element data
gwp_dict = retrieve_gwp_from_excel(results_sheet, start_row=14, end_row=100)



#-----------------------------------Add Reinforcement GWP to Parent GWP------------------------------------------------------------------------------

# Create a temporary dictionary to store GWP data for reinforcement types
reinforcement_gwp_dict = {}

# Add GWP to the reinforcement info
for (type_name, material, height), data in slab_info_dict.items():
    if 'Reinforcement' in type_name:
        input_key = f"{type_name} - {material} (Height: {height}m)"
        if input_key in gwp_dict:
            reinforcement_gwp_dict[input_key] = gwp_dict[input_key]

# Add GWP to the corresponding parent types
for (type_name, material, height), data in slab_info_dict.items():
    input_key = f"{type_name} - {material} (Height: {height}m)"
    if input_key in gwp_dict:
        data['GWP'] = gwp_dict[input_key]  # Match GWP based on the input key
    else:
        data['GWP'] = 'N/A'  # In case GWP is not found

    # If reinforcement GWP exists, add it to the parent GWP
    reinforcement_key = f"{type_name}_Reinforcement - Reinforcement (Height: {height}m)"
    if reinforcement_key in reinforcement_gwp_dict:
        data['GWP'] += reinforcement_gwp_dict[reinforcement_key]  # Add reinforcement GWP



#-------------------------------Normelization of GWP-values for colours------------------------------------------------------------

# Find the maximum GWP value for normalization (including reinforcement)
max_gwp = 0
for (type_name, material, height), data in slab_info_dict.items():
    if 'Reinforcement' not in type_name and data.get('GWP') != 'N/A':
        max_gwp = max(max_gwp, data['GWP'])  # Track the maximum GWP value

# List to store the type_name, height, and normalized GWP
gwp_data_list = []

# Iterate over the slabs and calculate GWP
for (type_name, material, height), data in slab_info_dict.items():
    if 'Reinforcement' not in type_name:  # Exclude reinforcement types
        real_gwp = data.get('GWP', 'N/A')
        
        # Normalize only if GWP is available and max_gwp is non-zero
        if real_gwp != 'N/A' and max_gwp != 0:
            normalized_gwp = round(real_gwp / max_gwp, 4)  # Normalized GWP
        else:
            normalized_gwp = 'N/A'  # Handle cases where normalization isn't possible
        
        # Append the type_name, height, and normalized GWP to the list
        gwp_data_list.append({
            'type_name': type_name,
            'height': height,
            'normalized_gwp': normalized_gwp,
            'real_gwp': real_gwp
        })


# Helper function to ensure the GWP value is a float
def ensure_float(value):
    # Check for common invalid values like 'N/A', None, or empty string
    if value in [None, 'N/A', '']:
        print(f"Warning: Invalid GWP value found: {value}")
        return None  # Return None for invalid values

    try:
        return float(value)  # Try to convert the value to a float
    except ValueError:
        print(f"Warning: Could not convert {value} to float.")  # Debugging message
        return None  # Return None if conversion fails
    


#---------------------------------Colour interpolation----------------------------------------------------------

# Interpolate color function: from green (low GWP) to yellow (medium GWP) to red (high GWP)
def interpolate_color(normalized_gwp):
    # Check if normalized_gwp is a valid number
    if isinstance(normalized_gwp, (int, float)):
        
        if normalized_gwp <= 0.5:
            # Interpolate between green and yellow
            green = 255
            red = int(255 * (normalized_gwp / 0.5))  # Gradually increase red as GWP approaches 0.5
            blue = 0
        else:
            # Interpolate between yellow and red
            red = 255
            green = int(255 * (1 - (normalized_gwp - 0.5) / 0.5))  # Gradually decrease green as GWP approaches 1
            blue = 0

        return (red, green, blue)  # Return the interpolated RGB color
    else:
        # Return a default color (e.g., white) if normalized_gwp is not a valid number
        return (255, 255, 255)

# Apply the color gradient to each entry in gwp_data_list based on the normalized GWP value
gwp_data_with_colors = []


#Append colour value to GWP data list
for entry in gwp_data_list:
    type_name = entry.get('type_name', 'Unknown')  # Get the type name or use 'Unknown' if missing
    height = entry.get('height', 'Unknown')  # Get the height or use 'Unknown' if missing
    normalized_gwp = ensure_float(entry.get('normalized_gwp'))  # Ensure the normalized GWP value is converted to float
    real_gwp = ensure_float(entry.get('real_gwp')) # Ensure the real GWP value is converted to float
    
    # Only assign colors if GWP is a valid number
    if normalized_gwp is not None:
        color = interpolate_color(normalized_gwp)
    else:
        color = (255, 255, 255)  # Default to white if GWP is not available or invalid

    # Append the data along with the color to the new list
    gwp_data_with_colors.append((type_name, height, normalized_gwp, real_gwp, color))


# Check: Print the data with colors
for type_name, height, normalized_gwp, real_gwp, color in gwp_data_with_colors:
    print(f"Type: {type_name}, Height: {height}m, Normalized GWP: {normalized_gwp}, Real GWP: {real_gwp}, Color: {color}")



#-----------------------------Prepare Speckle colours---------------------------------------------------------------------------------------

# gwp_data_with_colors is expected to be structured as [(type_name, height, normalized_gwp, real_gwp, color)]
predefined_colors = {
    (item[0], item[1]): item[4] for item in gwp_data_with_colors  # starting from index 0, item[4] should be an RGB tuple
}

# Convert gwp_data_with_colors to a dictionary to look up real_gwp by (type_name, height)
gwp_lookup = {
    (item[0], item[1]): item[3] for item in gwp_data_with_colors  # item[3] is the real_gwp
}

# Helper function to convert RGB to hexadecimal for Speckle compatibility
def rgb_to_hex(rgb):
    return (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]


#------------------------------Create speckle Geometry------------------------------------------------------------------------------------

# 1. Open the IFC file
ifc_file = ifcopenshell.open(ifc_file_path)

# 2. Extract all slabs
slabs = ifc_file.by_type("IfcSlab")
if len(slabs) == 0:
    raise Exception("No Slabs found in the IFC file.")

# 3. Define a scaling factor to convert from millimeters to meters, Speckle viewer expects dimensions in m
scale_factor = 0.001  # Convert from mm to m

# Function to calculate bounding box dimensions
def calculate_bounding_box(vertices):
    if not vertices or not isinstance(vertices, (tuple, list)):
        return None, None, None

    # Convert vertices from tuple to a list of (x, y, z) tuples
    vertices_list = [(vertices[i], vertices[i + 1], vertices[i + 2]) for i in range(0, len(vertices), 3)]

    # Extract x, y, z values from the vertices
    x_values = [v[0] for v in vertices_list]
    y_values = [v[1] for v in vertices_list]
    z_values = [v[2] for v in vertices_list]

    # Get minimum and maximum values for each axis
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    min_z, max_z = min(z_values), max(z_values)

    # Calculate the bounding box dimensions in meters
    length = (max_x - min_x) * scale_factor
    width = (max_y - min_y) * scale_factor
    height = (max_z - min_z) * scale_factor

    return length, width, height


# 4. Create a main Base object to hold all slabs
speckle_slabs = Base()

# Loop over all slabs and apply color, scaling, and placement adjustments
for slab in slabs:
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, slab)

    vertices = shape.geometry.verts
    faces = shape.geometry.faces

    if not vertices or not faces:
        print(f"No valid geometry found for slab: {slab.Name}")
        continue

    # Calculate bounding box dimensions
    length, width, height = calculate_bounding_box(vertices)

    # Retrieve the IfcLevel information (IfcBuildingStorey) for elevation
    elevation = 0  # Default to zero if level data is missing
    if hasattr(slab, 'ContainedInStructure') and slab.ContainedInStructure:
        level = slab.ContainedInStructure[0] if slab.ContainedInStructure else None
        if level:
            level_object = level.RelatingStructure
            elevation = getattr(level_object, 'Elevation', 0) * scale_factor  # Convert elevation to meters
        else:
            print(f"Warning: No IfcLevel found for slab: {slab.Name}, defaulting elevation to 0")
   

    # Try to retrieve height from OverallThickness or from the type name using regex
    height = getattr(slab, 'OverallThickness', None)
    type_name = getattr(slab, 'ObjectType', slab.Name or "Unnamed")
    if height is None:
        match = re.search(r'(\d+)mm', type_name, re.IGNORECASE)
        if match:
            height = int(match.group(1)) / 1000  # Convert matched height from mm to m
        else:
            height = 'N/A'

    # Assign color based on type_name and height using gwp_data_with_colors, default to white if not found
    key = (type_name, height)
    slab_color_rgb = predefined_colors.get(key, (255, 255, 255))  # Default color is white (255, 255, 255)
    slab_color_hex = rgb_to_hex(slab_color_rgb)

    # Lookup the real GWP value from gwp_data_with_colors
    real_gwp = gwp_lookup.get(key, 'N/A')

    # Adjust vertices based on the elevation of the IfcLevel and apply scale factor
    scaled_vertices = [
        vertices[i] * scale_factor if i % 3 != 2 else (vertices[i] + elevation) * scale_factor
        for i in range(len(vertices))
    ]

    # Format the faces for Speckle
    formatted_faces = [item for i in range(0, len(faces), 3) for item in (3, faces[i], faces[i + 1], faces[i + 2])]

    # Create a mesh for Speckle with the correct color and height information
    speckle_mesh = Mesh(
        name=f"IFC Slab - {slab.Name}",
        vertices=scaled_vertices,
        faces=formatted_faces,
        colors=[slab_color_hex] * (len(scaled_vertices) // 3)  # Apply the same color to all vertices
    )
    
    # Add Attributes visible in Speckle Selection viewer for selected object
    speckle_mesh['length'] = length
    speckle_mesh['width'] = width
    speckle_mesh['height'] = height
    speckle_mesh['elevation'] = elevation
    speckle_mesh['real_gwp'] = f'{real_gwp} [kg CO2-eq / m2]' 

    # Create a base object for Speckle and add its attributes
    slab_object = Base()
    slab_object['mesh'] = speckle_mesh
    slab_object['guid'] = slab.GlobalId or "No GUID"
    slab_object['name'] = slab.Name or "Unnamed Slab"
    slab_object['ifc_type'] = slab.is_a()
    slab_object['object_type'] = type_name
    slab_object['real_gwp'] = f'{real_gwp} [kg CO2-eq / m2]' 

    # Add to collection
    speckle_slabs[f'slab_{slab.GlobalId}'] = slab_object

#--------------Send Objects to Speckle viewer---------------------------------------------------------------------------

# Specify the correct server host
client = SpeckleClient(host)  # Specify the correct server host (e.g., app.speckle.systems)

# Authenticate with the token
client.authenticate_with_token(personal_access_token)

# Set up transport to the stream
transport = ServerTransport(client=client, stream_id=stream_id)

# Send all slabs as one object to Speckle
object_id = send(base=speckle_slabs, transports=[transport])
print(f"All slabs with colors and GWP values sent to Speckle with object ID: {object_id}")

# Print the Speckle viewer URL to view the object
print(f"View it at: https://{host}/streams/{stream_id}/objects/{object_id}")
