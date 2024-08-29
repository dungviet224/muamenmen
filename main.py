import sys
import os
import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QStackedWidget, 
                             QFormLayout, QHBoxLayout, QCheckBox, QComboBox, QFileDialog)
from selenium.webdriver.common.by import By
from threading import Thread, Event, Lock
from PyQt5.QtCore import Qt
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from PyQt5.QtWidgets import QLabel
from PIL import Image
import io
import base64
import random
import win32clipboard

import pyperclip
from selenium.webdriver.common.keys import Keys
CONFIG_FILE = 'cfg.json'
from PyQt5.QtGui import QImage
from selenium.webdriver.common.action_chains import ActionChains

import pkgutil
import subprocess
import sys

# Get all imported modules
imported_modules = {name for _, name, _ in pkgutil.iter_modules()}

# Install all the imported modules
subprocess.run([sys.executable, "-m", "pip", "install"] + list(imported_modules))


class FacebookGroupSearcher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadSettings()
        self.stop_event = Event()
        self.search_thread = None
        self.driver = None
        self.results_data = []
        self.failed_groups_data = []
        self.failed_groups_lock = Lock()
        self.title_sort_order = 0  # 0: original, 1: A-Z, 2: Z-A
        self.members_sort_order = 0  # 0: original, 1: high-to-low, 2: low-to-high

    def initUI(self):
        self.setWindowTitle('MEO BEO THICH MAC DO NO')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        # Create the stacked widget for page switching
        self.stackedWidget = QStackedWidget()

        # Create the search page and the settings page
        self.createSearchPage()
        self.createPostPage()
        self.createSettingsPage()
        

        # Add the pages to the stacked widget
        self.stackedWidget.addWidget(self.searchPage)
        self.stackedWidget.addWidget(self.settingsPage)
        self.stackedWidget.addWidget(self.postPage)

        # Create a horizontal layout for the tabs at the top
        tabLayout = QHBoxLayout()
        self.searchTabButton = QPushButton('Search')
        self.searchTabButton.clicked.connect(lambda: self.switchTab(self.searchPage))
        tabLayout.addWidget(self.searchTabButton)

        self.settingsTabButton = QPushButton('Settings')
        self.settingsTabButton.clicked.connect(lambda: self.switchTab(self.settingsPage))
        tabLayout.addWidget(self.settingsTabButton)
        self.postTabButton = QPushButton('Post')
        self.postTabButton.clicked.connect(lambda: self.switchTab(self.postPage))
        tabLayout.addWidget(self.postTabButton)


        
        # Add the tab layout and the stacked widget to the main layout
        layout.addLayout(tabLayout)
        layout.addWidget(self.stackedWidget)

        # Add buttons for clear console and export
        buttonLayout = QHBoxLayout()
        self.clearConsoleButton = QPushButton('Clear Console')
        self.clearConsoleButton.clicked.connect(self.clearConsole)
        buttonLayout.addWidget(self.clearConsoleButton)

        self.exportButton = QPushButton('Export')
        self.exportButton.clicked.connect(self.exportResults)
        buttonLayout.addWidget(self.exportButton)

        # Add sorting buttons
        self.sortByTitleButton = QPushButton('Sort by Title (A-Z)')
        self.sortByTitleButton.clicked.connect(self.sortByTitle)
        buttonLayout.addWidget(self.sortByTitleButton)

        self.sortByMembersButton = QPushButton('Sort by Members (High to Low)')
        self.sortByMembersButton.clicked.connect(self.sortByMembers)
        buttonLayout.addWidget(self.sortByMembersButton)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

        # Initialize the first tab as active
        self.switchTab(self.searchPage)

    def switchTab(self, widget):
        # Switch to the selected widget
        self.stackedWidget.setCurrentWidget(widget)

        # Update the style to show which tab is active
        if widget == self.searchPage:
            self.searchTabButton.setStyleSheet("background-color: #D3D3D3;")
            self.settingsTabButton.setStyleSheet("")
        else:
            self.searchTabButton.setStyleSheet("")
            self.settingsTabButton.setStyleSheet("background-color: #D3D3D3;")

    def createSearchPage(self):
        self.searchPage = QWidget()
        layout = QVBoxLayout()

        self.searchBox = QTextEdit()
        self.searchBox.setPlaceholderText('Enter search term...')
        layout.addWidget(self.searchBox)

        self.keywordFilterBox = QLineEdit()
        self.keywordFilterBox.setPlaceholderText('Enter keyword to filter titles...')
        self.keywordFilterBox.textChanged.connect(self.filterResults)
        layout.addWidget(self.keywordFilterBox)

        self.startSearchButton = QPushButton('Start Search')
        self.startSearchButton.clicked.connect(self.startSearch)
        layout.addWidget(self.startSearchButton)

        self.stopButton = QPushButton('Stop')
        self.stopButton.clicked.connect(self.stopSearch)
        layout.addWidget(self.stopButton)

        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(4)
        self.resultTable.setHorizontalHeaderLabels(['Title', 'Link', 'Members', 'Privacy'])
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resultTable.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.resultTable)

        self.statusLabel = QLabel('Status: Ready')
        layout.addWidget(self.statusLabel)

        self.searchPage.setLayout(layout)

    def createSettingsPage(self):
        self.settingsPage = QWidget()
        layout = QFormLayout()

        self.profileCreationButton = QPushButton('Create New Profile')
        self.profileCreationButton.clicked.connect(self.createNewProfile)
        layout.addRow(self.profileCreationButton)

        # ComboBox to select the profile subfolder
        self.profileComboBox = QComboBox()
        layout.addRow("Profile Subfolder:", self.profileComboBox)

        self.minMembersCheckBox = QCheckBox("Minimum Members")
        self.minMembersCheckBox.stateChanged.connect(self.toggleMinMembers)
        layout.addWidget(self.minMembersCheckBox)

        self.minMembersInput = QLineEdit()
        self.minMembersInput.setPlaceholderText("Enter minimum number of members")
        self.minMembersInput.setDisabled(True)
        layout.addWidget(self.minMembersInput)

        self.privacyComboBox = QComboBox()
        self.privacyComboBox.addItems(["Public", "All"])
        layout.addRow("Privacy:", self.privacyComboBox)

        self.filterByKeywordsCheckBox = QCheckBox("Filter Group by Keywords")
        self.filterByKeywordsCheckBox.stateChanged.connect(self.toggleFilterByKeywords)
        layout.addWidget(self.filterByKeywordsCheckBox)

        self.keywordsInput = QLineEdit()
        self.keywordsInput.setPlaceholderText("Enter keywords separated by commas")
        self.keywordsInput.setDisabled(True)
        layout.addWidget(self.keywordsInput)

        self.openCloseBrowserButton = QPushButton('Open Browser')
        self.openCloseBrowserButton.clicked.connect(self.toggleBrowser)
        layout.addWidget(self.openCloseBrowserButton)
        # Check box for "Like Post"
        self.likePostCheckBox = QCheckBox("Like Post")
        layout.addWidget(self.likePostCheckBox)

        # Check box for "Comment"
        self.commentCheckBox = QCheckBox("Comment")
        self.commentCheckBox.stateChanged.connect(self.toggleCommentInput)
        layout.addWidget(self.commentCheckBox)

        self.commentInput = QLineEdit()
        self.commentInput.setPlaceholderText("Enter comment text")
        self.commentInput.setDisabled(True)
        layout.addWidget(self.commentInput)

        # Check box for "Enter Content Word by Word"
        self.enterContentCheckBox = QCheckBox("Enter Content Slow (Icon not working)")
        self.enterContentCheckBox.stateChanged.connect(self.toggledelaytype)
        layout.addWidget(self.enterContentCheckBox)

        self.delaytype = QLineEdit()
        self.delaytype.setPlaceholderText("Enter delay in milliseconds (default is 0.005)")
        self.delaytype.setDisabled(True)
        layout.addWidget(self.delaytype)
        # Add the "Save Settings" button
        self.saveSettingsButton = QPushButton('Save Settings')
        self.saveSettingsButton.clicked.connect(self.saveSettings)
        layout.addWidget(self.saveSettingsButton)



        self.settingsPage.setLayout(layout)

    def toggleCommentInput(self, state):
        self.commentInput.setDisabled(state == 0)

    def toggledelaytype(self, state):
        self.delaytype.setDisabled(state == 0)

    def createPostPage(self):
        self.postPage = QWidget()
        layout = QVBoxLayout()

        # Text box for post content
        self.postContent = QTextEdit()
        self.postContent.setPlaceholderText('Enter post content...')
        self.postContent.setFixedHeight(100)  # Adjust the height as needed
        layout.addWidget(self.postContent)

        # Checkbox to enable or disable image selection
        self.enableImageCheckbox = QCheckBox("Attach an Image")
        self.enableImageCheckbox.stateChanged.connect(self.toggleImageSelection)
        layout.addWidget(self.enableImageCheckbox)

        # Button to select an image (initially hidden)
        self.selectImageButton = QPushButton('Select Image')
        self.selectImageButton.clicked.connect(self.selectImage)
        self.selectImageButton.setDisabled(True)  # Disable by default
        layout.addWidget(self.selectImageButton)

        # Label to display the selected image path
        self.imagePathLabel = QLabel('No image selected')
        layout.addWidget(self.imagePathLabel)

        # Button to post content
        self.postButton = QPushButton('Post Content')
        self.postButton.clicked.connect(self.startPosting)
        layout.addWidget(self.postButton)

        # New Stop Posting Button
        self.stopPostButton = QPushButton('Stop')
        self.stopPostButton.clicked.connect(self.stopPosting)
        layout.addWidget(self.stopPostButton)

        # New Delay Input
        self.delayInput = QLineEdit()
        self.delayInput.setPlaceholderText("Delay (seconds) between links")
        layout.addWidget(self.delayInput)

        # New Post Status Label
        self.postStatusLabel = QLabel('Status: Ready to post')
        layout.addWidget(self.postStatusLabel)

        # New Results Table
        self.resultTableaa = QTableWidget()
        self.resultTableaa.setColumnCount(4)
        self.resultTableaa.setHorizontalHeaderLabels(['Select', 'Title', 'Link', 'Status'])
        self.resultTableaa.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resultTableaa.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.resultTableaa)

        # New Load File Button
        self.loadFileButton = QPushButton('Load File')
        self.loadFileButton.clicked.connect(self.loadFile)
        layout.addWidget(self.loadFileButton)

        # New Select All Checkbox
        self.selectAllCheckBox = QCheckBox("Select All")
        self.selectAllCheckBox.stateChanged.connect(self.selectAll)
        layout.addWidget(self.selectAllCheckBox)

        self.postPage.setLayout(layout)

    def selectAll(self, state):
        # Set the check state for all items in the table
        check_state = Qt.Checked if state == Qt.Checked else Qt.Unchecked
        for row in range(self.resultTableaa.rowCount()):
            item = self.resultTableaa.item(row, 0)
            if item:
                item.setCheckState(check_state)

    def loadFile(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        
        if not file_path:
            return
        
        self.loadLinksFromExcel(file_path)

    def loadLinksFromExcel(self, file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            if 'Title' in df.columns and 'Link' in df.columns:
                self.resultTableaa.setRowCount(0)
                for index, row in df.iterrows():
                    self.resultTableaa.insertRow(index)
                    self.resultTableaa.setItem(index, 1, QTableWidgetItem(row['Title']))
                    self.resultTableaa.setItem(index, 2, QTableWidgetItem(row['Link']))
                    self.resultTableaa.setItem(index, 3, QTableWidgetItem('waiting...'))
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setCheckState(Qt.Unchecked)
                    self.resultTableaa.setItem(index, 0, checkbox_item)
        except Exception as e:
            self.postStatusLabel.setText(f'Status: Error loading file - {e}')

    def toggleImageSelection(self):
        self.selectImageButton.setEnabled(self.enableImageCheckbox.isChecked())
        if not self.enableImageCheckbox.isChecked():
            self.imagePathLabel.setText('No image selected')
            self.selected_image_path = None

    def stopPosting(self):
        # Set the stop event to signal the thread to stop
        self.stop_event.set()

        # Update the status label
        self.postStatusLabel.setText('Status: Posting stopped.')

        QApplication.processEvents()
        self.closeDriver()

    def selectImage(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", options=options)
        if file_path:
            self.selected_image_path = file_path
            self.imagePathLabel.setText(f'Selected Image: {file_path}')
            print(file_path)
        else:
            self.imagePathLabel.setText('No image selected')

    def startPosting(self):
        # Start the posting operation in a separate thread
        self.stop_event.clear()
        self.search_thread = Thread(target=self.processSelectedLinks)
        self.search_thread.start()

    def reloadTableState(self):
        # Force table to repaint
        self.resultTableaa.viewport().update()

    def processSelectedLinks(self):
        selected_links = []
        for row in range(self.resultTableaa.rowCount()):
            item = self.resultTableaa.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                link = self.resultTableaa.item(row, 2).text()
                selected_links.append((row, link))
        
        total_links = len(selected_links)
        if total_links == 0:
            self.postStatusLabel.setText('Status: No links selected.')
            return
        
        self.postStatusLabel.setText(f'Status: Processing 1/{total_links}')
        delay = int(self.delayInput.text()) if self.delayInput.text().isdigit() else 0
        
        # Initialize WebDriver here if needed

        
        for index, (row, link) in enumerate(selected_links):
            self.initDriver()
            if self.stop_event.is_set():
                self.postStatusLabel.setText('Status: Posting stopped.')
                break
            
            # Open the link
            status_itema = QTableWidgetItem('Processing ⏳')
            self.resultTableaa.setItem(row, 3, status_itema)
            self.reloadTableState()
            self.driver.get(link)
            time.sleep(2)  # Wait for the page to load; adjust if necessary
            
            # Post content to group
            self.postContentToGroup()
            
            # Update the status of the link in the table
            status_item = QTableWidgetItem('complete ✅')
            self.resultTableaa.setItem(row, 3, status_item)
            
            # Force the UI to update immediately
            self.resultTableaa.repaint()  # Or QApplication.processEvents()
            
            self.postStatusLabel.setText(f'Status: Processing {index + 1}/{total_links}')
            time.sleep(delay)
        
        self.postStatusLabel.setText('Status: All links processed.')
        self.driver.quit()



    def like_posts(self):
        if self.likePostCheckBox.isChecked():
            print("Bắt đầu quá trình like các bài đăng...")

            # Tìm tất cả các bài đăng trong feed
            posts = self.driver.find_elements(By.CSS_SELECTOR, "div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z")
            print(f"Tìm thấy {len(posts)} bài đăng.")

            # Chọn ngẫu nhiên số lượng post cần like từ 1 đến 5
            num_posts_to_like = random.randint(1, 5)
            print(f"Số bài đăng sẽ like: {num_posts_to_like}")

            for i in range(num_posts_to_like):
                try:
                    # Tìm nút like trong mỗi bài đăng
                    like_button = posts[i].find_element(By.CSS_SELECTOR, "div.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x16tdsg8.x1hl2dhg.x1ja2u2z.x1t137rt.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x3nfvp2.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.x5ve5x3")
                    print(f"Đã tìm thấy nút like cho bài đăng thứ {i + 1}.")

                    # Click vào nút like
                    like_button.click()
                    print(f"Đã like bài đăng thứ {i + 1}.")
                    time.sleep(1)  # Delay giữa các thao tác

                except Exception as e:
                    print(f"Lỗi khi like bài đăng thứ {i + 1}: {e}")
                    continue


    def comment(self):
        if self.commentCheckBox.isChecked():
            print("Bắt đầu quá trình comment...")

            posts = self.driver.find_elements(By.CSS_SELECTOR, "div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z")
            print(f"Tìm thấy {len(posts)} bài đăng.")

            try:
                comment_text = self.commentInput.text().split(',')
                print(f"Các comment có thể sử dụng: {comment_text}")
                comment_button =self.driver.find_element(By.XPATH, "//div[@aria-label='Viết bình luận']")
                comment_button.click()
                # Chọn ngẫu nhiên 1 từ từ danh sách comment
                random_comment = random.choice(comment_text).strip()
                print(f"Sẽ comment: {random_comment}")
                input_field = self.driver.find_element(By.XPATH, "//div[@role='textbox']") 
                # Gửi comment
                input_field.click()  # Click vào ô comment trước khi gửi
                time.sleep(1)  # Delay nhỏ trước khi nhập nội dung
                input_field.send_keys(random_comment)
                print("Đã nhập nội dung comment.")
                time.sleep(1)  # Delay trước khi gửi
                input_field.send_keys(Keys.RETURN)  # Gửi comment
                print("Đã gửi comment.")

            except Exception as e:
                print(f"Lỗi khi comment: {e}")




                    


    def postContentToGroup(self):
        # Kiểm tra nếu driver đã được khởi tạo
        if self.driver:



            # Nhấp vào ô để tạo bài đăng
            self.driver.find_element(By.CSS_SELECTOR, "div[class='xi81zsa x1lkfr7t xkjl1po x1mzt3pk xh8yej3 x13faqbe'] span[class='x1lliihq x6ikm8r x10wlt62 x1n2onr6']").click()
            time.sleep(3)
            post_content = self.postContent.toPlainText()

            
            # Kiểm tra nếu người dùng không nhập delay thì sử dụng giá trị mặc định 0.005
            delaytype = float(self.delaytype.text() or 0.005)  

            if self.enterContentCheckBox.isChecked():
                # Nếu "Enter Content Word by Word" được kích hoạt
                for char in post_content:
                    self.driver.find_element(By.CSS_SELECTOR, "div[data-contents='true']").send_keys(char)
                    time.sleep(delaytype)
            else:
                # Nếu "Enter Content Word by Word" không được kích hoạt
                pyperclip.copy(post_content)
                self.driver.find_element(By.CSS_SELECTOR, "div[data-contents='true']").send_keys(Keys.CONTROL + 'v')

            # Nếu có hình ảnh đã chọn
            if hasattr(self, 'selected_image_path') and os.path.exists(self.selected_image_path):
                # Sao chép hình ảnh vào clipboard
                image = Image.open(rf'{self.selected_image_path}')
                output = io.BytesIO()
                image.save(output, format='BMP')
                data = output.getvalue()[14:]  # Bỏ qua tiêu đề BMP

                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()

                # Dán hình ảnh vào textbox
                text_box = self.driver.find_element(By.CSS_SELECTOR, "div[data-contents='true']")
                text_box.click()  # Đảm bảo textbox được chọn
                text_box.send_keys(Keys.CONTROL + 'v')  # Dán từ clipboard

            max_attempts = 2
            attempt = 0
            time.sleep(3)

            while attempt < max_attempts:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, "div[class='x9f619 x1n2onr6 x1ja2u2z x78zum5 x2lah0s x1qughib x1qjc9v5 xozqiw3 x1q0g3np x1pi30zi x1swvt13 xyamay9 xykv574 xbmpl8g x4cne27 xifccgj'] div[class='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xsyo7zv x16hj40l x10b6aqq x1yrsyyn']")
                    element.click()
                    time.sleep(2)
                    attempt += 1
                except:
                    # Nếu không thấy element, tiếp tục thao tác tiếp theo
                    break
            print("posted wait for like and comment")
            time.sleep(20)
            self.comment()
            print("comment")
            self.like_posts()
            print("like")

            time.sleep(10)



    def updateProfileComboBox(self):
        path = self.chromeProfilePath.text().strip()
        self.profileComboBox.clear()

        if os.path.exists(path) and os.path.isdir(path):
            subfolders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
            self.profileComboBox.addItems(subfolders)
    
    def toggleBrowser(self):
        if self.driver is None:
            self.openBrowser()
        else:
            self.closeBrowser()

    def openBrowser(self):
        if self.driver is None:
            selected_profile = self.profileComboBox.currentText()
            profile_path = os.path.join(os.getcwd(), selected_profile)
            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={profile_path}")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.openCloseBrowserButton.setText('Close Browser')
            self.statusLabel.setText('Status: Browser opened.')

    def closeBrowser(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.openCloseBrowserButton.setText('Open Browser')
            self.statusLabel.setText('Status: Browser closed.')

    def loadSettings(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
                self.updateProfileComboBox()
                profile_subfolder = config.get("profile_subfolder", "")
                if profile_subfolder in [self.profileComboBox.itemText(i) for i in range(self.profileComboBox.count())]:
                    self.profileComboBox.setCurrentText(profile_subfolder)
                self.minMembersCheckBox.setChecked(config.get("min_members_enabled", False))
                self.minMembersInput.setText(config.get("min_members", ""))
                privacy_index = ["Public", "All"].index(config.get("privacy", "All"))
                self.privacyComboBox.setCurrentIndex(privacy_index)

                # Load additional settings
                self.likePostCheckBox.setChecked(config.get("like_post_enabled", False))
                self.commentCheckBox.setChecked(config.get("comment_enabled", False))
                self.commentInput.setText(config.get("comment_text", ""))
                self.enterContentCheckBox.setChecked(config.get("enter_content_word_by_word", False))
                self.delaytype.setText(config.get("delay_in_ms", ""))

        else:
            self.saveSettings()

    def saveSettings(self):
        config = {
            "profile_subfolder": self.profileComboBox.currentText(),
            "min_members_enabled": self.minMembersCheckBox.isChecked(),
            "min_members": self.minMembersInput.text(),
            "privacy": self.privacyComboBox.currentText(),
            
            # Save additional settings
            "like_post_enabled": self.likePostCheckBox.isChecked(),
            "comment_enabled": self.commentCheckBox.isChecked(),
            "comment_text": self.commentInput.text(),
            "enter_content_word_by_word": self.enterContentCheckBox.isChecked(),
            "delay_in_ms": self.delaytype.text()
        }
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        self.statusLabel.setText('Status: Settings saved.')



    def toggleMinMembers(self):
        # Enable or disable the minimum members input based on checkbox state
        self.minMembersInput.setEnabled(self.minMembersCheckBox.isChecked())

    def toggleFilterByKeywords(self):
        self.keywordsInput.setEnabled(self.filterByKeywordsCheckBox.isChecked())

    def normalizePath(self):
        # Normalize the path to use forward slashes
        path = self.chromeProfilePath.text()
        normalized_path = path.replace('\\', '/')
        self.chromeProfilePath.setText(normalized_path)


    def createNewProfile(self):
        # Generate a unique profile name
        profile_name = f'Profile_{int(time.time())}'
        profile_path = os.path.join(os.getcwd(), profile_name)

        if not os.path.exists(profile_path):
            os.makedirs(profile_path)

        # Update profile dropdown
        self.updateProfileComboBox()

    def updateProfileComboBox(self):
        # Get all profiles in the application directory
        profile_dir = os.getcwd()
        subfolders = [f for f in os.listdir(profile_dir) if os.path.isdir(os.path.join(profile_dir, f))]
        self.profileComboBox.clear()
        self.profileComboBox.addItems(subfolders)
        
    

    def startSearch(self):
        query = self.searchBox.toPlainText().strip()
        if not query:
            self.statusLabel.setText('Status: Please enter a search term.')
            return

        self.statusLabel.setText('Status: Starting search...')
        self.stop_event.clear()
        self.results_data = []
        self.failed_groups_data = []

        if self.search_thread is None or not self.search_thread.is_alive():
            self.search_thread = Thread(target=self.searchGroups, args=(query,))
            self.search_thread.start()

    def stopSearch(self):
       
        self.stop_event.set()
        self.statusLabel.setText('Status: Stoped search...')
        QApplication.processEvents()
        self.closeDriver()


    def searchGroups(self, query):
        self.initDriver()

        try:
            self.statusLabel.setText('Status: Loading Facebook page...')
            self.driver.get(f'https://www.facebook.com/search/groups/?q={query}')
            time.sleep(3)

            if self.privacyComboBox.currentText() == "Public":
                self.driver.get(f'https://www.facebook.com/search/groups/?q={query}&filters=eyJwdWJsaWNfZ3JvdXBzOjAiOiJ7XCJuYW1lXCI6XCJwdWJsaWNfZ3JvdXBzXCIsXCJhcmdzXCI6XCJcIn0ifQ%3D%3D')

            time.sleep(5)

            self.statusLabel.setText('Status: Scrolling and collecting data...')
            global_seen_links = set()  # Global seen links set
            results = []

            retry_attempts = 0
            wait_time = 1

            while not self.stop_event.is_set():
                groups = self.driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] .x1yztbdb")
                if not groups:
                    retry_attempts += 1
                    time.sleep(wait_time)
                    wait_time += 1
                    if retry_attempts >= 10:
                        self.statusLabel.setText('Status: Error - No groups found after multiple attempts.')
                        print('Status: Error - No groups found after multiple attempts.')
                        break
                    continue

                retry_attempts = 0
                wait_time = 1

                for group in groups:
                    if self.stop_event.is_set():
                        break
                    try:
                        title_elem = group.find_element(By.XPATH, './/a[@aria-hidden="true" and @role="presentation"]')
                        title = title_elem.text
                        href = title_elem.get_attribute('href')

                        if not title or href in global_seen_links:
                            continue  # Không xóa nhóm nếu nó hợp lệ nhưng đã thấy

                        privacy_elem = group.find_element(By.XPATH, './/span[contains(@class, "x1lliihq") and not(contains(@class, "x193iq5w"))]')
                        privacy = privacy_elem.text if privacy_elem else 'N/A'
                        members = privacy.split(' · ')[1].split(' ')[0] if ' · ' in privacy else '0'
                        if 'k' in members.lower():
                            members = members.lower().replace('k', '')
                            members = str(int(float(members) * 1000))
                        privacyy = privacy.split(' · ')[0] if ' · ' in privacy else privacy

                        # Áp dụng bộ lọc
                        min_members = self.minMembersInput.text()
                        min_members_enabled = self.minMembersCheckBox.isChecked()
                        if self.filterByKeywordsCheckBox.isChecked():
                            keywords = self.keywordsInput.text().lower().split(',')
                            if not any(keyword.strip() in title.lower() for keyword in keywords):
                                continue  # Giữ lại nhóm nếu nó không vượt qua bộ lọc

                        if min_members_enabled:
                            if not members.isdigit() or int(members) < int(min_members):
                                continue  # Giữ lại nhóm nếu nó không vượt qua bộ lọc số lượng thành viên

                        global_seen_links.add(href)  # Thay đổi ở đây
                        results.append((title, href, members, privacyy))
                        self.statusLabel.setText(f'đã tìm thấy: {title}')

                    except Exception as e:
                        continue

                if self.stop_event.is_set():
                    break

                if results:
                    self.results_data.extend(results)
                    self.updateResultTable()
                    results.clear()

                # Cuộn xuống liên tục
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                if len(groups) > 5:
                    for group in groups[:-5]:  # Chỉ xóa những cái cũ, giữ lại 5 cái mới nhất
                        self.driver.execute_script("arguments[0].remove();", group)

            if not self.stop_event.is_set():
                self.statusLabel.setText('Status: Done.')
            else:
                self.statusLabel.setText('Status: Search stopped.')
        except Exception as e:
            self.statusLabel.setText(f'Status: Error - {str(e)}')
            print(f'Status: Error - {str(e)}')
        finally:
            self.closeDriver()




            
    def updateResultTable(self):
        self.resultTable.setRowCount(0)
        for row_data in self.results_data:
            row_position = self.resultTable.rowCount()
            self.resultTable.insertRow(row_position)
            for column, data in enumerate(row_data):
                self.resultTable.setItem(row_position, column, QTableWidgetItem(data))

        if self.title_sort_order == 1:
            self.sortTable(0, True)
        elif self.title_sort_order == 2:
            self.sortTable(0, False)
        elif self.members_sort_order == 1:
            self.sortTable(2, True)
        elif self.members_sort_order == 2:
            self.sortTable(2, False)

    def sortByTitle(self):
        if self.title_sort_order == 0:
            self.title_sort_order = 1
            self.sortByTitleButton.setText('Sort by Title (Z-A)')
        elif self.title_sort_order == 1:
            self.title_sort_order = 2
            self.sortByTitleButton.setText('Sort by Title (A-Z)')
        else:
            self.title_sort_order = 0
            self.sortByTitleButton.setText('Sort by Title (A-Z)')
        self.updateResultTable()

    def sortByMembers(self):
        if self.members_sort_order == 0:
            self.members_sort_order = 1
            self.sortByMembersButton.setText('Sort by Members (Low to High)')
        elif self.members_sort_order == 1:
            self.members_sort_order = 2
            self.sortByMembersButton.setText('Sort by Members (High to Low)')
        else:
            self.members_sort_order = 0
            self.sortByMembersButton.setText('Sort by Members (High to Low)')
        self.updateResultTable()

    def sortTable(self, column, ascending):
        self.resultTable.sortItems(column, Qt.AscendingOrder if ascending else Qt.DescendingOrder)

    def initDriver(self):
        if self.driver is None:
            selected_profile = self.profileComboBox.currentText()
            profile_path = os.path.join(os.getcwd(), selected_profile)
            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={profile_path}")
            self.driver = webdriver.Chrome(options=chrome_options)


    def closeDriver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def clearConsole(self):
        self.resultTable.setRowCount(0)
        self.results_data = []
        self.failed_groups_data = []
        self.statusLabel.setText('Status: Console cleared.')

    def exportResults(self):
        if not self.results_data:
            self.statusLabel.setText('Status: No data to export.')
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_path:
            df = pd.DataFrame(self.results_data, columns=['Title', 'Link', 'Members', 'Privacy'])
            df.to_excel(file_path, index=False)
            self.statusLabel.setText('Status: Exported successfully.')



    def filterResults(self):
        keyword = self.keywordFilterBox.text().lower()
        if keyword:
            filtered_results = [result for result in self.results_data if keyword in result[0].lower()]
            self.resultTable.setRowCount(0)
            for row_data in filtered_results:
                row_position = self.resultTable.rowCount()
                self.resultTable.insertRow(row_position)
                for column, data in enumerate(row_data):
                    self.resultTable.setItem(row_position, column, QTableWidgetItem(data))
        else:
            self.updateResultTable()

    def closeEvent(self, event):
        # Save settings when the application is closed
        self.saveSettings()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FacebookGroupSearcher()
    ex.show()
    sys.exit(app.exec_())
