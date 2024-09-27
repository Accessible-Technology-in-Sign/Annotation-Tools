import sys
import os
import json
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QComboBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QTranslator, QSize
from PyQt5.QtGui import QKeySequence, QColor
import vlc

def load_config(config_path='config.json'):
    """
    Load the configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Configuration parameters.
    """
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

class AnnotationApp(QWidget):
    """
    Main application class for the Sign Language Annotation Tool.
    Inherits from PyQt5's QWidget.
    """

    def __init__(self, config):
        """
        Initialize the application with the provided configuration.

        Args:
            config (dict): Configuration parameters loaded from config.json.
        """
        super().__init__()
        self.config = config  # Store configuration
        self.translator = QTranslator()  # Translator for multilingual support
        self.initUI()  # Initialize the user interface
        self.load_signs()  # Load the list of signs from sign_list.txt
        self.load_batches()  # Load available review batches
        self.current_video_index = 0  # Index of the currently displayed video
        self.annotations = {}  # Dictionary to store annotations
        self.load_progress()  # Load previous annotation progress, if any
        self.apply_translation()  # Apply language translations based on config

    def initUI(self):
        """
        Set up the user interface components.
        """
        # Set the window title, which will be translated
        self.setWindowTitle(self.tr('Sign Language Annotation Tool'))

        # Create layout containers
        main_layout = QVBoxLayout()  # Main vertical layout
        top_layout = QHBoxLayout()  # Horizontal layout for selectors
        video_layout = QVBoxLayout()  # Layout for video display
        controls_layout = QHBoxLayout()  # Layout for video controls
        annotation_layout = QHBoxLayout()  # Layout for annotation buttons

        # ----- Top Panel: Batch and Word Selection -----

        # Label and combo box for selecting the review batch
        self.batch_label = QLabel(self.tr('Select Review Batch:'))
        self.batch_combo = QComboBox()
        self.batch_combo.currentIndexChanged.connect(self.batch_selected)  # Trigger when selection changes

        # Label and combo box for selecting the word within the batch
        self.word_label = QLabel(self.tr('Select Word:'))
        self.word_combo = QComboBox()
        self.word_combo.currentIndexChanged.connect(self.word_selected)  # Trigger when selection changes

        # Add batch and word selectors to the top layout
        top_layout.addWidget(self.batch_label)
        top_layout.addWidget(self.batch_combo)
        top_layout.addWidget(self.word_label)
        top_layout.addWidget(self.word_combo)
        # Note: Language selection has been removed from the UI as per requirements

        # ----- Video Player Area -----

        # Initialize VLC player instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Label to serve as the video display area
        
        self.video_frame = QLabel(self.tr("Video Display Area"))
        self.video_frame.setAlignment(Qt.AlignCenter)  # Center the text
        self.video_frame.setFixedSize(QSize(640, 480))  # Initial fixed size; will adjust dynamically

        # Ensure the video frame expands and centers the video
        self.video_frame.setSizePolicy(self.video_frame.sizePolicy().horizontalPolicy(), 
                                       self.video_frame.sizePolicy().verticalPolicy())
        
        '''
        # Frame to serve as the video display area
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")  # Set background to black for better visibility
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setSizePolicy(self.video_frame.sizePolicy().Expanding, 
                                       self.video_frame.sizePolicy().Expanding)
        '''


        # Add the video frame to the video layout
        video_layout.addWidget(self.video_frame)

        #video_layout.setCentralWidget(self.video_frame)
        #self.setCentralWidget(self.video_frame)
        

        # ----- Video Controls Panel -----

        # Create a merged Play/Pause button with translated labels
        self.play_pause_button = QPushButton(self.tr('Play'))
        self.play_pause_button.clicked.connect(self.toggle_play_pause)  # Connect to toggle function

        # Create additional video control buttons with translated labels
        self.replay_button = QPushButton(self.tr('Replay'))
        self.replay_button.clicked.connect(self.replay_video)  # Connect to replay function

        self.speed_up_button = QPushButton(self.tr('Speed Up'))
        self.speed_up_button.clicked.connect(self.speed_up)  # Connect to speed up function

        self.slow_down_button = QPushButton(self.tr('Slow Down'))
        self.slow_down_button.clicked.connect(self.slow_down)  # Connect to slow down function

        self.next_button = QPushButton(self.tr('Next'))
        self.next_button.clicked.connect(self.next_video)  # Connect to next video function
        self.next_button.setEnabled(False)  # Initially disabled until labeled

        self.prev_button = QPushButton(self.tr('Previous'))
        self.prev_button.clicked.connect(self.prev_video)  # Connect to previous video function

        # Add control buttons to the controls layout
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addWidget(self.replay_button)
        controls_layout.addWidget(self.speed_up_button)
        controls_layout.addWidget(self.slow_down_button)
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.next_button)

        # ----- Annotation Buttons Panel -----

        # Create annotation buttons with translated labels
        self.good_button = QPushButton(self.tr('Good'))
        self.good_button.clicked.connect(lambda: self.annotate('Good'))  # Annotate as 'Good'

        self.variant_button = QPushButton(self.tr('Variant'))
        self.variant_button.clicked.connect(lambda: self.annotate('Variant'))  # Annotate as 'Variant'

        self.unrecognizable_button = QPushButton(self.tr('Unrecognizable'))
        self.unrecognizable_button.clicked.connect(lambda: self.annotate('Unrecognizable'))  # Annotate as 'Unrecognizable'

        self.further_review_button = QPushButton(self.tr('Further Review'))
        self.further_review_button.clicked.connect(lambda: self.annotate('Further Review'))  # Annotate as 'Further Review'

        # Add annotation buttons to the annotation layout
        annotation_layout.addWidget(self.good_button)
        annotation_layout.addWidget(self.variant_button)
        annotation_layout.addWidget(self.unrecognizable_button)
        annotation_layout.addWidget(self.further_review_button)

        # ----- Current Label Display -----

        # Label to display the current annotation
        self.current_label_display = QLabel(self.tr('Current Label: None'))
        annotation_layout.addWidget(self.current_label_display)

        # ----- Help Button -----

        # Create a help button with a translated label
        self.help_button = QPushButton(self.tr('Help'))
        self.help_button.clicked.connect(self.show_help)  # Connect to help function

        # Add the help button to the annotation layout
        annotation_layout.addWidget(self.help_button)

        # ----- Assemble All Layouts into the Main Layout -----

        main_layout.addLayout(top_layout)  # Add top panel
        main_layout.addLayout(video_layout)  # Add video display
        main_layout.addLayout(controls_layout)  # Add video controls
        main_layout.addLayout(annotation_layout)  # Add annotation buttons and label display

        # Set the main layout for the QWidget
        self.setLayout(main_layout)

        # Set the initial size and position of the application window
        self.setGeometry(100, 100, 800, 600)

        # ----- Enable Keyboard Shortcuts (Hotkeys) -----

        # Load hotkey mappings from config
        self.hotkeys = self.config.get('hotkeys', {})
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure the widget can receive keyboard events

    def apply_translation(self):
        """
        Apply language translation based on the configuration file.
        Loads the appropriate .qm file and installs the translator.
        """
        selected_lang = self.config.get('language', 'en')  # Get the language code from config
        translation_file = f"translations/{selected_lang}.qm"  # Path to the .qm file

        # Attempt to load the translation file
        if self.translator.load(translation_file):
            app.installTranslator(self.translator)  # Install the translator to the application
            self.retranslate_ui()  # Update UI texts with the new translations
        else:
            # Show a warning if the translation file is not found
            QMessageBox.warning(
                self, 
                "Warning", 
                f"Translation file not found for language: {selected_lang}"
            )

    def retranslate_ui(self):
        """
        Update all UI elements with the translated text.
        This method is called after applying the translator.
        """
        self.setWindowTitle(self.tr('Sign Language Annotation Tool'))
        self.batch_label.setText(self.tr('Select Review Batch:'))
        self.word_label.setText(self.tr('Select Word:'))
        self.play_pause_button.setText(self.tr('Play'))  # Initial label
        self.replay_button.setText(self.tr('Replay'))
        self.speed_up_button.setText(self.tr('Speed Up'))
        self.slow_down_button.setText(self.tr('Slow Down'))
        self.next_button.setText(self.tr('Next'))
        self.prev_button.setText(self.tr('Previous'))
        self.good_button.setText(self.tr('Good'))
        self.variant_button.setText(self.tr('Variant'))
        self.unrecognizable_button.setText(self.tr('Unrecognizable'))
        self.further_review_button.setText(self.tr('Further Review'))
        self.help_button.setText(self.tr('Help'))
        self.video_frame.setText(self.tr("Video Display Area"))
        self.current_label_display.setText(self.tr('Current Label: None'))

    def load_signs(self):
        """
        Load the list of signs from the sign_list.txt file specified in the config.
        Populate the word_combo with the loaded signs.
        """
        sign_list_path = self.config['sign_list']  # Path to sign_list.txt
        with open(sign_list_path, 'r') as f:
            self.signs = [line.strip() for line in f.readlines()]  # Read and strip each line
        self.word_combo.addItems(self.signs)  # Populate the word selection combo box

    def load_batches(self):
        """
        Load available review batches from the review_source directory.
        Populate the batch_combo with the found batches.
        """
        review_source = self.config['review_source']  # Path to the review_source directory
        # List all directories within review_source
        self.batches = [
            d for d in os.listdir(review_source) 
            if os.path.isdir(os.path.join(review_source, d))
        ]
        self.batch_combo.addItems(self.batches)  # Populate the batch selection combo box

    def batch_selected(self):
        """
        Handle the event when a new batch is selected.
        Loads the corresponding words for the selected batch.
        """
        batch = self.batch_combo.currentText()  # Get the selected batch
        word_dir = os.path.join(self.config['review_source'], batch)  # Path to the selected batch directory
        # List all directories (words) within the selected batch
        words = [
            d for d in os.listdir(word_dir) 
            if os.path.isdir(os.path.join(word_dir, d))
        ]
        self.word_combo.clear()  # Clear existing word selections
        self.word_combo.addItems(words)  # Populate with new words

    def word_selected(self):
        """
        Handle the event when a new word is selected.
        Resets the video index and loads the videos for the selected word.
        """
        self.current_video_index = 0  # Reset to the first video
        self.load_videos()  # Load videos for the selected word

    def load_videos(self):
        """
        Load all videos for the currently selected batch and word.
        """
        batch = self.batch_combo.currentText()  # Get selected batch
        word = self.word_combo.currentText()  # Get selected word
        video_dir = os.path.join(self.config['review_source'], batch, word)  # Path to videos
        # List all video files with supported extensions and sort them
        self.videos = sorted([
            f for f in os.listdir(video_dir) 
            if f.endswith(('.mp4', '.avi', '.mov'))
        ])
        self.video_dir = video_dir  # Store the current video directory
        self.display_video()  # Display the first video

    def display_video(self):
        """
        Display the current video based on current_video_index.
        """
        if self.current_video_index < len(self.videos):
            video_path = os.path.join(
                self.video_dir, 
                self.videos[self.current_video_index]
            )
            self.play_video_path(video_path)  # Play the video at the given path
        else:
            # Inform the user if there are no more videos to annotate
            QMessageBox.information(
                self, 
                self.tr("Info"), 
                self.tr("No more videos in this batch.")
            )
            self.next_button.setEnabled(False)  # Disable Next button
            self.play_pause_button.setEnabled(False)  # Disable Play/Pause button

    def play_video_path(self, path):
        """
        Play the video located at the specified path using VLC.

        Args:
            path (str): Path to the video file.
        """
        if os.path.exists(path):
            media = self.instance.media_new(path)  # Create a new media instance
            self.player.set_media(media)  # Set media to the player

            # Platform-specific video frame handling
            if sys.platform.startswith('linux'):  # Linux
                self.player.set_xwindow(self.video_frame.winId())
            elif sys.platform == "win32":  # Windows
                self.player.set_hwnd(self.video_frame.winId())
            elif sys.platform == "darwin":  # macOS
                self.player.set_nsobject(int(self.video_frame.winId()))

            self.player.play()  # Start playing the video
            self.play_pause_button.setText(self.tr('Pause'))  # Update button to 'Pause'
            self.next_button.setEnabled(False)  # Disable Next until annotated
            self.current_label_display.setText(self.tr('Current Label: None'))  # Reset label display
        else:
            # Warn the user if the video file is not found
            QMessageBox.warning(
                self, 
                "Warning", 
                f"Video not found: {path}"
            )

    def toggle_play_pause(self):
        """
        Toggle between playing and pausing the video.
        Updates the button label accordingly.
        """
        state = self.player.get_state()
        if state == vlc.State.Playing:
            self.player.pause()
            self.play_pause_button.setText(self.tr('Play'))
        else:
            self.player.play()
            #self.display_video()
            self.play_pause_button.setText(self.tr('Pause'))

    def replay_video(self):
        """
        Replay the current video from the beginning.
        """
        self.player.stop()  # Stop the video
        self.player.play()  # Play again
        #self.display_video()
        self.play_pause_button.setText(self.tr('Pause'))  # Ensure button shows 'Pause'
        self.next_button.setEnabled(False)  # Disable Next until annotated
        self.current_label_display.setText(self.tr('Current Label: None'))  # Reset label display

    def speed_up(self):
        """
        Increase the playback speed of the current video.
        """
        current_rate = self.player.get_rate()  # Get current playback rate
        self.player.set_rate(current_rate + 0.1)  # Increase by 0.1x

    def slow_down(self):
        """
        Decrease the playback speed of the current video.
        Ensures the rate does not go below 0.1x.
        """
        current_rate = self.player.get_rate()  # Get current playback rate
        self.player.set_rate(max(0.1, current_rate - 0.1))  # Decrease by 0.1x, minimum 0.1x

    def next_video(self):
        """
        Move to the next video in the list after saving the current annotation.
        """
        self.save_annotation()  # Save current annotation
        self.current_video_index += 1  # Increment video index
        self.display_video()  # Display the next video

    def prev_video(self):
        """
        Move to the previous video in the list after saving the current annotation.
        """
        self.save_annotation()  # Save current annotation
        self.current_video_index = max(0, self.current_video_index - 1)  # Decrement index but not below 0
        self.display_video()  # Display the previous video

    def annotate(self, category):
        """
        Annotate the current video with the specified category.

        Args:
            category (str): The annotation category (e.g., 'Good', 'Variant').
        """
        video_name = self.videos[self.current_video_index]  # Get the current video filename
        word = self.word_combo.currentText()  # Get the current word being annotated
        self.annotations[video_name] = category  # Store the annotation

        self.current_label_display.setText(self.tr(f'Current Label: {category}'))  # Update label display
        self.next_button.setEnabled(True)  # Enable Next button after labeling

        self.save_annotation()  # Save the annotation to CSV
        self.save_state()  # Save the current state for resuming later

    def save_annotation(self):
        """
        Save all current annotations to the specified CSV file.
        Each word has its own annotations.csv file.
        """
        if hasattr(self, 'video_dir'):
            word = self.word_combo.currentText()  # Current word
            output_dir = os.path.join(self.config['output'], word)  # Output directory for the word
            os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

            annotations_file = os.path.join(output_dir, 'annotations.csv')  # Path to annotations.csv

            # Convert annotations dictionary to a DataFrame
            df = pd.DataFrame(
                list(self.annotations.items()), 
                columns=['filename', 'category']
            )
            df['sign'] = word  # Add the sign column
            df = df[['sign', 'filename', 'category']]  # Reorder columns

            # Append the annotations to the CSV file
            df.to_csv(
                annotations_file, 
                mode='a', 
                header=not os.path.exists(annotations_file),  # Write header only if file doesn't exist
                index=False
            )
            self.annotations = {}  # Clear the annotations dictionary

    def show_help(self):
        """
        Show a pop-up window with the reference video for the current word.
        """
        word = self.word_combo.currentText()  # Current word
        reference_path = os.path.join(
            self.config['reference_source'], 
            f"{word}.mp4"
        )  # Path to the reference video

        if os.path.exists(reference_path):
            help_window = HelpWindow(reference_path, self.config)  # Create a HelpWindow instance
            help_window.exec_()  # Execute the pop-up window
        else:
            # Warn the user if the reference video is not found
            QMessageBox.warning(
                self, 
                "Warning", 
                f"Reference video not found: {reference_path}"
            )

    def load_progress(self):
        """
        Load the annotation progress from a state file (state.json).
        This allows resuming annotation from where it was left off.
        """
        state_file = 'state.json'  # Name of the state file
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)  # Load the state data

            # Set the batch selection if it exists in the state
            batch_index = self.batch_combo.findText(state['batch'])
            if batch_index != -1:
                self.batch_combo.setCurrentIndex(batch_index)

            # Set the word selection if it exists in the state
            word_index = self.word_combo.findText(state['word'])
            if word_index != -1:
                self.word_combo.setCurrentIndex(word_index)

            # Set the current video index
            self.current_video_index = state.get('video_index', 0)
            self.display_video()  # Display the video at the loaded index

    def save_state(self):
        """
        Save the current annotation progress to a state file (state.json).
        """
        state = {
            'batch': self.batch_combo.currentText(),  # Current batch
            'word': self.word_combo.currentText(),  # Current word
            'video_index': self.current_video_index  # Current video index
        }
        with open('state.json', 'w') as f:
            json.dump(state, f)  # Write the state data to the file

    def keyPressEvent(self, event):
        """
        Handle key press events to map hotkeys to actions based on config.

        Args:
            event (QKeyEvent): The key event.
        """
        key = event.key()
        key_text = QKeySequence(key).toString().lower()  # Get the key as a string

        # Map hotkeys to actions
        if key_text == self.hotkeys.get('pause_key', '').lower():
            self.toggle_play_pause()
        elif key_text == self.hotkeys.get('replay_key', '').lower():
            self.replay_video()
        elif key_text == self.hotkeys.get('speed_up_key', '').lower():
            self.speed_up()
        elif key_text == self.hotkeys.get('slow_down_key', '').lower():
            self.slow_down()
        elif key_text == self.hotkeys.get('next_key', '').lower():
            if self.next_button.isEnabled():
                self.next_video()
        elif key_text == self.hotkeys.get('prev_key', '').lower():
            self.prev_video()
        elif key_text == self.hotkeys.get('good_key', '').lower():
            self.annotate('Good')
        elif key_text == self.hotkeys.get('variant_key', '').lower():
            self.annotate('Variant')
        elif key_text == self.hotkeys.get('unrecognizable_key', '').lower():
            self.annotate('Unrecognizable')
        elif key_text == self.hotkeys.get('further_review_key', '').lower():
            self.annotate('Further Review')
        else:
            super().keyPressEvent(event)  # Pass the event to the base class

class HelpWindow(QMessageBox):
    """
    Pop-up window to display the reference video for annotation.
    Inherits from PyQt5's QMessageBox.
    """

    def __init__(self, reference_video, config):
        """
        Initialize the HelpWindow with the reference video path.

        Args:
            reference_video (str): Path to the reference video file.
            config (dict): Configuration parameters.
        """
        super().__init__()
        self.setWindowTitle(self.tr("Reference Video"))  # Set the window title
        self.setText(self.tr("Reference Video for Annotation"))  # Set the display text
        self.reference_video = reference_video  # Store the reference video path

        # Create a play button to play the reference video
        self.play_button = QPushButton(self.tr('Play Reference Video'))
        self.play_button.clicked.connect(self.play_video)  # Connect to the play_video function

        # Add the play button to the message box layout
        self.layout().addWidget(self.play_button)

    def play_video(self):
        """
        Play the reference video using VLC when the play button is clicked.
        """
        instance = vlc.Instance()  # Create a new VLC instance
        player = instance.media_player_new()  # Create a new media player
        media = instance.media_new(self.reference_video)  # Load the media
        player.set_media(media)  # Set media to the player

        # Platform-specific video frame handling
        if sys.platform.startswith('linux'):
            player.set_xwindow(self.winId())
        elif sys.platform == "win32":
            player.set_hwnd(self.winId())
        elif sys.platform == "darwin":
            player.set_nsobject(int(self.winId()))

        player.play()  # Play the reference video
    
    def closeEvent(self, event):
         """
         Handle the event when the HelpWindow is closed.
         """
         # Ensure that the video stops playing when the window is closed
         super().closeEvent(event)

if __name__ == '__main__':
    """
    Entry point of the application.
    Loads the configuration, initializes the application, and starts the event loop.
    """
    config = load_config('config.json')  # Load configuration from config.json
    app = QApplication(sys.argv)  # Create the QApplication instance

    # Initialize the translator for the application before creating the main window
    translator = QTranslator()
    selected_lang = config.get('language', 'en')  # Get the language code from config
    translation_file = f"translations/{selected_lang}.qm"  # Path to the translation file

    # Attempt to load and install the translation
    if translator.load(translation_file):
        app.installTranslator(translator)  # Install the translator to the application
    else:
        # Show a warning if the translation file is not found
        QMessageBox.warning(
            None, 
            "Warning", 
            f"Translation file not found for language: {selected_lang}"
        )

    ex = AnnotationApp(config)  # Create an instance of the main application
    ex.show()  # Display the application window
    sys.exit(app.exec_())  # Start the application's event loop
