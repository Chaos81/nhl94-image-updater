# """ Program extracts or updates image assets for teams in a custom Genesis ROM"""
# """ Version 0.3 """
# Version History
# 0.1 - Original Python version with GUI: Import and Export of Images possible - 7/11/22
# 0.2 - Fix collection and import of Rink Logo and Team Logo (do not touch headers)
# 0.3 - Add 32 Team ROM option

from importlib.resources import path
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from IUGui import Ui_imageUpdate
from binascii import b2a_hex, hexlify
from pathlib import Path
import csv
import re
import os
from shutil import copyfile
import struct

class iUpdate(QMainWindow):
    def __init__(self):
        super(iUpdate, self).__init__()

        # User Interface from Designer
        self.ui = Ui_imageUpdate()
        self.ui.setupUi(self)

        # Local Modifications
        self.ui.menubar.setNativeMenuBar(False)  # for MacOS
        self.ui.importBtn.setEnabled(False)
        self.ui.extractBtn.setEnabled(False)

        # Instance Variables
        self.romFile = "No ROM loaded."
        self.tempRomFile = "temp.bin"
        self.romLoaded = False

        # Instance Variables for data
        self.tmptrs = []
        self.imgoffsets = []
        self.teamcnt = 24
        self.romtype = 30
      
        # Connect Actions
        self.ui.actionQuit.triggered.connect(self.cleanUp)
        self.ui.actionLoad_ROM.triggered.connect(self.loadRom)
        self.ui.romBtn.clicked.connect(self.loadRom)
        self.ui.actionExtractImages.triggered.connect(self.extractImages)
        self.ui.extractBtn.clicked.connect(self.extractImages)
        self.ui.actionImportImages.triggered.connect(self.importImages)
        self.ui.importBtn.clicked.connect(self.importImages)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionInstructions.triggered.connect(self.help)

    def cleanUp(self):
        # Remove Temp files before exiting
        if os.path.isfile("temp.bin"):
            os.remove("temp.bin")
        QApplication.quit()

    def clear(self):
        # Clears out data from class variables
        self.tmptrs.clear()
        self.imgoffsets.clear()

    def about(self):
        # About
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("NHL '94 Genesis ROM Image Updater version 0.3.\n\nAny problems or questions, please visit nhl94.com, "
                    "or email: chaos@nhl94.com")
        # msg.setStandardButtons(QMessageBox.OK)
        msg.exec_()

    def help(self):
        # Help
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("NHL '94 Genesis ROM Image Updater version 0.3.\n\n This program is designed to update image assets "
                    "of a custom ROM (team logos, center ice logos, jersey palettes, banners). Before running, "
                    "choose if you are using a 30 team ROM or a 32 team ROM. Please make sure the team names and rosters "
                    " are already set in the ROM, and set the number of active "
                    "teams in the ROM. There are 2 options you can use: \n\nExtract Images:\n Load the ROM in the program, "
                    "set the number of active teams, then click the Extract Images button. The program will output a folder "
                    "ROMs name containing the image assets for each team (listed by their team abbreviation).\n\nImport Images:\n"
                    "The program will use image asset data located in the import folder, and import it into the selected ROM. "
                    "It will only import the image assets that are present in the folder, and the program will notify you of "
                    "which teams were updated, and which were not. Once done, it will ask you for a location and a name to "
                    "save the modified ROM.")
        # msg.setStandardButtons(QMessageBox.OK)
        msg.exec_()

    def loadRom(self):
        # Loads ROM into temp file
        
        # Clear class variables (whenever a new ROM is loaded)
        self.clear() 

        ftypes = "'94 ROM Files, (*.bin *.smc)"
        home = os.path.expanduser('~/Desktop')
        file = QFileDialog.getOpenFileName(self, 'Select ROM', home, ftypes)

        if file[0]:
            with open(file[0], 'rb') as f:
                self.romFile = file[0]
                self.ui.romLabel.setText(self.romFile)
                copyfile(self.romFile, self.tempRomFile)
                self.romLoaded = True

            if self.romLoaded == True:
                self.ui.importBtn.setEnabled(True)
                self.ui.actionImportImages.setEnabled(True)
                self.ui.extractBtn.setEnabled(True)
                self.ui.actionExtractImages.setEnabled(True)

    def getImgOffsets(self):
        # Create Image Offset dictionary, append to the Image Offset list (30 or 32 team ROM)
        # Only storing for the number of active teams
        
        if self.romtype == 32:
            for count in range(0, self.teamcnt):
                # Starting Rink Logo Image Offset - 1E317E (start of first image), 300 each image
                rloffset = int('1E317E', 16) + (int('30A', 16) * count) # 300 + A for header of next image
                print('Rink Logo Offset: ' + str(rloffset))
                #f.seek(rloffset)
                #rlogo = b2a_hex(f.read(int('30A', 16)))
                
                # Starting Team Logo Image Offset - 1D38B0, 4CC each image
                tloffset = int('1D38B0', 16) + (int('4D6', 16) * count) # 4CC + A for header of next image
                print('Team Logo Offset: ' + str(tloffset))
                #f.seek(tloffset)
                #tmlogo = b2a_hex(f.read(int('4D6', 16)))

                # Starting Team Logo Palette Offset - 1D34A6, 20 each palette (Hex)
                lpoffset = int('1D34A6', 16) + (int('20', 16) * count)
                print('Team Logo Palette Offset: ' + str(lpoffset))
                #f.seek(lpoffset)
                #tmlogopal = b2a_hex(f.read(int('20', 16)))

                # Banner Image Offset - 1DD370, 2C0 each banner
                banoffset = int('1DD370', 16) + (int('2C0', 16) * count)
                print('Banner Offset: ' + str(banoffset))
                #f.seek(banoffset)
                #banner = b2a_hex(f.read(int('2C0', 16)))

                # Home/Visitor Palette - 1D1B0A, 40 each palette (Hex)
                hvpaloffset = int('1D1B0A', 16) + (int('40', 16) * count) 
                print('Home/Visitor Palette Offset: ' + str(hvpaloffset))
                #f.seek(hvpaloffset)
                #hmvispal = b2a_hex(f.read(int('40', 16)))

                self.imgoffsets.append(dict(rloffset=rloffset, tloffset=tloffset, lpoffset=lpoffset, banoffset=banoffset, 
                    hvpaloffset=hvpaloffset))
        else:
                
            for count in range(0, self.teamcnt):
                # Starting Rink Logo Image Offset - 1D6F02 (start of first image), 300 each image
                rloffset = int('1D6F02', 16) + (int('30A', 16) * count) # 300 + A for header of next image
                print('Rink Logo Offset: ' + str(rloffset))
                #f.seek(rloffset)
                #rlogo = b2a_hex(f.read(int('30A', 16)))
                
                # Starting Team Logo Image Offset - 1C85B8, 4CC each image
                tloffset = int('1C85B8', 16) + (int('4D6', 16) * count) # 4CC + A for header of next image
                print('Team Logo Offset: ' + str(tloffset))
                #f.seek(tloffset)
                #tmlogo = b2a_hex(f.read(int('4D6', 16)))

                # Starting Team Logo Palette Offset - 1C81EE, 20 each palette (Hex)
                lpoffset = int('1C81EE', 16) + (int('20', 16) * count)
                print('Team Logo Palette Offset: ' + str(lpoffset))
                #f.seek(lpoffset)
                #tmlogopal = b2a_hex(f.read(int('20', 16)))

                # Banner Image Offset - 1D16CC, 2C0 each banner
                banoffset = int('1D16CC', 16) + (int('2C0', 16) * count)
                print('Banner Offset: ' + str(banoffset))
                #f.seek(banoffset)
                #banner = b2a_hex(f.read(int('2C0', 16)))

                # Home/Visitor Palette - 1C6982, 40 each palette (Hex)
                hvpaloffset = int('1C6982', 16) + (int('40', 16) * count) 
                print('Home/Visitor Palette Offset: ' + str(hvpaloffset))
                #f.seek(hvpaloffset)
                #hmvispal = b2a_hex(f.read(int('40', 16)))

                self.imgoffsets.append(dict(rloffset=rloffset, tloffset=tloffset, lpoffset=lpoffset, banoffset=banoffset, 
                    hvpaloffset=hvpaloffset))
                
    
              
    def writeData(self, rom, data):
        # Write data in data list to ROM

        for row in data:
            rom.seek(row[0])
            code = bytes.fromhex(row[1])
            rom.write(code)

    def importImages(self):
        # Retrieve image data from folders, and overwrite the data in the ROM, then save the updated ROM
        # Data for import will be looked for in the import folder
        # Format of dict containing locations should be (abv, hmpal, awpal, tmlogo, tmpal, banner, hmawpal)

        message = ""
        # Set number of Teams

        self.teamcnt = self.ui.numTeams.value()

        # Set ROM Type

        type = self.ui.romType.currentIndex()
        if type == 1:
            self.romtype = 32
        else:
            self.romtype = 30

        # Retrieve Team Pointer List from ROM

        self.tmptrs = self.tm_ptrs()

        # Generate the image offset list

        self.getImgOffsets()

        with open(self.tempRomFile, 'rb+') as f:
            count = 0
            for ptr in self.tmptrs:
                tminfo = self.getTeamInfo(f, ptr)
                result = self.writeToRom(f, ptr, tminfo, count)
                message += result + "\n"
                count += 1
        
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        # msg.setStandardButtons(QMessageBox.OK)
        msg.exec_()

        # Save modified ROM to file

        home = os.path.expanduser('~/Desktop')

        try:
            save = QFileDialog.getSaveFileName(self, "Please choose a name and location for the ROM file...",
                                               home, "*.bin")

            if save[0].lower().endswith('.bin'):
                savefile = save[0]

            else:
                savefile = save[0] + ".bin"

            copyfile(self.tempRomFile, savefile)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("ROM successfully saved to " + savefile + ".")
            # msg.setStandardButtons(QMessageBox.OK)
            msg.exec_()

        except EnvironmentError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Could not save the ROM file.  Please check file permissions.")
            # msg.setStandardButtons(QMessageBox.OK)
            msg.exec_()



    def writeToRom(self, rom, ptr, tminfo, count):
        # Checks is data exists for Team, then writes the data to the ROM

        data = []

        folder = Path("import/" + tminfo['abv'])
        # Does the folder exist?
        if folder.exists():
            # Check each file one by one, and if it exists, read the data, and store it for writing
            # File List:
            # Rink_Logo_Jer_Palette_H.txt
            # Jer_Palette_A.txt
            # Rink_Logo.txt
            # Team_Logo.txt
            # Team_Logo_Palette.txt
            # Banner.txt
            # Home_Visitor_Palette.txt

            # Grab the image offset list for this team position

            offsets = self.imgoffsets[count]
            rjhpal = ptr + 12
            ajpal = ptr + 44

            filename = folder / "Rink_Logo_Jer_Palette_H.txt"
            if Path(filename).exists():
                hexcode = Path(filename).read_text()
                data.append([rjhpal, hexcode])

            filename = folder / "Jer_Palette_A.txt"
            if Path(filename).exists():
                hexcode = Path(filename).read_text()
                data.append([ajpal, hexcode])

            filename = folder / "Rink_Logo.txt"
            if Path(filename).exists():
                hexcode = Path(filename).read_text()
                data.append([offsets['rloffset'], hexcode])

            filename = folder / "Team_Logo.txt"
            if Path(filename).exists():
                hexcode = Path(filename).read_text()
                data.append([offsets['tloffset'], hexcode])

            filename = folder / "Team_Logo_Palette.txt"
            if Path(filename).exists():
                hexcode = Path(filename).read_text()
                data.append([offsets['lpoffset'], hexcode])

            filename = folder / "Banner.txt"
            if Path(filename).exists():
                hexcode = Path(filename).read_text()
                data.append([offsets['banoffset'], hexcode])

            filename = folder / "Home_Visitor_Palette.txt"
            if Path(filename).exists():
                hexcode = Path(filename).read_text()
                data.append([offsets['hvpaloffset'], hexcode])

            self.writeData(rom, data)
            message = tminfo['abv'] + " was updated."

        else:
            # Team did not have any data, so the user will be notified
            message = tminfo['abv'] + " data was not changed."

        # print(data) 
        return message   
    
  
    def tm_ptrs(self):
        # Retrieve Team Offset Pointers

        # Team Offset Start Position:
        # GENS - 782 (030E)

        # Retrieve # of Teams from GUI (right now, maximum of 32)

        numteams = self.teamcnt

        ptrstart = 782

        with open(self.tempRomFile, 'rb') as f:
            f.seek(ptrstart)

            ptrarray = []

            for i in range(0, numteams):

                firsttm = b2a_hex(f.read(4))
                data = int(firsttm, 16)

                print(firsttm)
                print(data)
                ptrarray.append(data)

        return ptrarray

    def getTeamInfo(self, f, ptr):
        # Retrieve Team Info

        # Team Name Data starts at the end of Player Data (offset given in bytes 5 and 6 in Team Data)
        # First offset: Length of Team City (including this byte)
        # AA AA TEAM CITY BB BB TEAM ABV CC CC TEAM NICKNAME DD DD TEAM ARENA
        # AA - Length of Team City (including these 2 bytes)
        # BB - Length of Team Abv (including these 2 bytes)
        # CC - Length of Team Nickname (including these 2 bytes)
        # DD - Length of Team Arena (including these 2 bytes)
        # All Name Data is in ASCII format.

        # Home Logo and Jersey Palette - 12 bytes from start (Dec)
        # Away Logo and Jersey Palette - 44 bytes from start (Dec)

        # Calculate Player Data Space

        # Move to Start of Team Data Bytes
        f.seek(ptr)

        # For GENS
        ploff = int(b2a_hex(f.read(2)), 16)

        # Team Name Data Position Offset - Team Offset + 4 bytes
        f.seek(ptr + 4)
        tmpos = b2a_hex(f.read(2))

        # Home Logo and Jersey Palette
        f.seek(ptr + 12)
        hmpal = f.read(32)

        # Away Logo and Jersey Palette
        f.seek(ptr + 44)
        awpal = f.read(32)

        # Player Data Size = Team Data Offset - Player Data Offset - 2 (last 2 bytes of Player Data - not used)
        plsize = int(tmpos, 16) - ploff - 2

        # Read Team City
        dataoff = ptr + int(tmpos, 16)
        f.seek(dataoff)
        tml = int(b2a_hex(f.read(2)), 16)
        tmcity = f.read(tml - 2).decode("utf-8")

        # Read Team Abv
        tml = int(b2a_hex(f.read(2)), 16)
        tmabv = f.read(tml - 2).decode("utf-8")

        # Read Team Nickname
        tml = int(b2a_hex(f.read(2)), 16)
        tmnm = f.read(tml - 2).decode("utf-8")

        # Remove unwanted characters (due to a bad job of ROM editing)
        tmcity = re.sub('[^A-Za-z ]', '', tmcity)
        tmabv = re.sub('[^A-Za-z]', '', tmabv)
        tmnm = re.sub('[^A-Za-z ]', '', tmnm)

        print(tmcity + tmabv + tmnm)

        return dict(city=tmcity, abv=tmabv, name=tmnm, ploff=str(ploff), plsize=str(plsize), hmpal=hmpal, awpal=awpal)

    def getPlayerInfo(self, f, ptr, ploff, plsize):
        # Retreive Player Info

        # Player Data

        # XX XX "PLAYER NAME" XX 123456789ABCDE

        # XX XX = "Player name length" + 2 (the two bytes in front of the name) in hex

        # ** We are only using Player Name and Jersey Number in this program **

        # "PLAYER NAME"

        # XX =	Jersey # (decimal)

        # 1 = Weight
        # 2 = Agility

        # 3 = Speed
        # 4 = Off. Aware.

        # 5 = Def. Aware.
        # 6 = Shot Power/Puck Control

        # 7 = Checking
        # 8 = Stick Hand (Uneven = Right. Even = Left. 0/1 will do.)

        # 9 = Stick Handling
        # A = Shot Accuracy

        # B = Endurance/StR
        # C = ? (Roughness on Genesis)/StL

        # D = Passing/GlR
        # E = Aggression/GlL

        # Calculate # of Players - Goalies First, then F and D
        # GENS: Ptr + 81 (2 bytes) for G, Ptr + 80 (first nibble F, second D)

        roster = []

        # For GENS
        goff = 80
        poff = 79

        f.seek(ptr + goff)
        gdata = b2a_hex(f.read(2)).decode("utf-8")
        numg = gdata.find("0")

        f.seek(ptr + poff)
        pdata = b2a_hex(f.read(1))
        numf = int(pdata[0:1], 16)
        numd = int(pdata[1:2], 16)

        nump = numg + numf + numd
        print(str(numg) + str(numf) + str(numd))

        # Move to Player Data

        f.seek(ptr + int(ploff))
        j = 0
        plend = ptr + int(ploff) + int(plsize)

        # Retrieve Roster

        while f.tell() < plend:
            # Name and JNo
            # For GENS
            pnl = int(b2a_hex(f.read(2)), 16)

            nm = f.read(pnl - 2).decode("utf-8")
            jno = b2a_hex(f.read(1)).decode("utf-8")
            j += 1

            # G, F or D?

            if j <= numg:
                pos = 'G'
            elif j <= (numg + numf):
                pos = 'F'
            else:
                pos = 'D'

            # Remove unwanted characters (due to a bad job of ROM editing)

            nm = re.sub('[^ A-Za-z]', '', nm)
            print(nm + jno + pos)
            roster.append(dict(name=nm, jno=jno, pos=pos))
            f.seek(7, 1)  # Move to next Player

        return roster

    def writeFiles(self, rom, p, teaminfo, count):
        # Pulls data from ROM, writes to files corresponding to team
        # self.imgoffsets.append(dict(rloffset=rloffset, tloffset=tloffset, lpoffset=lpoffset, banoffset=banoffset, 
        #        hvpaloffset=hvpaloffset))
        
        # Write the Rink Logo/Jersey palette to file
        file = "Rink_Logo_Jer_Palette_H.txt"
        filepath = p / file
        with filepath.open("w", encoding ="utf-8") as f:
            data = teaminfo['hmpal'].hex()
            f.write(data)
        file = "Jer_Palette_A.txt"
        filepath = p / file
        with filepath.open("w", encoding ="utf-8") as f:
            data = teaminfo['awpal'].hex()
            f.write(data)
        
        # Write other logos/palette, these need to be read from the ROM file first
        
        # Rink Logo
        rloffset = self.imgoffsets[count]['rloffset']
        rom.seek(rloffset)
        data = rom.read(int('300', 16)).hex()   # Image is 0x300 bytes
        file = "Rink_Logo.txt"
        filepath = p / file
        with filepath.open("w", encoding ="utf-8") as f:
            f.write(data)

        # Team Logo
        tloffset = self.imgoffsets[count]['tloffset']
        rom.seek(tloffset)
        data = rom.read(int('4CC', 16)).hex()   # Image is 0x4CC bytes  
        file = "Team_Logo.txt"
        filepath = p / file
        with filepath.open("w", encoding ="utf-8") as f:
            f.write(data)

        # Team Logo Palette
        lpoffset = self.imgoffsets[count]['lpoffset']
        rom.seek(lpoffset)
        data = rom.read(int('20', 16)).hex()
        file = "Team_Logo_Palette.txt"
        filepath = p / file
        with filepath.open("w", encoding ="utf-8") as f:
            f.write(data)
        
        # Banner
        banoffset = self.imgoffsets[count]['banoffset']
        rom.seek(banoffset)
        data = rom.read(int('2C0', 16)).hex()
        file = "Banner.txt"
        filepath = p / file
        with filepath.open("w", encoding ="utf-8") as f:
            f.write(data)
        
        # Home/Visitor Palette
        hvpaloffset = self.imgoffsets[count]['hvpaloffset']
        rom.seek(hvpaloffset)
        data = rom.read(int('40', 16)).hex()
        file = "Home_Visitor_Palette.txt"
        filepath = p / file
        with filepath.open("w", encoding ="utf-8") as f:
            f.write(data)
    
    def extractImages(self):
        # Generates folders to store ROM data, and pulls the data from the ROM and stores in files

        # Set number of Teams

        self.teamcnt = self.ui.numTeams.value()

         # Set ROM Type

        type = self.ui.romType.currentIndex()
        if type == 1:
            self.romtype = 32
        else:
            self.romtype = 30

        # Retrieve Team Pointer List from ROM

        self.tmptrs = self.tm_ptrs()

        # Generate the image offset list

        self.getImgOffsets()

        # Remove extension from Rom File name. This will be used as base folder

        romfolder = Path(self.romFile).stem
        # print(romfolder)

        with open(self.tempRomFile, 'rb') as f:
            count = 0
            # Create main folder
            Path(romfolder).mkdir(parents=True, exist_ok=True)
            for ptr in self.tmptrs:
                tminfo = self.getTeamInfo(f, ptr)

                # Create folder for Team
                p = Path(romfolder + "/" + tminfo['abv'])
                p.mkdir(parents=True, exist_ok=True)

                # Write the hex data to files
                self.writeFiles(f, p, tminfo, count)

                count += 1

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Images and Palettes from the ROM have been extracted.")
            # msg.setStandardButtons(QMessageBox.OK)
            msg.exec_()


def main():
    app = QApplication(sys.argv)
    updatetool = iUpdate()
    updatetool.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()