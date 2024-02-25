import os
import datetime
import pandas as pd
from experiments.process import create_approx, calc_correctness, plot_comparison

def data_prepare(docker_volume_path):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} lieberman_2009 data_prepare start")

    data_path = f"{docker_volume_path}/data/lieberman_2009"
    output_path=f"{docker_volume_path}/outputs/approx_pc1_pattern/lieberman_2009"
    resolutions = [1000000, 100000]
    cell_lines = ["gm06690", "k562"]
    methods = ["cxmax", "cxmin"]

    for resolution in resolutions:
        for cell_line in cell_lines:
            for method in methods:
                print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {resolution} {cell_line} {method} start")
                
                # There are some missing chromosomes in Lieberman's dataset.
                if cell_line == "k562" and resolution == 100000:
                    chroms = [str(i) for i in range(1, 23)]
                else:
                    chroms = [str(i) for i in range(1, 23)]
                    chroms.extend(["X"])
                
                for chrom in chroms:
                    pearson=f"{data_path}/heatmaps/HIC_{cell_line}_chr{chrom}_chr{chrom}_{resolution}_pearson.txt"
                    output=f"{output_path}/{cell_line}/{resolution}/{method}/approx_PC1_pattern_chr{chrom}.txt"
                    create_approx(pearson, output, method, source="2009")

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} lieberman_2009 data_prepare end")
    return

def summary_correctness(docker_volume_path):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} lieberman_2009 summary_correctness start")
    output = f"{docker_volume_path}/outputs/summary/summary_correctness_2009.xlsx"
    cxmax_df = pd.DataFrame()
    cxmin_df = pd.DataFrame()
    pc1_path = f"{docker_volume_path}/data/lieberman_2009/eigenvectors"
    approx_path = f"{docker_volume_path}/outputs/approx_pc1_pattern/lieberman_2009"

    cell_lines = ["gm06690", "k562"]
    methods = ["cxmax", "cxmin"]

    '''
        https://ftp.ncbi.nlm.nih.gov/geo/series/GSE18nnn/GSE18199/suppl/GSE18199%5Freadme%5Fv4.txt
        "chromosome" nomenclature: 
        0 Mitochondrial
        23 X
        24 Y

        Notes: 
        In Lieberman's dataset, 
        1. The symbol used for the 23 chromosome are not the same in the `eigenvectors` and `heatmaps` diractory. (eigenvectors: 23, heatmaps: X)
        2. There's no chromosome Y(24) in the datasets, 
        3. There's 100000 resolution pearson matrix for k562 (chr1 - chr22, "no" chrX), 
        4. There's "no" 100000 resolution PC1 for k562.
    '''
    
    for cell_line in cell_lines:
        if cell_line == "k562":
            resolutions = [1000000]
            chroms = [str(i) for i in range(1, 23)]
        else:
            resolutions = [1000000, 100000]
            chroms = [str(i) for i in range(1, 24)]

        for resolution in resolutions:
            for method in methods:
                for chrom in chroms:
                    if cell_line == "gm06690":
                        if chrom == "23":
                            pc1 = f"{pc1_path}/GM-combined.ctg{chrom}.ctg{chrom}.{resolution}bp.hm.eigenvector.tab"
                            approx = f"{approx_path}/{cell_line}/{resolution}/{method}/approx_PC1_pattern_chrX.txt"
                        else:
                            pc1 = f"{pc1_path}/GM-combined.ctg{chrom}.ctg{chrom}.{resolution}bp.hm.eigenvector.tab"
                            approx = f"{approx_path}/{cell_line}/{resolution}/{method}/approx_PC1_pattern_chr{chrom}.txt"
                    elif cell_line == "k562":
                        pc1 = f"{pc1_path}/K562-HindIII.ctg{chrom}.ctg{chrom}.{resolution}bp.hm.eigenvector.tab"
                        approx = f"{approx_path}/{cell_line}/{resolution}/{method}/approx_PC1_pattern_chr{chrom}.txt"

                    pc1_df = pd.read_table(pc1, header=None, sep="\t")
                    pc1_df = pc1_df.iloc[:, [2]]
                    approx_df = pd.read_table(approx, header=None)

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
        output_df.to_excel(writer, sheet_name="summary_correctness_2009")

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} lieberman_2009 summary_correctness end")
    return

def plot_all_comparisons(docker_volume_path):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} lieberman_2009 plot_comparison start")
    data_path = f"{docker_volume_path}/data"
    cell_lines = ["gm06690", "k562"]
    methods = ["cxmax", "cxmin"]

    for cell_line in cell_lines:
        if cell_line == "k562":
            resolutions = [1000000]
            chroms = [str(i) for i in range(1, 23)]
        else:
            resolutions = [1000000, 100000]
            chroms = [str(i) for i in range(1, 24)]

        for resolution in resolutions:
            for method in methods:
                print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} lieberman_2009 plot_comparison {resolution} {cell_line} {method}")

                for chrom in chroms:
                    if resolution == 1000000:
                        figsize = 20
                    elif resolution == 100000:
                        figsize = 40

                    if cell_line == "gm06690":
                        if chrom == "23":
                            pc1 = f"{data_path}/lieberman_2009/eigenvectors/GM-combined.ctg{chrom}.ctg{chrom}.{resolution}bp.hm.eigenvector.tab"
                            approx = f"{docker_volume_path}/outputs/approx_pc1_pattern/lieberman_2009/{cell_line}/{resolution}/{method}/approx_PC1_pattern_chrX.txt"
                        else:
                            pc1 = f"{data_path}/lieberman_2009/eigenvectors/GM-combined.ctg{chrom}.ctg{chrom}.{resolution}bp.hm.eigenvector.tab"
                            approx = f"{docker_volume_path}/outputs/approx_pc1_pattern/lieberman_2009/{cell_line}/{resolution}/{method}/approx_PC1_pattern_chr{chrom}.txt"
                    elif cell_line == "k562":
                        pc1 = f"{data_path}/lieberman_2009/eigenvectors/K562-HindIII.ctg{chrom}.ctg{chrom}.{resolution}bp.hm.eigenvector.tab"
                        approx = f"{docker_volume_path}/outputs/approx_pc1_pattern/lieberman_2009/{cell_line}/{resolution}/{method}/approx_PC1_pattern_chr{chrom}.txt"


                    output_path = f"{docker_volume_path}/outputs/plots/lieberman_2009/{cell_line}/{resolution}/{method}"
                    os.makedirs(f"{output_path}/scatter", exist_ok=True)
                    os.makedirs(f"{output_path}/relative_magnitude", exist_ok=True)
                    plot_comparison(pc1, approx, relative_magnitude=f"{output_path}/relative_magnitude/relative_magnitude_chr{chrom}.png", scatter=f"{output_path}/scatter/scatter_chr{chrom}.png", figsize=figsize, source="2009")

    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} lieberman_2009 plot_comparison end")
    return

def run_all(docker_volume_path):
    data_prepare(docker_volume_path)
    summary_correctness(docker_volume_path)
    plot_all_comparisons(docker_volume_path)
