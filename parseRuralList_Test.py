import os, sys
import unittest
import tabula
import csv
import pandas
from parseRuralList import ParseRuralList as prl

class RuralListTestCase(unittest.TestCase):

    def setUp(self): 
        try:
            testPrlApp = prl()
            ruralPdfList = testPrlApp.ruralOriginalPDFFileAbsPath
            testPrlApp.createCsvRawRuralList(ruralPdfList)
        except FileNotFoundError:
            print("Please check if PDF file exists before re-running the application.")
        except NameError:
            print(sys.exc_info()[0])

    def tearDown(self):
        try:
            os.remove(psl.getRuralRawCsvAbsPath())
        except FileNotFoundError:
            print("File may have already been deleted.")
        except Exception:
            print(sys.exc_info()[0])

    def test_rawCsvFileExists(self):
        testPrlApp = prl()
        self.assertTrue(os.path.isfile(testPrlApp.getRuralRawCsvAbsPath()))

    def test_newCombinedCountryNameFileCreation(self):
        testPrlApp = prl()
        rawCsvRuralList = testPrlApp.getRuralRawCsvAbsPath()
        testPrlApp.createNewFileWithCombinedCountryName(rawCsvRuralList)
        self.assertTrue(os.path.isfile(testPrlApp.getCsvCombinedCountryNamesAbsPath()))

    def test_allCountriesAccountedFor(self):
        testPrlApp = prl()
        csvWithCombinedNames = testPrlApp.getCsvCombinedCountryNamesAbsPath()
        self.assertTrue(testPrlApp.accountForAllCountries(csvWithCombinedNames))

    def test_comparePagesOfOriginalPdfAndCsv(self):
        testPrlApp = prl()
        numOfPdfPages = testPrlApp.ruralOriginalPDFNumOfPage
        csvWithCombinedNames = testPrlApp.getCsvCombinedCountryNamesAbsPath()
        keyValuePairsOfAllCells = testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
        numOfCsvPages = len(testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells))
        self.assertEqual(numOfPdfPages, numOfCsvPages)

    def test_compareKeyValueCountWithAndWithoutPage(self):
        testPrlApp = prl()
        csvWithCombinedNames = testPrlApp.getCsvCombinedCountryNamesAbsPath()
        keyValuePairsOfAllCells = testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
        lenOfKeyValuePairs = len(keyValuePairsOfAllCells)
        rowBreakIndex = testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells)
        keyValueWithPageCount = testPrlApp.getKeyValuePairsWithPageForCells(keyValuePairsOfAllCells, rowBreakIndex, csvWithCombinedNames)
        lenOfKeyValueWithPageCount = len(keyValueWithPageCount)
        self.assertEqual(lenOfKeyValuePairs, lenOfKeyValueWithPageCount)

    def test_compareRefListCountryCountAndCountryDictCount(self):
        testPrlApp = prl()
        csvWithCombinedNames = testPrlApp.getCsvCombinedCountryNamesAbsPath()
        keyValuePairsOfAllCells = testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
        rowBreakIndex = testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells)
        keyValueWithPages = testPrlApp.getKeyValuePairsWithPageForCells(keyValuePairsOfAllCells, rowBreakIndex, csvWithCombinedNames)
        countryRawDictCount = len(testPrlApp.countryPostalCodeRawDict(keyValueWithPages, rowBreakIndex))
        refListCount = len(testPrlApp.getCountriesInRuralList())-1
        self.assertEqual(refListCount, countryRawDictCount)

    def test_checkNumRangeValues(self):
        testPrlApp = prl()
        sampleRange = "35000-35019"
        sampleParsedRange = [35000, 35001, 35002, 35003, 35004, 35005, 35006, 35007, 35008, 35009, 35010, 35011, 35012, 35013, 35014, 35015, 35016, 35017, 35018, 35019]
        parseResult = testPrlApp.detectAndParseRange(sampleRange)
        self.assertEqual(parseResult, sampleParsedRange)

    # def test_removeNonApplicableDoubleAsterix(self):
    #     testPrlApp = prl()
    #     csvWithCombinedNames = testPrlApp.getCsvCombinedCountryNamesAbsPath()
    #     keyValuePairsOfAllCells = testPrlApp.getKeyValuePairsNoPageNumForCells(csvWithCombinedNames)
    #     rowBreakIndex = testPrlApp.getRowBreakIndex(keyValuePairsOfAllCells)
    #     keyValueWithPages = testPrlApp.getKeyValuePairsWithPageForCells(keyValuePairsOfAllCells, rowBreakIndex, csvWithCombinedNames)
    #     countryRawDict = testPrlApp.countryPostalCodeRawDict(keyValueWithPages, rowBreakIndex)


if __name__ == "__main__":
    unittest.main()
