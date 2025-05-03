import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLabel,
    QVBoxLayout, QFrame, QSizePolicy, QLineEdit, QPushButton, QHBoxLayout, QGridLayout
)
from PyQt5.QtGui import QMovie, QColor, QTextCharFormat, QFont, QTextBlockFormat, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values

os.environ["QT_LOGGING_RULES"] = "*.debug=false"

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")

current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")
DataPath = os.path.join(current_dir, "Data")

os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(DataPath, exist_ok=True)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, Filename)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    return '\n'.join([line for line in lines if line.strip()])

def QueryModifier(query):
    query = query.lower().strip()
    if any(word in query for word in ["how", "what", "who", "where", "when"]):
        return query.capitalize().rstrip('.!?') + "?"
    return query.capitalize().rstrip('.!?') + "."

def SetGenerationPrompt(prompt):
    try:
        with open(TempDirectoryPath("ImageGeneration.data"), "w", encoding="utf-8") as file:
            file.write(f"{prompt},True")
    except Exception as e:
        print("Error writing image generation prompt:", e)

def ShowTextToScreen(Text):
    try:
        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
            file.write(Text)
    except Exception as e:
        print("Error writing response text:", e)

class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self.old_chat_message = ""

        layout = QVBoxLayout(self)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        layout.addWidget(self.chat_text_edit)

        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        movie.setScaledSize(QSize(220, 220))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()

        self.label = QLabel()
        self.label.setStyleSheet("color: white; font-size:16px;")
        self.label.setAlignment(Qt.AlignRight)

        layout.addWidget(self.gif_label)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.LoadMessages)
        self.timer.start(200)

    def LoadMessages(self):
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages and messages != self.old_chat_message:
                    self.addMessage(messages, color='White')
                    self.old_chat_message = messages
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

    def set_status(self, status: str):
        """
        Sets the assistant's status message in the label.
        """
        self.label.setText(status)
        self.label.adjustSize()  # Adjust label size after text change

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Image Generator")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: magenta ; color: red;")
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.chat_section = ChatSection()
        main_layout.addWidget(self.chat_section)

        prompt_layout = QHBoxLayout()
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Enter prompt to generate images")
        self.prompt_input.setStyleSheet("background-color: white; color: black;")
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setStyleSheet("background-color: green; color: white;")
        self.generate_btn.clicked.connect(self.handle_generate)
        prompt_layout.addWidget(self.prompt_input)
        prompt_layout.addWidget(self.generate_btn)

        self.image_grid = QGridLayout()
        self.image_labels = [QLabel() for _ in range(4)]
        for i, label in enumerate(self.image_labels):
            label.setFixedSize(250, 250)
            label.setStyleSheet("border: 1px solid white;")
            self.image_grid.addWidget(label, i // 2, i % 2)

        main_layout.addLayout(prompt_layout)
        main_layout.addLayout(self.image_grid)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.load_generated_images)
        self.timer.start(2000)

    def handle_generate(self):
        prompt = self.prompt_input.text().strip()
        if prompt:
            self.chat_section.set_status("Processing...")
            SetGenerationPrompt(prompt)
            ShowTextToScreen(f"Prompt submitted: {prompt}")
            self.chat_section.set_status("Image Generated")

    def load_generated_images(self):
        prompt = self.prompt_input.text().strip().replace(" ", "-")
        for i in range(4):
            image_path = os.path.join(DataPath, f"{prompt}{i+1}.png")
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path).scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_labels[i].setPixmap(pixmap)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    GraphicalUserInterface()

