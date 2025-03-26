import easyocr
import cv2
import re
import pandas as pd
import requests
from sklearn.cluster import DBSCAN
import ollama





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
        if "invoice#" in s.lower():
            invoice_num = s[8:]
            data["invoice_num"].append(invoice_num)
        if re.match(r"(^| )total",s,re.IGNORECASE):
            total = re.findall(r"[\d,]+\.?\d{0,2}(?!.*\d+\.\d+)",s)
            if total:
                data["total"].append(total[0])
        if "tax" in s.lower():
            tax = re.findall(r"[\d,]+\.?\d{0,2}(?!.*\d+\.\d+)",s)
            if tax:
                data["tax"].append(tax[0])
        if "date" in s.lower():
            d = re.findall(r"\d+[\/l\- ][\da-z]+[\/l\- ]\d+",s,re.IGNORECASE)
            if d:
                dd = d[0]
                if "l" in dd:
                    dd.replace("l","/")
                if "due" in s.lower():
                    data["due"].append(dd)
                else:
                    data["date"].append(dd)
        if re.search(r'\d+[ ](?:[A-Za-z0-9.-]+)+\s(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?',s,re.IGNORECASE):
            if not re.search(r'bill(?:ed)? to',s ,re.IGNORECASE):
                if not re.search(r'(ship|sell|sold) to',s, re.IGNORECASE):
                    vendor = re.findall(r'[a-z& ]+',s, re.IGNORECASE)
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
            tax = re.findall(r"[\d,]+\.?\d{0,2}(?!.*\d+\.\d+)", line)
            if tax:
                data["tax"].append(tax[0])
        if re.match(r"(^| )total", line, re.IGNORECASE):
            total = re.findall(r"[\d,]+\.?\d{0,2}(?!.*\d+\.\d+)", line, flags=re.IGNORECASE)
            if not total:
                total = lines[i+1]
                total = total[1:]
            if total:
                data["total"].append(total[0])
        if "invoice #" in line.lower():
            invoice_num = re.findall(r"# (.*)", line)
            if invoice_num:
                data["invoice_num"].append(invoice_num[0])
        if "invoice number" in line.lower():
            invoice_num = re.findall(r"# ([\w\d\- ]+)",line)
            if invoice_num:
                i = invoice_num[0]
                data["invoice_num"].append(i)
        if "invoice#" in line.lower():
            invoice_num = re.findall(r"# ([\w\d\- ]+)",line)
            if invoice_num:
                i = invoice_num[0]
                data["invoice_num"].append(i)
        if "date" in line.lower():
            d = re.findall(r"\d+[\/l\- ][\da-z]+[\/l\- ]\d+", line, re.IGNORECASE)
            if d:
                dd = d[0]
                if "l" in dd:
                    dd.replace("l", "/")
                if "due" in line.lower():
                    data["due"].append(dd)
                else:
                    data["date"].append(dd)
        if re.match(r"sub(t|l)o(t|l)a(t|l)",line,re.IGNORECASE):
            subtotal = re.findall(r"[\d,]+\.?\d{0,2}(?!.*\d+\.\d+)",line)
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
    print("First OCR Pass")
    reader = easyocr.Reader(['en'], gpu=True)


    ocr_results = reader.readtext(file, detail=1, paragraph=True)
    d = extract_text(ocr_results)
    print(d)

    print("Second OCR Pass")
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


    print(x)

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
    missing = 0
    for key, x in combined.items():
        if not x:
            missing = missing + 1
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




    # call for ai for any values not extracted manually
    if missing > 0:
        try:
            response = requests.get("http://localhost:11434")
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            online = True
            print("Ollama AI Online, Attempting To Extract",missing, "Missing Values")
        except requests.exceptions.RequestException:
            online = False
            print("Ollama AI Offline, Some Values May Be Missing")

        if online:
            for key in combined:
                if not combined[key]:
                    item = aiExtraction(file,key)
                    if "NULL" not in item:
                        combined[key].append(item)

    data = {}

    for key, item in combined.items():
        if item:
            t = item.pop()
            if "$" in t:
                t = t[1:]
            if "5" in t[1]:
                t = t[1:]
            data[key] = t

    print("Done")
    return data


def aiExtraction(img, t):
    text = "you will only give me exactly what is written in the picture, no extra characters. if there is no answer, respond with NULL. what is the "
    text = text + t
    res = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                'role':'user',
                'content':text,
                'images':[img]
            }
        ]
    )
    return res['message']['content']


#d = OCR('uploads/invoice1.png')
#print(d)
