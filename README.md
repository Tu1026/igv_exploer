### Windows compiled exe download here:

https://github.com/Tu1026/igv_exploer/blob/pyqt/dist/IGV%20Tindel.exe

### Build Code

pyinstaller --name "IGV Tindel" -F --icon=APP.ico --add-data="APP.ico;." --add-data="APPICON.png;." --noconsole viewer.py

### Usage (Please read **VERY CARFULLY** )

Please note that the screeshots must be named with this convention **chorm.position.gene.sample.mutantReads.png**

The betastasis file must have the mutant reads contain in the format of (123) or 0:123:0::0

A current known bug is you cannot undo curation on the first image. I will find some time to implement the fix

#### Setup:

- Open up the application
- Select folder option on the top left corner and select option "select screenshot folder". You will ger prompted to select the folder where all the igv screenshots are located.
- (optional for first time) You will get asked if you want to load previous progress, ignore if the first time using app.
- Select the file option at the top left and select the "select betastasis TSV" you will get prompted to select the betastsis TSV that is exported for the webpage. **_Remember to show all silent genes before you export TSV from betastsis_**

You are ready to start curating the mutations!

#### Curation:

Control:

- press q to blacklist a gene
- press e to whitelist a gene
- press w to doubt a gene (all the doubted screeshots will be stored in one file so you can review all of them later)
- press b to go back (undo what you just did, you have unlimited undos meaning you can go all the way back to first screenshot)

Output:
A results folder will be created in the same directory that the app is in.

Inside the folder you will have three files.

- Blacklist file is the standard format that betastasis uses so you can upload this to tambio and let the machine do the blacklisting.

- CuratedFile has all the records of all the screeshot so you can see if something has bee curated, blacklisted or doubted.

- Finally, you have the checklist, which contains all the screenshots that you doubted so you will need to review these.
