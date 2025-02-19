from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QWidget, QComboBox,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, QTimer
import cv2
import sys


class ImageEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelFlow")

        # ضبط أبعاد النافذة
        window_width, window_height = 1090, 600
        self.resize(window_width, window_height)

        # الحصول على أبعاد الشاشة
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # حساب موقع النافذة لتكون في منتصف الشاشة
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.move(x, y)

        # ضبط الأيقونة
        self.setWindowIcon(QIcon(r"C:\Users\Adel\Desktop\سنة ثالثة\د -محمد الشبلي\pythonProject\illustrator.ico"))

        # إعداد المتغيرات
        self.cv_image = None
        self.original_image = None
        self.history = []
        self.camera_active = False
        self.capture = None

        # تهيئة الواجهة
        self.init_ui()

    def init_ui(self):
        # التخطيط الرئيسي
        main_layout = QHBoxLayout()

        # تخطيط الأزرار اليسرى واليمنى
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        self.create_left_buttons(left_layout)
        self.create_right_buttons(right_layout)

        # منطقة عرض الصورة
        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)
        self.image_label.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444; border-radius: 10px;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # دمج التخطيطات
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(right_layout)

        # تعيين التخطيط في الواجهة الرئيسية
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_left_buttons(self, layout):
        button_style = self.get_button_style()

        open_button = QPushButton("📂 Open Image")
        open_button.setStyleSheet(button_style)
        open_button.clicked.connect(self.open_image)
        layout.addWidget(open_button)

        camera_button = QPushButton("📸 Open Camera")
        camera_button.setStyleSheet(button_style)
        camera_button.clicked.connect(self.open_camera)
        layout.addWidget(camera_button)

        save_button = QPushButton("💾 Save Image")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(self.save_image)
        layout.addWidget(save_button)

        reset_button = QPushButton("🔄 Reset Image")
        reset_button.setStyleSheet(button_style)
        reset_button.clicked.connect(self.reset_image)
        layout.addWidget(reset_button)

        exit_button = QPushButton("🚪 Exit")
        exit_button.setStyleSheet(button_style)
        exit_button.clicked.connect(self.exit_app)
        layout.addWidget(exit_button)

        layout.addStretch()

    def create_right_buttons(self, layout):
        button_style = self.get_button_style()

        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(["Choose Filter", "Grayscale", "Mirror Image", "Increase Brightness", "Blur"])
        self.filter_dropdown.setStyleSheet(self.get_combobox_style())
        self.filter_dropdown.currentIndexChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_dropdown)

        zoom_in_button = QPushButton("🔍 Zoom In")
        zoom_in_button.setStyleSheet(button_style)
        zoom_in_button.clicked.connect(self.zoom_in)
        layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton("🔎 Zoom Out")
        zoom_out_button.setStyleSheet(button_style)
        zoom_out_button.clicked.connect(self.zoom_out)
        layout.addWidget(zoom_out_button)

        undo_button = QPushButton("↩️ Undo")
        undo_button.setStyleSheet(button_style)
        undo_button.clicked.connect(self.undo)
        layout.addWidget(undo_button)

        layout.addStretch()

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.cv_image = cv2.imread(file_path)
            self.original_image = self.cv_image.copy()
            self.history = [self.cv_image.copy()]
            self.display_image()

    def open_camera(self):
        if not self.camera_active:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                QMessageBox.critical(self, "Error", "Failed to open camera!")
                return

            self.camera_active = True
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
        else:
            self.close_camera()

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            self.cv_image = frame
            self.display_image()

    def close_camera(self):
        self.camera_active = False
        self.timer.stop()
        self.capture.release()
        self.cv_image = None
        self.image_label.clear()

    def save_image(self):
        if self.cv_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
            if file_path:
                cv2.imwrite(file_path, self.cv_image)
                QMessageBox.information(self, "Saved", "Image saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "No image to save.")

    def apply_filter(self, index):
        if self.cv_image is not None:
            if index == 1:  # Grayscale
                self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
                self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_GRAY2BGR)
            elif index == 2:  # Mirror Image
                self.cv_image = cv2.flip(self.cv_image, 1)
            elif index == 3:  # Increase Brightness
                self.cv_image = cv2.convertScaleAbs(self.cv_image, alpha=1.2, beta=30)
            elif index == 4:  # Blur
                self.cv_image = cv2.GaussianBlur(self.cv_image, (15, 15), 0)
            self.history.append(self.cv_image.copy())
            self.display_image()

    def reset_image(self):
        if self.original_image is not None:
            self.cv_image = self.original_image.copy()
            self.history = [self.cv_image.copy()]
            self.display_image()

    def zoom_in(self):
        if self.cv_image is not None:
            self.cv_image = cv2.resize(self.cv_image, None, fx=1.2, fy=1.2)
            self.history.append(self.cv_image.copy())
            self.display_image()

    def zoom_out(self):
        if self.cv_image is not None:
            self.cv_image = cv2.resize(self.cv_image, None, fx=0.8, fy=0.8)
            self.history.append(self.cv_image.copy())
            self.display_image()

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.cv_image = self.history[-1]
            self.display_image()

    def display_image(self):
        if self.cv_image is not None:
            rgb_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_image.shape
            bytes_per_line = channel * width
            q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def exit_app(self):
        self.close_camera()
        self.close()

    def get_button_style(self):
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            padding: 12px;
            border: none;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        """

    def get_combobox_style(self):
        return """
        QComboBox {
            font-size: 16px;
            padding: 8px;
            border-radius: 6px;
            background-color: #ddd;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageEditorApp()
    window.show()
    sys.exit(app.exec())
