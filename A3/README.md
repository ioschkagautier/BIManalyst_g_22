About the tool - Use Case Analysis LCA on CO₂-eq for phases A1-A3, C3 and C4

**Problem Statement:**  
Currently, there is limited visibility into the Life Cycle Assessment (LCA) and CO₂-eq consumption of individual building components in BIM models. The available information does not include detailed CO₂ metrics, with sometimes even only basic object measurements and dimensions available. This tool is providing a visual display of the C02-eq embedment of the IFC Objects, making the data accessible accross disciplines for design improvemnts. 

**Problem State:** 

-> Client Report CES_BLD_24_06 Page 29 - LCA (Slabs and Columns)

The issue was identified when we found no accessible CO₂ data to verify any claims made in the report. The available roughly defined materiality not including reinforcement Data nor concrete mixture does not provide adequate detail for quick LCA or CO₂ evaluation. 

**Tool Description:**  
Our tool provides a solution by tracking information from the BIM model and integrating it with actual material values as well as integrating assumptions on missing data, to create a comprehensive overview for LCA evaluation. This is done by implementing a preset LCA Excel table with values for materials used from the EPD-data base. The unique column Types, identifyed by the Key(Type_name, height, level), get witten into excel where their materiality gets mapped directly to the EPD Data-base to extract the valid CO2 value for each material type. Since no information on reiinforcement was available within the IFC file an estimate of the amount of steel (Kg/m3) gets assigned to each column type. he CO2 data gets pulled back into python where the reinforcement co2 values get added on to the parent columns CO2 values resulting in a final value for each unique column type. The output is fed into a Speckle viewer, displaying data with a visual color overlay to indicate environmental impact. Each object in the model is clickable, showing its dimensions and corresponding CO₂ impact.

This tool contains an extra feature where the user can chose between two display methods for viewing the aquired Data in Speckle. 

   METHOD 1 is to display the true CO2 values for each object.
   
   METHOD 2 is to show adjusted CO2 values for each Object, where an adjustment factor has been added to take into account the increasing CO2 demand for the columns as floors are added. The logic of CO2 allocation, according to the representive level the column is assigned to, is as follows:

   level_allocation_factor = 1 - (average_gwp_top_level / average_gwp_level_0)
   level_allocation_factor_pr_level = level_allocation_factor/n
   adjustment_factor = (-(n - L) + L) * level_allocation_factor_pr_level 
   djusted_gwp = real_gwp + (real_gwp * adjustment_factor)

   Where n is the amount of storys excluding the ground floor and L is the individual columns assigned level.

**Instructions to Run the Tool:**

1. **Preparation**  
   - Open the script.
   - Download the IFC file and the provided Excel sheet for LCA data.

2. **Install Required Packages**  
   Run the following commands in the command prompt to install necessary libraries:
   ```
   pip install ifcopenshell
   pip install xlwings
   pip install specklepy
   pip install matplotlib
   ```

3. **Update File Paths**  
   - Replace the IFC file path in the script:
     ifc_file = ifcopenshell.open('yourpath/ifc')

   - Replace the Excel sheet file path in the script:
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




