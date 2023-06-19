import os
import sys
import datetime
from fpdf import FPDF
import dataframe_image as dfi
import pandas as pd

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')] + sys.path


def compile_assembly_report(bacteria_parser):
    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}.pdf".format(bacteria_parser.data.entry_id)

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/lpf_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, bacteria_parser.data.entry_id, "lpf analytical report, Version: {}".format(bacteria_parser.data.version))
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "{}, {} \n"\
                 "Suggested reference: {} \n\n" \
                 "No related phylogeny cluster was identified. \n" \
                 "".format(bacteria_parser.data.entry_id, bacteria_parser.data.city, bacteria_parser.data.country, bacteria_parser.data.reference_header_text) #What do we do here? How do we assign a name to a reference assembly? Manuel or automatic?
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(20)

    df = pd.read_csv(bacteria_parser.data.target_dir + "/quast_output/report.tsv", sep='\t')
    df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
    #dfi.export(df_styled, bacteria_parser.data.target_dir + "/quast_table.png")
    #pdf.image("{}/quast_table.png".format(bacteria_parser.data.target_dir), x=10, y=90, w=pdf.w / 2.5, h=pdf.h / 2.7)
    pdf.set_xy(x=10, y=58)
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(51, 153, 255)
    pdf.image("{}/contigs.jpg".format(bacteria_parser.data.target_dir), x=115, y=90, w=pdf.w / 2.5, h=pdf.h / 2.7)

    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/lpf_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, bacteria_parser.data.entry_id, "CGE Finder results")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Antimicrobial Genes Found:", 0, 1, 'L')

    csv_data = derive_amr_stats(bacteria_parser)

    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    print ('This worked')

    pdf.cell(85, 5, "Virulence Genes Found: ", 0, 1, 'L')

    csv_data = derive_virulence_stats(bacteria_parser)
    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Plasmids Found:", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    textstring = ""
    for item in bacteria_parser.data.plasmid_hits:
        textstring += "* {}\n".format(item)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)

    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.cell(85, 5, "All analysis results and additional data can be found in /opt/lpf_analyses/{}".format(
        bacteria_parser.data.entry_id), 0, 1, 'L')

    pdf.output("{}/{}".format(bacteria_parser.data.target_dir, filename), 'F')


def compile_alignment_report(bacteria_parser):
    pdf = FPDF()  # A4 (210 by 297 mm)

    filename = "{}.pdf".format(bacteria_parser.data.entry_id)
    clusterSize = len(bacteria_parser.data.isolate_list)

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/lpf_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)

    create_title(pdf, bacteria_parser.data.entry_id, "lpf analytical report, Version : {}".format(bacteria_parser.data.version))
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)

    textstring = "ID: {} \n" \
                 "sample_name: {} \n" \
                 "Identified reference: {} \n" \
                 "".format(bacteria_parser.data.entry_id, bacteria_parser.data.sample_name, bacteria_parser.data.reference_header_text)
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(10)
    pdf.set_font('Arial', '', 10)

    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(51, 153, 255)
    pdf.set_xy(x=10, y=60)
    pdf.cell(85, 5, "Sample information: ", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)

    pdf.set_font('Arial', '', 10)
    textstring = "{}, {} \n" \
                 "Time of sampling: No INPUT \n" \
                 "Number of associated isolates: {} \n" \
                 "".format(bacteria_parser.data.city, bacteria_parser.data.country, clusterSize)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)
    pdf.set_text_color(51, 153, 255)
    pdf.set_font('Arial', '', 12)
    pdf.cell(85, 5, "CGE results: ", 0, 1, 'L')

    textstring = "AMR genes in this sample: {}. \n" \
                 "Plasmids in this sample: {}. \n" \
                 "Virulence genes in this sample: {}. \n" \
                 "MLST: ST {}. \n" \
                 "".format(len(bacteria_parser.data.resfinder_hits), len(bacteria_parser.data.plasmid_hits), len(bacteria_parser.data.virulence_hits), bacteria_parser.data.mlst_type)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)

    pdf.set_xy(x=105, y=65)

    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/lpf_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)
    create_title(pdf, bacteria_parser.data.entry_id, "CGE Finder results")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Antimicrobial Genes Found:", 0, 1, 'L')

    csv_data = derive_amr_stats(bacteria_parser)


    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Virulence Genes Found: ", 0, 1, 'L')

    csv_data = derive_virulence_stats(bacteria_parser)
    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Plasmids Found:", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    textstring = ""
    for item in bacteria_parser.data.plasmid_hits:
        textstring += "* {}\n".format(item)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)

    pdf.set_font('Arial', '', 12)

    ''' Third Page '''
    pdf.add_page()
    pdf.image("/opt/lpf_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, bacteria_parser.data.entry_id, "Cluster phylogeny:")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Phylo tree for cluser {}: ".format(bacteria_parser.data.reference_header_text.split("\t")[0]), 0, 1, 'L')

    #Currently no tree outputted

    #bacteria_parser.data = create_phylo_tree(bacteria_parser.data)

    #pdf.image("{}/phytree_output/tree.png".format(bacteria_parser.data.target_dir), x=10, y=55, w=pdf.w / 1.5, h=pdf.h / 1.75)

    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.cell(85, 5, "All analysis results and additional data can be found in /opt/lpf_analyses/{}".format(
        bacteria_parser.data.entry_id), 0, 1, 'L')

    pdf.output("{}/{}".format(bacteria_parser.data.target_dir, filename), 'F')


def create_title(pdf, id, string):
  # Unicode is not yet supported in the py3k version; use windows-1252 standard font
  pdf.set_text_color(51, 153, 255)
  pdf.set_font('Arial', 'BU', 24)
  pdf.ln(10)
  pdf.write(5, f"{string}")
  pdf.ln(10)
  pdf.set_text_color(0, 0, 0)

def derive_amr_stats(bacteria_parser): #TBD rewrite and remove.
    phenotype = dict()
    infile = open("/opt/lpf_databases/resfinder_db/phenotypes.txt", 'r')
    for line in infile:
        if not line.startswith("Gene_accession"):
            line = line.rstrip().split("\t")
            if line[0] in bacteria_parser.data.resfinder_hits:
                phenotype[line[0]] = [line[1], line[2]]
    csv_data = []
    csv_data.append(("Gene", "Resistance Class", "Phenotype"))
    for item in phenotype:
        csv_data.append([item, phenotype[item][0], phenotype[item][1]])
    return csv_data

def derive_virulence_stats(bacteria_parser):  #TBD rewrite and remove.
    new_genes = list()
    for item in bacteria_parser.data.virulence_hits:
        new_genes.append(item.split(":")[0])
    genes = new_genes
    phenotype = dict()
    infile = open("/opt/lpf_databases/virulencefinder_db/notes.txt", 'r')
    for line in infile:
        if line[0] != "#":
            line = line.rstrip().split(":")
            if line[0] in genes:
                if line[1] in phenotype:
                    phenotype[line[1].strip()].append(line[0])
                else:
                    phenotype[line[1].strip()] = [line[0]]

    csv_data = []
    csv_data.append(("Virulence", "Genes"))
    for item in phenotype:
        csv_data.append((item, ", ".join(phenotype[item])))
    print (csv_data)
    return csv_data


def compile_virus_report(virus_parser):
    print ("Compiling virus report")
    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}.pdf".format(virus_parser.data.entry_id)

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/lpf_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, virus_parser.data.entry_id, "lpf virus report, Version: {}".format(virus_parser.data.version))
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    textstring = "lpf ID: {} \n" \
                 "Location: {}, {} \n"\
                 "Identified reference: {} \n".format(virus_parser.data.entry_id, virus_parser.data.city, virus_parser.data.country, virus_parser.data.reference_header_text) #What do we do here? How do we assign a name to a reference assembly? Manuel or automatic?
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    if virus_parser.data.prokka_tsv_list != None:
        pdf.set_font('Arial', '', 16)
        pdf.ln(10)
        pdf.cell(85, 5, "Prokka annotations (hypothetical proteins not included):", 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(5)
        with pdf.table() as table:
            for data_row in virus_parser.data.prokka_tsv_list:
                if not data_row[-1] == "hypothetical protein":
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)
    else:
        pdf.set_font('Arial', '', 16)
        pdf.ln(10)
        pdf.cell(85, 5, "No prokka annotations were found.", 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
    '''
    if virus_parser.data.cdd_hits != None:
        pdf.set_font('Arial', '', 16)
        pdf.ln(10)
        pdf.cell(85, 5, "Conserved Domain Annotations:", 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(5)
        with pdf.table() as table:
            for data_row in virus_parser.data.cdd_hits:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
    else:
        pdf.set_font('Arial', '', 16)
        pdf.ln(10)
        pdf.cell(85, 5, "No conserved domain annotations were found.", 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
    '''
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.cell(85, 5, "All analysis results and additional data can be found in /opt/lpf_analyses/{}".format(virus_parser.data.entry_id), 0, 1, 'L')


    pdf.output("{}/{}.pdf".format(virus_parser.data.target_dir, virus_parser.data.entry_id), 'F')



