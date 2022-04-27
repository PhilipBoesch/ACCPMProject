# -*- coding: utf-8 -*-
"""
Checking / converting gene names for MAIC input,
collating to single input file

Including Excel date formatting error correction.

Gene names will be converted to HGNC symbol where one exists;
if no HGNC equivalent, GenCode names used as second choice;
otherwise Refseq/other original symbol will be used.
For ambiguous symbols which could refer to more than one HGNC symbol:
    If the symbol is a current HGNC symbol, it will be assumed that is what the
    symbol refers to (unless this is already another entry in list).
    If not (i.e. could be from outdated HGNC or to another annotation system),
    the script will count up usage of other annotation systems in non-ambiguous
    genes and allocate to most popular annotation system; if not possible to
    distinguish on this basis, will arbitrarily allocate.

Any unrecognised gene names / symbols will be left in their original form,
but will be listed in a separate output file to allow error checking.

Current version of alias dictionary file (June2020) support the following
formats:
    HGNC symbol
    HGNC approved name (if spelled exactly as source!!)
    HGNC number as 'HGNC:1234'
    Old HGNC symbols
    Mouse homologs (ferrets in theory, but few in database)
    GenCode gene names (including lncRNAs etc not included in HGNC)
    Ensembl gene/transcript ID (ENSG / ENST)
    ucsc ID (e.g. uc123abc.1)
    uniprot ID (e.g Q9UNA3)
    gi numbers formatted as gi|123456|
    Vega / havana  e.g. OTTHUMG / OTTHUMT...
    refseq ID beginning with NM_, XR_ LOC... etc.
    Miscellaneous symbols including old symbols, Cosmic symbols etc


Usage: python MAIC_inputcheck.py [-d target directory] [-a alias file]
                                        [-s input suffix] [-o output file]

Requires: Python 3, packages including pickle
          .pkl file of gene aliases (default gene_name_aliases.pkl)
          all input files as tab-delimited files in the same directory,
          with the same suffix.
          (Defaults are .txt suffix and current working directory)


Created on Tue Jun  9 15:28:14 2020

@author: nparkins
"""

import argparse
import os
from datetime import date
import sys
import re
# import json
import pickle


class ListFormatter(object):
    """
    Wrapper in which to collate all gene list and formatting data
    """

    def __init__(self, options, singlefile=False):
        """
        Set up a ListFormatter object.
        Required parameters are parsed options
        """
        self.options = options
        with open(self.options.aliasfile, 'rb') as a:
            self.alias_dict = pickle.load(a)
        self.genelists = []
        self.categories = []
        self.singlefile = singlefile

    def process_lists(self):
        """
        Iterate through and format gene list files
        """
        if self.options.gmt:
            self.extract_lists(self.singlefile)
        else:
            for file in os.listdir(self.options.inputdir):
                if file.endswith(self.options.suffix) and not file.startswith(
                        self.options.outputfile[:4]):
                    self.extract_lists(file)
            self.screen_duplicates()
        if self.options.gmt:
            self.output_gmt()
        else:
            self.output_lists()
            self.output_failures()

    def extract_lists(self, file):
        """
        Read in a file, check format and read list(s)
        """
        with open(os.path.join(self.options.inputdir, file)) as f:
            # print('extracting,',file)
            lines = [[g for g in i.strip("\n").split("\t")
                      if g != ""] for i in f.readlines()]
        if self.options.gmt:
            for line in lines:
                if len(line) > 1:
                    self.genelists.append(GeneList(line, self, file))
        elif len(lines) > 4 and len(lines[0]) == 1:
            # single list, vertical format
            try:
                self.genelists.append(GeneList([i[0] for i in lines
                                                if i != []], self, file))
            except IndexError:
                raise Exception("Input file formatting error, {}".format(file))
        elif len(lines) == 1 and len(lines[0]) > 4:
            # single list, horizontal format
            self.genelists.append(GeneList(lines[0], self, file))
        elif (len(lines) > 4 and len(lines[0]) > 1
              and set(lines[3]) in ({'NAMED_GENES'}, {'GENE_NAMES'}, {'GENE_LIST'},
                                    {'NAMED_GENES', 'GENE_NAMES'})):
            # multiple lists, vertical
            for i in range(len(lines[0])):
                self.genelists.append(GeneList([line[i] for line in lines],
                                               self, file))
        elif (len(lines[0]) > 4 and len(lines) > 1 and
              set([i[3] for i in lines]) in ({'NAMED_GENES'}, {'GENE_NAMES'},
                                             {'NAMED_GENES', 'GENE_NAMES'})):
            # multiple lists, horizontal
            for line in lines:
                self.genelists.append(GeneList(line, self, file))
        else:
            raise Exception("Input file formatting error, {}".format(file))

    def screen_duplicates(self):
        """
        Checks list names, only includes once if duplicates
        """
        included = []
        keep = []
        for glist in self.genelists:
            if glist.name not in included:
                included.append(glist.name)
                keep.append(glist)
        self.genelists = keep

    def output_lists(self):
        """
        Writes formatted lists to file
        """
        with open(os.path.join(self.options.inputdir,
                               self.options.outputfile), 'w') as o:
            for glist in self.genelists:
                self.categories.append(glist.category)
                try:
                    o.write("{}\t{}\t{}\t{}\t{}\n".format(
                        glist.category,
                        glist.name,
                        glist.type,
                        glist.named,
                        "\t".join(glist.genes)
                    )
                    )
                except TypeError:
                    print(glist.name, glist.genes)
                    raise Exception("type error")
        print("Total lists included: ", len(self.genelists))
        print("Categories included: ")
        print(set(self.categories))

    def output_gmt(self):
        """
        Write formatted .gmt (gene set) files instead of MAIC format
        """
        outputpath = os.path.join(self.options.inputdir,
                                  '{}.gmt'.format(self.singlefile))
        with open(outputpath, 'w') as o:
            o.write("\n".join(["{}\t{}".format(glist.category,
                                               "\t".join(glist.genes))
                               for glist in self.genelists]))

    def output_failures(self):
        """
        Outputs a second file with a list of any unrecognised gene symbols
        for each gene list, to allow error checking.
        """
        failure_out = self.options.outputfile + ".unconverted.txt"
        duplicates_out = self.options.outputfile + ".duplicates.txt"
        with open(os.path.join(self.options.inputdir,
                               failure_out), 'w') as o:
            for glist in self.genelists:
                if glist.unconverted != []:
                    o.write("{}\t{}\n".format(glist.name,
                                              "\t".join(glist.unconverted)))
        with open(os.path.join(self.options.inputdir,
                               duplicates_out), 'w') as o:
            for glist in self.genelists:
                if glist.duplicates != [] or glist.redundant != []:
                    o.write("{}\t{}\t{}\n".format(glist.name,
                                                  ",".join(glist.duplicates),
                                                  ",".join([str(i) for i in
                                                            glist.redundant])))


class GeneList(object):
    """
    Container for gene lists and associated attributes,
    and name correction functions
    """

    def __init__(self, genelist, formatter, filename):
        """
        Set up object from list and convert names
        """
        self.formatter = formatter
        self.name = genelist[1]
        self.category = genelist[0]
        if not self.formatter.options.gmt:
            self.type = genelist[2].upper()
            self.named = genelist[3].upper()
        if self.formatter.options.gmt:
            self.genes = [i for i in genelist[1:] if i != ""]
        else:
            self.genes = [i for i in genelist[4:] if i != ""]
        self.filename = filename
        self.usage = {}
        self.unconverted = []
        self.duplicates = []
        self.redundant = []  # original / converted pairs
        self.ambiguous = {}
        if not self.formatter.options.gmt:
            self.check_fields()
            self.correct_categories()
        self.check_genelist()
        self.convert_names()
        self.resolve_ambiguity()

    def check_fields(self):
        """
        Checks some of expected fields are in the right position,
        corrects common errors in ranking/named_gene fields.
        """
        if self.named != 'NAMED_GENES':
            if 'NAME' in self.named.upper() and 'GENE' in self.named.upper():
                self.named = 'NAMED_GENES'
            elif 'GENE_LIST' in self.named.upper():
                self.named = 'NAMED_GENES'
            else:
                raise Exception('List format error, {}, NAMED_GENES expected'
                                ' in field 4'.format(self.filename))
        if self.type not in ['RANKED', 'NOT_RANKED']:
            if self.type.upper() == 'UNRANKED':
                self.type = 'NOT_RANKED'
            else:
                raise Exception('List format error, {}, RANKED or NOT_RANKED '
                                'expected in field 3'.format(self.filename))

    def correct_categories(self):
        """
        Corrects common typos / inconsistencies in category field
        """
        if self.category.endswith('omic'):
            self.category = self.category + 's'
            # convention is to use 'omics'
        if self.category.endswith('ics'):
            self.category = self.category.lower()
            # lower case for transcriptomics etc
        if self.category in ('transciptomics', 'tanscriptomics',
                             'transcription'):
            self.category = 'transcriptomics'
        if 'RNAI' in self.category.upper():
            self.category = 'RNAi'
        if ('protein' in self.category.lower() and
                'interaction' in self.category.lower()):
            self.category = 'proteinproteininteraction'
        if 'CRISPR' in self.category.upper():
            self.category = 'CRISPR_screen'
        if self.category.upper() == 'GENETICS':
            self.category = 'human_genetics'
        if self.category.lower() == 'humangenetics':
            self.category = 'human_genetics'
        if self.category.lower() == 'cross' or ('genetics' in self.category.lower() and 'non' in self.category.lower()):
            self.category = 'nonhuman_genetics'
        if 'screen' in self.category.lower() and (
                'crispr' not in self.category.lower() and 'rnai' not in self.category.lower()):
            self.category = 'gene_set_screen'
        if 'human' in self.category.lower() and 'genetic' in self.category.lower() and 'other' in self.category.lower():
            self.category = "human_genetic_other"

    def check_genelist(self):
        """
        Checks for duplicates within the same list: if any detected,
        keep first instance and keep names for error checking.
        """
        if len(self.genes) != len(set(self.genes)):
            print("Warning: duplicates list entries in file {}, "
                  "list {}".format(self.filename, self.name))
            print("First instance kept.")
            filtered = []
            for i, j in enumerate(self.genes):
                if j not in self.genes[0:i]:
                    filtered.append(j)
                else:
                    self.duplicates.append(j)
            self.genes = filtered

    def convert_names(self):
        """
        Corrects names, converts to hgnc if possible;
        or alternatives as listed in alias dictionary if no hgnc equivalent.
        Makes best guess if ambiguous gene symbol.
        If not in dictionary, keep as is but report.
        """
        xcel_checked = list(map(self.correct_excel_error, self.genes))
        corrected_list = list(map(self.trim_suffixes, xcel_checked))
        newlist = []
        for gene in corrected_list:
            gene = gene.strip()
            found = False
            # if entered gene not found, try variants:
            for variant in [gene,
                            gene.split(".")[0],
                            gene.replace("SEPT", "SEP"),
                            gene + ".1",
                            gene.upper(),
                            gene[0].upper() + gene[1:].lower()]:
                try:
                    genedata = self.formatter.alias_dict[variant]
                    found = True
                    break
                except KeyError:
                    continue
            if not found:
                # newlist.append(gene)
                self.unconverted.append(gene)
                continue

            if len(genedata) == 1:
                # non-ambiguous gene; keep if ref gene not already there
                new = list(genedata.values())[0]
                if new not in newlist:
                    newlist.append(new)
                else:  # must be present under another alias, keep first only
                    self.redundant.append((gene, new))
                # record annotation system
                annotation = list(genedata.keys())[0]
                if annotation not in self.usage:
                    self.usage[annotation] = 1
                else:
                    self.usage[annotation] += 1

            else:
                # ambiguous label; leave tag in place for now to preserve rankings,
                # and save to sort out after the others
                self.ambiguous.update({gene: genedata})
                newlist.append(gene + "#")
        self.genes = newlist

    def correct_excel_error(self, gene):
        """
        Corrects errors introduced by Excel where gene names are converted
        to dates. One name at a time.
        """
        monthnamecorrections = {
            'Sep-': 'SEPT', '-Sep': 'SEPT', 'Mar-': 'MARCH', '-Mar': 'MARCH',
            'Oct-': 'OCT', 'Dec-': "DEC", '-Dec': 'DEC',
            'Sep-0': 'SEPT', '-Sep': 'SEPT', 'Mar-0': 'MARCH',
            'Oct-0': 'OCT', '-Oct': 'OCT', '-Jun': 'JUN',
            'Dec-0': "DEC", 'Jun-': 'JUN', 'Jun-0': 'JUN'
        }
        check = re.match('((Sep-)|(Mar-)|(Oct-)|(Dec-)|(Jun-))0{0,1}', gene)
        if check is not None:
            return gene.replace(check.group(0),
                                monthnamecorrections[check.group(0)])
        check2 = re.search('(-Sep)|(-Mar)|(-Oct)|(-Dec)|(-Jun)', gene)
        if check2 is not None:
            numeral = gene[:check2.start(0):]
            if numeral.startswith('0'):
                numeral = numeral[1:]
            newgene = gene[check2.start(0):].replace(check2.group(0),
                                                     monthnamecorrections[check2.group(0)]) + numeral
            return (newgene)
        else:
            return gene

    def trim_suffixes(self, gene):
        """
        Removes '.x or '.xx' suffixes from ENST, ENSG, OTTHUMG and OTTHUMT IDs.
        Will leave these in for others e.g. ucsc IDs.
        """
        if re.match('((ENS)|(OTT)|(NM_)|(XM_)|(NR_)|(XR_))\A', gene) is not None:
            suffix_start = gene.find('.')
            gene = gene[:suffix_start]
        return gene

    def resolve_ambiguity(self):
        """
        For labels that could refer to more than one possible gene:
            1. exclude any options already in gene list
            2. If still >1 option, choose 'hgnc' if this is an option
            3. If not, choose most popular of the available annotation
                schemes among non-ambiguous genes
            4. If still can't resolve, arbitrarily assign to first in list
        """
        for gene, genedata in self.ambiguous.items():
            filtered = {k: v for k, v in genedata.items()
                        if v not in self.genes}
            if len(filtered) == 0:
                self.redundant.append(gene)
                continue
            if len(filtered) == 1:
                new = list(filtered.values())[0]
            else:
                if 'hgnc' in filtered.keys():
                    new = filtered['hgnc']
                else:
                    for f in list(filtered.keys()):
                        if f not in self.usage:
                            self.usage[f] = 0
                    annot_order = sorted(list(filtered.keys()),
                                         key=lambda x: self.usage[x],
                                         reverse=True)
                    new = filtered[annot_order[0]]
            self.genes[self.genes.index(gene + "#")] = new


def get_parsed_options(args=None):
    """Parse any command line arguments and convert them into a Namespace
    object that we can query as required elsewhere in the code
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--inputdir', default=os.getcwd(),
                        help='directory for input lists')
    parser.add_argument('-a', '--aliasfile',
                        default="gene_name_aliases.pkl",
                        help='gene alias pickle file')
    parser.add_argument('-s', '--suffix', default='.txt',
                        help='suffix to identify input lists')
    parser.add_argument('-o', '--outputfile',
                        default='MAIC_input_{}.txt'.format(date.today()),
                        help='outputfilename')
    parser.add_argument('-gmt', '--gmt', default=False, action='store_true',
                        help='convert gmt pathway files rather than MAIC')

    parsed_options = parser.parse_args(args)
    return parsed_options


if __name__ == "__main__":
    options = get_parsed_options(args=sys.argv[1:])
    if options.gmt:
        print("Converting gene sets to .gmt files")
        for file in os.listdir(options.inputdir):
            if file.endswith(options.suffix):
                formatter = ListFormatter(options, singlefile=file)
                formatter.process_lists()
    else:
        print("Converting gene lists to MAIC input")
        formatter = ListFormatter(options)
        formatter.process_lists()

# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/Dropbox-MAC/ranking aggregation comparison/collected_real_data/SHIELD/extracted_lists/unranked_list_seperate/' -a '/Users/s1718825/Dropbox/gene_name_aliases.pkl'

# Update: 2021-Jan-12: adding bovine and pig genes(but not using the data for ID->symbol). (already have mouse and macaque)

# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Documents/colleboration/Sara-gene_lists_compare_2021-01-06/comparision_with_colleborators/lists_to_compare/' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'

# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/Dropbox-MAC/corona_maic/2_gene lists/5_ready_for_maic_run/' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'
# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/pneumococcus_lists_2/' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'
# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/Dropbox-MAC/corona_maic/2_gene_lists/complement_list/' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'
# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/Dropbox-MAC/corona_maic/2_gene_lists/5_ready_for_maic_run/' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'
# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/Dropbox-MAC/corona_maic/GWAS_WGS/' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'
# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/copd_lists' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'
# command line: python MAIC_inputcheck.py -d '/Users/s1718825/Dropbox/Dropbox-MAC/corona_maic/GWAS_WGS/' -a '/Users/s1718825/Dropbox/gene_name_aliases_v2species-2.pkl'

