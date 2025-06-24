import sys
import os
import json
import time
import pyautogui
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QStackedWidget, 
                             QFormLayout, QHBoxLayout, QCheckBox, QComboBox, QFileDialog, QFrame, 
                             QScrollArea, QGroupBox)
from selenium.webdriver.common.by import By
from threading import Thread, Event, Lock
from PyQt5.QtCore import Qt
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import urllib.parse
import re
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
from PyQt5.QtGui import QImage, QFont, QIcon
from selenium.webdriver.common.action_chains import ActionChains
import requests
import pkgutil
import subprocess
import sys
import tempfile
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication
# Get all imported modules
imported_modules = {name for _, name, _ in pkgutil.iter_modules()}
# Install all the imported modules
subprocess.run([sys.executable, "-m", "pip", "install"] + list(imported_modules))


class FacebookGroupSearcher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.applyStyles()
        self.loadSettings()
        self.stop_event = Event()
        self.search_thread = None
        self.driver = None
        self.results_data = []
        self.failed_groups_data = []
        self.failed_groups_lock = Lock()
        self.post_counter = 0  # Add this line
        self.title_sort_order = 0  # 0: original, 1: A-Z, 2: Z-A
        self.members_sort_order = 0  # 0: original, 1: high-to-low, 2: low-to-high
        self.pc = 0

    def applyStyles(self):
            # Enhanced modern dark theme with improved visuals
            self.setStyleSheet("""
                QWidget {
                    background-color: #2d2d30;
                    color: #ffffff;
                    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
                    font-size: 10pt;
                }
                
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #252528, stop:0.5 #2d2d30, stop:1 #363639);
                }
                
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0078d4, stop:1 #005a9e);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 10pt;
                    min-height: 16px;
                    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #106ebe, stop:1 #0078d4);
                    transform: translateY(-3px) scale(1.02);
                    box-shadow: 0 8px 20px rgba(0, 120, 212, 0.4);
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #005a9e, stop:1 #004578);
                    transform: translateY(-1px) scale(0.98);
                    box-shadow: 0 4px 12px rgba(0, 120, 212, 0.3);
                    transition: all 0.1s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                QPushButton:disabled {
                    background: linear-gradient(135deg, #2a2a2a, #1f1f1f);
                    color: #666666;
                    box-shadow: none;
                }
                
                /* Tab buttons with glass effect */
                QPushButton[objectName*="TabButton"] {
                    background: rgba(255, 255, 255, 0.08);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 12px 12px 0px 0px;
                    padding: 14px 28px;
                    font-weight: 600;
                    font-size: 11pt;
                    margin-right: 3px;
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2);
                    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QPushButton[objectName*="TabButton"]:hover {
                    background: rgba(255, 255, 255, 0.12);
                    border: 1px solid rgba(0, 120, 212, 0.4);
                    box-shadow: 0 4px 20px rgba(0, 120, 212, 0.15);
                    transform: translateY(-2px);
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                /* Enhanced action buttons */
                QPushButton[objectName*="Action"] {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #667eea, stop:0.5 #764ba2, stop:1 #0078d4);
                    font-weight: 700;
                    padding: 14px 32px;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QPushButton[objectName*="Action"]:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #7c8df0, stop:0.5 #8a5fb8, stop:1 #106ebe);
                    transform: translateY(-4px) scale(1.05);
                    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QPushButton[objectName*="Danger"] {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #ff6b6b, stop:1 #ee5a52);
                    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
                }
                
                QPushButton[objectName*="Danger"]:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #ff8e8e, stop:1 #f77c75);
                    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
                }
                
                /* Glass-morphism secondary buttons */
                QPushButton[objectName*="Secondary"] {
                    background: rgba(255, 255, 255, 0.08);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 8px;
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2);
                    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QPushButton[objectName*="Secondary"]:hover {
                    background: rgba(255, 255, 255, 0.12);
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    box-shadow: 0 4px 15px rgba(255, 255, 255, 0.08);
                    transform: translateY(-2px) scale(1.02);
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QTextEdit, QLineEdit {
                    background: rgba(255, 255, 255, 0.06);
                    backdrop-filter: blur(10px);
                    border: 2px solid rgba(255, 255, 255, 0.15);
                    border-radius: 10px;
                    padding: 12px 16px;
                    font-size: 10pt;
                    selection-background-color: rgba(0, 120, 212, 0.3);
                    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
                    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QTextEdit:focus, QLineEdit:focus {
                    border: 2px solid #0078d4;
                    background: rgba(255, 255, 255, 0.1);
                    box-shadow: 0 0 20px rgba(0, 120, 212, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.05);
                    transform: scale(1.02);
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QComboBox {
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 10px 16px;
                    font-size: 10pt;
                    min-height: 22px;
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
                }
                
                QComboBox:hover {
                    border: 2px solid rgba(0, 132, 255, 0.5);
                    box-shadow: 0 4px 15px rgba(0, 132, 255, 0.1);
                }
                
                QComboBox:focus {
                    border: 2px solid #0084ff;
                    box-shadow: 0 0 20px rgba(0, 132, 255, 0.2);
                }
                
                QComboBox::drop-down {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0084ff, stop:1 #0066cc);
                    border: none;
                    border-radius: 0px 8px 8px 0px;
                    width: 24px;
                }
                
                QComboBox::down-arrow {
                    image: none;
                    border-left: 6px solid transparent;
                    border-right: 6px solid transparent;
                    border-top: 6px solid white;
                    margin: 6px;
                }
                
                QComboBox QAbstractItemView {
                    background: rgba(45, 45, 48, 0.95);
                    backdrop-filter: blur(15px);
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    selection-background-color: rgba(0, 120, 212, 0.3);
                    border-radius: 8px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                }
                
                QCheckBox {
                    spacing: 10px;
                    font-size: 10pt;
                    font-weight: 500;
                }
                
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 6px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    background: rgba(255, 255, 255, 0.06);
                    backdrop-filter: blur(10px);
                    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QCheckBox::indicator:hover {
                    border: 2px solid rgba(0, 120, 212, 0.6);
                    box-shadow: 0 0 15px rgba(0, 120, 212, 0.2);
                    transform: scale(1.1);
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QCheckBox::indicator:checked {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0078d4, stop:1 #005a9e);
                    border: 2px solid #0078d4;
                    image: none;
                    box-shadow: 0 0 20px rgba(0, 120, 212, 0.4);
                    transform: scale(1.05);
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QCheckBox::indicator:checked:after {
                    content: "✓";
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
                
                QTableWidget {
                    background: rgba(255, 255, 255, 0.04);
                    alternate-background-color: rgba(255, 255, 255, 0.06);
                    gridline-color: rgba(255, 255, 255, 0.15);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 12px;
                    font-size: 9pt;
                    backdrop-filter: blur(10px);
                }
                
                QTableWidget::item {
                    padding: 10px;
                    border: none;
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QTableWidget::item:selected {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 120, 212, 0.3), stop:1 rgba(0, 120, 212, 0.2));
                    color: white;
                    border-radius: 4px;
                    transform: scale(1.02);
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QTableWidget::item:hover {
                    background: rgba(255, 255, 255, 0.08);
                    border-radius: 4px;
                    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
                }
                
                QHeaderView::section {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(255, 255, 255, 0.08), stop:1 rgba(255, 255, 255, 0.03));
                    color: #ffffff;
                    padding: 12px;
                    border: none;
                    border-right: 1px solid rgba(255, 255, 255, 0.1);
                    font-weight: 700;
                    font-size: 10pt;
                    backdrop-filter: blur(10px);
                }
                
                QHeaderView::section:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(0, 132, 255, 0.1), stop:1 rgba(0, 132, 255, 0.05));
                }
                
                QLabel {
                    color: #f0f0f0;
                    font-size: 10pt;
                }
                
                QLabel[objectName*="Status"] {
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-weight: 600;
                    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
                }
                
                QLabel[objectName*="Title"] {
                    font-size: 16pt;
                    font-weight: 800;
                    color: #ffffff;
                    margin-bottom: 8px;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                }
                
                QGroupBox {
                    font-weight: 700;
                    font-size: 12pt;
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    margin-top: 12px;
                    padding-top: 12px;
                    background: rgba(255, 255, 255, 0.02);
                    backdrop-filter: blur(10px);
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 12px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 132, 255, 0.8), stop:1 rgba(102, 126, 234, 0.8));
                    color: white;
                    border-radius: 6px;
                    font-weight: 700;
                }
                
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                
                QScrollBar:vertical {
                    background: rgba(255, 255, 255, 0.05);
                    width: 14px;
                    border-radius: 7px;
                    backdrop-filter: blur(10px);
                }
                
                QScrollBar::handle:vertical {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 132, 255, 0.6), stop:1 rgba(0, 132, 255, 0.4));
                    border-radius: 7px;
                    min-height: 24px;
                    box-shadow: 0 2px 8px rgba(0, 132, 255, 0.2);
                }
                
                QScrollBar::handle:vertical:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 132, 255, 0.8), stop:1 rgba(0, 132, 255, 0.6));
                    box-shadow: 0 4px 12px rgba(0, 132, 255, 0.3);
                }
                
                QFrame[objectName*="Separator"] {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 transparent, stop:0.5 rgba(255, 255, 255, 0.2), stop:1 transparent);
                    max-height: 1px;
                    margin: 12px 0;
                }
            """)

    def initUI(self):
        self.setWindowTitle('🔍 Facebook Group Searcher Pro')
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Main layout with margins
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header with title
        header_layout = QHBoxLayout()
        title_label = QLabel('Facebook Group Searcher Pro')
        title_label.setObjectName('titleLabel')
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setObjectName('separatorFrame')
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)

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
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(5)
        
        self.searchTabButton = QPushButton('🔍 Search')
        self.searchTabButton.setObjectName('searchTabButton')
        self.searchTabButton.clicked.connect(lambda: self.switchTab(self.searchPage))
        tab_layout.addWidget(self.searchTabButton)

        self.settingsTabButton = QPushButton('⚙️ Settings')
        self.settingsTabButton.setObjectName('settingsTabButton')
        self.settingsTabButton.clicked.connect(lambda: self.switchTab(self.settingsPage))
        tab_layout.addWidget(self.settingsTabButton)
        
        self.postTabButton = QPushButton('📝 Post')
        self.postTabButton.setObjectName('postTabButton') 
        self.postTabButton.clicked.connect(lambda: self.switchTab(self.postPage))
        tab_layout.addWidget(self.postTabButton)

        tab_layout.addStretch()
        
        # Add the tab layout and the stacked widget to the main layout
        main_layout.addLayout(tab_layout)
        main_layout.addWidget(self.stackedWidget)

        # Add buttons for clear console and export with better styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.clearConsoleButton = QPushButton('🗑️ Clear Console')
        self.clearConsoleButton.setObjectName('secondaryButton')
        self.clearConsoleButton.clicked.connect(self.clearConsole)
        button_layout.addWidget(self.clearConsoleButton)

        self.exportButton = QPushButton('📤 Export Results')
        self.exportButton.setObjectName('actionButton')
        self.exportButton.clicked.connect(self.exportResults)
        button_layout.addWidget(self.exportButton)

        # Add sorting buttons
        self.sortByTitleButton = QPushButton('🔤 Sort by Title')
        self.sortByTitleButton.setObjectName('secondaryButton')
        self.sortByTitleButton.clicked.connect(self.sortByTitle)
        button_layout.addWidget(self.sortByTitleButton)

        self.sortByMembersButton = QPushButton('👥 Sort by Members')
        self.sortByMembersButton.setObjectName('secondaryButton')
        self.sortByMembersButton.clicked.connect(self.sortByMembers)
        button_layout.addWidget(self.sortByMembersButton)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Initialize the first tab as active
        self.switchTab(self.searchPage)

    def switchTab(self, widget):
        # Switch to the selected widget
        self.stackedWidget.setCurrentWidget(widget)

        # Update the style to show which tab is active
        all_buttons = [self.searchTabButton, self.settingsTabButton, self.postTabButton]
        for btn in all_buttons:
            btn.setStyleSheet("")
            
        if widget == self.searchPage:
            self.searchTabButton.setStyleSheet("background-color: #0078d4; color: white;")
        elif widget == self.settingsPage:
            self.settingsTabButton.setStyleSheet("background-color: #0078d4; color: white;")
        elif widget == self.postPage:
            self.postTabButton.setStyleSheet("background-color: #0078d4; color: white;")

    def createSearchPage(self):
        self.searchPage = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Search input group
        search_group = QGroupBox("🔍 Search Configuration")
        search_layout = QVBoxLayout()
        
        self.searchBox = QTextEdit()
        self.searchBox.setPlaceholderText('Enter your search terms here...')
        self.searchBox.setMaximumHeight(80)
        search_layout.addWidget(self.searchBox)

        self.keywordFilterBox = QLineEdit()
        self.keywordFilterBox.setPlaceholderText('🔍 Filter results by keywords...')
        self.keywordFilterBox.textChanged.connect(self.filterResults)
        search_layout.addWidget(self.keywordFilterBox)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.startSearchButton = QPushButton('🚀 Start Search')
        self.startSearchButton.setObjectName('actionButton')
        self.startSearchButton.clicked.connect(self.startSearch)
        control_layout.addWidget(self.startSearchButton)

        self.stopButton = QPushButton('⏹️ Stop Search')
        self.stopButton.setObjectName('dangerButton')
        self.stopButton.clicked.connect(self.stopSearch)
        control_layout.addWidget(self.stopButton)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Results table
        results_group = QGroupBox("📊 Search Results")
        results_layout = QVBoxLayout()
        
        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(4)
        self.resultTable.setHorizontalHeaderLabels(['Title', 'Link', 'Members', 'Privacy'])
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resultTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.resultTable.setAlternatingRowColors(True)
        results_layout.addWidget(self.resultTable)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Status
        self.statusLabel = QLabel('✅ Status: Ready to search')
        self.statusLabel.setObjectName('statusLabel')
        layout.addWidget(self.statusLabel)

        self.searchPage.setLayout(layout)
    def createSettingsPage(self):
        self.settingsPage = QWidget()
        
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Profile Management Group
        profile_group = QGroupBox("👤 Profile Management")
        profile_layout = QVBoxLayout()
        
        profile_control_layout = QHBoxLayout()
        self.profileCreationButton = QPushButton('➕ Create New Profile')
        self.profileCreationButton.setObjectName('actionButton')
        self.profileCreationButton.clicked.connect(self.createNewProfile)
        profile_control_layout.addWidget(self.profileCreationButton)
        
        self.openCloseBrowserButton = QPushButton('🌐 Open Browser')
        self.openCloseBrowserButton.setObjectName('secondaryButton')
        self.openCloseBrowserButton.clicked.connect(self.toggleBrowser)
        profile_control_layout.addWidget(self.openCloseBrowserButton)
        
        profile_layout.addLayout(profile_control_layout)

        # Profile selector
        profile_selector_layout = QHBoxLayout()
        profile_selector_layout.addWidget(QLabel("Profile:"))
        self.profileComboBox = QComboBox()
        profile_selector_layout.addWidget(self.profileComboBox)
        profile_layout.addLayout(profile_selector_layout)
        
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        # ✨ DISCORD INTEGRATION GROUP - THÊM MỚI
        discord_group = QGroupBox("🎮 Discord Integration")
        discord_layout = QVBoxLayout()

        # Enable Discord notifications
        self.enableDiscordCheckBox = QCheckBox("📸 Enable Discord Screenshots")
        self.enableDiscordCheckBox.setChecked(True)  # Mặc định bật
        self.enableDiscordCheckBox.stateChanged.connect(self.toggleDiscordSettings)
        discord_layout.addWidget(self.enableDiscordCheckBox)

        # Discord webhook URL
        webhook_layout = QHBoxLayout()
        webhook_layout.addWidget(QLabel("🔗 Webhook URL:"))
        self.discordWebhookInput = QLineEdit()
        self.discordWebhookInput.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.discordWebhookInput.setText("https://discord.com/api/webhooks/1384427749955080192/NCgPMyFZ7tHOtLOt0lo2iJEvPcKCH2flGXeXKpnHxnYz99rQ8eVTpdu3dC7F8BfF-Wc_")
        webhook_layout.addWidget(self.discordWebhookInput)
        discord_layout.addLayout(webhook_layout)

        # Test Discord connection
        test_layout = QHBoxLayout()
        self.testDiscordButton = QPushButton('🧪 Test Discord Connection')
        self.testDiscordButton.setObjectName('secondaryButton')
        self.testDiscordButton.clicked.connect(self.testDiscordConnection)
        test_layout.addWidget(self.testDiscordButton)
        
        self.discordStatusLabel = QLabel('📡 Status: Not tested')
        self.discordStatusLabel.setStyleSheet("color: #888888; font-style: italic;")
        test_layout.addWidget(self.discordStatusLabel)
        test_layout.addStretch()
        discord_layout.addLayout(test_layout)

        # Discord message template
        template_layout = QVBoxLayout()
        template_layout.addWidget(QLabel("📝 Message Template:"))
        self.discordMessageTemplate = QTextEdit()
        self.discordMessageTemplate.setMaximumHeight(80)
        self.discordMessageTemplate.setPlaceholderText("Custom message template (optional)")
        template_layout.addWidget(self.discordMessageTemplate)
        discord_layout.addLayout(template_layout)

        # Screenshot options
        screenshot_options_layout = QHBoxLayout()
        self.screenshotDelayCheckBox = QCheckBox("⏰ Delay before screenshot")
        screenshot_options_layout.addWidget(self.screenshotDelayCheckBox)
        
        self.screenshotDelayInput = QLineEdit()
        self.screenshotDelayInput.setPlaceholderText("seconds")
        self.screenshotDelayInput.setMaximumWidth(80)
        self.screenshotDelayInput.setText("2")
        self.screenshotDelayInput.setDisabled(True)
        screenshot_options_layout.addWidget(self.screenshotDelayInput)
        screenshot_options_layout.addStretch()
        discord_layout.addLayout(screenshot_options_layout)

        # Connect delay checkbox to input field
        self.screenshotDelayCheckBox.stateChanged.connect(
            lambda state: self.screenshotDelayInput.setEnabled(state == Qt.Checked)
        )
        
        discord_group.setLayout(discord_layout)
        layout.addWidget(discord_group)

        # Search Filters Group
        filters_group = QGroupBox("🔧 Search Filters")
        filters_layout = QVBoxLayout()

        # Privacy filter
        privacy_layout = QHBoxLayout()
        privacy_layout.addWidget(QLabel("Privacy Level:"))
        self.privacyComboBox = QComboBox()
        self.privacyComboBox.addItems(["Public", "All"])
        privacy_layout.addWidget(self.privacyComboBox)
        privacy_layout.addStretch()
        filters_layout.addLayout(privacy_layout)

        # Minimum members filter
        self.minMembersCheckBox = QCheckBox("🔢 Filter by Minimum Members")
        self.minMembersCheckBox.stateChanged.connect(self.toggleMinMembers)
        filters_layout.addWidget(self.minMembersCheckBox)

        self.minMembersInput = QLineEdit()
        self.minMembersInput.setPlaceholderText("Enter minimum number of members")
        self.minMembersInput.setDisabled(True)
        filters_layout.addWidget(self.minMembersInput)

        # Include keywords filter
        self.filterByKeywordsCheckBox = QCheckBox("✅ Include Groups with Keywords")
        self.filterByKeywordsCheckBox.stateChanged.connect(self.toggleFilterByKeywords)
        filters_layout.addWidget(self.filterByKeywordsCheckBox)

        self.keywordsInput = QLineEdit()
        self.keywordsInput.setPlaceholderText("Enter keywords to include (comma separated)")
        self.keywordsInput.setDisabled(True)
        filters_layout.addWidget(self.keywordsInput)

        # Exclude keywords filter
        self.excludeKeywordsCheckBox = QCheckBox("❌ Exclude Groups with Keywords")
        self.excludeKeywordsCheckBox.stateChanged.connect(self.toggleExcludeKeywords)
        filters_layout.addWidget(self.excludeKeywordsCheckBox)

        self.excludeKeywordsInput = QLineEdit()
        self.excludeKeywordsInput.setPlaceholderText("Enter keywords to exclude (comma separated)")
        self.excludeKeywordsInput.setDisabled(True)
        filters_layout.addWidget(self.excludeKeywordsInput)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        # Interaction Settings Group
        interaction_group = QGroupBox("💬 Interaction Settings")
        interaction_layout = QVBoxLayout()

        # Like post checkbox
        self.likePostCheckBox = QCheckBox("👍 Auto-like Posts")
        interaction_layout.addWidget(self.likePostCheckBox)

        # Comment settings
        self.commentCheckBox = QCheckBox("💬 Auto-comment on Posts")
        self.commentCheckBox.stateChanged.connect(self.toggleCommentInput)
        interaction_layout.addWidget(self.commentCheckBox)

        self.commentInput = QLineEdit()
        self.commentInput.setPlaceholderText("Enter your comment text")
        self.commentInput.setDisabled(True)
        interaction_layout.addWidget(self.commentInput)

        # Typing speed settings
        self.enterContentCheckBox = QCheckBox("⌨️ Slow Typing Mode")
        self.enterContentCheckBox.stateChanged.connect(self.toggledelaytype)
        interaction_layout.addWidget(self.enterContentCheckBox)

        self.delaytype = QLineEdit()
        self.delaytype.setPlaceholderText("Typing delay in milliseconds (default: 5)")
        self.delaytype.setDisabled(True)
        interaction_layout.addWidget(self.delaytype)
        
        interaction_group.setLayout(interaction_layout)
        layout.addWidget(interaction_group)

        # Save settings button
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.saveSettingsButton = QPushButton('💾 Save All Settings')
        self.saveSettingsButton.setObjectName('actionButton')
        self.saveSettingsButton.clicked.connect(self.saveSettings)
        save_layout.addWidget(self.saveSettingsButton)
        layout.addLayout(save_layout)

        scroll_widget.setLayout(layout)
        scroll.setWidget(scroll_widget)
        
        # Main settings page layout
        main_settings_layout = QVBoxLayout()
        main_settings_layout.addWidget(scroll)
        self.settingsPage.setLayout(main_settings_layout)

    # ✨ THÊM CÁC METHOD MỚI CHO DISCORD
    def toggleDiscordSettings(self, state):
        """Toggle Discord settings based on checkbox state"""
        enabled = state == Qt.Checked
        self.discordWebhookInput.setEnabled(enabled)
        self.testDiscordButton.setEnabled(enabled)
        self.discordMessageTemplate.setEnabled(enabled)
        self.screenshotDelayCheckBox.setEnabled(enabled)
        
        if not enabled:
            self.screenshotDelayInput.setEnabled(False)
        else:
            self.screenshotDelayInput.setEnabled(self.screenshotDelayCheckBox.isChecked())

    def testDiscordConnection(self):
        """Test Discord webhook connection"""
        webhook_url = self.discordWebhookInput.text().strip()
        
        if not webhook_url:
            self.discordStatusLabel.setText('❌ Status: Please enter webhook URL')
            self.discordStatusLabel.setStyleSheet("color: #ff4444;")
            return
        
        try:
            self.discordStatusLabel.setText('🔄 Status: Testing...')
            self.discordStatusLabel.setStyleSheet("color: #ffaa00;")
            
            # Test message
            test_data = {
                'content': '🧪 **Test Message from Facebook Auto Poster**\n✅ Discord integration is working correctly!'
            }
            
            response = requests.post(webhook_url, json=test_data, timeout=10)
            
            if response.status_code == 204:
                self.discordStatusLabel.setText('✅ Status: Connection successful!')
                self.discordStatusLabel.setStyleSheet("color: #44ff44;")
            else:
                self.discordStatusLabel.setText(f'❌ Status: Error {response.status_code}')
                self.discordStatusLabel.setStyleSheet("color: #ff4444;")
                
        except Exception as e:
            self.discordStatusLabel.setText(f'❌ Status: Connection failed')
            self.discordStatusLabel.setStyleSheet("color: #ff4444;")
            print(f"Discord test error: {e}")

    def getDiscordSettings(self):
        """Get current Discord settings"""
        return {
            'enabled': self.enableDiscordCheckBox.isChecked(),
            'webhook_url': self.discordWebhookInput.text().strip(),
            'message_template': self.discordMessageTemplate.toPlainText().strip(),
            'screenshot_delay': int(self.screenshotDelayInput.text()) if self.screenshotDelayCheckBox.isChecked() and self.screenshotDelayInput.text().isdigit() else 0
        }
    def toggleCommentInput(self, state):
        self.commentInput.setDisabled(state == 0)

    def toggledelaytype(self, state):
        self.delaytype.setDisabled(state == 0)

    def createPostPage(self):
        self.postPage = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Post Content Group
        content_group = QGroupBox("📝 Post Content")
        content_layout = QVBoxLayout()

        self.postContent = QTextEdit()
        self.postContent.setPlaceholderText('Write your post content here...')
        self.postContent.setMinimumHeight(120)
        content_layout.addWidget(self.postContent)

        # Image settings
        image_layout = QHBoxLayout()
        self.enableImageCheckbox = QCheckBox("🖼️ Attach Image")
        self.enableImageCheckbox.stateChanged.connect(self.toggleImageSelection)
        image_layout.addWidget(self.enableImageCheckbox)

        self.selectImageButton = QPushButton('📁 Select Image')
        self.selectImageButton.setObjectName('secondaryButton')
        self.selectImageButton.clicked.connect(self.selectImage)
        self.selectImageButton.setDisabled(True)
        image_layout.addWidget(self.selectImageButton)
        image_layout.addStretch()
        content_layout.addLayout(image_layout)

        self.imagePathLabel = QLabel('No image selected')
        self.imagePathLabel.setStyleSheet("color: #888888; font-style: italic;")
        content_layout.addWidget(self.imagePathLabel)
        
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)

        # Post Controls Group
        controls_group = QGroupBox("🎛️ Post Controls")
        controls_layout = QVBoxLayout()

        # Delay setting
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("⏱️ Delay between posts:"))
        self.delayInput = QLineEdit()
        self.delayInput.setPlaceholderText("seconds")
        self.delayInput.setMaximumWidth(100)
        delay_layout.addWidget(self.delayInput)
        delay_layout.addStretch()
        controls_layout.addLayout(delay_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        self.postButton = QPushButton('🚀 Start Posting')
        self.postButton.setObjectName('actionButton')
        self.postButton.clicked.connect(self.startPosting)
        button_layout.addWidget(self.postButton)

        self.stopPostButton = QPushButton('⏹️ Stop Posting')
        self.stopPostButton.setObjectName('dangerButton')
        self.stopPostButton.clicked.connect(self.stopPosting)
        button_layout.addWidget(self.stopPostButton)
        button_layout.addStretch()
        controls_layout.addLayout(button_layout)

        # File operations
        file_layout = QHBoxLayout()
        self.loadFileButton = QPushButton('📂 Load Groups File')
        self.loadFileButton.setObjectName('secondaryButton')
        self.loadFileButton.clicked.connect(self.loadFile)
        file_layout.addWidget(self.loadFileButton)

        self.selectAllCheckBox = QCheckBox("☑️ Select All Groups")
        self.selectAllCheckBox.stateChanged.connect(self.selectAll)
        file_layout.addWidget(self.selectAllCheckBox)
        file_layout.addStretch()
        controls_layout.addLayout(file_layout)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Status
        self.postStatusLabel = QLabel('✅ Status: Ready to post')
        self.postStatusLabel.setObjectName('statusLabel')
        layout.addWidget(self.postStatusLabel)

        # Groups Table
        table_group = QGroupBox("📋 Target Groups")
        table_layout = QVBoxLayout()
        
        self.resultTableaa = QTableWidget()
        self.resultTableaa.setColumnCount(4)
        self.resultTableaa.setHorizontalHeaderLabels(['Select', 'Title', 'Link', 'Status'])
        self.resultTableaa.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resultTableaa.setEditTriggers(QTableWidget.NoEditTriggers)
        self.resultTableaa.setAlternatingRowColors(True)
        table_layout.addWidget(self.resultTableaa)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        self.postPage.setLayout(layout)

    def selectAll(self, state):
        # Set the check state for all items in the table
        check_state = Qt.Checked if state == Qt.Checked else Qt.Unchecked
        for row in range(self.resultTableaa.rowCount()):
            item = self.resultTableaa.item(row, 0)
            if item:
                item.setCheckState(check_state)
                
    def toggleExcludeKeywords(self, state):
        self.excludeKeywordsInput.setDisabled(state != Qt.Checked)

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

    def run_watch_or_reel(self, delay):
        link = random.choice(["https://www.facebook.com/watch", "https://www.facebook.com/reel/"])
        print(f"Mở link: {link}")
        self.driver.get(link)

        start_time = time.time()

        if "watch" in link:
            print(f"Đang ở trang 'watch', chờ {delay} giây...")
            time.sleep(delay)
        else:
            print(f"Đang ở trang 'reel', sẽ click trong khoảng {delay} giây...")
            while True:
                elapsed = time.time() - start_time
                if elapsed >= delay:
                    print("Hết thời gian delay.")
                    break

                sleep_time = random.randint(5, 20)  # ngắn hơn để tránh bị delay quá lâu
                remaining = int(delay - elapsed)
                print(f"Click vào div... Còn lại {remaining} giây (ngủ {sleep_time}s)")

                time.sleep(sleep_time)

                pyautogui.moveTo(960, 540)  # Tùy độ phân giải màn hình, đây là 1920x1080

                # Cuộn xuống
                pyautogui.scroll(-300)  # Dấu trừ để cuộn xuống, dương là cuộn lên

                time.sleep(0.5)

        # Gọi hành động like sau khi đã xem xong
        try:
            self.like_posts()
            print("✅ Đã hoàn thành like các bài viết.")
        except Exception as e:
            print(f"❌ Lỗi khi like bài viết: {e}")
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
            cc = f"{index + 1}/{total_links}"
            # Post content to group
            
            self.postContentToGroup(cc)
            self.run_watch_or_reel(delay)
            # Update the status of the link in the table
            status_item = QTableWidgetItem('complete ✅')
            self.resultTableaa.setItem(row, 3, status_item)
            
            # Force the UI to update immediately
            self.resultTableaa.repaint()  # Or QApplication.processEvents()
            
            self.postStatusLabel.setText(f'Status: Processing {index + 1}/{total_links}')
            

            time.sleep(5)
        self.postStatusLabel.setText('Status: All links processed.')
        self.driver.quit()


    def like_posts(self):
        if self.likePostCheckBox.isChecked():
            print("🔍 Đang tìm các nút 'Thích'...")

            try:
                # Tìm tất cả các nút 'Thích' trên trang
                like_buttons = self.driver.find_elements(By.XPATH, "//div[@aria-label='Thích' and @role='button']")
                total = len(like_buttons)
                print(f"🔘 Tìm thấy {total} nút 'Thích'.")

                if total == 0:
                    print("⚠️ Không có nút 'Thích' nào để like.")
                    return

                # Chọn ngẫu nhiên 1–5 chỉ số không trùng để like
                num_to_like = min(random.randint(1, 7), total)
                selected_indexes = random.sample(range(total), num_to_like)
                print(f"❤️ Sẽ like {num_to_like} nút ở vị trí: {selected_indexes}")

                for i, idx in enumerate(selected_indexes):
                    try:
                        like_buttons[idx].click()
                        print(f"✅ Đã like nút thứ {idx + 1} ({i + 1}/{num_to_like})")
                        time.sleep(1)
                    except Exception as e:
                        print(f"⚠️ Không thể like nút thứ {idx + 1}: {e}")
                        continue

                print("🎯 Hoàn tất quá trình like.")
            
            except Exception as e:
                print(f"❌ Lỗi khi xử lý: {e}")


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
    def postContentToGroup(self,cc):
            """
            Posts content to a Facebook group with improved error handling and reliability
            """
            if not self.driver:
                print("❌ Error: WebDriver not initialized")
                return False

            try:
                current_link = self.driver.current_url
                try:
                    post_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "span[class='x1lliihq x6ikm8r x10wlt62 x1n2onr6']"))
                    )
                    post_button.click()
                    time.sleep(3)
                except TimeoutException:
                    print("⚠️ Post creation button not found or not clickable")
                    return False
                except Exception as e:
                    print(f"❌ Error clicking post area: {e}")
                    return False

                # Get post content
                post_content = self.postContent.toPlainText().strip()
                if not post_content and not hasattr(self, 'selected_image_path'):
                    print("⚠️ No content or image to post")
                    return False

                # Nhập nội dung
                if post_content:
                    try:
                        content_area = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "p[class='xdj266r x14z9mp xat24cr x1lziwak x16tdsg8']"))
                        )
                        # Dán hình nếu có
                        if hasattr(self, 'selected_image_path') and os.path.exists(self.selected_image_path):
                            try:
                                image = Image.open(rf'{self.selected_image_path}')
                                output = io.BytesIO()
                                image.save(output, format='BMP')
                                data = output.getvalue()[14:]

                                win32clipboard.OpenClipboard()
                                win32clipboard.EmptyClipboard()
                                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                                win32clipboard.CloseClipboard()
                                time.sleep(1)
                                content_area.click()
                                content_area.send_keys(Keys.CONTROL, 'v')
                                time.sleep(3)
                            except Exception as e:
                                print(f"⚠️ Error attaching image: {e}")
                                return False

                        try:
                            delay = float(self.delaytype.text() or 0.0005)
                        except ValueError:
                            print("⚠️ Invalid delay value, using default 0.0005")
                            delay = 0.0005

                        if self.enterContentCheckBox.isChecked():
                            try:
                                import unicodedata
                                post_content = unicodedata.normalize('NFC', post_content)

                                content_area.click()
                                time.sleep(0.1)

                                for char in post_content:
                                    try:
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        ActionChains(self.driver).send_keys(char).perform()
                                    except Exception:
                                        try:
                                            content_area.send_keys(char)
                                        except Exception:
                                            try:
                                                self.driver.execute_script(
                                                    "arguments[0].value += arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                                                    content_area, char
                                                )
                                            except Exception:
                                                print(f"⚠️ Skipped character: {repr(char)}")
                                    time.sleep(delay)                                
                            except Exception as e:
                                print(f"❌ Error typing content slowly: {e}")
                                return False
                        else:
                            try:
                                pyperclip.copy(post_content)
                                content_area.click()
                                content_area.send_keys(Keys.CONTROL + 'v')
                                time.sleep(1)
                            except Exception as e:
                                print(f"❌ Error pasting content: {e}")
                                return False

                    except TimeoutException:
                        print("⚠️ Content area not found")
                        return False
                    except Exception as e:
                        print(f"❌ Error entering post content: {e}")
                        return False

                # Submit bài viết (3 lần thử)
                post_submitted = False
                max_attempts = 3

                for attempt in range(1, max_attempts + 1):
                    try:
                        print(f"🟡 Attempt {attempt} to submit post...")

                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                "div[aria-label='Đăng'] div[class='html-div xdj266r xat24cr xexx8yu xyri2b x18d9i69 x1c1uobl x6s0dn4 x78zum5 xl56j7k x14ayic xwyz465 x1e0frkt']"))
                        )
                        submit_button.click()
                        time.sleep(5)

                        print(f"✅ Post submitted successfully on attempt {attempt}")
                        post_submitted = True
                        break

                    except (TimeoutException, NoSuchElementException):
                        print(f"⚠️ Submit button not found or not clickable on attempt {attempt}")
                    except Exception as e:
                        print(f"❌ Unexpected error on attempt {attempt}: {e}")
                    time.sleep(2)

                if not post_submitted:
                    print("❌ Failed to submit post after all attempts.")
                    return False

                print("⏳ Post submitted successfully, performing post-submission actions...")

                # Gửi thông báo Discord
                try:
                    if hasattr(self, '_handle_discord_notification'):
                        self._handle_discord_notification(current_link,cc)
                except Exception as e:
                    print(f"⚠️ Error during Discord notification: {e}")

                # Hành động sau post
                try:
                    if hasattr(self, '_perform_post_actions'):
                        self._perform_post_actions()
                except Exception as e:
                    print(f"⚠️ Error during post actions: {e}")

                return True

            except Exception as e:
                print(f"❌ Error in postContentToGroup: {e}")
                return False


    def _handle_discord_notification(self, current_link,cc):
        """Handle Discord notification with error handling"""
        try:
            discord_settings = self.getDiscordSettings()
            
            if not discord_settings.get('enabled') or not discord_settings.get('webhook_url'):
                print("Discord integration disabled or webhook URL not set")
                return
            
            # Apply screenshot delay if configured
            screenshot_delay = discord_settings.get('screenshot_delay', 0)
            if screenshot_delay > 0:
                time.sleep(screenshot_delay)
            # Take screenshot and send to Discord
            self.take_screenshot_and_send_discord(
                link=current_link,
                status="Đăng bài thành công ✅",
                order=cc,
                custom_message=discord_settings.get('message_template', ''),
                webhook_url=discord_settings['webhook_url']
            )
            
        except Exception as e:
            print(f"Error handling Discord notification: {e}")

    def _perform_post_actions(self):
        """Perform post-submission actions (like, comment) with error handling"""
        try:
            time.sleep(40)  # Wait for post to be fully loaded
            
            # Comment on the post
            try:
                self.comment()
                print("Comment action completed")
            except Exception as e:
                print(f"Error commenting: {e}")
            
            # Like posts
            try:
                self.like_posts()
                print("Like action completed")
            except Exception as e:
                print(f"Error liking posts: {e}")
            
            time.sleep(10)  # Final wait
            
        except Exception as e:
            print(f"Error in post-submission actions: {e}")

    def take_screenshot_and_send_discord(self, link, status, order, custom_message="", webhook_url=""):
        """Chụp màn hình và gửi lên Discord với settings tùy chỉnh"""
        try:
            app = QApplication.instance()
            if app is None:
                return
                
            screen = app.primaryScreen()
            screenshot = screen.grabWindow(0)
            
            # Tạo file tạm thời
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(temp_dir, f"facebook_post_{timestamp}.png")
            
            # Lưu ảnh
            screenshot.save(temp_file, "PNG")
            
            # Gửi lên Discord với webhook URL từ settings
            self.send_to_discord(temp_file, link, status, order, custom_message, webhook_url)
            
            # Xóa file tạm
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            print(f"Lỗi khi chụp màn hình: {e}")

    def send_to_discord(self, file_path, link, status, order, custom_message="", webhook_url=""):
        """Gửi file và thông tin lên Discord webhook với message tùy chỉnh"""
        try:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Tạo nội dung message
            if custom_message.strip():
                # Sử dụng template tùy chỉnh
                content = custom_message.replace("{timestamp}", timestamp) \
                                    .replace("{link}", link) \
                                    .replace("{status}", status) \
                                    .replace("{order}", str(order))
            else:
                # Sử dụng template mặc định
                content = f"""📸 **Facebook Auto Post Screenshot**
    📅 **Ngày giờ:** {timestamp}
    🔗 **Link:** {link}
    📊 **Trạng thái:** {status}
    🔢 **Thứ tự:** {order}
    ━━━━━━━━━━━━━━━━━━━━━━━━━"""
            
            # Chuẩn bị data
            with open(file_path, 'rb') as f:
                files = {
                    'file': (f'facebook_post_{order}.png', f, 'image/png')
                }
                data = {
                    'content': content
                }
                
                # Gửi request với webhook URL từ settings
                response = requests.post(webhook_url, data=data, files=files, timeout=30)
                
                if response.status_code == 200 or response.status_code == 204:
                    print(f"✅ Đã gửi screenshot bài đăng #{order} lên Discord")
                else:
                    print(f"❌ Lỗi gửi Discord: {response.status_code}")
                    
        except Exception as e:
            print(f"Lỗi khi gửi lên Discord: {e}")



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

            # Tạo thư mục profile nếu chưa tồn tại
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            self.driver = webdriver.Chrome(options=chrome_options)

            # Ẩn các dấu hiệu trình duyệt điều khiển
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'languages', { get: () => ['vi-VN', 'vi'] });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    window.chrome = { runtime: {} };
                """
            })

            # Cập nhật trạng thái UI
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
                self.postContent.setPlainText(config.get("textpost"))
                self.selected_image_path = config.get("imgaepath", "")
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
            "delay_in_ms": self.delaytype.text(),
            "textpost": self.postContent.toPlainText(),
            "imgaepath": self.selected_image_path if hasattr(self, 'selected_image_path') else ""
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
        # Tạo thư mục gốc "profiles" nếu chưa tồn tại
        base_dir = os.path.join(os.getcwd(), 'profiles')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Tạo tên profile duy nhất
        profile_name = f'Profile_{int(time.time())}'
        profile_path = os.path.join(base_dir, profile_name)

        if not os.path.exists(profile_path):
            os.makedirs(profile_path)

        # Cập nhật lại ComboBox
        self.updateProfileComboBox()

    def updateProfileComboBox(self):
        # Chỉ lấy các folder trong thư mục "profiles"
        profile_dir = os.path.join(os.getcwd(), 'profiles')
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)  # Đảm bảo tồn tại thư mục

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
        """Tìm kiếm groups Facebook với các bộ lọc được tối ưu"""
        self.initDriver()

        try:
            self.statusLabel.setText('Status: Loading Facebook page...')
            # Encode query để tránh lỗi URL
            encoded_query = urllib.parse.quote(query)
            
            # Load trang tìm kiếm
            base_url = f'https://www.facebook.com/search/groups/?q={encoded_query}'
            if self.privacyComboBox.currentText() == "Public":
                base_url += '&filters=eyJwdWJsaWNfZ3JvdXBzOjAiOiJ7XCJuYW1lXCI6XCJwdWJsaWNfZ3JvdXBzXCIsXCJhcmdzXCI6XCJcIn0ifQ%3D%3D'
            
            self.driver.get(base_url)
            
            # Đợi trang load
            self.waitForPageLoad()
            
            self.statusLabel.setText('Status: Scrolling and collecting data...')
            
            # Initialize tracking variables
            global_seen_links = set()
            results = []
            no_new_groups_count = 0
            max_no_new_attempts = 5
            
            while not self.stop_event.is_set():
                # Tìm tất cả groups trên trang
                groups = self.findGroupElements()
                
                if not groups:
                    no_new_groups_count += 1
                    if no_new_groups_count >= max_no_new_attempts:
                        self.statusLabel.setText('Status: No more groups found.')
                        break
                    
                    # Đợi và thử lại
                    time.sleep(2)
                    self.scrollDown()
                    continue
                
                # Xử lý từng group
                for group in groups:
                    if self.stop_event.is_set():
                        break
                    
                    group_data = self.extractGroupData(group)
                    if not group_data:
                        continue
                    
                    title, href, members, privacy = group_data
                    
                    # Kiểm tra duplicate
                    if href in global_seen_links:
                        continue
                    
                    # Áp dụng các bộ lọc
                    if not self.passesFilters(title, members, privacy):
                        global_seen_links.add(href)  # Vẫn đánh dấu là đã thấy
                        continue
                    
                    # Thêm vào kết quả
                    global_seen_links.add(href)
                    results.append((title, href, members, privacy))
                    new_groups_found += 1
                    
                    self.statusLabel.setText(f'Found: {title} ({len(results)} total)')
                
                # Cập nhật UI nếu có kết quả mới
                if results:
                    self.results_data.extend(results)
                    self.updateResultTable()
                    results.clear()
                
                # Nếu không tìm thấy group mới nào, tăng counter
                if new_groups_found == 0:
                    no_new_groups_count += 1
                
                # Kiểm tra điều kiện dừng
                if self.stop_event.is_set():
                    break
                
                # Scroll và cleanup
                self.scrollAndCleanup(groups)
                
                # Nghỉ ngắn để tránh spam
                time.sleep(1.5)
            
            # Cập nhật status cuối cùng
            final_status = 'Status: Search completed.' if not self.stop_event.is_set() else 'Status: Search stopped.'
            self.statusLabel.setText(final_status)
            
        except Exception as e:
            error_msg = f'Status: Error - {str(e)}'
            self.statusLabel.setText(error_msg)
            print(error_msg)
            
        finally:
            self.closeDriver()

    def waitForPageLoad(self, timeout=10):
        """Đợi trang load xong"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            time.sleep(3)  # Thêm thời gian cho JS load
        except TimeoutException:
            print("Page load timeout, continuing anyway...")

    def findGroupElements(self):
        """Tìm các element group trên trang"""
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] .x1yztbdb")
        except Exception as e:
            print(f"Error finding group elements: {e}")
            return []

    def extractGroupData(self, group):
        """Trích xuất dữ liệu từ group element"""
        try:
            # Tìm title và link
            title_elem = group.find_element(By.XPATH, './/a[@aria-hidden="true" and @role="presentation"]')
            title = title_elem.text.strip()
            href = title_elem.get_attribute('href')
            
            if not title or not href:
                return None
            
            # Tìm thông tin privacy và members
            privacy_elem = group.find_element(By.XPATH, './/span[contains(@class, "x1lliihq") and not(contains(@class, "x193iq5w"))]')
            privacy_text = privacy_elem.text.strip() if privacy_elem else 'N/A'
            
            # Parse privacy và members
            privacy, members = self.parsePrivacyAndMembers(privacy_text)
            
            return (title, href, members, privacy)
            
        except Exception as e:
            # Không log lỗi để tránh spam
            return None

    def parsePrivacyAndMembers(self, privacy_text):
        """Parse thông tin privacy và số lượng thành viên"""
        try:
            if ' · ' in privacy_text:
                parts = privacy_text.split(' · ')
                privacy = parts[0].strip()
                
                # Tìm số members từ phần thứ 2
                members_part = parts[1].strip()
                members = self.extractMemberCount(members_part)
            else:
                privacy = privacy_text
                members = '0'
            
            return privacy, members
            
        except Exception:
            return privacy_text, '0'

    def extractMemberCount(self, members_text):
        """Trích xuất số lượng thành viên từ text"""
        try:
            # Tìm số đầu tiên trong text
            import re
            
            # Xử lý các trường hợp: "1K members", "1.5K members", "100 members", etc.
            match = re.search(r'([\d,\.]+)\s*([KMkmb]?)', members_text)
            if match:
                number_str = match.group(1).replace(',', '')
                multiplier = match.group(2).upper()
                
                try:
                    number = float(number_str)
                    
                    if multiplier == 'K':
                        number *= 1000
                    elif multiplier == 'M':
                        number *= 1000000
                    
                    return str(int(number))
                except ValueError:
                    return '0'
            
            return '0'
            
        except Exception:
            return '0'

    def passesFilters(self, title, members, privacy):
        """Kiểm tra xem group có đạt các điều kiện lọc không"""
        try:
            # Lọc theo từ khóa bắt buộc
            if self.filterByKeywordsCheckBox.isChecked():
                keywords = [kw.strip().lower() for kw in self.keywordsInput.text().split(',') if kw.strip()]
                if keywords and not any(kw in title.lower() for kw in keywords):
                    return False
            
            # Lọc loại trừ từ khóa
            if self.excludeKeywordsCheckBox.isChecked():
                exclude_keywords = [kw.strip().lower() for kw in self.excludeKeywordsInput.text().split(',') if kw.strip()]
                if any(ex_kw in title.lower() for ex_kw in exclude_keywords):
                    return False
            
            # Lọc theo số lượng thành viên tối thiểu
            if self.minMembersCheckBox.isChecked():
                try:
                    min_members = int(self.minMembersInput.text().strip() or '0')
                    member_count = int(members) if members.isdigit() else 0
                    
                    if member_count < min_members:
                        return False
                except ValueError:
                    # Nếu không parse được, bỏ qua filter này
                    pass
            
            # Lọc theo privacy nếu cần
            privacy_filter = self.privacyComboBox.currentText()
            if privacy_filter != "All" and privacy_filter.lower() not in privacy.lower():
                return False
            
            return True
            
        except Exception as e:
            print(f"Error in filter check: {e}")
            return True  # Mặc định cho phép nếu có lỗi

    def scrollDown(self):
        """Scroll xuống trang"""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception as e:
            print(f"Error scrolling: {e}")

    def scrollAndCleanup(self, groups):
        """Scroll và cleanup các element cũ"""
        try:
            # Scroll xuống
            self.scrollDown()
            
            # Cleanup các element cũ để tránh memory leak
            if len(groups) > 10:
                for group in groups[:-5]:  # Giữ lại 5 element mới nhất
                    try:
                        self.driver.execute_script("arguments[0].remove();", group)
                    except:
                        continue  # Ignore nếu element đã bị remove
                        
        except Exception as e:
            print(f"Error in scroll and cleanup: {e}")



            
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

            if not os.path.exists(profile_path):
                os.makedirs(profile_path)

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            self.driver = webdriver.Chrome(options=chrome_options)

            # Ẩn navigator.webdriver và một số dấu hiệu automation
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'languages', { get: () => ['vi-VN', 'vi'] });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    window.chrome = { runtime: {} };
                """
            })





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
