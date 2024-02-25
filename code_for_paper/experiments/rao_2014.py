import os
import datetime
import pandas as pd
from experiments.process import create_approx, calc_correctness, plot_comparison

def data_prepare(docker_volume_path):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} rao_2014 data_prepare start")
    data_path = f"{docker_volume_path}/data/rao_2014/juicer_outputs"
    output_path=f"{docker_volume_path}/outputs/approx_pc1_pattern/rao_2014"
    resolutions = [1000000, 100000]
    cell_lines = ["gm12878", "imr90", "hmec", "nhek", "k562", "kbm7", "huvec", "hela", "ch12-lx"]
    methods = ["cxmax", "cxmin"]

    for resolution in resolutions:
        for cell_line in cell_lines:
            for method in methods:
                print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {resolution} {cell_line} {method} start")
                
                # There are only 19 chromosome in CH12-LX, 
                if cell_line == "ch12-lx":
                    chroms = [str(i) for i in range(1, 20)]
                    chroms.extend(["X", "Y"])
                else:
                    chroms = [str(i) for i in range(1, 23)]
                    chroms.extend(["X", "Y"])
                
                for chrom in chroms:
                    pearson=f"{data_path}/{cell_line}/{resolution}/pearsons/pearson_chr{chrom}.txt"
                    output=f"{output_path}/{cell_line}/{resolution}/{method}/approx_pc1_pattern_chr{chrom}.txt"
                    create_approx(pearson, output, method, source="2014")

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} rao_2014 data_prepare end")
    return

def summary_correctness(docker_volume_path):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} rao_2014 summary_correctness start")
    output = f"{docker_volume_path}/outputs/summary/summary_correctness_2014.xlsx"
    cxmax_df = pd.DataFrame()
    cxmin_df = pd.DataFrame()
    pc1_path = f"{docker_volume_path}/data/rao_2014/juicer_outputs"
    approx_path = f"{docker_volume_path}/outputs/approx_pc1_pattern/rao_2014"

    for species in ["human", "mouse"]:
        if species == "human":
            cell_lines = ["gm12878", "hela", "hmec", "huvec", "imr90", "k562", "kbm7", "nhek"]
            chroms = [str(i) for i in range(1, 23)]
        elif species == "mouse":
            cell_lines = ["ch12-lx"]
            chroms = [str(i) for i in range(1, 20)]
    
        chroms.extend(["X", "Y"])
        resolutions = [1000000, 100000]
        methods = ["cxmax", "cxmin"]

        for resolution in resolutions:
            for cell_line in cell_lines:
                for chrom in chroms:
                    for method in methods:
                        pc1_df = pd.read_table(f"{pc1_path}/{cell_line}/{resolution}/eigenvector/pc1_chr{chrom}.txt", header=None)
                        pc1_df = pc1_df.fillna(0)
                        approx_df = pd.read_table(f"{approx_path}/{cell_line}/{resolution}/{method}/approx_pc1_pattern_chr{chrom}.txt", header=None)

                        correctness_info = calc_correctness(pc1_df, approx_df)

                        if method == "cxmax":
                            if cxmax_df.empty:
                                cxmax_df = pd.DataFrame(
                                    [[cell_line, resolution, f"chr{chrom}", method, correctness_info["valid_entry_num"], correctness_info["correct_num"], correctness_info["correct_rate"]]],
                                    columns=['cell', 'resolution', 'chromosome', "method", "valid_entry_num", "correct_num", "correct_rate"]
                                )
                            else:
                                new_row_df = pd.DataFrame(
                                    [[cell_line, resolution, f"chr{chrom}", method, correctness_info["valid_entry_num"], correctness_info["correct_num"], correctness_info["correct_rate"]]],
                                    columns=['cell', 'resolution', 'chromosome', "method", "valid_entry_num", "correct_num", "correct_rate"]
                                )
                                cxmax_df = pd.concat([cxmax_df, new_row_df], ignore_index=True)
                        elif method == "cxmin":
                            if cxmin_df.empty:
                                cxmin_df = pd.DataFrame(
                                    [[cell_line, resolution, f"chr{chrom}", method, correctness_info["valid_entry_num"], correctness_info["correct_num"], correctness_info["correct_rate"]]],
                                    columns=['cell', 'resolution', 'chromosome', "method", "valid_entry_num", "correct_num", "correct_rate"]
                                )
                            else:
                                new_row_df = pd.DataFrame(
                                    [[cell_line, resolution, f"chr{chrom}", method, correctness_info["valid_entry_num"], correctness_info["correct_num"], correctness_info["correct_rate"]]],
                                    columns=['cell', 'resolution', 'chromosome', "method", "valid_entry_num", "correct_num", "correct_rate"]
                                )
                                cxmin_df = pd.concat([cxmin_df, new_row_df], ignore_index=True)

    output_df = pd.concat([cxmax_df, cxmin_df], ignore_index=True)

    filename = output
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with pd.ExcelWriter(filename, mode="w") as writer:
        output_df.to_excel(writer, sheet_name="summary_correctness_2014")

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} rao_2014 summary_correctness end")
    return

def plot_all_comparisons(docker_volume_path):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} rao_2014 plot_comparison start")
    data_path = f"{docker_volume_path}/data"

    resolutions = [1000000, 100000]
    cell_lines = ["gm12878", "hela", "hmec", "huvec", "imr90", "k562", "kbm7", "nhek", "ch12-lx"]
    methods = ["cxmax", "cxmin"]

    for resolution in resolutions:
        for cell_line in cell_lines:
            for method in methods:
                if resolution == 1000000:
                    figsize = 20
                elif resolution == 100000:
                    figsize = 40

                if cell_line == "ch12-lx":
                    chroms = [str(i) for i in range(1, 20)]
                else:
                    chroms = [str(i) for i in range(1, 23)]
                chroms.extend(["X", "Y"])

                print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} rao_2014 plot_comparison {resolution} {cell_line} {method}")
                for chrom in chroms:
                    pc1 = f"{data_path}/rao_2014/juicer_outputs/{cell_line}/{resolution}/eigenvector/pc1_chr{chrom}.txt"
                    approx=f"{docker_volume_path}/outputs/approx_pc1_pattern/rao_2014/{cell_line}/{resolution}/{method}/approx_pc1_pattern_chr{chrom}.txt"
                    output_path = f"{docker_volume_path}/outputs/plots/rao_2014/{cell_line}/{resolution}/{method}"
                    os.makedirs(f"{output_path}/scatter", exist_ok=True)
                    os.makedirs(f"{output_path}/relative_magnitude", exist_ok=True)
                    plot_comparison(pc1, approx, relative_magnitude=f"{output_path}/relative_magnitude/relative_magnitude_chr{chrom}.png", scatter=f"{output_path}/scatter/scatter_chr{chrom}.png", figsize=figsize)

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} rao_2014 plot_comparison end")
    return

def run_all(docker_volume_path):
    data_prepare(docker_volume_path)
    summary_correctness(docker_volume_path)
    plot_all_comparisons(docker_volume_path)