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
        "invoice_num":[],
        "total":[],
        "tax":[],
        "date":[],
        "due":[],
        "subTotal":[],
        "vendor":[],
        "email":[]
    }

    for x in res:
        s = x[1]
        if "invoice number" in s.lower():
            invoice_num = s[14:]
            data["invoice_num"].append(invoice_num)
        if "invoice #" in s.lower():
            invoice_num = s[9:]
            data["invoice_num"].append(invoice_num)
        if re.match(r"(^| )total",s,re.IGNORECASE):
            total = re.findall(r"\d+\.\d+(?!.*\d+\.\d+)",s)
            if total:
                data["total"].append(total[0])
        if "tax" in s.lower():
            tax = re.findall(r"\d+\.\d+(?!.*\d+\.\d+)",s)
            if tax:
                data["tax"].append(tax[0])
        if "date" in s.lower():
            date = re.findall(r"\d+l\d+l\d+", s)
            if date:
                data["date"].append(date)
        if re.search(r'\d+[ ](?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?',s):
            if not re.search(r'bill(?:ed)? to',s ,re.IGNORECASE):
                if not re.search(r'(ship|sell|sold) to',s, re.IGNORECASE):
                    vendor = re.findall(r'[a-z ]+',s, re.IGNORECASE)
                    if vendor:
                        vend = vendor[0]
                        if "invoice" in vend.lower():
                            vend = vend[8:]
                        data["vendor"].append(vend)
        if re.match(r"sub(t|l)o(t|l)a(t|l)",s,re.IGNORECASE):
            subtotal = re.findall(r'\d+\.?\d{0,2}',s)
            if subtotal:
                data["subTotal"].append(subtotal[0])

    return data


def splitText(res):
    data = {
        "invoice_num":[],
        "total":[],
        "tax":[],
        "date":[],
        "due":[],
        "subTotal":[],
        "vendor":[],
        "email":[]
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
        if re.match(r"sub(t|l)o(t|l)a(t|l)",line,re.IGNORECASE):
            subtotal = re.findall(r"\d+\.?\d{0,2}",line)
            if subtotal:
                data["subTotal"].append(subtotal[0])
        if "@" in line:
            email = re.findall(r"\w+@\w+\.?\w+",line,re.IGNORECASE)
            if email:
                e = email[0]
                if e:
                    if not re.match(r"\.",e):
                        if "ca" in e:
                            e = e[:len(e)-2] + "." + e[len(e)-2:]
                        if ("com" or "net") in e:
                            e = e[:len(e)-3] + "." + e[len(e)-3:]
                    data["email"].append(e)
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
    eps = 5
    dbscan = DBSCAN(eps=eps, min_samples=1, metric='euclidean')
    df['line_cluster'] = dbscan.fit_predict(df[['mid_y']])

    df_sorted = df.sort_values(by=['line_cluster', 'tl_x'])
    grouped_texts = df_sorted.groupby('line_cluster')['text'].apply(lambda words: " ".join(words)).tolist()
    extracted_text = "\n".join(grouped_texts)



    x = splitText(extracted_text)

    #print(d)
    #print(x)
#combining
    combined = {}



    for key, value in d.items():
        combined[key] = value

    for key,value in x.items():
        if value:
            if key in combined:
                combined[key].append(value[0])
            else:
                combined[key] = value[0]


#cleaning
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

d = OCR('uploads/invoice2.png')
print(d)