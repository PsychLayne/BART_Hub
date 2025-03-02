"""
BART Utils - Shared utilities and UI components for BART Hub 2.0
"""

import tkinter as tk
from tkinter import ttk
import os
import math
import csv
from datetime import datetime


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Create a rounded rectangle on a canvas"""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


class ModernButton(tk.Canvas):
    """Modern styled button with rounded corners"""

    def __init__(self, parent, text, command, **kwargs):
        super().__init__(
            parent,
            bd=0,
            highlightthickness=0,
            bg=kwargs.get('bg', '#f0f0f0'),  # Background of parent
            height=kwargs.get('height', 50),
            relief='ridge'
        )

        # Button properties
        self.bg_color = kwargs.get('bg_color', '#4a86e8')
        self.hover_color = kwargs.get('hover_color', '#2b5bac')
        self.text_color = kwargs.get('text_color', '#ffffff')
        self.font = kwargs.get('font', ('Helvetica', 12, 'bold'))
        self.command = command
        self.text = text
        self.disabled = False

        # Bind events
        self.bind('<Configure>', self._create_button)
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _create_button(self, event=None):
        """Create the rounded rectangle button"""
        self.delete('all')  # Clear canvas

        # Get current dimensions
        width = self.winfo_width()
        height = self.winfo_height()

        # Create rounded rectangle
        radius = height // 2  # Pill shape
        self.rect = create_rounded_rectangle(
            self, 2, 2, width - 2, height - 2, radius,
            fill=self.bg_color if not self.disabled else "#cccccc",
            outline=''
        )

        # Add text
        self.create_text(
            width // 2,
            height // 2,
            text=self.text,
            font=self.font,
            fill=self.text_color if not self.disabled else "#888888",
            anchor='center'
        )

    def _on_click(self, event):
        """Handle click event"""
        if not self.disabled and self.command:
            self.command()

    def _on_enter(self, event):
        """Handle mouse enter event"""
        if not self.disabled:
            self.itemconfig(self.rect, fill=self.hover_color)

    def _on_leave(self, event):
        """Handle mouse leave event"""
        if not self.disabled:
            self.itemconfig(self.rect, fill=self.bg_color)

    def state(self, state):
        """Handle ttk-like state changes"""
        if state == ['disabled']:
            self.disabled = True
            self.itemconfig(self.rect, fill="#cccccc")
        elif state == ['!disabled'] or state == ['normal']:
            self.disabled = False
            self.itemconfig(self.rect, fill=self.bg_color)
        self._create_button()


class SimpleDataLogger:
    """Utility class for logging BART experiment data"""

    def __init__(self, experiment_type, subject_info, output_directory=None):
        self.experiment_type = experiment_type
        self.subject_info = subject_info
        self.output_directory = output_directory or os.path.join(os.path.expanduser('~'), 'BART_Data')

        # Create the log file
        self.setup_log_file()

    def setup_log_file(self):
        """Create log file with appropriate headers"""
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create filename with experiment type
        filename = f"{self.experiment_type}_data_{timestamp}.csv"

        # Create directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)

        # Full path to file
        self.log_filename = os.path.join(self.output_directory, filename)

        # Updated headers to include block_num and explosion_point
        headers = [
            'balloon_num', 'block_num', 'num_pumps', 'exploded', 'money_earned',
            'reaction_time', 'balloon_color', 'explosion_point', 'max_pop', 'cents_per_pump',
            'age', 'sex', 'session', 'subject_id'
        ]

        # Create the log file with headers
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def log_trial(self, balloon_num, block_num, num_pumps, exploded, money_earned,
                 reaction_time=None, balloon_color='blue', explosion_point=None,
                 min_pop=None, max_pop=None, cents_per_pump=None):
        """Log a single trial to the CSV file with expanded block information"""
        with open(self.log_filename, 'a', newline='') as f:
            writer = csv.writer(f)

            # Compile all data
            row = [
                balloon_num,
                block_num,
                num_pumps,
                exploded,
                money_earned,
                reaction_time or '',  # Handle None values
                balloon_color,
                explosion_point or '',  # Handle None values
                max_pop or '',
                self.subject_info.get('age', ''),
                self.subject_info.get('sex', ''),
                self.subject_info.get('session', ''),
                self.subject_info.get('id', '')
            ]

            # Write row
            writer.writerow(row)