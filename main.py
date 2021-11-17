##  Required imports
import matplotlib

matplotlib.use("Agg")
import sdesk
import os
from VAMAS import parseVAMAS, extract_vamas_data_and_meta
import numpy as np

##


# Define your method main()
def main():
    process = sdesk.Process()
    # LOAD INPUT FILES OR SAMPLES
    input_file = process.input_files[0]
    filename, file_extension = os.path.splitext(input_file.properties["name"])
    if file_extension.lower() not in [".vms", ".vamas", ".txt"]:
        # STOP AND DO NOTHING
        return 0

    # PROCESS INPUT FILE AND EXTRACT DATA
    output_files = []
    with open(input_file.path, "r") as fp:
        vamas_data = parseVAMAS(fp)
        for dict_data in vamas_data["blocks"]:
            jHeader, jInfo, data = extract_vamas_data_and_meta(dict_data)
            data = np.array(data)
            xdata = data[:, 0]
            minx = np.min(xdata)
            maxx = np.max(xdata)
            print("block_identifier")
            print(dict_data["block_identifier"])

            output_files.append(
                {
                    "name": "{}_ke.txt".format(dict_data["block_identifier"]),
                    "columns": jInfo["columnNames"],
                    "data": data,
                    "header": sdesk.json_to_text(jHeader),
                    "zoom": 1 / (maxx - minx + 1),
                }
            )

    # UPDATE CUSTOM PROPERTIES OF INPUT FILE
    new_properties = {"technique": "XPS"}
    input_file.custom_properties.update(new_properties)
    input_file.save_custom_properties()

    # Create output files derived from the processing of input file
    for out_file in output_files:
        sdesk_output_file = process.create_output_file(out_file["name"])
        sdesk.write_tsv_file(
            sdesk_output_file.path,
            out_file["columns"],
            out_file["data"],
            out_file["header"],
        )


# Call method main()
main()
