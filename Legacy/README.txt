Hello! Welcome to PoliSee, a service created by John Wilmerding to serve congressional offices. Often, it's helpful to have a searchable, sortable, editable, and updatable list of bills that your member has sponsored and cosponsored. Whether you plan to use this list internally or externally, PoliSee is here to help. By the end of this setup, you'll be able to regularly and effortlessly produce Excel spreadsheets or CSV files.

First, let's get your version configured. In your default text editor (Notepad for Windows, TextEdit for Mac), please open the file EDITME.json. It should look something like this in its current state:

{
	"congressNum": "[CONGRESS NUMBER HERE]"
	"memberID": "[MEMBER CODE HERE]"
	"memberLastName": "[MEMBER LAST NAME HERE]"
	"memberFirstName": "[MEMBER FIRST NAME HERE]"
}

Please fill out this JSON file and save it as "creds.json" to the same folder. Here is how it should look before you press save:

{
	"congressNum": "117"
	"memberID": "F000466"
	"memberLastName": "Fitzpatrick"
	"memberFirstName": "Brian"
}

Next, please ensure that you have Python 3 installed. To do this, you can go to your command line and run the following command:

python --version
