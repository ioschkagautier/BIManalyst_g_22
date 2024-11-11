About the tool - Use Case Analysis LCA on CO₂-eq for phases A1-A3, C3 and C4

**Problem Statement:**  
Currently, there is limited visibility into the Life Cycle Assessment (LCA) and CO₂ consumption of individual building components in BIM models. The available information does not include detailed CO₂ metrics or object data such as volume and mass, with only basic measurements and dimensions available. This tool is providing a visual display of the C02 embedment of the IFC Objects. Making the data accessible for design improvemnts. 

**Problem State:** 

-> Client Report CES_BLD_24_06 Page 29 - LCA (Slabs and Columns)

The issue was identified when we found no accessible CO₂ data to verify any claims made in the report. The available roughly defined materiality not including reinforcement Data nor concrete mixture does not provide adequate detail for quick LCA or CO₂ evaluation. 

**Tool Description:**  
Our tool provides a solution by tracking information from the BIM model and integrating it with actual material values as well as integrating assumptions on missing data, to create a comprehensive overview for LCA evaluation. This is done by implementing a preset LCA Excel table with values for materials used from the EPD-data base. The output is fed into a Speckle viewer, displaying data with a visual color overlay to indicate environmental impact. Each object in the model is clickable, showing its dimensions and corresponding CO₂ impact.

**Instructions to Run the Tool:**

1. **Preparation**  
   - Open the script.
   - Download the 3D IFC model and the provided Excel sheet for LCA data.

2. **Install Required Packages**  
   Run the following commands in the command prompt to install necessary libraries:
   ```
   pip install ifcopenshell
   pip install xlwings
   pip install specklepy
   pip install matplotlib
   ```

3. **Update File Paths**  
   - Replace the IFC model file path in the script:
     ifc_file = ifcopenshell.open('yourpath/ifc')

   - Replace the Excel sheet path in the script:
     wb = xw.Book('yourpath/LCA_Advanced_BIM_to_Python.xlsx')

     Connect Speckle Account 
     personal_access_token = your PAT
     stream_id = your Stream ID
     host = used server host

     Choose Method 1 or Method 2
     method = '1' (real GWP Values displayed)
     method = '2' (adjusted GWP Values by level penalty)

**Advanced Building Design**

**Tool Relevance in Advanced Building Design Stages**  
- **Stage:** The tool would be most useful in **Stage B** (Design) and **Stage C** (Detailing). These stages involve refining structural details and performing evaluations, including environmental impact assessments like LCA, making it an ideal time to integrate CO₂ tracking.

**Relevant Subjects for Tool Usage**  
- **Subjects:** This tool could be utilized in courses or subjects related to:
    PM - Project Manager (Evaluate CO2 / improved descision making based on early  LCA Feeback)

    STR - Structure (Desgin Improvment)

    Client - Simplified view on Project Data

**Required Information in the Model for Tool Functionality**  

Object Type must contain Material and Dimensions in Type_Name




