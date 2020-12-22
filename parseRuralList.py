import csv
import os
import re
import tabula


class ParseRuralList:

    def __init__(self):
        self.countriesRefList = "Country_Names_Ref_List.csv" 
        self.countriesRefListAbsPath = os.path.join(os.getcwd(), self.countriesRefList)

        self.ruralOriginalPDFFileName = "Rural Surcharge Areas.pdf" 
        self.ruralOriginalPDFFileAbsPath = os.path.join(os.getcwd(), self.ruralOriginalPDFFileName)
        self.ruralOriginalPDFNumOfPage = 67
        self.ruralPDFNumOfColumns = 7

        self.ruralRawCsvFileName = "Rural Surcharge Areas RAW.csv" 
        self.ruralRawCsvFileAbsPath = os.path.join(os.getcwd(), self.ruralRawCsvFileName)

        self.csvCombinedCountryNames = "csvCombinedCountryNames.csv"
        self.csvCombinedCountryNamesAbsPath = os.path.join(os.getcwd(), self.csvCombinedCountryNames)

    def getCountriesRefListAbsPath(self):
        return self.countriesRefListAbsPath

    def getRuralOriginalPDFAbsPath(self):
        return self.ruralOriginalPDFFileAbsPath

    def getRuralOriginalPDFNumOfPage(self):
        return self.ruralOriginalPDFNumOfPage
    
    def getRuralPDFMaxRowPerPageConstraint(self, rowBreakIndex):
        endOfPageOneIndex = rowBreakIndex[1]
        endOfPageTwoIndex = rowBreakIndex[2]
        numOfRowsInPageOne = int(re.search(r'R([0-9]+)', endOfPageOneIndex).group(1))
        numOfRowsInPageTwo = int(re.search(r'R([0-9]+)', endOfPageTwoIndex).group(1))
        return numOfRowsInPageOne+numOfRowsInPageTwo

    def getRuralRawCsvAbsPath(self):
        return self.ruralRawCsvFileAbsPath

    def getCsvCombinedCountryNamesAbsPath(self):
        return self.csvCombinedCountryNamesAbsPath

    def createCsvRawRuralList(self, ruralOriginalPDFFileAbsPath):
        pdfFilePath = ruralOriginalPDFFileAbsPath
        csvFilePath = self.getRuralRawCsvAbsPath()
        tabula.convert_into(pdfFilePath, csvFilePath, pages = "all")
        return csvFilePath


    #separate function for cities as some names breaks between columns. Parse cities later after more formatting for more accurate results.
    def createNewFileWithCombinedCountryName(self, ruralRawCsvFileAbsPath):
        csvCombinedNameAbsPath = self.getCsvCombinedCountryNamesAbsPath()
        with open(ruralRawCsvFileAbsPath, "r") as readRawCsvRuralList:
            with open(csvCombinedNameAbsPath, "w") as writeCsvCombinedCountryNamesList:
                readerA = csv.reader(readRawCsvRuralList)
                writerA = csv.writer(writeCsvCombinedCountryNamesList, lineterminator='\n')

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

        return csvCombinedNameAbsPath

    def getCountriesInRuralList(self):
        refListOfCountries = []
        countryRefList = self.getCountriesRefListAbsPath()
        with open(countryRefList, "r") as readRefList:
            readerA = csv.reader(readRefList)
            for row in readerA:
                if row[1].strip() != "" and row[1].strip() != "Country Not In Rural List":
                    refListOfCountries.append(row[1].strip())
        return refListOfCountries

    #tally all countries in reference list is in the Rural list
    def accountForAllCountries(self, csvCombinedCountryNamesAbsPath):
        refListOfCountries = self.getCountriesInRuralList()

        with open(csvCombinedCountryNamesAbsPath, "r") as readRuralList:
            readerB = csv.reader(readRuralList)
            for row in readerB:
                for item in row:
                    if item in refListOfCountries: refListOfCountries.remove(item)

        if len(refListOfCountries) == 1: return True
        else: return False


    def getKeyValuePairsNoPageNumForCells(self, csvCombinedCountryNamesAbsPath):
        keyValuePairsForAllCells = {}
        with open(csvCombinedCountryNamesAbsPath, "r") as readPageCutIndex:
            reader = csv.reader(readPageCutIndex)
            for index, row in enumerate(reader):
                for i, item in enumerate(row):
                    key = "R" + str(index) + "C" + str(i)
                    keyValuePairsForAllCells[key] = item
        return keyValuePairsForAllCells


    def getRowBreakIndex(self, keyValuePairsOfAllCells):
        countryRefList = self.getCountriesInRuralList()
        rowBreakIndex = []
        for key, value in keyValuePairsOfAllCells.items():
            firstCol = "C0"
            if firstCol in key and value in countryRefList and value!="":
                rowId = re.search(r'R([0-9]+)', key).group(1)
                prevCell = "R"+ str(int(rowId)-1) + firstCol if (rowId != "0") else "R0C0"
                if (prevCell and keyValuePairsOfAllCells[prevCell].strip()):
                    rowBreakIndex.append(key)
        return rowBreakIndex


    def getKeyValuePairsWithPageForCells(self, keyValuePairsOfAllCells, rowBreakIndex, csvCombinedCountryNamesAbsPath):
        countryRefList = self.getCountriesRefListAbsPath()
        keyValuePairsWithPage = {}
        with open(csvCombinedCountryNamesAbsPath, "r") as readCSVRural:
            pageNum = 0
            reader = csv.reader(readCSVRural)
            for index, row in enumerate(reader):
                if index!=0 and ("R" + str(index) + "C0") in rowBreakIndex: 
                    pageNum +=1
                for i, item in enumerate(row):
                    key = "P" + str(pageNum) + "R" + str(index) + "C" + str(i)
                    keyValuePairsWithPage[key] = item
        return keyValuePairsWithPage


    def countryPostalCodeRawDict(self, keyValuePairsWithPages, rowBreakIndex):
        countryRefList = self.getCountriesInRuralList()
        countryPostalRawDict = {}
        firstCountryIndex = "P0R0C0"
        currentCountry = keyValuePairsWithPages[firstCountryIndex]
        currentRow = 0
        currentColumn = 0
        prevRowBreakIndex = 0
        maxPage = self.ruralOriginalPDFNumOfPage
        maxColumnInPdf = self.ruralPDFNumOfColumns

        for page in range(0, maxPage):
            currentRow = prevRowBreakIndex

            currentRowBreakIndex = int(re.search(r'R([0-9]+)', rowBreakIndex[page+1]).group(1)) if page+1<maxPage else int(re.search(r'R([0-9]+)', rowBreakIndex[page]).group(1))

            firstCellOfPage = keyValuePairsWithPages["P"+str(page)+"R"+str(currentRow)+"C0"]

            if (firstCellOfPage in countryRefList and firstCellOfPage!=currentCountry): currentCountry = firstCellOfPage

            if page == maxPage-1: currentRowBreakIndex += self.getRuralPDFMaxRowPerPageConstraint(rowBreakIndex)

            for column in range(0, maxColumnInPdf):
                firstCellOfColumn = keyValuePairsWithPages["P"+str(page)+"R"+str(currentRow)+"C"+str(column)] if "P"+str(page)+"R"+str(currentRow)+"C"+str(column) in keyValuePairsWithPages else currentCountry
                if (firstCellOfColumn in countryRefList and firstCellOfColumn!=currentCountry): currentCountry = firstCellOfColumn
                for row in range(currentRow, currentRowBreakIndex):
                    if row >= currentRowBreakIndex: break
                    key = "P"+str(page)+"R"+str(row)+"C"+str(column)
                    value = keyValuePairsWithPages[key] if key in keyValuePairsWithPages else ""
                    
                    if key in keyValuePairsWithPages:
                        valueInPrevCell = keyValuePairsWithPages["P"+str(page)+"R"+str(row-1)+"C"+str(column)] if (row!=prevRowBreakIndex) else keyValuePairsWithPages["P"+str(page)+"R"+str(row)+"C"+str(column)]
                    else:
                        break

                    if value!="" and value in countryRefList and valueInPrevCell=="": 
                        currentCountry=value

                    if value:
                        if currentCountry in countryPostalRawDict:
                            countryPostalRawDict[currentCountry].append(value)
                        else:
                            countryPostalRawDict[currentCountry] = [value]

            prevRowBreakIndex=currentRowBreakIndex

        return countryPostalRawDict

    
    def countryPostalDictRemovedIrrelevant(self, countryPostalRawDict):
        for country in countryPostalRawDict:
            postalCodeRemoved = []
            for postalCode in countryPostalRawDict[country]:
                if "**" in postalCode: 
                    countryPostalRawDict[country].remove(postalCode)
                    postalCodeRemoved.append(postalCode)
                if "**" not in postalCode and "*" in postalCode: 
                    index = countryPostalRawDict[country].index(postalCode)
                    postalCodeRemovedSingleAsterix = postalCode.replace("*", "")
                    countryPostalRawDict[country].remove(postalCode)
                    countryPostalRawDict[country].insert(index, postalCodeRemovedSingleAsterix)
                    postalCodeRemoved.append(postalCode)

        return countryPostalRawDict


    def detectZeroPadding(self, startNum, endNum):
        startNumPadCount = 0
        endNumPadCount = 0
        for num in startNum:
            if num=="0": startNumPadCount+=1
            else: break
        for num in endNum:
            if num=="0": endNumPadCount+=1
            else: break
        
        if startNumPadCount == endNumPadCount: return startNumPadCount*"0"
        else: raise(SyntaxError("Some postal codes have differing zreo paddings within a range"))


    def detectAndParseRange(self, valueWithNumberRange):
        numStart, numEnd = valueWithNumberRange.split("-")
        padding = self.detectZeroPadding(numStart, numEnd)
        numStart = int(numStart)
        numEnd = int(numEnd)
        indPostalCodeBetweenRange = []
        rangeInBetweenStartAndEnd = numEnd-numStart
        for i in range(rangeInBetweenStartAndEnd):
            num = numStart
            postalCodeToAdd = padding + str(num)
            indPostalCodeBetweenRange.append(postalCodeToAdd)
            numStart += 1
        indPostalCodeBetweenRange.append(padding + str(numEnd))
        return indPostalCodeBetweenRange

    def parseCanadianPostalRange(self, canadianPostalRange):
        indPostalCodesBetweenRange = []
        delimiter = "-"
        start, end = canadianPostalRange.split(delimiter)
        if re.search(r'^[A-Z][0-9][A-Z][0-9][A-Z][0-9]$', start) != None and re.search(r'^[A-Z][0-9][A-Z][0-9][A-Z][0-9]$', end) != None:
            if start[0:3] != end[0:3]:
                raise(SyntaxError("The first half of the postal code should be the same for start and end of a range."))
            else:
                hundredsStart = int(start[3])
                hundredsEnd = int(end[3]) + 1
                if hundredsStart>hundredsEnd: raise(SyntaxError("Range started with larger number than end."))
                for hundreds in range(hundredsStart, hundredsEnd):
                    tensStart = ord(start[4]) if (hundreds==hundredsStart) else ord("A")
                    tensEnd = ord(end[4]) if (hundreds==hundredsEnd) else ord("Z")+1
                    for tens in range(tensStart, tensEnd):
                        onesStart = int(start[5]) if (tens==tensStart) else 0
                        onesEnd = int(end[5]) if (tens==tensEnd) else 10 
                        for ones in range(onesStart, onesEnd):
                            currentLastThreeCharacter = str(hundreds) + chr(tens) + str(ones)
                            indPostalCode = start[0:3] + currentLastThreeCharacter
                            indPostalCodesBetweenRange.append(indPostalCode)
        
        return indPostalCodesBetweenRange


    def parseAndAddNumRangeToPostalCodesDict(self, countryPostalDictRemovedIrrelevant, withCanada=False):
        newCountryPostalCodeDict = countryPostalDictRemovedIrrelevant
        for country in countryPostalDictRemovedIrrelevant:
            for postalCodeEntry in countryPostalDictRemovedIrrelevant[country]:
                indexOfPostalCodeEntry = newCountryPostalCodeDict[country].index(postalCodeEntry)
                delimiter = "-"
                if delimiter in postalCodeEntry and postalCodeEntry.count(delimiter)==1:
                    if country=="Canada" and withCanada:
                        indPostalCodeInRangeCanada = self.parseCanadianPostalRange(postalCodeEntry)
                        newCountryPostalCodeDict[country].remove(postalCodeEntry)
                        newCountryPostalCodeDict[country][indexOfPostalCodeEntry:indexOfPostalCodeEntry]=indPostalCodeInRangeCanada
                    else:
                        start, end = postalCodeEntry.split(delimiter)
                        if start.isnumeric() and end.isnumeric():
                            indPostalCodeInRange = self.detectAndParseRange(postalCodeEntry)
                            newCountryPostalCodeDict[country].remove(postalCodeEntry)
                            newCountryPostalCodeDict[country][indexOfPostalCodeEntry:indexOfPostalCodeEntry]=indPostalCodeInRange
        return newCountryPostalCodeDict






