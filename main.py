import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget
from moviepy.editor import VideoFileClip

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        # Set up the main window
        self.setWindowTitle("Video Trimmer")
        self.setGeometry(100, 100, 800, 600)

        # Create the central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create the video preview window
        self.video_label = QLabel(self.central_widget)
        self.layout.addWidget(self.video_label)

        # Create the time stamp input field and add button
        self.time_stamp_input = QLineEdit(self.central_widget)
        self.layout.addWidget(self.time_stamp_input)
        self.add_button = QPushButton("Add", self.central_widget)
        self.layout.addWidget(self.add_button)
        
        # Create the list of time stamps to remove
        self.time_stamps = []

        # Create the open and save buttons
        self.open_button = QPushButton("Open", self.central_widget)
        self.layout.addWidget(self.open_button)
        self.save_button = QPushButton("Save", self.central_widget)
        self.layout.addWidget(self.save_button)
        
        # Connect the buttons to their respective handlers
        self.open_button.clicked.connect(self.onopen)
        self.add_button.clicked.connect(self.onadd)
        self.save_button.clicked.connect(self.onsave)
        
        # Set up the video preview timer
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.update_preview)

    def onopen(self):
        # Show a file dialog to choose the video file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mov)")
        if not file_name:
            return

        # Open the video file and start the preview
        self.original_video = VideoFileClip(file_name)
        self.current_frame = 0
        self.preview_timer.start(round(1000 // self.original_video.fps))
    
    def onadd(self):
        # Parse the time stamp input and add it to the list
        time_stamp = self.parse_time_stamp(self.time_stamp_input.text())
        if time_stamp is not None:
            self.time_stamps.append(time_stamp)
            self.time_stamp_input.clear()
    
    def onsave(self):
        # Stop the preview and trim the video
        self.preview_timer.stop()
        trimmed_video = self.original_video.subclip(0, self.original_video.duration, True)
        for start, end in self.time_stamps:
            trimmed_video = trimmed_video.without_range(start, end)

        # Show a file dialog to choose the save location
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "Video Files (*.mp4)")
        if not file_name:
            return

        # Save the trimmed video to the chosen location
        trimmed_video.write_videofile(file_name)
        
    def update_preview(self):
        # Get the current frame and convert it to a QImage
        frame = self.original_video.get_frame(self.current_frame)
        frame = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)

        # Update the video preview label with the current frame
        self.video_label.setPixmap(QPixmap.fromImage(frame))

        # Increment the current frame and wrap around if necessary
        self.current_frame += 1
        if self.current_frame >= self.original_video.fps * self.original_video.duration:
            self.current_frame = 0
            
    def parse_time_stamp(self, time_stamp_str):
        # Split the time stamp string into its components
        try:
            hh, mm, ss, ms = map(int, time_stamp_str.split(":"))
        except ValueError:
            return None

        # Convert the time stamp to seconds and return it
        return hh * 3600 + mm * 60 + ss + ms / 1000
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
