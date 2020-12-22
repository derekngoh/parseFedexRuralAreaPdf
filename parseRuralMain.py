from parseRuralList import ParseRuralList as parse
import os
import sys
import csv


def createDict(WithCanada=False):
    parser = parse()

    csvCombinedCountryNamesAbsPath = parser.getCsvCombinedCountryNamesAbsPath()
    keyValuePairsOfAllCells = parser.getKeyValuePairsNoPageNumForCells(csvCombinedCountryNamesAbsPath)
    rowBreakIndex = parser.getRowBreakIndex(keyValuePairsOfAllCells)

    keyValuePairsWithPages = parser.getKeyValuePairsWithPageForCells(keyValuePairsOfAllCells, rowBreakIndex, csvCombinedCountryNamesAbsPath)

    rawDict = parser.countryPostalCodeRawDict(keyValuePairsWithPages, rowBreakIndex)
    dictRemovedIrrelevant = parser.countryPostalDictRemovedIrrelevant(rawDict)

    postalDict = parser.parseAndAddNumRangeToPostalCodesDict(dictRemovedIrrelevant, WithCanada)

    return postalDict

def createCSVCountryPostalCodeTable(dict, newfilename):
    absFilePath = os.path.join(os.getcwd(), newfilename)
    checkOverwrite = True if os.path.isfile(absFilePath) else False
    postalnum = ""
    postalalpha = ""
    if (not checkOverwrite):
        with open (newfilename, "w") as csvFile:
            writer = csv.writer(csvFile,  lineterminator='\n')
            for country in dict:
                for postalCode in dict[country]:
                    if postalCode.isnumeric(): 
                        postalnum = postalCode
                        postalalpha = ""
                    else: 
                        postalnum = ""
                        postalalpha = postalCode
                    writer.writerow([country, postalnum, postalalpha])


if __name__ == "__main__":
    postalCodeDict = createDict(True)
    createCSVCountryPostalCodeTable(postalCodeDict, "newPostalCodeFileWithCanada.csv")
