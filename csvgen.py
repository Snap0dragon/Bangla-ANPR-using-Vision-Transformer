import os
import xml.etree.ElementTree as ET
import csv
import glob
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_folder(base_dir, folder_name):
    folder_path = os.path.join(base_dir, folder_name)
    img_folder = os.path.join(folder_path, 'img')
    annotation_folder = os.path.join(folder_path, 'annotation')
    csv_file = os.path.join(folder_path, f'{folder_name}_annotations.csv')
    log_file = os.path.join(folder_path, f'{folder_name}_processing_log.txt')

    os.makedirs(folder_path, exist_ok=True)

    processed_count = 0
    skipped_count = 0
    csv_record_count = 0

    with open(csv_file, 'w', newline='') as f, open(log_file, 'w') as log:
        writer = csv.writer(f)
        writer.writerow(['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax', 'license_plate_present'])

        xml_files = glob.glob(os.path.join(annotation_folder, '*.xml'))
        total_files = len(xml_files)

        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                filename = root.find('filename').text
                img_file = os.path.join(img_folder, filename)

                if not os.path.exists(img_file):
                    raise FileNotFoundError(f"Image file not found: {img_file}")

                width = int(root.find('size/width').text)
                height = int(root.find('size/height').text)

                objects = root.findall('object')
                
                if not objects:
                    # No license plate found
                    writer.writerow([filename, width, height, '', '', '', '', '', '0'])
                    csv_record_count += 1
                else:
                    # License plate(s) found
                    for obj in objects:
                        name = obj.find('name').text
                        xmin = int(obj.find('bndbox/xmin').text)
                        ymin = int(obj.find('bndbox/ymin').text)
                        xmax = int(obj.find('bndbox/xmax').text)
                        ymax = int(obj.find('bndbox/ymax').text)

                        writer.writerow([filename, width, height, name, xmin, ymin, xmax, ymax, '1'])
                        csv_record_count += 1


                processed_count += 1

            except Exception as e:
                skipped_count += 1
                error_message = f"Error processing {xml_file}: {str(e)}"
                logging.error(error_message)
                log.write(error_message + '\n')

    logging.info(f"Folder: {folder_name}")
    logging.info(f"Total XML files: {total_files}")
    logging.info(f"Processed XML files: {processed_count}")
    logging.info(f"Skipped XML files: {skipped_count}")
    logging.info(f"Total CSV records written: {csv_record_count}")
    logging.info(f"CSV file created: {csv_file}")
    logging.info(f"Log file created: {log_file}")

    return total_files, processed_count, csv_record_count

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folders = ['train', 'test', 'validation']
    for folder in folders:
        total_files, processed_files, csv_records = process_folder(base_dir, folder)
        if csv_records != total_files:
            logging.warning(f"Mismatch in {folder}: {total_files} XML files, but {csv_records} CSV records")
            logging.warning("This might be due to multiple license plates in some images")

if __name__ == "__main__":
    main()