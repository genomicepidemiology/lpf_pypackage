async function generatePDFReport2(analysisId, type) {
    dtu_logo_base64 = '/home/satya/dev/moss/local_app/js/image_data/dtu_logo_base64.txt';
    let amr_data = '/opt/lpf_analyses/'+analysisId+'/pdf_resources/amr_data.csv';
    let vir_data = '/opt/lpf_analyses/'+analysisId+'/pdf_resources/virulence_data.csv';
    let plas_data = '/opt/lpf_analyses/'+analysisId+'/pdf_resources/plasmid_data.csv';
    let quast_data = '/opt/lpf_analyses/'+analysisId+'/pdf_resources/quast_report.csv';
    let contigs_jpg = '/opt/lpf_analyses/'+analysisId+'/contigs.jpg';
    let bacteria_parser = '/opt/lpf_analyses/'+analysisId+'/pdf_resources/bacteria_parser.json';
    let bact_parse_data =  require(bacteria_parser);
    const output_pdf_file = '/opt/lpf_analyses/'+analysisId+'/'+analysisId+'.pdf';

    var imageData = "";
        await fetch(dtu_logo_base64) //to fetch the encoded base64 text
        .then(response => response.text()).then(text => imageData = text)
    const { jsPDF } = require("jspdf"); // will automatically load the jspdf
    const { autoTable } = require("jspdf-autotable");  //load autotable in jspdf
    const docsize = 'a4';
    var doc = new jsPDF('l', 'pt', docsize);
    var base64 = require('base-64');
    doc.setTextColor(0,0,255);
    doc.setFontSize(24);
    var title = "lpf ANALYTICAL REPORT, Version: "+(bact_parse_data).version;
    doc.text(110, 60, title);
    doc.addImage(imageData,'PNG', 750, 15, 70, 70);
    doc.setTextColor(0,0,0);
    doc.setFontSize(14);
    var sample =  "The ID: "+(bact_parse_data).entry_id+"\nSample_name: "+(bact_parse_data).sample_name+"\nIdentified reference: "+(bact_parse_data).reference_header_text;
    doc.text(60, 120, sample);
    doc.setTextColor(0, 0, 255);
    doc.text(60, 200, "Sample Information");
    var sample_info = " City: "+(bact_parse_data).city+"\n Country: "+(bact_parse_data).country+"\n Date of Sampling: "+(bact_parse_data).collection_date+"\n Number of associated isolates: "+((bact_parse_data).isolate_list.length);
    doc.setTextColor(0, 0, 0);
    doc.text(80, 220, sample_info);
    doc.setTextColor(0, 0, 255);
    doc.text(60, 320, "CGE Results");
    var hits = " AMR genes in this sample: "+ ((bact_parse_data).resfinder_hits.length)+"\n virulence in this sample: "+((bact_parse_data).virulence_hits.length)+"\n Plasmids genes in this sample: "+((bact_parse_data).plasmid_hits.length)+"\n MLST: "+((bact_parse_data).mlst_type);
    doc.setTextColor(0, 0 ,0);
    doc.text(80, 340, hits);

    if (type == "assembly") {
        await generateAssemblyReport(quast_data, doc, imageData, contigs_jpg); // Assembly Report
    }
    else if (type == "alignment") {
        await generateAlignmentReport(amr_data, vir_data, plas_data, doc, imageData); // Alignment Report
    }
    doc.save(output_pdf_file);
}
async function generateAssemblyReport(quast_data, doc, imageData, contigs_jpg) { //assembly function for the load and display
    var error = await loadTableData(quast_data, doc, imageData);
        if(error == null) {
            doc.text(50, 70, "Assembly Report:");
        }
        const image = contigs_jpg; //to display the contigs image after the assembly
        fetch(image).then((res) => res.blob()).then((blob) => {  // Read the Blob as DataURL using the FileReader API
        const reader = new FileReader();
        const base64 = [];
     reader.onloadend = () => {
        const base64 = (reader.result);
        doc.addPage();
        doc.addImage(imageData,'PNG', 750, 10, 65, 65);
        doc.text(50, 55, "Contigs found from Assembly:")
        doc.addImage(base64, 'PNG', 150, 65, 400, 500);
        };
         reader.readAsDataURL(blob);
         });
}

async function generateAlignmentReport(amr_data, vir_data, plas_data, doc, imageData) { //alignment function to load and display
    await loadTableData(amr_data, doc, imageData);
        doc.text(50, 50, "CGE FINDER RESULTS");
        doc.text(50, 70, "Antimicrobial resistance Genes Found:");

        await loadTableData(vir_data, doc, imageData);
        doc.text(50, 70, "Virulence Genes Found:");

        await loadTableData(plas_data, doc, imageData);
        doc.text(50, 70, "Plasmids Found:");
}

async function readFileData(file) {   //parse the csv data
    const fs = require('fs');
    const parse = require('csv-parser');
    var output = [];
    var outData = [];
    var error = "";
    await fetch(file).catch((err) => {
                            error = err;
                            throw new Error(error);
                         });
    if(error == "") {
         await fetch(file).then(response => response.text())
                              .then(text => {
                              for (let i = 0; i < text.toString().split("\n").length ; i++) {    //converting text into strings & for displaying rows
                                  output[i] = text.toString().split("\n")[i].toString();
                              }
                                  return output;
                              })
                                .then(output => {
                              var headerLength = output[0].toString().split(",").length;
                              for(let i=0; i < output.length-1 ; i++) {
                                  var row = output[i].toString().split(",");
                                  for(let j=0; j < headerLength ; j++) {
                                      var cData = row[j].toString();
                                      if(i != 0 && headerLength != 1 && j == headerLength-1) {
                                         cData = row.slice(-1*(row.length-headerLength-1)).toString();
                                      }
                                     if (Array.isArray(outData[i])) {
                                          outData[i][j] = cData;
                                      } else {
                                          outData[i] = [cData];
                                      }
                                  }
                              }
                              return outData;
                              })
                              return outData;
    }
}

function createTable(doc, data, imageData) {   //creating tables for all the loaded data
   doc.addPage();
   doc.addImage(imageData,'PNG', 750, 10, 65, 65);
   doc.autoTable({
           startY: 80,
           theme: 'grid',
           showHead: 'everyPage',
           tableWidth: 'auto',
           head: [data[0]],
           body: data.slice(1)
       });
    return doc;
}

async function loadTableData(data, doc, imageData) { //create the tables without quast output for alignment
    var error = "";
    await readFileData(data).catch((err) => {
                                           error = err;
                                        });
    if(error == "") {
        await readFileData(data).then(newData => {
            doc = createTable(doc, newData, imageData);
        });
    }else {
        return error;
    }
}
