import js2py
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-assembly', action="store_true", default=False, dest="assembly")
    parser.add_argument('-alignment', action="store_true", default=False, dest="alignment")
    parser.add_argument('-id ', action="store", default="", dest="id")
    args = parser.parse_args()
    eval_res, js_file = js2py.run_file("/opt/lpf/local_app/js/createReport.js")
    if args.assembly:
        js_file.generatePDFReport(args.id, 'assembly')
    elif args.alignment:
        js_file.generatePDFReport(args.id, 'alignment')

if __name__ == "__main__":
    main()