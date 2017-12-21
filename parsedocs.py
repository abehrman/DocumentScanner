import pandas as pd
import argparse
import scan_utilities
import cv2
import os
import warnings

def Main(templateFileName, filesDirectory, outputFileName):
    print('Opening template...')
    boxes_df = pd.read_csv(templateFileName)
    boxes = boxes_df.drop('Unnamed: 0', axis=1).to_dict('records')

    for record in boxes:
        record['start'] = [int(x) for x in record['start'].strip("'").strip("()").strip('[]').split(",")]
        record['end'] = [int(x) for x in record['end'].strip("'").strip("()").strip('[]').split(",")]

    outputFile = open('outputs/{}'.format(outputFileName), 'w')
    headers=None

    for document in os.listdir(filesDirectory):
        print('Preprocessing document...{}'.format(document))
        imgPrepped = scan_utilities.prepare_image(filesDirectory + '\\' + document, True, 'thresh')
        print('Scanning results and performing OCR')
        results = scan_utilities.process_image(cv2.imread(imgPrepped), boxes)
        print('Writing output for {}...'.format(document))

        if headers is None:
            headers = []
            for result in results:
                headers.append(result['name'])

            outputFile.write('\t'.join(headers) + '\n')

        vals = []
        for result in results:
            vals.append(result['value'])

        outputFile.write('\t'.join(vals) + '\n')

        os.remove(imgPrepped)

    print('Done...')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--template", required=True,
                    help="template file name")
    ap.add_argument("-p", "--path", type=str, required=True,
                    help="path of files to be processed")
    ap.add_argument("-o", "--output", type=str, required=True,
                    help="output file name")
    args = vars(ap.parse_args())
    # load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it

    Main(args['template'], args['path'], args['output'])