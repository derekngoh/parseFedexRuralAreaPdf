import os, sys
import unittest
import tabula
import csv
import pandas
from parseRuralList import ParseRuralList

class RuralListTestCase(unittest.TestCase):

    countriesRefList = "Country_Names_Ref_List.csv" 
    countriesRefListAbsPath = os.path.join(os.getcwd(), countriesRefList)

    ruralListFileName = "Rural Surcharge Areas.pdf" 
    fileAbsPath = os.path.join(os.getcwd(), ruralListFileName)

    new_Filename = "CSV_Rural_List.csv"
    new_FileAbsPath = os.path.join(os.getcwd(), new_Filename)
    if (os.path.isfile(new_FileAbsPath)):  
        raise NameError("Please ensure filename is unique before proceeding.")

    new_IndexedFilename = "Indexed_CSV_Rural_List.csv"
    new_IndexedFileAbsPath = os.path.join(os.getcwd(), new_IndexedFilename)
    if (os.path.isfile(new_IndexedFileAbsPath)):  
        raise NameError("Please ensure filename for new indexed file is unique before writing.")

    new_CombinedNamesFilename = "Indexed_Rural_List_With_Combined_Country_Names.csv"
    new_CombinedNamesFileAbsPath = os.path.join(os.getcwd(), new_CombinedNamesFilename)
    # if (os.path.isfile(new_CombinedNamesFileAbsPath)):  
    #     raise NameError("Please ensure filename for new combined name indexed file is unique before writing.")

    
    def setUp(self): 
        try:
            tabula.convert_into(type(self).fileAbsPath, type(self).new_Filename, pages = "all")
        except FileNotFoundError:
            print("Please check if PDF file exists before re-running the application.")
        except Exception:
            print(sys.exc_info()[0])

        finally:
            try:
                with open(type(self).new_FileAbsPath, "r") as readF:
                    with open(type(self).new_IndexedFileAbsPath, "w") as writeF:
                        reader = csv.reader(readF)
                        writer = csv.writer(writeF, lineterminator='\n')

                        for row in reader:
                            row.append(reader.line_num)
                            writer.writerow(row)
                    
            except FileNotFoundError:
                print("Something weird has happened. Did you move the file?")
            except Exception:
                print(sys.exc_info()[0])

    def tearDown(self):
        try:
            os.remove(type(self).new_FileAbsPath)
            os.remove(type(self).new_IndexedFileAbsPath)
        except FileNotFoundError:
            print("File may have already been deleted.")
        except Exception:
            print(sys.exc_info()[0])

    def test_newCombinedCountryNameFileCreation(self):
        ParseRuralList.createNewFileWithCombinedCountryName(type(self).new_IndexedFileAbsPath, type(self).new_CombinedNamesFileAbsPath)
        self.assertTrue(os.path.isfile(type(self).new_CombinedNamesFileAbsPath))

    def test_allCountriesAccountedFor(self):
        self.assertTrue(ParseRuralList.accountForAllCountries(type(self).countriesRefListAbsPath, type(self).new_CombinedNamesFileAbsPath))

    def test_splitPagesToColumn(self):
        numOfPages = ParseRuralList.countNumOfPDFPages
        numOfColumns = ParseRuralList.countNumOfColumnsAfterSplit
        self.assertEqual(numOfPages, numOfColumns)



if __name__ == "__main__":
    unittest.main()