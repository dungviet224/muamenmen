import sys
import os
import json
import time
import pyautogui
import pandas as pd
import unicodedata
import threading
from selenium import webdriver
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium.webdriver.chrome.options import Options
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QStackedWidget, 
                             QFormLayout, QHBoxLayout, QCheckBox, QComboBox, QFileDialog, QFrame, 
                             QScrollArea, QGroupBox, QAbstractItemView, QMessageBox)
from selenium.webdriver.common.by import By
from threading import Thread, Event, Lock
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QEvent
from groq import Groq

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
        self.pc = 0

    def applyStyles(self):
            # Giao diện tối giản màu hồng trắng
        self.setStyleSheet("""
             QWidget {
    background-color: #fafafa;
    color: #333333;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background: #ffffff;
}

QPushButton {
    background: #FF008A;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 10pt;
    min-height: 16px;
    transition: all 0.2s ease;
}

QPushButton:hover {
    background: #e60078;
    transform: scale(1.05);
}

QPushButton:pressed {
    background: #cc0070;
}

QPushButton:disabled {
    background: #e0e0e0;
    color: #999999;
}

/* Tab buttons */
QPushButton[objectName*="TabButton"] {
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 12px 12px 0px 0px;
    padding: 14px 28px;
    font-weight: 600;
    font-size: 11pt;
    margin-right: 3px;
    color: #666666;
    transition: all 0.2s ease;
}

QPushButton[objectName*="TabButton"]:hover {
    background: #f5f5f5;
    color: #333333;
    transform: scale(1.03);
}

/* Nút hành động chính */
QPushButton[objectName*="Action"] {
    background: #FF008A;
    font-weight: 700;
    padding: 14px 32px;
    border-radius: 12px;
    color: white;
    transition: all 0.2s ease;
}

QPushButton[objectName*="Action"]:hover {
    background: #e60078;
    transform: scale(1.08);
}

QPushButton[objectName*="Danger"] {
    background: #ff6b6b;
    transition: all 0.2s ease;
}

QPushButton[objectName*="Danger"]:hover {
    background: #ff5252;
    transform: scale(1.05);
}

/* Nút phụ */
QPushButton[objectName*="Secondary"] {
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    color: #666666;
    transition: all 0.2s ease;
}

QPushButton[objectName*="Secondary"]:hover {
    background: #f5f5f5;
    color: #333333;
    transform: scale(1.05);
}

QTextEdit, QLineEdit {
    background: #ffffff;
    border: 2px solid #ddd;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 10pt;
    color: #333333;
}

QTextEdit:focus, QLineEdit:focus {
    border: 2px solid #FF008A;
}

QComboBox {
    background: #ffffff;
    border: 2px solid #ddd;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 10pt;
    min-height: 22px;
    color: #333333;
}

QComboBox:hover {
    border: 2px solid #FF008A;
}

QComboBox:focus {
    border: 2px solid #FF008A;
}

QComboBox::drop-down {
    background: #FF008A;
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
    background: #ffffff;
    border: 1px solid #ddd;
    selection-background-color: #FFE6F0;
    border-radius: 8px;
}

QCheckBox {
    spacing: 10px;
    font-size: 10pt;
    font-weight: 500;
    color: #333333;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 2px solid #ddd;
    background: #ffffff;
}

QCheckBox::indicator:hover {
    border: 2px solid #FF008A;
}

QCheckBox::indicator:checked {
    background: #FF008A;
    border: 2px solid #FF008A;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #f9f9f9;
    gridline-color: #ddd;
    border: 1px solid #ddd;
    border-radius: 12px;
    font-size: 9pt;
    color: #333333;
}

QTableWidget::item {
    padding: 10px;
    border: none;
}

QTableWidget::item:selected {
    background: #FFE6F0;
    color: #333333;
}

QTableWidget::item:hover {
    background: #f5f5f5;
}

QHeaderView::section {
    background: #f9f9f9;
    color: #333333;
    padding: 12px;
    border: none;
    border-right: 1px solid #ddd;
    font-weight: 700;
    font-size: 10pt;
}

QHeaderView::section:hover {
    background: #f0f0f0;
}

QLabel {
    color: #333333;
    font-size: 10pt;
}

QLabel[objectName*="Status"] {
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
}

QLabel[objectName*="Title"] {
    font-size: 16pt;
    font-weight: 800;
    color: #333333;
    margin-bottom: 8px;
}

QGroupBox {
    font-weight: 700;
    font-size: 12pt;
    border: 2px solid #ddd;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
    background: #ffffff;
    color: #333333;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    background: #FF008A;
    color: white;
    border-radius: 6px;
    font-weight: 700;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: #f0f0f0;
    width: 14px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background: #FF008A;
    border-radius: 7px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #e60078;
}

QFrame[objectName*="Separator"] {
    background: #ddd;
    max-height: 1px;
    margin: 12px 0;
}
            """)
    def initUI(self):
        self.setWindowTitle('🔍 Facebook SKIBIDI')
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowState(Qt.WindowMaximized)
     

        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left sidebar for tabs (vertical layout)
        sidebar_widget = QWidget()
        sidebar_widget.setMaximumWidth(200)
        sidebar_widget.setMinimumWidth(180)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(8)

        # Header title in sidebar
        title_label = QLabel('Facebook Group\nSearcher Pro')
        title_label.setObjectName('titleLabel')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        sidebar_layout.addWidget(title_label)

        # Separator
        separator = QFrame()
        separator.setObjectName('separatorFrame')
        separator.setFrameShape(QFrame.HLine)
        sidebar_layout.addWidget(separator)

        # Vertical tab buttons
        self.searchTabButton = QPushButton('🔍 Search')
        self.searchTabButton.setObjectName('searchTabButton')
        self.searchTabButton.setMinimumHeight(45)
        self.searchTabButton.clicked.connect(lambda: self.switchTab(self.searchPage))
        sidebar_layout.addWidget(self.searchTabButton)

        self.postTabButton = QPushButton('📝 Post')
        self.postTabButton.setObjectName('postTabButton')
        self.postTabButton.setMinimumHeight(45)
        self.postTabButton.clicked.connect(lambda: self.switchTab(self.postPage))
        sidebar_layout.addWidget(self.postTabButton)
        
        self.profileTabButton = QPushButton('👤 Profile Manager')
        self.profileTabButton.setObjectName('profileTabButton')
        self.profileTabButton.setMinimumHeight(45)
        self.profileTabButton.clicked.connect(lambda: self.switchTab(self.profilePage))
        sidebar_layout.addWidget(self.profileTabButton)

        sidebar_layout.addStretch()

        # Action buttons at bottom of sidebar
        self.clearConsoleButton = QPushButton('🗑️ Clear Console')
        self.clearConsoleButton.setObjectName('secondaryButton')
        self.clearConsoleButton.setMinimumHeight(40)
        self.clearConsoleButton.clicked.connect(self.clearConsole)
        sidebar_layout.addWidget(self.clearConsoleButton)

        self.exportButton = QPushButton('📤 Export Results')
        self.exportButton.setObjectName('actionButton')
        self.exportButton.setMinimumHeight(40)
        self.exportButton.clicked.connect(self.exportResults)
        sidebar_layout.addWidget(self.exportButton)

        sidebar_widget.setLayout(sidebar_layout)

        # Create the stacked widget for page switching
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.setMinimumWidth(800)

        # Create pages
        self.createSearchPage()
        self.createPostPage()
        self.createProfilePage()
        
        # Add pages to stacked widget
        self.stackedWidget.addWidget(self.searchPage)
        self.stackedWidget.addWidget(self.postPage)
        self.stackedWidget.addWidget(self.profilePage)

        # Add sidebar and main content to main layout
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.stackedWidget)

        self.setLayout(main_layout)
        self.switchTab(self.searchPage)

    def switchTab(self, widget):
        self.stackedWidget.setCurrentWidget(widget)
        
        # Add hover effect animation
        self.animateButtonPress(widget)
        
        all_buttons = [self.searchTabButton, self.postTabButton, self.profileTabButton]
        for btn in all_buttons:
            btn.setStyleSheet("")
            btn.installEventFilter(self)
            
        if widget == self.searchPage:
            self.searchTabButton.setStyleSheet("background-color: #0078d4; color: white; border-radius: 8px;")
        elif widget == self.postPage:
            self.postTabButton.setStyleSheet("background-color: #0078d4; color: white; border-radius: 8px;")
        elif widget == self.profilePage:
            self.profileTabButton.setStyleSheet("background-color: #0078d4; color: white; border-radius: 8px;")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.HoverEnter:
            if obj in [self.searchTabButton, self.postTabButton, self.profileTabButton]:
                if obj.styleSheet() == "":
                    QTimer.singleShot(0, lambda: obj.setStyleSheet("background-color: #e6f3ff; border-radius: 8px;"))
        elif event.type() == QEvent.HoverLeave:
            if obj in [self.searchTabButton, self.postTabButton, self.profileTabButton]:
                if "background-color: #e6f3ff" in obj.styleSheet():
                    QTimer.singleShot(250, lambda: obj.setStyleSheet("") if "background-color: #e6f3ff" in obj.styleSheet() else None)
        return super().eventFilter(obj, event)

    def animateButtonPress(self, widget):
        if widget == self.searchPage:
            button = self.searchTabButton
        elif widget == self.postPage:
            button = self.postTabButton
        elif widget == self.profilePage:
            button = self.profileTabButton
        else:
            return
            
        # Simple press animation
        button.setStyleSheet("background-color: #005a9e; color: white; border-radius: 8px;")
        QTimer.singleShot(100, lambda: button.setStyleSheet("background-color: #0078d4; color: white; border-radius: 8px;"))

    def createSearchPage(self):
        self.searchPage = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Search input group
        search_group = QGroupBox("🔍 Search Configuration")
        search_group.setMinimumHeight(200)
        search_layout = QVBoxLayout()
        search_layout.setSpacing(10)
        
        self.searchBox = QTextEdit()
        self.searchBox.setPlaceholderText('Enter your search terms here...')
        self.searchBox.setFixedHeight(100)
        search_layout.addWidget(self.searchBox)

        self.keywordFilterBox = QLineEdit()
        self.keywordFilterBox.setPlaceholderText('🔍 Filter results by keywords...')
        self.keywordFilterBox.setFixedHeight(40)
        self.keywordFilterBox.textChanged.connect(self.filterResults)
        search_layout.addWidget(self.keywordFilterBox)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Search Filters Group
        filters_group = QGroupBox("🔧 Search Filters")
        filters_group.setMinimumHeight(220)
        filters_layout = QVBoxLayout()
        filters_layout.setSpacing(10)

        # Include keywords filter
        self.filterByKeywordsCheckBox = QCheckBox("✅ Include Groups with Keywords")
        self.filterByKeywordsCheckBox.setFixedHeight(35)
        filters_layout.addWidget(self.filterByKeywordsCheckBox)

        self.keywordsInput = QLineEdit()
        self.keywordsInput.setPlaceholderText("Enter keywords to include (comma separated)")
        self.keywordsInput.setFixedHeight(40)
        self.keywordsInput.setDisabled(True)
        filters_layout.addWidget(self.keywordsInput)

        # Exclude keywords filter
        self.excludeKeywordsCheckBox = QCheckBox("❌ Exclude Groups with Keywords")
        self.excludeKeywordsCheckBox.setFixedHeight(35)
        filters_layout.addWidget(self.excludeKeywordsCheckBox)

        self.excludeKeywordsInput = QLineEdit()
        self.excludeKeywordsInput.setPlaceholderText("Enter keywords to exclude (comma separated)")
        self.excludeKeywordsInput.setFixedHeight(40)
        self.excludeKeywordsInput.setDisabled(True)
        filters_layout.addWidget(self.excludeKeywordsInput)
        
        # Connect signals
        self.filterByKeywordsCheckBox.stateChanged.connect(self.toggleFilterByKeywords)
        self.excludeKeywordsCheckBox.stateChanged.connect(self.toggleExcludeKeywords)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(20)
        
        self.startSearchButton = QPushButton('🚀 Start Search')
        self.startSearchButton.setObjectName('actionButton')
        self.startSearchButton.setFixedHeight(50)
        self.startSearchButton.setMinimumWidth(160)
        self.startSearchButton.clicked.connect(self.startSearch)
        control_layout.addWidget(self.startSearchButton)

        self.stopButton = QPushButton('⏹️ Stop Search')
        self.stopButton.setObjectName('dangerButton')
        self.stopButton.setFixedHeight(50)
        self.stopButton.setMinimumWidth(160)
        self.stopButton.clicked.connect(self.stopSearch)
        control_layout.addWidget(self.stopButton)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Add some spacing
        layout.addSpacing(20)

        # Results table
        results_group = QGroupBox("📊 Search Results")
        results_layout = QVBoxLayout()
        
        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(4)
        self.resultTable.setHorizontalHeaderLabels(['Title', 'Link', 'Members', 'Post per day'])
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resultTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.resultTable.setAlternatingRowColors(True)
        self.resultTable.setMinimumHeight(300)
        results_layout.addWidget(self.resultTable)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Status
        self.statusLabel = QLabel('✅ Status: Ready to search')
        self.statusLabel.setObjectName('statusLabel')
        self.statusLabel.setFixedHeight(35)
        layout.addWidget(self.statusLabel)

        self.searchPage.setLayout(layout)

    def createPostPage(self):
        self.postPage = QWidget()
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Post Content Group
        content_group = QGroupBox("📝 Post Content")
        content_group.setMinimumHeight(350)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        self.postContent = QTextEdit()
        self.postContent.setPlaceholderText('Write your post content here...')
        self.postContent.setFixedHeight(170)
        content_layout.addWidget(self.postContent)

        self.AI = QPushButton('🤖 AI Rewirte')
        self.AI.setObjectName('secondaryButton')
        self.AI.setFixedHeight(45)
        self.AI.setMinimumWidth(200)
        self.AI.clicked.connect(self.rewrite_jd_with_ai)
        content_layout.addWidget(self.AI)
        # Image settings
        image_layout = QHBoxLayout()
        image_layout.setSpacing(15)
        
        self.enableImageCheckbox = QCheckBox("🖼️ Attach Image")
        self.enableImageCheckbox.setFixedHeight(35)
        self.enableImageCheckbox.stateChanged.connect(self.toggleImageSelection)
        image_layout.addWidget(self.enableImageCheckbox)

        self.selectImageButton = QPushButton('📁 Select Image')
        self.selectImageButton.setObjectName('secondaryButton')
        self.selectImageButton.setFixedHeight(40)
        self.selectImageButton.setMinimumWidth(130)
        self.selectImageButton.clicked.connect(self.selectImage)
        self.selectImageButton.setDisabled(True)
        image_layout.addWidget(self.selectImageButton)
        
        image_layout.addStretch()
        content_layout.addLayout(image_layout)

        self.imagePathLabel = QLabel('No image selected')
        self.imagePathLabel.setStyleSheet("color: #888888; font-style: italic;")
        self.imagePathLabel.setFixedHeight(30)
        content_layout.addWidget(self.imagePathLabel)
        
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)

        # Interaction Settings Group
        interaction_group = QGroupBox("💬 Interaction Settings")
        interaction_group.setMinimumHeight(350)
        interaction_layout = QVBoxLayout()
        interaction_layout.setSpacing(10)

        # Like post checkbox
        self.likePostCheckBox = QCheckBox("👍 Auto-like Posts")
        self.likePostCheckBox.setFixedHeight(35)
        interaction_layout.addWidget(self.likePostCheckBox)

        # Comment settings
        self.commentCheckBox = QCheckBox("💬 Auto-comment on Posts")
        self.commentCheckBox.setFixedHeight(35)
        self.commentCheckBox.stateChanged.connect(self.toggleCommentInput)
        interaction_layout.addWidget(self.commentCheckBox)
        
        self.onlyCommentNoPostCheckBox = QCheckBox("💭 Only comment, no post")
        self.onlyCommentNoPostCheckBox.setFixedHeight(35)
        interaction_layout.addWidget(self.onlyCommentNoPostCheckBox)
        
        # Min/Max comment delay range
        delay_range_layout = QHBoxLayout()
        delay_range_layout.setSpacing(10)
        
        delay_range_layout.addWidget(QLabel("🕓 Random range (min - max):"))

        self.minDelayInput = QLineEdit()
        self.minDelayInput.setPlaceholderText("Min")
        self.minDelayInput.setFixedHeight(40)
        self.minDelayInput.setFixedWidth(80)
        delay_range_layout.addWidget(self.minDelayInput)

        self.maxDelayInput = QLineEdit()
        self.maxDelayInput.setPlaceholderText("Max")
        self.maxDelayInput.setFixedHeight(40)
        self.maxDelayInput.setFixedWidth(80)
        delay_range_layout.addWidget(self.maxDelayInput)

        delay_range_layout.addStretch()
        interaction_layout.addLayout(delay_range_layout)
        
        self.commentInput = QTextEdit()
        self.commentInput.setPlaceholderText("Nhập nội dung comment")
        self.commentInput.setFixedHeight(80)
        self.commentInput.setDisabled(True)
        interaction_layout.addWidget(self.commentInput)

        # Typing speed settings
        self.enterContentCheckBox = QCheckBox("⌨️ Slow Typing Mode")
        self.enterContentCheckBox.setFixedHeight(35)
        self.enterContentCheckBox.stateChanged.connect(self.toggledelaytype)
        interaction_layout.addWidget(self.enterContentCheckBox)

        self.delaytype = QLineEdit()
        self.delaytype.setPlaceholderText("Typing delay in milliseconds (default: 5)")
        self.delaytype.setFixedHeight(40)
        self.delaytype.setDisabled(True)
        interaction_layout.addWidget(self.delaytype)
        
        interaction_group.setLayout(interaction_layout)
        layout.addWidget(interaction_group)

        # Discord Integration Group
        discord_group = QGroupBox("🎮 Discord Integration")
        discord_group.setMinimumHeight(400)
        discord_layout = QVBoxLayout()
        discord_layout.setSpacing(10)

        # Enable Discord notifications
        self.enableDiscordCheckBox = QCheckBox("📸 Enable Discord Screenshots")
        self.enableDiscordCheckBox.setFixedHeight(35)
        self.enableDiscordCheckBox.setChecked(True)
        self.enableDiscordCheckBox.stateChanged.connect(self.toggleDiscordSettings)
        discord_layout.addWidget(self.enableDiscordCheckBox)

        # Discord webhook URL
        webhook_layout = QHBoxLayout()
        webhook_layout.setSpacing(10)
        webhook_layout.addWidget(QLabel("🔗 Webhook URL:"))
        
        self.discordWebhookInput = QLineEdit()
        self.discordWebhookInput.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.discordWebhookInput.setFixedHeight(40)
        webhook_layout.addWidget(self.discordWebhookInput)
        discord_layout.addLayout(webhook_layout)

        # Test Discord connection
        test_layout = QHBoxLayout()
        test_layout.setSpacing(15)
        
        self.testDiscordButton = QPushButton('🧪 Test Discord Connection')
        self.testDiscordButton.setObjectName('secondaryButton')
        self.testDiscordButton.setFixedHeight(45)
        self.testDiscordButton.setMinimumWidth(200)
        self.testDiscordButton.clicked.connect(self.testDiscordConnection)
        test_layout.addWidget(self.testDiscordButton)
        
        self.discordStatusLabel = QLabel('📡 Status: Not tested')
        self.discordStatusLabel.setStyleSheet("color: #888888; font-style: italic;")
        self.discordStatusLabel.setFixedHeight(30)
        test_layout.addWidget(self.discordStatusLabel)
        
        test_layout.addStretch()
        discord_layout.addLayout(test_layout)

        # Discord message template
        template_layout = QVBoxLayout()
        template_layout.setSpacing(5)
        template_layout.addWidget(QLabel("📝 Message Template:"))
        
        # Screenshot options
        screenshot_options_layout = QHBoxLayout()
        screenshot_options_layout.setSpacing(10)
        
        self.screenshotDelayCheckBox = QCheckBox("⏰ Delay before screenshot")
        self.screenshotDelayCheckBox.setFixedHeight(35)
        screenshot_options_layout.addWidget(self.screenshotDelayCheckBox)
        
        self.screenshotDelayInput = QLineEdit()
        self.screenshotDelayInput.setPlaceholderText("seconds")
        self.screenshotDelayInput.setFixedHeight(40)
        self.screenshotDelayInput.setFixedWidth(80)
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

        # Post Controls Group
        controls_group = QGroupBox("🎛️ Post Controls")
        controls_group.setMinimumHeight(200)
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)

        # Delay setting
        delay_layout = QHBoxLayout()
        delay_layout.setSpacing(10)
        delay_layout.addWidget(QLabel("⏱️ Delay between posts:"))
        
        self.delayInput = QLineEdit()
        self.delayInput.setPlaceholderText("seconds")
        self.delayInput.setFixedHeight(40)
        self.delayInput.setFixedWidth(120)
        delay_layout.addWidget(self.delayInput)
        
        delay_layout.addStretch()
        controls_layout.addLayout(delay_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.postButton = QPushButton('🚀 Start Posting')
        self.postButton.setObjectName('actionButton')
        self.postButton.setFixedHeight(50)
        self.postButton.setMinimumWidth(160)
        self.postButton.clicked.connect(self.startPosting)
        button_layout.addWidget(self.postButton)

        self.stopPostButton = QPushButton('⏹️ Stop Posting')
        self.stopPostButton.setObjectName('dangerButton')
        self.stopPostButton.setFixedHeight(50)
        self.stopPostButton.setMinimumWidth(160)
        self.stopPostButton.clicked.connect(self.stopPosting)
        button_layout.addWidget(self.stopPostButton)
        
        button_layout.addStretch()
        controls_layout.addLayout(button_layout)

        # File operations
        file_layout = QHBoxLayout()
        file_layout.setSpacing(20)
        
        self.loadFileButton = QPushButton('📂 Load Groups File')
        self.loadFileButton.setObjectName('secondaryButton')
        self.loadFileButton.setFixedHeight(45)
        self.loadFileButton.setMinimumWidth(160)
        self.loadFileButton.clicked.connect(self.loadFile)
        file_layout.addWidget(self.loadFileButton)

        self.selectAllCheckBox = QCheckBox("☑️ Select All Groups")
        self.selectAllCheckBox.setFixedHeight(35)
        self.selectAllCheckBox.stateChanged.connect(self.selectAll)
        file_layout.addWidget(self.selectAllCheckBox)
        
        file_layout.addStretch()
        controls_layout.addLayout(file_layout)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Status
        self.postStatusLabel = QLabel('✅ Status: Ready to post')
        self.postStatusLabel.setObjectName('statusLabel')
        self.postStatusLabel.setFixedHeight(35)
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
        self.resultTableaa.setMinimumHeight(300)
        table_layout.addWidget(self.resultTableaa)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Set layout for scroll widget
        scroll_widget.setLayout(layout)
        scroll.setWidget(scroll_widget)

        # Main layout for post page
        main_layout = QVBoxLayout(self.postPage)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def createProfilePage(self):
            self.profilePage = QWidget()
            
            # Create scroll area for profile settings
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            scroll_widget = QWidget()
            layout = QVBoxLayout()
            layout.setSpacing(25)
            layout.setContentsMargins(30, 30, 30, 30)

            # Profile Management Group
            profile_group = QGroupBox("👤 Profile Management")
            profile_group.setMinimumHeight(180)
            profile_layout = QVBoxLayout()
            profile_layout.setSpacing(15)
            
            # Profile control buttons
            profile_control_layout = QHBoxLayout()
            profile_control_layout.setSpacing(20)
            
            self.profileCreationButton = QPushButton('➕ Create New Profile')
            self.profileCreationButton.setObjectName('actionButton')
            self.profileCreationButton.setFixedHeight(50)
            self.profileCreationButton.setMinimumWidth(200)
            self.profileCreationButton.clicked.connect(self.createNewProfile)
            profile_control_layout.addWidget(self.profileCreationButton)
            
            self.openCloseBrowserButton = QPushButton('🌐 Open Browser')
            self.openCloseBrowserButton.setObjectName('secondaryButton')
            self.openCloseBrowserButton.setFixedHeight(50)
            self.openCloseBrowserButton.setMinimumWidth(160)
            self.openCloseBrowserButton.clicked.connect(self.toggleBrowser)
            profile_control_layout.addWidget(self.openCloseBrowserButton)
            
            profile_control_layout.addStretch()
            profile_layout.addLayout(profile_control_layout)

 
            self.startProfileButton = QPushButton('▶️ Start Selected')
            self.startProfileButton.setObjectName('actionButton')
            self.startProfileButton.setFixedHeight(40)
            self.startProfileButton.setMinimumWidth(140)
            self.startProfileButton.clicked.connect(self.run_random_nurture_account)
            profile_control_layout.addWidget(self.startProfileButton)

            self.stopProfileButton = QPushButton('⏸️ Stop Selected')
            self.stopProfileButton.setObjectName('actionButton')
            self.stopProfileButton.setFixedHeight(40)
            self.stopProfileButton.setMinimumWidth(140)
            self.stopProfileButton.clicked.connect(self.stop_nurture_account)
            profile_control_layout.addWidget(self.stopProfileButton)  
            self.statusLabel1 = QLabel('idk')
            self.statusLabel1.setObjectName('statusLabel')
            self.statusLabel1.setFixedHeight(35)
            layout.addWidget(self.statusLabel1)
            profile_control_layout.addStretch()
        
            # Add spacing
            profile_layout.addSpacing(10)

            # Profile selector
            profile_selector_layout = QHBoxLayout()
            profile_selector_layout.setSpacing(15)
            
            profile_label = QLabel("Select Profile:")
            profile_label.setMinimumWidth(100)
            profile_selector_layout.addWidget(profile_label)
            
            self.profileComboBox = QComboBox()
            self.profileComboBox.setFixedHeight(40)
            self.profileComboBox.setMinimumWidth(300)
            profile_selector_layout.addWidget(self.profileComboBox)
            
            profile_selector_layout.addStretch()
            profile_layout.addLayout(profile_selector_layout)
            
            profile_group.setLayout(profile_layout)
            layout.addWidget(profile_group)
            # Add stretch to push save button to bottom
            layout.addStretch()

            # Save settings button
            save_layout = QHBoxLayout()
            save_layout.addStretch()
            
            self.saveSettingsButton = QPushButton('💾 Save All Settings')
            self.saveSettingsButton.setObjectName('actionButton')
            self.saveSettingsButton.setFixedHeight(50)
            self.saveSettingsButton.setMinimumWidth(180)
            self.saveSettingsButton.clicked.connect(self.saveSettings)
            save_layout.addWidget(self.saveSettingsButton)
            
            layout.addLayout(save_layout)

            # Set layout for scroll widget
            scroll_widget.setLayout(layout)
            scroll.setWidget(scroll_widget)
            
            # Main profile page layout
            main_profile_layout = QVBoxLayout()
            main_profile_layout.setContentsMargins(0, 0, 0, 0)
            main_profile_layout.addWidget(scroll)
            self.profilePage.setLayout(main_profile_layout)

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
    def rewrite_jd_with_ai(self):
        # Lấy nội dung JD từ widget
        jd_text = self.postContent.toPlainText().strip()

        # Tạo prompt chuẩn
        prompt = (
            "Bạn là chuyên gia viết content tuyển dụng người Việt. Hãy đọc mô tả công việc sau và viết lại thành nội dung tuyển dụng thu hút, phù hợp đăng Facebook.\n\n"
            "⚠️ Chỉ trả về nội dung đúng theo định dạng chuẩn bên dưới, tuyệt đối không thêm câu giải thích, không nhận xét, không thừa thông tin:\n\n"
            "[Địa điểm]\n"
            "📢 TIÊU ĐỀ TUYỂN DỤNG (ví dụ: TUYỂN DỤNG UI ARTIST – GAME MOBILE)\n"
            "👉 Đoạn giới thiệu hấp dẫn về công ty, cơ hội phát triển, lý do nên ứng tuyển.\n\n"
            "💼 VỊ TRÍ: [Tên vị trí]\n\n"
            "💰 THU NHẬP & PHÚC LỢI:\n"
            "✅ [Các quyền lợi, mức lương, chế độ phúc lợi]\n\n"
            "🌟 MÔI TRƯỜNG LÀM VIỆC:\n"
            "- [Các đặc điểm nổi bật về môi trường, cơ hội học hỏi]\n\n"
            "👉 CÔNG VIỆC CHÍNH:\n"
            "- [Các đầu việc chính cần thực hiện]\n\n"
            "🔥 Kêu gọi ứng tuyển hấp dẫn (tạo cảm hứng cho ứng viên nộp CV ngay)\n"
            "______________________\n"
            "📩 Hướng dẫn nộp CV, thông tin liên hệ chi tiết (email, số điện thoại, zalo…)\n\n"
            f"Mô tả công việc cần viết lại: {jd_text}"
        )

        try:
            # Khởi tạo client Groq
            client = Groq(api_key="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")  # Thay bằng API Key thật của bạn

            # Gửi yêu cầu
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
            )

            # Lấy kết quả
            result = response.choices[0].message.content

            # Gán kết quả lên label
            self.postContent.setText(result)

        except Exception as e:
            print(e)

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
            'screenshot_delay': int(self.screenshotDelayInput.text()) if self.screenshotDelayCheckBox.isChecked() and self.screenshotDelayInput.text().isdigit() else 0
        }
    def toggleCommentInput(self, state):
        self.commentInput.setDisabled(state == 0)

    def toggledelaytype(self, state):
        self.delaytype.setDisabled(state == 0)

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

# Connect button in your createProfilePage method:
# self.recheckButton
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
            cc = f"{index + 1}/{total_links}"
            # Post content to group
            if self.onlyCommentNoPostCheckBox.isChecked():
                        self.comment()
                        self.driver.get("https://www.facebook.com/watch/")
                        time.sleep(delay)
            else:                      
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
    def run_random_nurture_account(self):
        """Hàm chính chạy ngẫu nhiên các hành động nuôi acc"""
        if hasattr(self, 'is_running') and self.is_running:
            print("⚠️ Bot đang chạy rồi!")
            self.statusLabel1.setText("⚠️ Bot đang chạy rồi!")
            return
        
        # Chạy trong thread riêng để không freeze UI
        self.nurture_thread = threading.Thread(target=self._nurture_worker)
        self.nurture_thread.daemon = True
        self.nurture_thread.start()

    def _nurture_worker(self):
        """Worker function chạy trong thread riêng"""
        # Khởi tạo trạng thái
        self.is_running = True
        self.initDriver()

        start_time = time.time()
        total_duration = random.randint(30, 60) * 60  # 30-120 phút
        
        print(f"🚀 Bắt đầu nuôi acc - thời gian: {total_duration//60} phút")
        self.statusLabel1.setText(f"🚀 Đang nuôi acc - {total_duration//60} phút")
        
        # Danh sách các hành động
        actions = [
            ('Like Posts', lambda: self.like_posts()),
            ('Like Pages', lambda: self.like_pages()),
            ('Click Friends', lambda: self.combined_click_friends()),
            ('Watch Stories', lambda: self.watch_stories(random.randint(10, 30))),
            ('Pokes', lambda: self.pokes()),
            ('Watch/Reel', lambda: self.run_watch_or_reel(random.randint(3, 10)))
        ]
        
        while self.is_running and (time.time() - start_time) < total_duration:
            try:
                # Tính thời gian còn lại
                elapsed = time.time() - start_time
                remaining = total_duration - elapsed
                
                if remaining <= 0:
                    break
                    
                # Cập nhật trạng thái
                remaining_minutes = int(remaining // 60)
                remaining_seconds = int(remaining % 60)
                self.statusLabel1.setText(f"⏳ Còn lại: {remaining_minutes:02d}:{remaining_seconds:02d}")
                
                # Chọn hành động ngẫu nhiên
                action_name, action_func = random.choice(actions)
                print(f"🎯 Thực hiện: {action_name}")
                self.statusLabel1.setText(f"🎯 Đang {action_name} - Còn {remaining_minutes:02d}:{remaining_seconds:02d}")
                
                # Chạy hành động
                action_func()
                
                # Delay ngẫu nhiên giữa các hành động (2-10 phút)
                delay = random.randint(120, 600)
                print(f"😴 Nghỉ {delay//60} phút {delay%60} giây...")
                
                # Đếm ngược delay
                for i in range(delay):
                    if not self.is_running:
                        break
                    remaining_delay = delay - i
                    remaining_total = remaining - i
                    total_minutes = int(remaining_total // 60)
                    total_seconds = int(remaining_total % 60)
                    self.statusLabel1.setText(f"😴 Nghỉ {remaining_delay}s - Còn {total_minutes:02d}:{total_seconds:02d}")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Lỗi: {e}")
                self.statusLabel1.setText(f"❌ Lỗi: {str(e)[:50]}")
                time.sleep(5)
                continue
        
        # Kết thúc
        self.is_running = False
        if remaining <= 0:
            print("⏰ Hoàn thành ")
            self.statusLabel1.setText("⏰ Hoàn thành ")
        else:
            print("🛑 Đã dừng")
            self.statusLabel1.setText("🛑 Đã dừng ")

    def stop_nurture_account(self):
        """Dừng quá trình"""
        self.is_running = False
        print("🛑 Đã dừng")
        self.statusLabel1.setText("🛑 Đã dừng ")
        self.driver.quit
        # Đợi thread kết thúc
        if hasattr(self, 'nurture_thread') and self.nurture_thread.is_alive():
            self.nurture_thread.join(timeout=2)
    def like_pages(self):
        self.driver.get("https://www.facebook.com/pages/?category=top&ref=bookmarks")
        time.sleep(5)  # chờ trang load

        # Tìm tất cả div có đủ các class chỉ định
        page_buttons = self.driver.find_elements(
            "xpath",
            "//div"
            "[contains(@class,'xdj266r') and "
            "contains(@class,'xat24cr') and "
            "contains(@class,'xexx8yu') and "
            "contains(@class,'xyri2b') and "
            "contains(@class,'x18d9i69') and "
            "contains(@class,'x1c1uobl') and "
            "contains(@class,'x6s0dn4') and "
            "contains(@class,'x78zum5') and "
            "contains(@class,'xl56j7k') and "
            "contains(@class,'x14ayic') and "
            "contains(@class,'xwyz465') and "
            "contains(@class,'x1e0frkt')]"
        )

        if not page_buttons or len(page_buttons) <= 2:
            print("❗ Không đủ nút page để like (hoặc không tìm thấy).")
            return

        # Bỏ 2 nút đầu tiên
        available_buttons = page_buttons[2:]

        # Chọn ngẫu nhiên 1–3 nút, không vượt quá số nút còn lại
        num_to_click = random.randint(1, min(3, len(available_buttons)))
        selected_buttons = random.sample(available_buttons, num_to_click)

        print(f"🔎 Đang like {num_to_click} page trong {len(available_buttons)} page có sẵn (đã bỏ qua 2 cái đầu).")

        for idx, btn in enumerate(selected_buttons, 1):
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(random.uniform(0.5, 1.5))  # delay trước khi click
                btn.click()
                print(f"👍 Đã like page thứ {idx}/{num_to_click}")
                time.sleep(random.uniform(2, 4))  # delay sau click
            except Exception as e:
                print(f"⚠️ Lỗi khi like page thứ {idx}: {e}")

    def combined_click_friends(self):
        self.driver.get("https://www.facebook.com/friends")
        time.sleep(5)  # chờ trang load

        # --------- Lượt 1: click nút với 20 class ---------
        buttons1 = self.driver.find_elements(
            "xpath",
            "//div"
            "[contains(@class,'x1ja2u2z') and "
            "contains(@class,'x78zum5') and "
            "contains(@class,'x2lah0s') and "
            "contains(@class,'x1n2onr6') and "
            "contains(@class,'xl56j7k') and "
            "contains(@class,'x6s0dn4') and "
            "contains(@class,'xozqiw3') and "
            "contains(@class,'x1q0g3np') and "
            "contains(@class,'x14ldlfn') and "
            "contains(@class,'x1b1wa69') and "
            "contains(@class,'xws8118') and "
            "contains(@class,'x5fzff1') and "
            "contains(@class,'x972fbf') and "
            "contains(@class,'x10w94by') and "
            "contains(@class,'x1qhh985') and "
            "contains(@class,'x14e42zd') and "
            "contains(@class,'x9f619') and "
            "contains(@class,'xpdmqnj') and "
            "contains(@class,'x1g0dm76') and "
            "contains(@class,'xtvsq51') and "
            "contains(@class,'x1r1pt67')]"
        )

        if buttons1:
            print(f"🔎 Lượt 1: tìm thấy {len(buttons1)} nút.")
            num_loops1 = random.randint(1, 3)
            print(f"🔄 Lượt 1 sẽ lặp {num_loops1} lần.")
            index1 = 0
            for loop in range(1, num_loops1 + 1):
                if index1 >= len(buttons1):
                    print("✅ Lượt 1: đã click hết các nút, dừng sớm.")
                    break
                try:
                    btn = buttons1[index1]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(random.uniform(0.5, 1.5))
                    btn.click()
                    print(f"✅ Lượt 1: đã click nút {index1+1}/{len(buttons1)}")
                    index1 += 1
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"⚠️ Lượt 1: lỗi khi click nút {index1+1}: {e}")
        else:
            print("❗ Lượt 1: không tìm thấy nút nào.")

        # --------- Lượt 2: click nút với 21 class ---------
        buttons2 = self.driver.find_elements(
            "xpath",
            "//div"
            "[contains(@class,'x1ja2u2z') and "
            "contains(@class,'x78zum5') and "
            "contains(@class,'x2lah0s') and "
            "contains(@class,'x1n2onr6') and "
            "contains(@class,'xl56j7k') and "
            "contains(@class,'x6s0dn4') and "
            "contains(@class,'xozqiw3') and "
            "contains(@class,'x1q0g3np') and "
            "contains(@class,'x14ldlfn') and "
            "contains(@class,'x1b1wa69') and "
            "contains(@class,'xws8118') and "
            "contains(@class,'x5fzff1') and "
            "contains(@class,'x972fbf') and "
            "contains(@class,'x10w94by') and "
            "contains(@class,'x1qhh985') and "
            "contains(@class,'x14e42zd') and "
            "contains(@class,'x9f619') and "
            "contains(@class,'xpdmqnj') and "
            "contains(@class,'x1g0dm76') and "
            "contains(@class,'x1hr4nm9') and "
            "contains(@class,'x1r1pt67')]"
        )

        if buttons2:
            print(f"🔎 Lượt 2: tìm thấy {len(buttons2)} nút.")
            num_loops2 = random.randint(1, 2)
            print(f"🔄 Lượt 2 sẽ lặp {num_loops2} lần.")
            index2 = 0
            for loop in range(1, num_loops2 + 1):
                if index2 >= len(buttons2):
                    print("✅ Lượt 2: đã click hết các nút, dừng sớm.")
                    break
                try:
                    btn = buttons2[index2]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(random.uniform(0.5, 1.5))
                    btn.click()
                    print(f"✅ Lượt 2: đã click nút {index2+1}/{len(buttons2)}")
                    index2 += 1
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"⚠️ Lượt 2: lỗi khi click nút {index2+1}: {e}")
        else:
            print("❗ Lượt 2: không tìm thấy nút nào.")

    def watch_stories(self, delay):
        self.driver.get("https://www.facebook.com/stories")
        time.sleep(5)  # chờ trang stories load

        # Tìm tất cả các nút story đủ class
        story_buttons = self.driver.find_elements(
            "xpath",
            "//div[contains(@class,'x9f619') and "
            "contains(@class,'x1ja2u2z') and "
            "contains(@class,'x78zum5') and "
            "contains(@class,'x2lah0s') and "
            "contains(@class,'x1n2onr6') and "
            "contains(@class,'x1qughib') and "
            "contains(@class,'x6s0dn4') and "
            "contains(@class,'xozqiw3') and "
            "contains(@class,'x1q0g3np')]"
        )

        if len(story_buttons) < 3:
            print("❗ Không đủ story để click (phải >= 3).")
            return

        # Bỏ qua 2 cái đầu, chọn 1 cái ngẫu nhiên trong phần còn lại
        available_buttons = story_buttons[2:]
        selected_button = random.choice(available_buttons)

        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", selected_button)
            time.sleep(random.uniform(0.5, 1.5))
            selected_button.click()
            print("✅ Đã mở story.")
            time.sleep(delay)
        except Exception as e:
            print(f"⚠️ Lỗi khi click vào story: {e}")

    def pokes(self):
        self.driver.get("https://www.facebook.com/pokes")
        time.sleep(5)  # đợi trang load xong

        # Tìm tất cả các nút chọc
        poke_buttons = self.driver.find_elements(
            "xpath", "//div[contains(@class,'x1diwwjn') and contains(@class,'x1n2onr6') and contains(@class,'x1e56ztr') and contains(@class,'x1xmf6yo') and contains(@class,'xamitd3')]"
        )

        # Kiểm tra có nút nào không
        if not poke_buttons:
            print("❗ Không tìm thấy nút chọc nào.")
            return

        # Chọn ngẫu nhiên số lượng người cần chọc (2-5, nhưng không vượt quá tổng số nút có sẵn)
        num_to_poke = random.randint(2, min(10, len(poke_buttons)))
        poke_sample = random.sample(poke_buttons, num_to_poke)

        for idx, button in enumerate(poke_sample, 1):
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(random.uniform(0.5, 1.5))  # delay tự nhiên
                button.click()
                print(f"✅ Đã chọc người thứ {idx}/{num_to_poke}")
            except Exception as e:
                print(f"⚠️ Không chọc được người thứ {idx}: {e}")
    def run_watch_or_reel(self, delay):
        link = random.choice(["https://www.facebook.com/watch"])
        print(f"Mở link: {link}")
        self.driver.get(link)
        print(f"Đang ở trang 'watch', chờ {delay} giây...")
        time.sleep(delay)

        # Gọi hành động like sau khi đã xem xong
        try:
            self.like_posts()
            print("✅ Đã hoàn thành like các bài viết.")
        except Exception as e:
            print(f"❌ Lỗi khi like bài viết: {e}")
    def like_posts(self):
        if self.likePostCheckBox.isChecked():
            print("🔍 Đang tìm các nút 'Thích'...")
            try:
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
            try:
                min_val = int(self.minDelayInput.text() or 1)
                max_val = int(self.maxDelayInput.text() or 1)
                num_to_comment = random.randint(min_val, max_val)

                comment_block = self.commentInput.toPlainText().strip()
                if not comment_block:
                    print("Không có nội dung comment.")
                    return

                count = 0
                scroll_try = 0
                max_scroll = 50
                element_index = 1

                while count < num_to_comment and scroll_try < max_scroll:
                    try:
                        # Tìm tất cả textarea hoặc div có text giống "Viết bình luận công khai..."
                        comment_boxes = self.driver.find_elements(
                            By.XPATH,
                            "//div[@contenteditable='true' and @data-lexical-editor='true' and (@aria-placeholder='Viết câu trả lời...' or @aria-placeholder='Viết bình luận công khai...')]"
                        )

                        if element_index >= len(comment_boxes):
                            self.driver.execute_script("window.scrollBy(0, 400);")
                            time.sleep(2)
                            scroll_try += 1
                            continue

                        comment_box = comment_boxes[element_index]
                        if comment_box:
                            comment_text = unicodedata.normalize('NFC', comment_block)

                            comment_box.click()
                            time.sleep(0.1)

                            for char in comment_text:
                                if char == '\n':
                                    # Dùng Shift+Enter để xuống dòng mà không gửi comment
                                    ActionChains(self.driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
                                else:
                                    try:
                                        ActionChains(self.driver).send_keys(char).perform()
                                    except Exception:
                                        try:
                                            comment_box.send_keys(char)
                                        except Exception:
                                            try:
                                                self.driver.execute_script(
                                                    "arguments[0].value += arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                                                    comment_box, char
                                                )
                                            except Exception:
                                                print(f"⚠️ Skipped character: {repr(char)}")

                            # Enter 2 lần cho chắc
                            comment_box.send_keys(Keys.ENTER)
                            time.sleep(1)
                            comment_box.send_keys(Keys.ENTER)

                            print(f"→ [{count+1}] Đã comment: {comment_block}")
                            count += 1
                            element_index += 1
                            scroll_try = 0  # Reset scroll counter khi comment thành công
                            time.sleep(random.uniform(20, 50))
                            
                            # Chỉ cuộn khi chưa đủ số lượng comment cần thiết
                            if count < num_to_comment:
                                self.driver.execute_script("window.scrollBy(0, 250);")
                                time.sleep(random.uniform(3, 6))

                    except Exception as e:
                        print(f"→ Lỗi khi comment post thứ {element_index}: {e}")
                        # Khi có lỗi, cuộn để tìm element tiếp theo
                        self.driver.execute_script("window.scrollBy(0, 250);")
                        time.sleep(1)

                print(f"Đã comment xong {count} lần.")

            except Exception as e:
                print(f"Lỗi chung khi thực hiện comment: {e}")
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
                        try:
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
                            pyperclip.copy(post_content)
                            content_area.click()
                            content_area.send_keys(Keys.CONTROL + 'v')
                            time.sleep(1)
                            print(f"❌ Error typing content slowly: {e}")
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
                webhook_url=discord_settings['webhook_url']
            )
            
        except Exception as e:
            print(f"Error handling Discord notification: {e}")

    def _perform_post_actions(self):
        """Perform post-submission actions (like, comment) with error handling"""
        try:
            time.sleep(20)  # Wait for post to be fully loaded
            
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

    def take_screenshot_and_send_discord(self, link, status, order, webhook_url=""):
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
            self.send_to_discord(temp_file, link, status, order, webhook_url)
            
            # Xóa file tạm
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            print(f"Lỗi khi chụp màn hình: {e}")

    def send_to_discord(self, file_path, link, status, order,  webhook_url=""):
        """Gửi file và thông tin lên Discord webhook với message tùy chỉnh"""
        try:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
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
       
   
                # Load additional settings
                self.likePostCheckBox.setChecked(config.get("like_post_enabled", False))
                self.commentCheckBox.setChecked(config.get("comment_enabled", False))
                self.commentInput.setText(config.get("comment_text", ""))
                self.enterContentCheckBox.setChecked(config.get("enter_content_word_by_word", False))
                self.delaytype.setText(config.get("delay_in_ms", ""))
                self.onlyCommentNoPostCheckBox.setChecked(config.get("onlycomment_enabled", False))
                self.maxDelayInput.setText(config.get("max", ""))
                self.minDelayInput.setText(config.get("min", ""))
                self.postContent.setPlainText(config.get("textpost"))
                self.selected_image_path = config.get("imgaepath", "")
        else:
            self.saveSettings()

    def saveSettings(self):
        config = {
            "profile_subfolder": self.profileComboBox.currentText(),
            # Save additional settings
            "like_post_enabled": self.likePostCheckBox.isChecked(),
            "comment_enabled": self.commentCheckBox.isChecked(),
            "comment_text": self.commentInput.toPlainText(),
            "enter_content_word_by_word": self.enterContentCheckBox.isChecked(),
            "delay_in_ms": self.delaytype.text(),
            "textpost": self.postContent.toPlainText(),
            "imgaepath": self.selected_image_path if hasattr(self, 'selected_image_path') else "",
            "onlycomment_enabled": self.onlyCommentNoPostCheckBox.isChecked(),
            "min": self.minDelayInput.text(),
            "max": self.maxDelayInput.text()
        }
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        self.statusLabel.setText('Status: Settings saved.')





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
            new_groups_found = 0
            
            max_groups_to_find = 200  # Số nhóm cần quét tối đa
            groups_found = 0

            for _ in range(max_groups_to_find):
                if self.stop_event.is_set():
                    break
                
                # Tìm tất cả groups trên trang
                groups = self.findGroupElements()

                if not groups:
                    no_new_groups_count += 1
                    if no_new_groups_count >= max_no_new_attempts:
                        self.statusLabel.setText('Status: No more groups found.')
                        break

                    time.sleep(2)
                    self.scrollDown()
                    continue

                for group in groups:
                    if self.stop_event.is_set():
                        break

                    group_data = self.extractGroupData(group)
                    if not group_data:
                        continue

                    title, href, members, privacy = group_data

                    if href in global_seen_links:
                        continue

                    global_seen_links.add(href)

                    results.append((title, href, members,))
                    new_groups_found += 1
                    groups_found += 1

                    self.statusLabel.setText(f'Found: {title} ({groups_found} total)')

                    if groups_found >= max_groups_to_find:
                        break

                if results:
                    self.results_data.extend(results)
                    self.updateResultTable()
                    results.clear()

                if new_groups_found == 0:
                    no_new_groups_count += 1

                if self.stop_event.is_set():
                    break

                self.scrollAndCleanup(groups)
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
                privacy = parts[2].strip()
                
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
            df = pd.DataFrame(self.results_data, columns=['Title', 'Link', 'Members', 'post per day'])
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
