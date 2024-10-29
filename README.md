# FTP_Project
Repository dedicated to the project for the partial automation of the process of retrieving files from FTP.
===============

The program is designed to extract files from four distinct FTP networks and transfer them to specific folders within a base directory. After the transfer, the program extracts the file names, which are predominantly PDFs but can also include PNG files. The program removes non-numeric characters from the UC (Consumer unit) sequence present in the file names.

With the file names, the program executes a query in the Oracle database using PL/SQL and exports the results to a spreadsheet. This spreadsheet consists of two main columns: Uc_Cod (numeric sequence) and Cod_Loc (location). Subsequently, the program adds a third column with the current date for each entry in the query.

Next, the program queries a CSV database to replace the Cod_Locs with their respective locations. It adjusts the names of the locations for files originating from a specific folder within the base directory, following the model: Company - São Paulo. After these modifications, the program copies the final results to a base spreadsheet, completing the process.
