<ids:ids xmlns:ids="http://standards.buildingsmart.org/IDS" xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <ids:info>
        <ids:title>Column and Slab Attribute Specification</ids:title>
        <ids:author>group22@example.com</ids:author>
        <ids:date>2024-11-11</ids:date>
        <ids:description>Specification for IfcColumn and IfcSlab elements, including Type Name, Volume, Material, and Level attributes.</ids:description>
    </ids:info>
    <ids:specifications>
        <!-- Specification for IfcColumn -->
        <ids:specification minOccurs="1" ifcVersion="IFC4" name="Column Attributes">
            <ids:applicability>
                <ids:entity>
                    <ids:name>IFCCOLUMN</ids:name>
                </ids:entity>
            </ids:applicability>
            <ids:requirements>
                <ids:propertySet>
                    <ids:name>ColumnAttributes</ids:name>
                    <ids:property>
                        <ids:name>TypeName</ids:name>
                        <ids:datatype>IfcLabel</ids:datatype>
                        <ids:value>Type Name of the Column Element</ids:value>
                    </ids:property>
                    <ids:property>
                        <ids:name>Volume</ids:name>
                        <ids:datatype>IfcVolumeMeasure</ids:datatype>
                        <ids:value>Calculated Volume of the Column</ids:value>
                    </ids:property>
                    <ids:property>
                        <ids:name>Material</ids:name>
                        <ids:datatype>IfcLabel</ids:datatype>
                        <ids:value>Material of the Column (e.g., Concrete C25/30)</ids:value>
                    </ids:property>
                    <ids:property>
                        <ids:name>Level</ids:name>
                        <ids:datatype>IfcLabel</ids:datatype>
                        <ids:value>Assigned Level in Building</ids:value>
                    </ids:property>
                </ids:propertySet>
            </ids:requirements>
        </ids:specification>

        <!-- Specification for IfcSlab -->
        <ids:specification minOccurs="1" ifcVersion="IFC4" name="Slab Attributes">
            <ids:applicability>
                <ids:entity>
                    <ids:name>IFCSLAB</ids:name>
                </ids:entity>
            </ids:applicability>
            <ids:requirements>
                <ids:propertySet>
                    <ids:name>SlabAttributes</ids:name>
                    <ids:property>
                        <ids:name>TypeName</ids:name>
                        <ids:datatype>IfcLabel</ids:datatype>
                        <ids:value>Type Name of the Slab Element</ids:value>
                    </ids:property>
                    <ids:property>
                        <ids:name>Volume</ids:name>
                        <ids:datatype>IfcVolumeMeasure</ids:datatype>
                        <ids:value>Calculated Volume of the Slab</ids:value>
                    </ids:property>
                    <ids:property>
                        <ids:name>Material</ids:name>
                        <ids:datatype>IfcLabel</ids:datatype>
                        <ids:value>Material of the Slab (e.g., Reinforced Concrete)</ids:value>
                    </ids:property>
                    <ids:property>
                        <ids:name>Level</ids:name>
                        <ids:datatype>IfcLabel</ids:datatype>
                        <ids:value>Assigned Level in Building</ids:value>
                    </ids:property>
                </ids:propertySet>
            </ids:requirements>
        </ids:specification>
    </ids:specifications>
</ids:ids>
