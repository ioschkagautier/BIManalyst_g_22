import ifcopenshell
import ifcopenshell.geom
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects.geometry import Mesh
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send
import random

# Define a scaling factor to convert from millimeters to meters
scale_factor = 0.001  # Convert from mm to m

# Function to generate a random color in hexadecimal format
def generate_random_color():
    return int(f'{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}', 16)

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

# 1. Open the IFC file
ifc_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc'
ifc_file = ifcopenshell.open(ifc_file_path)

# 2. Extract only slabs with PredefinedType FLOOR
floor_slabs = [slab for slab in ifc_file.by_type("IfcSlab") if slab.PredefinedType == "FLOOR"]
if len(floor_slabs) == 0:
    raise Exception("No floor slabs found in the IFC file.")

# 3. Dictionary to hold unique colors for each combination of ObjectType 
type_colors = {}

# 4. Create a main Base object to hold all floor slabs
speckle_slabs = Base()

# Function to calculate the absolute placement in Z direction
def get_absolute_z_offset(placement):
    if placement is None:
        return 0
    # Start with the local Z offset
    z_offset = placement.RelativePlacement.Location.Coordinates[2]
    # If there's a PlacementRelTo, recursively add its offset
    if hasattr(placement, 'PlacementRelTo') and placement.PlacementRelTo:
        z_offset += get_absolute_z_offset(placement.PlacementRelTo)
    return z_offset

# 5. Loop over all floor slabs and extract geometry, applying color based on ObjectType
for slab in floor_slabs:
    settings = ifcopenshell.geom.settings()  # Default settings for geometry extraction
    shape = ifcopenshell.geom.create_shape(settings, slab)  # Extract geometry

    # Get the geometry vertices and faces
    vertices = shape.geometry.verts
    faces = shape.geometry.faces

    if not vertices or not faces:
        print(f"No valid geometry found for slab: {slab.Name}")
        continue  # Skip if no valid geometry found

    # Calculate bounding box dimensions to determine height
    dimensions = calculate_bounding_box(vertices)
    if dimensions is None:
        print(f"Could not calculate dimensions for slab: {slab.Name}")
        continue

    length, width, height = dimensions

    # Get the slab's absolute placement elevation (Z-coordinate) using the recursive function
    placement = slab.ObjectPlacement
    z_offset = get_absolute_z_offset(placement) * scale_factor  # Convert Z offset to meters

    # Apply the Z offset to all vertices and convert to meters
    adjusted_vertices = []
    for i in range(0, len(vertices), 3):
        adjusted_vertices.extend([
            vertices[i] * scale_factor,               # X-coordinate in meters
            vertices[i + 1] * scale_factor,           # Y-coordinate in meters
            (vertices[i + 2] + z_offset) * scale_factor  # Z-coordinate in meters with offset
        ])

    # Get ObjectType (or a fallback if not available)
    object_type = getattr(slab, 'ObjectType', None)
    if not object_type:
        object_type = slab.Name if slab.Name else "Unnamed"

    # Create a unique key based on ObjectType 
    key = (object_type)

    # Assign a unique color for each key if it doesn't already exist
    if key not in type_colors:
        type_colors[key] = generate_random_color()  # Assign a random color for each unique key

    # Format the faces for Speckle
    formatted_faces = []
    for i in range(0, len(faces), 3):
        formatted_faces.extend([3, faces[i], faces[i + 1], faces[i + 2]])

    # Create a Mesh for this slab
    speckle_mesh = Mesh(
        name=f"IFC Floor Slab - {slab.Name}",
        vertices=adjusted_vertices,
        faces=formatted_faces
    )

    # Apply the color to the mesh
    speckle_mesh.colors = [type_colors[key]] * (len(adjusted_vertices) // 3)  # Same color for all vertices

    # Assign other attributes (like height) if needed
    speckle_mesh['height'] = height*1000  # Add height as a direct attribute in meters

    # Create a Speckle Base object for the slab, which includes the mesh and GUID
    slab_object = Base()
    slab_object['mesh'] = speckle_mesh
    slab_object['guid'] = slab.GlobalId if slab.GlobalId else "No GUID"
    slab_object['name'] = slab.Name if slab.Name else "Unnamed Floor Slab"
    slab_object['ifc_type'] = slab.is_a()  # e.g., IfcSlab
    slab_object['height'] = height*1000  # Add height to the slab object in meters
    slab_object['object_type'] = object_type  # Add ObjectType to the slab object

    # Add this slab object to the main collection of slabs
    speckle_slabs[f'slab_{slab.GlobalId}'] = slab_object

# 6. Authenticate with your Speckle account using a Personal Access Token (PAT)
client = SpeckleClient(host="app.speckle.systems")  # Make sure to specify the correct server host (e.g., app.speckle.systems)

# Replace this with your actual personal access token (PAT) #could also use default account method
personal_access_token = "e84c64a17e9103569a55ccb97e2f00526982240229"  

# Authenticate with the token
client.authenticate_with_token(personal_access_token)

# 7. Set up transport to the stream
stream_id = "2a3df00e3e"  # Your specified stream ID
transport = ServerTransport(client=client, stream_id=stream_id)

# 8. Send all floor slabs as one object to Speckle
object_id = send(base=speckle_slabs, transports=[transport])
print(f"All floor slabs with colors sent to Speckle with object ID: {object_id}")

# 9. Print the Speckle viewer URL to view the object
print(f"View it at: https://app.speckle.systems/streams/{stream_id}/objects/{object_id}")
