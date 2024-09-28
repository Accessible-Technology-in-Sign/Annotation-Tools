import sys
import os
import json
import pandas as pd
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QComboBox, QMessageBox, QFrame, QDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QTranslator, QSize, QTimer
from PyQt5.QtGui import QKeySequence, QColor, QResizeEvent
import vlc

# Configure logging
logging.basicConfig(
    filename='annotation_app.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def load_config(config_path='config.json'):
    """
    Load and validate the configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Configuration parameters.

    Raises:
        KeyError: If required configuration keys are missing.
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the configuration file contains invalid JSON.
    """
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        logging.critical(f"Configuration file {config_path} not found.")
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    except json.JSONDecodeError as e:
        logging.critical(f"Error decoding JSON from {config_path}: {e}")
        raise ValueError(f"Error decoding JSON from {config_path}: {e}")

    # Validate required keys
    required_keys = ['sign_list', 'review_source', 'output', 'reference_source', 'language', 'hotkeys', 'annotation_categories']
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required config key: {key}")
            raise KeyError(f"Missing required config key: {key}")

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
        self.current_video_index = 0  # Index of the currently displayed video
        self.annotations = {}  # Dictionary to store final annotations
        self.in_progress_annotations = {}  # Temporary in-progress annotations
        self.initUI()  # Initialize the user interface
        self.load_signs()  # Load the list of signs from sign_list.txt
        self.load_batches()  # Load available review batches
        self.load_state()  # Load previous annotation progress, if any
        self.apply_translation()  # Apply language translations based on config
        logging.info("AnnotationApp initialized.")

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
        self.word_combo.setEnabled(False)  # Disabled until a batch is selected

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

        # Use QFrame instead of QLabel for better video rendering
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setMinimumSize(640, 480)  # Set minimum size
        self.video_frame.setSizePolicy(
            self.video_frame.sizePolicy().Expanding, 
            self.video_frame.sizePolicy().Expanding
        )

        # Add the video frame to the video layout
        video_layout.addWidget(self.video_frame)

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

        # Load annotation categories from config
        self.annotation_categories = self.config.get('annotation_categories', ['Good', 'Variant', 'Unrecognizable', 'Further Review'])

        # Dynamically create annotation buttons based on categories
        self.annotation_buttons = {}
        for category in self.annotation_categories:
            button = QPushButton(self.tr(category))
            button.clicked.connect(lambda checked, cat=category: self.annotate(cat))
            annotation_layout.addWidget(button)
            self.annotation_buttons[category] = button

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
        self.setGeometry(100, 100, 800, 700)  # Increased height for better layout

        # ----- Enable Keyboard Shortcuts (Hotkeys) -----

        # Load hotkey mappings from config
        self.hotkeys = self.config.get('hotkeys', {})
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure the widget can receive keyboard events

        # ----- Initialize In-Progress Annotations -----
        self.in_progress_file = 'in_progress.csv'  # Temporary in-progress annotations file
        logging.info("UI initialized.")

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
            logging.info(f"Loaded translation for language: {selected_lang}")
        else:
            # Show a warning if the translation file is not found
            QMessageBox.warning(
                self, 
                self.tr("Warning"), 
                self.tr(f"Translation file not found for language: {selected_lang}")
            )
            logging.warning(f"Translation file not found for language: {selected_lang}")

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
        # Update annotation buttons
        for category, button in self.annotation_buttons.items():
            button.setText(self.tr(category))
        self.help_button.setText(self.tr('Help'))
        self.video_frame.setToolTip(self.tr("Video Display Area"))
        self.current_label_display.setText(self.tr('Current Label: None'))
        logging.info("UI retranslated.")

    def load_signs(self):
        """
        Load the list of signs from the sign_list.txt file specified in the config.
        Populate the word_combo with the loaded signs based on the selected batch.
        """
        sign_list_path = self.config['sign_list']  # Path to sign_list.txt
        try:
            with open(sign_list_path, 'r') as f:
                self.signs = [line.strip() for line in f.readlines()]  # Read and strip each line
            # Note: The word_combo is now populated based on selected batch
            logging.info(f"Loaded {len(self.signs)} signs from {sign_list_path}.")
        except Exception as e:
            logging.error(f"Failed to load sign list from {sign_list_path}: {e}")
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Failed to load sign list: {e}")
            )

    def load_batches(self):
        """
        Load available review batches from the review_source directory.
        Populate the batch_combo with the found batches.
        """
        review_source = self.config['review_source']  # Path to the review_source directory
        try:
            # List all directories within review_source
            self.batches = [
                d for d in os.listdir(review_source) 
                if os.path.isdir(os.path.join(review_source, d))
            ]
            self.batch_combo.addItems(self.batches)  # Populate the batch selection combo box
            logging.info(f"Loaded {len(self.batches)} batches from {review_source}.")
        except Exception as e:
            logging.error(f"Failed to load batches from {review_source}: {e}")
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Failed to load batches: {e}")
            )

    def batch_selected(self):
        """
        Handle the event when a new batch is selected.
        Loads the corresponding words for the selected batch.
        Enables the word_combo.
        """
        batch = self.batch_combo.currentText()  # Get the selected batch
        word_dir = os.path.join(self.config['review_source'], batch)  # Path to the selected batch directory
        try:
            # List all directories (words) within the selected batch
            words = [
                d for d in os.listdir(word_dir) 
                if os.path.isdir(os.path.join(word_dir, d))
            ]
            self.word_combo.clear()  # Clear existing word selections
            self.word_combo.addItems(words)  # Populate with new words
            self.word_combo.setEnabled(True)  # Enable word_combo now that a batch is selected
            logging.info(f"Batch selected: {batch}. Loaded {len(words)} words.")
        except Exception as e:
            logging.error(f"Failed to load words for batch {batch}: {e}")
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Failed to load words for batch {batch}: {e}")
            )
            self.word_combo.setEnabled(False)  # Disable word_combo if loading fails

    def word_selected(self):
        """
        Handle the event when a new word is selected.
        Resets the video index and loads the videos for the selected word.
        """
        self.current_video_index = 0  # Reset to the first video
        self.load_videos()  # Load videos for the selected word
        logging.info(f"Word selected: {self.word_combo.currentText()}. Reset video index.")

    def load_videos(self):
        """
        Load all videos for the currently selected batch and word.
        """
        batch = self.batch_combo.currentText()  # Get selected batch
        word = self.word_combo.currentText()  # Get selected word
        video_dir = os.path.join(self.config['review_source'], batch, word)  # Path to videos
        try:
            # List all video files with supported extensions and sort them
            self.videos = sorted([
                f for f in os.listdir(video_dir) 
                if f.endswith(('.mp4', '.avi', '.mov'))
            ])
            self.video_dir = video_dir  # Store the current video directory
            if not self.videos:
                logging.warning(f"No videos found in {video_dir}.")
                QMessageBox.information(
                    self, 
                    self.tr("Info"), 
                    self.tr("No videos found for the selected word.")
                )
                self.next_button.setEnabled(False)
                self.play_pause_button.setEnabled(False)
                return
            logging.info(f"Loaded {len(self.videos)} videos from {video_dir}.")
            self.display_video()  # Display the first video
        except Exception as e:
            logging.error(f"Failed to load videos from {video_dir}: {e}")
            QMessageBox.critical(
                self, 
                self.tr("Error"), 
                self.tr(f"Failed to load videos: {e}")
            )

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
            # Retrieve existing annotation if any
            video_name = self.videos[self.current_video_index]
            category = self.in_progress_annotations.get(video_name, self.annotations.get(video_name))
            if category:
                self.current_label_display.setText(self.tr(f'Current Label: {category}'))
                self.next_button.setEnabled(True)
            else:
                self.current_label_display.setText(self.tr('Current Label: None'))
                self.next_button.setEnabled(False)
            logging.info(f"Displaying video: {video_path}. Current label: {category}")
        else:
            # Inform the user if there are no more videos to annotate
            QMessageBox.information(
                self, 
                self.tr("Info"), 
                self.tr("No more videos in this batch.")
            )
            self.next_button.setEnabled(False)  # Disable Next button
            self.play_pause_button.setEnabled(False)  # Disable Play/Pause button
            logging.info("No more videos to display.")

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

            try:
                self.player.play()  # Start playing the video
                self.play_pause_button.setText(self.tr('Pause'))  # Update button to 'Pause'
                self.next_button.setEnabled(False)  # Disable Next until annotated
                self.play_pause_button.setEnabled(True)  # Ensure Play/Pause is enabled
                logging.info(f"Playing video: {path}")
            except Exception as e:
                logging.error(f"Failed to play video {path}: {e}")
                QMessageBox.critical(
                    self, 
                    self.tr("Error"), 
                    self.tr(f"Failed to play video: {e}")
                )
        else:
            # Warn the user if the video file is not found
            QMessageBox.warning(
                self, 
                self.tr("Warning"), 
                self.tr(f"Video not found: {path}")
            )
            logging.warning(f"Video not found: {path}")

    def toggle_play_pause(self):
        """
        Toggle between playing and pausing the video.
        Updates the button label accordingly.
        """
        state = self.player.get_state()
        if state == vlc.State.Playing:
            self.player.pause()
            self.play_pause_button.setText(self.tr('Play'))
            logging.info("Video paused.")
        else:
            self.player.play()
            self.play_pause_button.setText(self.tr('Pause'))
            logging.info("Video played.")

    def replay_video(self):
        """
        Replay the current video from the beginning.
        """
        self.player.stop()  # Stop the video
        self.player.play()  # Play again
        self.play_pause_button.setText(self.tr('Pause'))  # Ensure button shows 'Pause'
        self.next_button.setEnabled(False)  # Disable Next until annotated
        self.current_label_display.setText(self.tr('Current Label: None'))  # Reset label display
        logging.info("Video replayed.")

    def speed_up(self):
        """
        Increase the playback speed of the current video.
        """
        current_rate = self.player.get_rate()  # Get current playback rate
        new_rate = current_rate + 0.1
        self.player.set_rate(new_rate)  # Increase by 0.1x
        logging.info(f"Playback speed increased to {new_rate}x.")

    def slow_down(self):
        """
        Decrease the playback speed of the current video.
        Ensures the rate does not go below 0.1x.
        """
        current_rate = self.player.get_rate()  # Get current playback rate
        new_rate = max(0.1, current_rate - 0.1)  # Decrease by 0.1x, minimum 0.1x
        self.player.set_rate(new_rate)
        logging.info(f"Playback speed decreased to {new_rate}x.")

    def next_video(self):
        """
        Move to the next video in the list after saving the current annotation.
        """
        self.save_annotations_final()  # Save current annotation to final CSV
        self.current_video_index += 1  # Increment video index
        self.display_video()  # Display the next video
        logging.info("Moved to next video.")

    def prev_video(self):
        """
        Move to the previous video in the list after saving the current annotation.
        """
        self.save_annotations_final()  # Save current annotation to final CSV
        self.current_video_index = max(0, self.current_video_index - 1)  # Decrement index but not below 0
        self.display_video()  # Display the previous video
        logging.info("Moved to previous video.")

    def annotate(self, category):
        """
        Annotate the current video with the specified category.

        Args:
            category (str): The annotation category (e.g., 'Good', 'Variant').
        """
        if not hasattr(self, 'videos') or not self.videos:
            QMessageBox.warning(
                self, 
                self.tr("Warning"), 
                self.tr("No video loaded to annotate.")
            )
            logging.warning("Attempted to annotate without a loaded video.")
            return

        video_name = self.videos[self.current_video_index]  # Get the current video filename
        word = self.word_combo.currentText()  # Get the current word being annotated
        self.annotations[video_name] = category  # Store the annotation
        self.in_progress_annotations[video_name] = category  # Also store in in-progress

        self.current_label_display.setText(self.tr(f'Current Label: {category}'))  # Update label display
        self.next_button.setEnabled(True)  # Enable Next button after labeling

        self.save_annotations_in_progress()  # Save the annotation to in-progress CSV
        self.save_state()  # Save the current state for resuming later
        logging.info(f"Annotated video {video_name} as {category}.")

    def save_annotations_in_progress(self):
        """
        Save all current in-progress annotations to the in-progress CSV file.
        """
        if hasattr(self, 'video_dir'):
            word = self.word_combo.currentText()  # Current word
            in_progress_file = os.path.join(self.config['output'], word, self.in_progress_file)
            os.makedirs(os.path.dirname(in_progress_file), exist_ok=True)  # Create directory if it doesn't exist

            # Convert in-progress annotations dictionary to a DataFrame
            df = pd.DataFrame(
                list(self.in_progress_annotations.items()), 
                columns=['filename', 'category']
            )
            df['sign'] = word  # Add the sign column
            df = df[['sign', 'filename', 'category']]  # Reorder columns

            # Save to in-progress CSV
            df.to_csv(
                in_progress_file, 
                index=False
            )
            logging.info(f"Saved in-progress annotations to {in_progress_file}.")

    def save_annotations_final(self):
        """
        Save all current annotations to the final output CSV file.
        """
        if hasattr(self, 'video_dir'):
            word = self.word_combo.currentText()  # Current word
            output_dir = os.path.join(self.config['output'], word)  # Output directory for the word
            os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

            annotations_file = os.path.join(output_dir, 'annotations.csv')  # Path to annotations.csv

            # Check if 'self.annotations' exists
            if not hasattr(self, 'annotations'):
                logging.error("self.annotations not defined.")
                QMessageBox.critical(
                    self, 
                    self.tr("Error"), 
                    self.tr("Annotations not initialized.")
                )
                return

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
            logging.info(f"Saved final annotations to {annotations_file}.")

            # Clear in-progress annotations after saving
            self.in_progress_annotations = {}
            self.save_annotations_in_progress()  # Overwrite in-progress file with empty data

    def show_help(self):
        """
        Show a pop-up window with the reference video for the current word.
        The pop-up includes both help text and the reference video.
        """
        word = self.word_combo.currentText()  # Current word
        reference_path = os.path.join(
            self.config['reference_source'], 
            f"{word}.mp4"
        )  # Path to the reference video

        if os.path.exists(reference_path):
            help_window = HelpWindow(reference_path, self.config)  # Create a HelpWindow instance
            help_window.exec_()  # Execute the pop-up window
            logging.info(f"Opened HelpWindow for word: {word}.")
        else:
            # Warn the user if the reference video is not found
            QMessageBox.warning(
                self, 
                self.tr("Warning"), 
                self.tr(f"Reference video not found: {reference_path}")
            )
            logging.warning(f"Reference video not found: {reference_path}")

    def load_state(self):
        """
        Load the annotation progress from a state file (state.json).
        This allows resuming annotation from where it was left off.
        """
        state_file = 'state.json'  # Name of the state file
        if os.path.exists(state_file):
            try:
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

                # Load in-progress annotations
                in_progress_file = os.path.join(self.config['output'], state['word'], self.in_progress_file)
                if os.path.exists(in_progress_file):
                    df = pd.read_csv(in_progress_file)
                    for _, row in df.iterrows():
                        self.in_progress_annotations[row['filename']] = row['category']
                    logging.info(f"Loaded in-progress annotations from {in_progress_file}.")

                self.display_video()  # Display the video at the loaded index
                logging.info(f"Resumed state from {state_file}.")
            except Exception as e:
                logging.error(f"Failed to load state from {state_file}: {e}")
                QMessageBox.warning(
                    self, 
                    self.tr("Warning"), 
                    self.tr(f"Failed to load previous state: {e}")
                )
        else:
            logging.info("No previous state found. Starting fresh.")

    def save_state(self):
        """
        Save the current annotation progress to a state file (state.json).
        """
        state = {
            'batch': self.batch_combo.currentText(),  # Current batch
            'word': self.word_combo.currentText(),  # Current word
            'video_index': self.current_video_index  # Current video index
        }
        try:
            with open('state.json', 'w') as f:
                json.dump(state, f)  # Write the state data to the file
            logging.info("State saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save state: {e}")

    def keyPressEvent(self, event):
        """
        Handle key press events to map hotkeys to actions based on config.

        Args:
            event (QKeyEvent): The key event.
        """
        key = event.key()
        modifiers = event.modifiers()
        key_sequence = QKeySequence(modifiers | key).toString().lower()  # Get the key as a string

        # Map hotkeys to actions
        action_mappings = {
            self.hotkeys.get('pause_key', '').lower(): self.toggle_play_pause,
            self.hotkeys.get('replay_key', '').lower(): self.replay_video,
            self.hotkeys.get('speed_up_key', '').lower(): self.speed_up,
            self.hotkeys.get('slow_down_key', '').lower(): self.slow_down,
            self.hotkeys.get('next_key', '').lower(): self.next_video if self.next_button.isEnabled() else None,
            self.hotkeys.get('prev_key', '').lower(): self.prev_video,
            self.hotkeys.get('good_key', '').lower(): lambda: self.annotate('Good'),
            self.hotkeys.get('variant_key', '').lower(): lambda: self.annotate('Variant'),
            self.hotkeys.get('unrecognizable_key', '').lower(): lambda: self.annotate('Unrecognizable'),
            self.hotkeys.get('further_review_key', '').lower(): lambda: self.annotate('Further Review'),
        }

        action = action_mappings.get(key_sequence)
        if action:
            action()
            logging.info(f"Hotkey triggered action for key: {key_sequence}")
        else:
            super().keyPressEvent(event)  # Pass the event to the base class

    def closeEvent(self, event):
        """
        Handle the event when the application is closed.
        Ensures that annotations are saved before exiting.
        """
        self.save_annotations_in_progress()  # Save in-progress annotations
        self.save_state()  # Save current state
        self.player.stop()  # Stop the video player
        logging.info("Application closed by user.")
        super().closeEvent(event)

class HelpWindow(QDialog):
    """
    Pop-up window to display help information and the reference video for annotation.
    Inherits from PyQt5's QDialog.
    """

    def __init__(self, reference_video, config):
        """
        Initialize the HelpWindow with the reference video path.

        Args:
            reference_video (str): Path to the reference video file.
            config (dict): Configuration parameters.
        """
        super().__init__()
        self.config = config  # Store configuration
        self.setWindowTitle(self.tr("Help & Reference Video"))  # Set the window title
        self.setGeometry(150, 150, 1000, 800)  # Set a larger geometry for combined content

        layout = QVBoxLayout()
        self.setLayout(layout)

        # ----- Help Text -----
        help_text = QLabel(self.tr("Use the annotation buttons to categorize the videos.\n"
                                   "You can use hotkeys for faster annotation. "
                                   "Refer to the reference video below for guidance."))
        help_text.setAlignment(Qt.AlignLeft)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # ----- Reference Video Player -----
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setMinimumSize(640, 480)  # Set minimum size
        self.video_frame.setSizePolicy(
            self.video_frame.sizePolicy().Expanding, 
            self.video_frame.sizePolicy().Expanding
        )
        layout.addWidget(self.video_frame)

        # ----- Video Control Buttons -----
        controls_layout = QHBoxLayout()

        # Play / Replay Button
        self.play_replay_button = QPushButton(self.tr('Play'))
        self.play_replay_button.clicked.connect(self.play_or_replay_video)
        controls_layout.addWidget(self.play_replay_button)

        # Pause Button
        self.pause_button = QPushButton(self.tr('Pause'))
        self.pause_button.clicked.connect(self.pause_video)
        controls_layout.addWidget(self.pause_button)

        # Loop Checkbox
        #self.loop_checkbox = QCheckBox(self.tr('Loop'))
        #self.loop_checkbox.stateChanged.connect(self.toggle_loop)
        #controls_layout.addWidget(self.loop_checkbox)

        layout.addLayout(controls_layout)

        # Load and set media
        self.reference_video = reference_video
        media = self.instance.media_new(self.reference_video)
        self.player.set_media(media)

        if sys.platform.startswith('linux'):
            self.player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_frame.winId()))

        # Connect the end of media event to handle replay
        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_media_end)

        # Initialize loop state
        self.is_looping = False

        logging.info(f"HelpWindow initialized with reference video: {self.reference_video}")

    def play_or_replay_video(self):
        """
        Play the reference video or replay it if it has ended.
        """
        state = self.player.get_state()
        if state == vlc.State.Ended:
            self.player.stop()
            self.player.play()
            self.play_replay_button.setText(self.tr('Replay'))
            logging.info("Reference video replayed.")
        elif state in [vlc.State.Stopped, vlc.State.NothingSpecial]:
            self.player.play()
            self.play_replay_button.setText(self.tr('Replay'))
            logging.info("Reference video played.")
        elif state == vlc.State.Paused:
            self.player.play()
            self.play_replay_button.setText(self.tr('Replay'))
            logging.info("Reference video resumed from pause.")
        else:
            logging.info("Reference video is already playing.")

    def pause_video(self):
        """
        Pause the reference video playback.
        """
        state = self.player.get_state()
        if state == vlc.State.Playing:
            self.player.pause()
            self.play_replay_button.setText(self.tr('Play'))
            logging.info("Reference video paused.")

    def toggle_loop(self, state):
        """
        Toggle the looping of the reference video based on the checkbox state.

        Args:
            state (int): The state of the checkbox.
        """
        if state == Qt.Checked:
            self.is_looping = True
            logging.info("Reference video looping enabled.")
        else:
            self.is_looping = False
            logging.info("Reference video looping disabled.")

    def on_media_end(self, event):
        """
        Handle the event when the reference video reaches the end.
        If looping is enabled, restart the video. Otherwise, update the Play/Repply button.

        Args:
            event: The VLC event.
        """
        if self.is_looping:
            self.player.stop()
            self.player.play()
            logging.info("Reference video looped.")
        else:
            self.play_replay_button.setText(self.tr('Replay'))
            logging.info("Reference video ended.")

    def closeEvent(self, event):
        """
        Handle the event when the HelpWindow is closed.
        Ensures that the reference video stops playing.
        """
        try:
            self.player.stop()
            logging.info("HelpWindow closed and reference video stopped.")
        except Exception as e:
            logging.error(f"Error while closing HelpWindow: {e}")
        super().closeEvent(event)

if __name__ == '__main__':
    """
    Entry point of the application.
    Loads the configuration, initializes the application, and starts the event loop.
    """
    try:
        config = load_config('config.json')  # Load configuration from config.json
    except Exception as e:
        logging.critical(f"Failed to load configuration: {e}")
        sys.exit(f"Failed to load configuration: {e}")

    app = QApplication(sys.argv)  # Create the QApplication instance

    # Initialize the translator for the application before creating the main window
    translator = QTranslator()
    selected_lang = config.get('language', 'en')  # Get the language code from config
    translation_file = f"translations/{selected_lang}.qm"  # Path to the translation file

    # Attempt to load and install the translation
    if translator.load(translation_file):
        app.installTranslator(translator)  # Install the translator to the application
        logging.info(f"Translator loaded for language: {selected_lang}")
    else:
        # Show a warning if the translation file is not found
        QMessageBox.warning(
            None, 
            "Warning", 
            f"Translation file not found for language: {selected_lang}"
        )
        logging.warning(f"Translation file not found for language: {selected_lang}")

    ex = AnnotationApp(config)  # Create an instance of the main application
    ex.show()  # Display the application window
    logging.info("Application started.")
    sys.exit(app.exec_())  # Start the application's event loop
