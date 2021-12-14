import os
import shutil

import cairosvg
from svglib.svglib import *
from reportlab.graphics import renderPDF, renderPM
from PyPDF2 import PdfFileMerger
import threading
from Py.all_svg2pdf import *
from Py.requester import Digi4SchoolCommunicator
import time

run_Download = False
run_SVG_2_PDF = True
run_PDF_merger = True


# URL to download
bookNr = "4016"
bookUrl = 'https://a.digi4school.at/ebook/' + bookNr + "/"
urlParts = bookUrl.split("/")

# Paths from URL
bookPath = "./" + urlParts[urlParts.__len__() - 2] + "/" + urlParts[urlParts.__len__() - 1]


png = urlParts[urlParts.__len__()-1]

if run_Download:
    if os.path.exists(bookPath) and os.path.isdir(bookPath):
        shutil.rmtree(bookPath)

    for page in range(1, 386):


        print(page)
        pagePath = bookPath + str(page)
        pageUrl = bookUrl + str(page)
        imagePath = pagePath + "/img/"

        name = (3-str(page).__len__())*"0" + str(page)
        svgUrl = pageUrl + "/" + str(page) + ".svg"
        svgPath = pagePath + "/" + name + ".svg"

        for image in range(1, 64):

            #name = (3-str(image).__len__())*"0" + str(image)
            png = str(image) + ".png"
            imageUrl = pageUrl + "/img/" + str(image) + ".png"

            answer = Digi4SchoolCommunicator.get_file(imageUrl)

            if answer == "404" or answer.text.__contains__("Fehler"):
                break
            print("\t image: " + png + " 200 OK")
            os.makedirs(imagePath, 0o777, True)
            open(imagePath + png, 'wb').write(answer.content)



        for shade in range(1, 200):
            #name = (3-str(shade).__len__())*"0" + str(shade)

            shading = str(shade) + ".png"
            imageUrl = pageUrl + "/shade/" + str(shade) + ".png"

            answer = Digi4SchoolCommunicator.get_file(imageUrl)

            if answer == "404" or answer.text.__contains__("Fehler"):
                break
            print("\t shade: " + shading + " 200 OK")
            os.makedirs(pagePath + "/shade", 0o777, True)
            open(pagePath + "/shade/" + shading, 'wb').write(answer.content)

        answer = Digi4SchoolCommunicator.get_file(svgUrl)
        name = (3-str(page).__len__())*"0" + str(page)

        if answer == "404" or answer.text.__contains__("Fehler"):
            break
        print("\t" + name + ".svg" + " 200 OK")
        os.makedirs(pagePath, 0o777, True)
        open(svgPath, 'wb').write(answer.content)

def threaded_svg_converter(svgList):

    startTime = time.time()
    for svg in svgList:
        svgParts = str(svg).split("\\")


        input = svg
        output = "C:\\Users\\sasch\\Documents\\GitHub Reps\\Digi4SchoolDownloader\\Py\\output\\" + svgParts[1].split(".")[0] + ".pdf"

        cairosvg.svg2pdf(file_obj=open(input, "rb+"), write_to=output)
        print(svg)
    print(time.time()-startTime)


if run_SVG_2_PDF:

    if os.path.exists("./output/") and os.path.isdir("./output/"):
        shutil.rmtree("./output/")

    os.makedirs("./output/", 0o777, True)


    svgList = getFileList("./"+bookNr+"/", ".svg")
    # thread1 = threading.Thread(target=threaded_svg_converter, args=(svgList[0:int(nr/4)],)).start()
    # thread2 = threading.Thread(target=threaded_svg_converter, args=(svgList[int(nr/4)+1:int(nr/4)*2],)).start()
    # thread3 = threading.Thread(target=threaded_svg_converter, args=(svgList[int(nr/4)*2+1:int(nr/4)*3],)).start()
    # thread4 = threading.Thread(target=threaded_svg_converter, args=(svgList[int(nr/4)*3+1:int(nr/4)*4],)).start()

    threaded_svg_converter(svgList)


if run_PDF_merger:

    merger = PdfFileMerger()

    for pdf in getFileList("./", ".pdf"):
        merger.append(pdf)

    merger.write("result.pdf")
    merger.close()
