#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 11:36:13 2022

@author: philipboesch
"""
import os
import shutil
from maic_dates import test_date
# convert vertical individual files to horizontal combined maic inputs

files = ''
path = r"gene_lists_copy"
def folder_files(test_range):
    """combine gene lists into one folder to then be used to check the maic input formatting"""
    for file in test_range:
        os.mkdir(os.path.join(path, file.split(".")[0]))
        shutil.copy(os.path.join(path, file), os.path.join(path, file.split(".")[0]))

def compile_files(files):
    """combine gene lists and create a combined maic input"""
    for file in files:
        # read all files and create a new file for the combined data
        try:
            with open('gene_lists/' + file, 'r') as in_file, open(
                    test_date + '.txt', 'a') as out_file:
                col = ""  # setting the column variable to nothing
                for line in in_file:
                    # making data flat by removing \n
                    line = line.replace('\n', "")
                    # if the next line is blank but we still have lines left then
                    # we want to create a new row - ie if we've reached the end
                    # of the gene list for one study, we want to move on to the
                    # next study
                    if line == "" and len(col) > 0:
                        out_file.write(col + '\n')
                        col = ""
                    # if we still have stuff going on, then we want to seperate
                    # each gene with the '\t' seperator
                    else:
                        if len(col) > 0:
                            col += '\t'
                        col += line
                # as long as we have stuff to write - we want to write it
                # to the document
                if len(col) > 0:
                    out_file.write(col + '\n')
        except FileNotFoundError:
            print(file)  # prints out unmatched gene lists


# following files not the same in excel and gene list (excel:gene_list)
# note, ive changed the excel to match the gene_list

# NEED NEW COPY OF WEI CRISPR LIST
# had to seperate the several files ones into new lines on excel

# 2012_Li_et_al_Proteomics_proteomics_format.txt : 2012_Li_et_al_Proteomics_proteomics.txt
# 2015_Yu_BiochemBiophysResCommun_proteinproteininteraction.txt : 2015_yu_Biochem Biophys Res Commun_proteinproteininteraction.txt
# 2020_Messner_et_al_medRxiv_proteomics.txt : 2020_Messner_cellsystems_proteomics.txt
# 2020_Pfaender_Biorxiv_screen.txt : 2021_Pfaender_natmicro_screen
# 2020_Akgun_Medrxiv_proteomics.txt : 2020_Akgun_plosone_proteomics.txt
# 2020_Hou_et_al_Medrxiv_proteomics.txt : 2020_Hou_mcp_proteomics.txt
# 2020_vanderVeerdonk_A_systems_approach_to_inflammation.txt : 2020_vanderveerdonk_medrxiv_proteomics.txt
# Re : removed
# 2020_patel_medrxiv_proteomics.txt : 2021_patel_scireports_proteomics.txt
# 2020_lieberman_et_al_plosbiology_transcriptomics.txt : 2020_lieberman_plosbiology_transcriptomics.txt
# 2020_zhang_natureimmunology_scRNA.txt : several lists
# 2021_almasy_biorxiv_proteinproteininteraction : sIN GENE LIST BUT NOT EXCEL??
# 2020_schneider_biorxiv_crispr.txt : several files
# 2020_Akgun_plosone_proteomic.txt : already have this, this is the new version, old was preprint
# 2021_wei_cell_crispr.txt : NEED NEW COPY
# 2021_wang_cell_crispr_oc43; 2021_wang_cell_crispr_sars2; 2021_wang_cell_crispr_229e.txt : sevreal files
# 2021_lambarallerie_microorganisms_transcriptom_infnasal, 2021_lambarallerie_microorganisms_transcriptom_infbronc.txt : several files
# 2021_schneider_cell_transcriptomics_sarscov2_33;oc43_33;nl63_33;229e_33.txt: several files
# 2021_heinrichhoffman_cellhostandmicrobe_crispr_37C_229e.txt : several files
# 2021_ng_sciadv_sars2-np; 2021_ng_sciadv_seasonal-np; 2021_ng_sciadv_sars2-blood.txt: sevreal files
# 2021_daniloski_cell_crispr_high, 2021_daniloski_cell_crispr_low.txt : several files
# 2010_yoshikawa_plosone_transcription_unranked.txt :  changed the gene list name too: 2010_yoshikawa_plosone_transcriptomics.txt
# 2020_hadjadj_medrxiv_transcription.txt : 2020_Hadjadj_science_transcriptomics.txt
# 2020_ravindra_et_al_bioRxiv_transciptomics_format.txt : 2020_ravindra_et_al_bioRxiv_transciptomics.txt
# 2020_Pfaender_naturemicrobiology_screen.txt : duplicate
# 2020_hadjadj_science_transcription.txt : duplicate
# 2020_li_med = duplicate
# issue with bamberger formatting --> removed ^\s*$ and ^\n in sublime
# 2020_blanco_nhbe_ranked_cell_transcriptomics.txt : 2020_blanco_nhbe_ranked_cell_transcriptomics.txt
# 2020 messner duplicate
# 2020 hou duoplicate
# lieberman duplicate
# mick naturecomms duplicate
