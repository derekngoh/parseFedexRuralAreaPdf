import os, sys
import unittest
import tabula
import csv
import pandas
from parseRuralList import ParseRuralList as prl

class RuralListTestCase(unittest.TestCase):

    def setUp(self): 
        try:
            self.testPrlApp = prl()
            self.ruralPdfList = self.testPrlApp.ruralOriginalPDFFileAbsPath
            self.testPrlApp.createCsvRawRuralList(ruralPdfList)
        except FileNotFoundError:
            print("Please check if PDF file exists before re-running the application.")
        except NameError:
            print(sys.exc_info()[0])

    def tearDown(self):
        try:
            os.remove(self.prl().getRuralRawCsvAbsPath())
        except FileNotFoundError:
            print("File may have already been deleted.")
        except Exception:
            print(sys.exc_info()[0])

    def test_rawCsvFileExists(self):
        self.assertTrue(os.path.isfile(self.testPrlApp.getRuralRawCsvAbsPath()))

    def test_newCombinedCountryNameFileCreation(self):
        rawCsvRuralList = self.testPrlApp.getRuralRawCsvAbsPath()
        self.testPrlApp.createNewFileWithCombinedCountryName(rawCsvRuralList)
        self.assertTrue(os.path.isfile(self.testPrlApp.getCsvCombinedCountryNamesAbsPath()))

    def test_allCountriesAccountedFor(self):
        csvWithCombinedNames = self.testPrlApp.getCsvCombinedCountryNamesAbsPath()
        self.assertTrue(self.testPrlApp.accountForAllCountries(csvWithCombinedNames))

    def test_comparePagesOfOriginalPdfAndCsv(self):
        numOfPdfPages = self.testPrlApp.ruralOriginalPDFNumOfPage
        csvWithCombinedNames = self.testPrlApp.getCsvCombinedCountryNamesAbsPath()
        keyValuePairsOfAllCells = self.testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
        numOfCsvPages = len(self.testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells))
        self.assertEqual(numOfPdfPages, numOfCsvPages)

    def test_compareKeyValueCountWithAndWithoutPage(self):
        csvWithCombinedNames = self.testPrlApp.getCsvCombinedCountryNamesAbsPath()
        keyValuePairsOfAllCells = self.testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
        lenOfKeyValuePairs = len(keyValuePairsOfAllCells)
        rowBreakIndex = self.testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells)
        keyValueWithPageCount = self.testPrlApp.getKeyValuePairsWithPageForCells(keyValuePairsOfAllCells, rowBreakIndex, csvWithCombinedNames)
        lenOfKeyValueWithPageCount = len(keyValueWithPageCount)
        self.assertEqual(lenOfKeyValuePairs, lenOfKeyValueWithPageCount)

    def test_compareRefListCountryCountAndCountryDictCount(self):
        csvWithCombinedNames = self.testPrlApp.getCsvCombinedCountryNamesAbsPath()
        keyValuePairsOfAllCells = self.testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
        rowBreakIndex = self.testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells)
        keyValueWithPages = self.testPrlApp.getKeyValuePairsWithPageForCells(keyValuePairsOfAllCells, rowBreakIndex, csvWithCombinedNames)
        countryRawDictCount = len(self.testPrlApp.countryPostalCodeRawDict(keyValueWithPages, rowBreakIndex))
        refListCount = len(self.testPrlApp.getCountriesInRuralList())-1
        self.assertEqual(refListCount, countryRawDictCount)

    def test_checkNumRangeValues(self):
        sampleRange = "35000-35019"
        sampleParsedRange = ["35000", "35001", "35002", "35003", "35004", "35005", "35006", "35007", "35008", "35009", "35010", "35011", "35012", "35013", "35014", "35015", "35016", "35017", "35018", "35019"]
        parseResult = self.testPrlApp.detectAndParseRange(sampleRange)
        self.assertEqual(parseResult, sampleParsedRange)

    # def test_removeNonApplicableDoubleAsterix(self):
    #     self.testPrlApp = prl()
    #     csvWithCombinedNames = self.testPrlApp.getCsvCombinedCountryNamesAbsPath()
    #     keyValuePairsOfAllCells = self.testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
    #     rowBreakIndex = self.testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells)
    #     keyValueWithPages = self.testPrlApp.getKeyValuePairsWithPageForCells(keyValuePairsOfAllCells, rowBreakIndex, csvWithCombinedNames)
    #     countryRawDict = self.testPrlApp.countryPostalCodeRawDict(keyValueWithPages, rowBreakIndex)


if __name__ == "__main__":
    unittest.main()
