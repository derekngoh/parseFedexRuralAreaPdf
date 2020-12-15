import csv
import os
from pyPDF2 import PdfFileReader

class ParseRuralList:

    #separate function for cities as some names breaks between columns. Parse cities later after more formatting for more accurate results.
    def createNewFileWithCombinedCountryName(rawCSVRuralListFile, csvCombinedCountryNameList):

        with open(rawCSVRuralListFile, "r") as readRawCSVRuralList:
            with open(csvCombinedCountryNameList, "w") as writeCSVCombinedCountryNamesList:
                readerA = csv.reader(readRawCSVRuralList)
                writerA = csv.writer(writeCSVCombinedCountryNamesList, lineterminator='\n')

                prevRow = next(readerA)

                for rowA in readerA:
                    try:
                        for item in rowA:
                            if (item[0:2] == "- "):
                                itemIndex = rowA.index(item)
                                prevRow[itemIndex] += item[1:]  

                    except StopIteration:
                        break

                    writerA.writerow(prevRow)
                    prevRow = rowA
        
        return

    def getCountriesInRuralList(countryRefList):
        refListOfCountries = []
        with open(countryRefList, "r") as readRefList:
            readerA = csv.reader(readRefList)
            for row in readerA:
                if row[1].strip() != "" and row[1].strip() != "Country Not In Rural List":
                    refListOfCountries.append(row[1].strip())
        return refListOfCountries

    #tally all countries in reference list is in the Rural list
    def accountForAllCountries(countryRefList, ruralList):
        refListOfCountries = getCountriesInRuralList(countryRefList)

        with open(ruralList, "r") as readRuralList:
            readerB = csv.reader(readRuralList)
            for row in readerB:
                for item in row:
                    if item in refListOfCountries: refListOfCountries.remove(item)
        
        if len(refListOfCountries) == 1: return True
        else: return False


    def indexingAllCells(CSVRuralFileWithIndex, countryRefList):
        keyValuePairsForAllCells = {}
        with open(CSVRuralFileWithIndex, "r") as readPageCutIndex:
            for index, row in enumerate(readPageCutIndex):
                for i, item in enumerate(row):
                    key = "R" + index + "C" + i
                    keyValuePairsForAllCells[key] = item

        return keyValuePairsForAllCells

    
    def identifyEndOfPageRow(keyValuePairOfAllCells, countryRefList):
        countryRefList = getCountriesInRuralList(countryRefList)
        rowBreakIndex = []

        for key, value in keyValuePairOfAllCells.items():
            if "C0" in key and value in countryRefList:
                rowBreakIndex.append(key)
        
        return rowBreakIndex


    def splitOnePageToOneColumn(keyValuePairOfAllCells, newCSVFile, countryRefList):
        rowBreakIndex = identifyEndOfPageRow(keyValuePairOfAllCells, countryRefList)
        with open(newCSVFile, "w") as writeOneColumnPerPDFPage:




    def countNumOfColumnsAfterSplit():
        pass



    def countNumOfPDFPages(pathOfPDFFile):
        with open(pathOfPDFFile, 'rb') as f:
            reader = PdfFileReader(f)
            return reader.getNumPages()

