import easyocr
import cv2
import re
import pandas as pd
from sklearn.cluster import DBSCAN


def draw_bounding_boxes(image_path, results):
        # Load the image using OpenCV
        image = cv2.imread(image_path)

        # Loop over each detected text result
        for result in results:
            bbox, text = result  # Bounding box and text

            # Extract coordinates from the bounding box
            (tl_x, tl_y), (tr_x, tr_y), (br_x, br_y), (bl_x, bl_y) = bbox

            # Draw a rectangle around the detected text
            cv2.rectangle(image, (int(tl_x), int(tl_y)), (int(br_x), int(br_y)), (0, 255, 0), 2)

        return image

def display_image(image):
        # Display the image in a window
        cv2.imshow('Invoice with Bounding Boxes', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def extract_text(res):
    data = {
        "bill_to": [],
        "invoice_num":[],
        "total":[],
        "tax":[],
        "date":[]
    }

    for x in res:
        s = x[1]
        if "bill to" in s.lower():
            bill_to = s[8:]
            data["bill_to"].append(bill_to)
        if "billed to" in s.lower():
            bill_to = s[9:]
            data["bill_to"].append(bill_to)
        if "invoice number" in s.lower():
            invoice_num = s[14:]
            data["invoice_num"].append(invoice_num)
        if "invoice #" in s.lower():
            invoice_num = s[9:]
            data["invoice_num"].append(invoice_num)
        if "total" in s.lower():
            total = s[5:]
            data["total"].append(total)
        if "tax" in s.lower():
            #idk for this one
            tax = s
            data["tax"].append(tax)
        if "date" in s.lower():
            date = re.findall(r"\d+l\d+l\d+", s)
            data["date"].append(date)

    return data


def splitText(res):
    data = {
        "bill_to": [],
        "invoice_num": [],
        "total": [],
        "tax": [],
        "date": []
    }
    lines = res.splitlines()
    for i, line in enumerate(lines):
        if "tax" in line.lower():
            tax = re.findall(r"\d+\.\d+(?!.*\d+\.\d+)", line)
            if tax:
                data["tax"].append(tax[0])
        if "total" in line.lower():
            total = re.findall(r"\d+\.\d+(?!.*\d+\.\d+)", line, flags=re.I)
            if not total:
                total = lines[i+1]
                total = total[1:]
            if total:
                data["total"].append(total[0])
        if "invoice #" in line.lower():
            invoice_num = re.findall(r"# (.*)", line)
            if invoice_num:
                data["invoice_num"].append(invoice_num[0])
        if "date" in line.lower():
            date = re.findall(r"\d+l\d+l\d+", line)
            if date:
                data["date"].append(date[0])
    return data


def OCR(file):

    reader = easyocr.Reader(['en'], gpu=True)


    ocr_results = reader.readtext(file, detail=1, paragraph=True)
    d = extract_text(ocr_results)
    #display_image(draw_bounding_boxes(file,ocr_results))

    result = reader.readtext(file)

    data = []
    for entry in result:
        coordinates, text, confidence = entry
        (tl_x, tl_y), (tr_x, tr_y), (br_x, br_y), (bl_x, bl_y) = coordinates
        data.append([text, tl_x, tl_y, tr_x, tr_y, bl_x, bl_y, br_x, br_y, confidence])

    df = pd.DataFrame(data, columns=['text', 'tl_x', 'tl_y', 'tr_x', 'tr_y', 'bl_x', 'bl_y', 'br_x', 'br_y', 'confidence'])

    df['mid_y'] = (df['tl_y'] + df['bl_y']) / 2

    #  DBSCAN Clustering algo
    eps = 5  # !!!!!!! CHANGE IT IF NEEDED !!!!!! max distance to be on one line
    dbscan = DBSCAN(eps=eps, min_samples=1, metric='euclidean')
    df['line_cluster'] = dbscan.fit_predict(df[['mid_y']])

    df_sorted = df.sort_values(by=['line_cluster', 'tl_x'])
    grouped_texts = df_sorted.groupby('line_cluster')['text'].apply(lambda words: " ".join(words)).tolist()
    extracted_text = "\n".join(grouped_texts)



    x = splitText(extracted_text)

    combined = {}



    for key, value in d.items():
        combined[key] = value

    for key,value in x.items():
        if value:
            if key in combined:
                combined[key].append(value[0])
            else:
                combined[key] = value[0]


    for key, x in combined.items():
        for i in x:
            if not i:
                combined[key].remove(i)

    for i in combined['invoice_num']:
        if not re.search(r'\d', i):
            combined['invoice_num'].remove(i)

    for i in combined['total']:
        if re.search(r'[a-z]', i):
            combined['total'].remove(i)

    for i in combined['tax']:
        if re.search(r'[a-z]', i):
            combined['tax'].remove(i)


    data = {}

    for key, item in combined.items():
        if item:
            data[key] = item.pop()

    return data

# basically just go by location if not grouped.

