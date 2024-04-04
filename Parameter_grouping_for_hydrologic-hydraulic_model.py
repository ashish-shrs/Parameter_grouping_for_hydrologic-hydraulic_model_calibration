# Author: Ashish Shrestha
# Date: March, 2024
# Purpose: Function to group sub-catchments based on publicly LULC (raster) and soil types (vector) data,
# using example of Flagstaff SWMM model's subcatchments

import arcpy
import string

# Part A: For sub-catchments
# Creating a function...(function begins)...
def parameter_grouping_for_subcatchments(path_to_folder, subcatchments, lulc, soiltypes):
    arcpy.env.workspace = path_to_folder
    arcpy.env.overwriteOutput = True

    out_table = "zon_stat.dbf"  #Zonal statistics table for LULC
    target_features = "Subcatchments_example.shp"  #Target polygon feature for spatial join
    out_feature_class = "Subcat_FL_polygon.shp"  #Output for extracted data

    # Running "Zonal statistics to table" using LULC to sub-catchments layer
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data = subcatchments,
        zone_field = "FID",
        in_value_raster = lulc,
        out_table = out_table,
        statistics_type = "MAJORITY",
        ignore_nodata = "DATA"
    )
    
    fields = arcpy.ListFields(out_table)
    first_colname = fields[0].name if fields else None

    # Running "Spatial join" using soil types to sub-catchments layer
    arcpy.analysis.SpatialJoin(
        target_features = target_features,
        join_features = soiltypes,
        out_feature_class = out_feature_class,
        join_operation = "JOIN_ONE_TO_ONE",
        join_type = "KEEP_ALL",
        field_mapping = 'ANSICODE "ANSICODE" true true false 8 Text 0 0,First,#,Polygon1,ANSICODE,0,7;AREAID "AREAID" true true false 22 Text 0 0,First,#,Polygon1,AREAID,0,21;FULLNAME "FULLNAME" true true false 100 Text 0 0,First,#,Polygon1,FULLNAME,0,99;MTFCC "MTFCC" true true false 5 Text 0 0,First,#,Polygon1,MTFCC,0,4;ALAND "ALAND" true true false 8 Double 0 0,First,#,Polygon1,ALAND,-1,-1;AWATER "AWATER" true true false 8 Double 0 0,First,#,Polygon1,AWATER,-1,-1;INTPTLAT "INTPTLAT" true true false 11 Text 0 0,First,#,Polygon1,INTPTLAT,0,10;INTPTLON "INTPTLON" true true false 12 Text 0 0,First,#,Polygon1,INTPTLON,0,11;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,Polygon1,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,Polygon1,Shape_Area,-1,-1;AREASYMBOL "AREASYMBOL" true true false 20 Text 0 0,First,#,soilmu_a_aoi,AREASYMBOL,0,19;SPATIALVER "SPATIALVER" true true false 10 Long 0 10,First,#,soilmu_a_aoi,SPATIALVER,-1,-1;MUSYM "MUSYM" true true false 6 Text 0 0,First,#,soilmu_a_aoi,MUSYM,0,5;MUKEY "MUKEY" true true false 30 Text 0 0,First,#,soilmu_a_aoi,MUKEY,0,29',
        match_option = "LARGEST_OVERLAP"
    )

    # Running "Join field" using table generated above and to the sub-catchments layer
    arcpy.management.JoinField(
        in_data = out_feature_class,
        in_field = "FID",
        join_table = out_table,
        join_field = first_colname,
        fields = "MAJORITY",
        fm_option = "NOT_USE_FM",
        field_mapping = None,
        index_join_fields = "NO_INDEXES"
    )

    # If you want o see unique values in "MUSYM" and "MAJORITY"
    musym_values = set(row[0] for row in arcpy.da.SearchCursor(out_feature_class, "MUSYM"))
    for value in musym_values:
        print(f"Unique value of - MUSYM: {value}")
    majority_values = set(row[0] for row in arcpy.da.SearchCursor(out_feature_class, "MAJORITY"))
    for value in majority_values:
        print(f"Unique value of - MAJORITY: {value}")

    # Adding new field called "Category"
    arcpy.AddField_management(out_feature_class, "Category", "TEXT")
    with arcpy.da.UpdateCursor(out_feature_class, ["MUSYM", "MAJORITY", "Category"]) as mat:
        for row in mat:
            musym, majority, category = row[0], int(row[1]), None 
            # Criterias
            if musym in ["2", "11", "2A", "2B"] and majority == 24:
                category = "A"
            elif musym in ["2","11", "2A", "2B"] and majority in [22, 23]:
                category = "B"
            elif musym in ["2", "11", "2A", "2B"] and majority in [21, 52, 42, 0, 71, 95]:
                category = "C"
            elif musym in ["1", "12", "18", "15A", "15"] and majority == 24:
                category = "D"
            elif musym in ["1", "12", "18", "15A", "15"] and majority in [22, 23]:
                category = "E"
            elif musym in ["1", "12", "18", "15A", "15"] and majority in [21, 52, 42, 0, 71, 95]:
                category = "F"
            elif musym == "13" and majority == 24:
                category = "G"
            elif musym == "13" and majority in [22, 23]:
                category = "H"
            elif musym == "13" and majority in [21, 52, 42, 0, 71, 95]:
                category = "I"
            elif musym in ["14", "17"] and majority == 24:
                category = "J"
            elif musym in ["14", "17"] and majority in [22, 23]:
                category = "K"
            elif musym in ["14", "17"] and majority in [21, 52, 42, 0, 71, 95]:
                category = "L"

            if category:
                row[2] = category
                mat.updateRow(row)
# ... (function ends here)

# Loading required files
path_to_folder = "D:\\Working_Directory\\" #Assign working directory path
subcatchments = "Subcatchments_example.shp"
lulc = "lulc_layer_fl_resample.tif" #This is resampled LULC raster from 30 m to finer resolution
soiltypes = "soiltypes_fl.shp"

# Run above function with data
parameter_grouping_for_subcatchments(path_to_folder, subcatchments, lulc, soiltypes)

# This create a shapefile called "Subcat_FL_polygon.shp" with added attribute field called 
# "Category" which can be used for grouping parameters for calibration for other model analysis
# Note (Examples of Raster values):
# Stony clay loam = 2, 11, 2A, 2B
# Cobbly clay loam = 12, 15, 15A, 1, 18, 
# Lynx loam = 13
# Sandy loam = 14, 17
# and
# High = 24
# Medium-low = 22, 23
# Open = 0, 42, 52, 21, 71, 95


# Part B: For conduits
# This function already assumes that the material types and age of infrastructure is present as the attribute 
# fields in the conduit shapefile. Example of "smooth" material type is Steel or PVC, "concrete" type is RCP or reinforced
# concrete, "rough" material type is corrugated metal pipe. Age is defined as whether the infrastructure is old or new, with respect
# to a historical time period e.g. before or after 1990.

# Creating a function...(function begins)...
def parameter_grouping_for_conduits(path_to_folder, conduit_features):
    arcpy.env.workspace = path_to_folder
    arcpy.env.overwriteOutput = True

    out_feature_class = conduit_features 
    arcpy.AddField_management(out_feature_class, "Category", "TEXT")
    with arcpy.da.UpdateCursor(out_feature_class, ["MATERIAL", "Age", "Category"]) as mat:
        for row in mat:
            material, age, category = row[0], row[1], None 
            # Criterias
            if material in ["Smooth"] and age == "New":
                category = "A"
            elif material in ["Smooth"] and age == "Old":
                category = "B"
            elif material in ["Concrete"] and age == "New":
                category = "C"
            elif material in ["Concrete"] and age == "Old":
                category = "D"
            elif material in ["Rough"] and age == "New":
                category = "E"
            elif material in ["Rough"] and age == "Old":
                category = "F"
            elif material in ["Unknown or missing"] and age == "New":
                category = "G"
            elif material in ["Unknown or missing"] and age == "Old":
                category = "H"

            if category:
                row[2] = category
                mat.updateRow(row)
# ... (function ends here)
 
# Loading required files
path_to_folder = "D:\\Working_Directory\\" #Assign working directory path
conduit_features = "Conduit.shp"

# Run above function with data
parameter_grouping_for_conduits(path_to_folder, conduit_features)

# End of script