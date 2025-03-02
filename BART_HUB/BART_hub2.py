"""
BART Hub 2.0 - Main hub application for BART experiments
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import utilities
from BART_utils import ModernButton

# Import experiment classes
from BART_experiment import StandardBART, PresetBART, AutoBART, BARTY


class BARTHub:
    """Main hub application for managing BART experiments"""

    def __init__(self, master):
        self.master = master
        self.master.title("BART Hub")
        self.master.geometry("1000x1000")
        self.master.minsize(800, 600)

        # Set application icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'bart_icon.ico')
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
        except:
            pass

        # Default settings
        self.default_settings = {
            'balloon_parameters': {
                'num_blocks': 3,
                'balloons_per_block': 10,
                'block_settings': [
                    {'max_pop': 128, 'balloon_color': 'blue'},
                    {'max_pop': 128, 'balloon_color': 'red'},
                    {'max_pop': 128, 'balloon_color': 'green'}
                ]
            },
            'standard': {
                'cents_per_pump': 5,
                'fullscreen': False,
                'show_container': True,
                'fun_mode': True
            },
            'preset': {
                'cents_per_pump': 5,
                'input_timeout': 10,
                'fullscreen': False,
                'show_container': True,
                'fun_mode': True
            },
            'auto': {
                'cents_per_pump': 5,
                'inflation_speed': 1.5,
                'fullscreen': False,
                'show_container': True,
                'fun_mode': True
            },
            'bart_y': {
                'points_per_pump': 100,
                'fullscreen': False,
                'show_container': True,
                'fun_mode': True,
                'prize_thresholds': {
                    'small': 5000,
                    'medium': 10000,
                    'large': 15000,
                    'bonus': 20000
                }
            },
            'subject': {
                'id': '',
                'age': '18',
                'sex': 'M',
                'session': '1'
            },
            'output_directory': os.path.join(os.path.expanduser('~'), 'BART_Data')
        }

        # Load settings
        self.settings = self.load_settings()

        # Setup styles
        self.setup_styles()

        # Create main interface
        self.create_main_interface()

    def setup_styles(self):
        """Set up custom styles for the application"""
        style = ttk.Style()

        # Configure frame styles
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')

        # Configure notebook styles
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Helvetica', 10))

        # Configure button styles
        style.configure('TButton', font=('Helvetica', 10))

        # Configure entry styles
        style.configure('TEntry', background='white')

        # Configure labelframe styles
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', background='#f0f0f0', font=('Helvetica', 10, 'bold'))

    def load_settings(self):
        """Load settings from file or use defaults"""
        settings_path = os.path.join(os.path.expanduser('~'), 'BART_Data', 'bart_settings.json')

        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)

                # Verify all required settings exist, use defaults for missing ones
                for category in self.default_settings:
                    if category not in settings:
                        settings[category] = self.default_settings[category]
                    else:
                        for key in self.default_settings[category]:
                            if key not in settings[category]:
                                settings[category][key] = self.default_settings[category][key]

                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")

        # Return defaults if loading fails
        return self.default_settings.copy()

    def save_settings(self):
        """Save settings to file"""
        settings_path = os.path.join(os.path.expanduser('~'), 'BART_Data', 'bart_settings.json')

        # Ensure directory exists
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)

        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            return False

    def create_main_interface(self):
        """Create the main application interface"""
        # Clear any existing widgets
        for widget in self.master.winfo_children():
            widget.destroy()

        # Main frame
        main_frame = ttk.Frame(self.master, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Application title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            title_frame,
            text="BART Hub",
            font=('Helvetica', 26, 'bold'),
            foreground='#4a86e8'
        )
        title_label.pack(side=tk.LEFT, padx=10)

        subtitle_label = ttk.Label(
            title_frame,
            text="Balloon Analogue Risk Task",
            font=('Helvetica', 20),
            foreground='#666666'
        )
        subtitle_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.create_experiments_tab()
        self.create_settings_tab()
        self.create_data_tab()

    def create_experiments_tab(self):
        """Create the Experiments tab with launch buttons"""
        experiments_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(experiments_frame, text="Experiments")

        # Title and description
        ttk.Label(
            experiments_frame,
            text="Launch BART Experiment",
            font=('Helvetica', 18, 'bold')
        ).pack(pady=(0, 5))

        ttk.Label(
            experiments_frame,
            text="Select an experiment type to launch",
            font=('Helvetica', 12)
        ).pack(pady=(0, 20))

        # Create grid for experiment options
        experiments_grid = ttk.Frame(experiments_frame)
        experiments_grid.pack(fill=tk.BOTH, expand=True, padx=20)

        # Configure grid columns and rows
        for i in range(2):
            experiments_grid.columnconfigure(i, weight=1, uniform='column')
        for i in range(2):
            experiments_grid.rowconfigure(i, weight=1, uniform='row')

        # Define experiments with descriptions
        experiments = [
            {
                "name": "Standard BART",
                "description": "Classic BART experiment where the participant pumps up balloons and decides when to collect.",
                "command": lambda: self.launch_experiment('standard')
            },
            {
                "name": "Preset Pumps BART",
                "description": "Participants decide how many pumps before seeing the balloon inflate.",
                "command": lambda: self.launch_experiment('preset')
            },
            {
                "name": "Auto-Inflate BART",
                "description": "Balloon inflates automatically. Participant stops inflation when ready.",
                "command": lambda: self.launch_experiment('auto')
            },
            {
                "name": "BART-Y",
                "description": "Child-friendly version with points and prizes instead of money.",
                "command": lambda: self.launch_experiment('bart_y')
            }
        ]

        # Create button cards for each experiment
        for i, experiment in enumerate(experiments):
            row, col = divmod(i, 2)
            self.create_experiment_card(experiments_grid, experiment, row, col)

    def create_experiment_card(self, parent, experiment, row, col):
        """Create a card-style button for experiment selection"""
        # Create frame for the card
        card = ttk.Frame(parent, borderwidth=2, relief="solid")
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        # Configure card layout
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=0)  # Title
        card.rowconfigure(1, weight=1)  # Description
        card.rowconfigure(2, weight=0)  # Button

        # Card title
        ttk.Label(
            card,
            text=experiment["name"],
            font=('Helvetica', 14, 'bold')
        ).grid(row=0, column=0, sticky="nw", padx=10, pady=(10, 5))

        # Card description
        desc_label = ttk.Label(
            card,
            text=experiment["description"],
            wraplength=300,
            justify=tk.LEFT
        )
        desc_label.grid(row=1, column=0, sticky="nw", padx=10, pady=5)

        # Launch button
        launch_button = ModernButton(
            card,
            text="Launch",
            command=experiment["command"],
            height=40,
            font=('Helvetica', 12, 'bold')
        )
        launch_button.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

    def create_settings_tab(self):
        """Create the Settings tab with configuration options"""
        settings_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(settings_frame, text="Settings")

        # Title
        ttk.Label(
            settings_frame,
            text="Experiment Settings",
            font=('Helvetica', 18, 'bold')
        ).pack(pady=(0, 20))

        # Create sub-notebook for different settings sections
        settings_notebook = ttk.Notebook(settings_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for each settings section - note new order with balloon parameters second
        self.create_subject_tab(settings_notebook)
        self.create_balloon_parameters_tab(settings_notebook)  # New tab
        self.create_standard_settings_tab(settings_notebook)
        self.create_preset_settings_tab(settings_notebook)
        self.create_auto_settings_tab(settings_notebook)
        self.create_barty_settings_tab(settings_notebook)

        # Save button below notebook
        save_button = ModernButton(
            settings_frame,
            text="Save All Settings",
            command=self.save_all_settings,
            height=40,
            font=('Helvetica', 12, 'bold'),
            bg_color="#4CAF50",  # Green
            hover_color="#388E3C"  # Darker green
        )
        save_button.pack(pady=20)

    def create_subject_tab(self, parent):
        """Create tab for subject information settings"""
        subject_frame = ttk.Frame(parent, padding=15)
        parent.add(subject_frame, text="Subject Information")

        # Create settings sections
        self.create_subject_info_section(subject_frame)
        self.create_output_directory_section(subject_frame)

    def create_subject_info_section(self, parent):
        """Create section for subject demographic information"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Subject Demographics", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Variables for subject info
        self.subject_vars = {}

        # Subject ID
        ttk.Label(frame, text="Subject ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.subject_vars['id'] = tk.StringVar(value=self.settings['subject'].get('id', ''))
        ttk.Entry(frame, textvariable=self.subject_vars['id']).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)

        # Age
        ttk.Label(frame, text="Age:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.subject_vars['age'] = tk.StringVar(value=self.settings['subject'].get('age', '18'))
        ttk.Entry(frame, textvariable=self.subject_vars['age']).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5)

        # Sex
        ttk.Label(frame, text="Sex:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.subject_vars['sex'] = tk.StringVar(value=self.settings['subject'].get('sex', 'M'))
        ttk.Combobox(frame, textvariable=self.subject_vars['sex'], values=['M', 'F'], state='readonly').grid(
            row=2, column=1, sticky="ew", padx=5, pady=5)

        # Session
        ttk.Label(frame, text="Session:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.subject_vars['session'] = tk.StringVar(value=self.settings['subject'].get('session', '1'))
        ttk.Entry(frame, textvariable=self.subject_vars['session']).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5)

    def create_output_directory_section(self, parent):
        """Create section for output directory selection"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Data Output", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Output directory
        output_frame = ttk.Frame(frame)
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 5))

        self.output_dir_var = tk.StringVar(value=self.settings.get('output_directory',
                                                                   os.path.join(os.path.expanduser('~'), 'BART_Data')))

        dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=40)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_button = ttk.Button(output_frame, text="Browse...", command=self.select_output_directory)
        browse_button.pack(side=tk.LEFT)

        # Current directory display
        ttk.Label(
            frame,
            text="Data will be saved in CSV format with timestamps.",
            font=('Helvetica', 9, 'italic'),
            foreground='#666666'
        ).pack(anchor="w", pady=(5, 0))

    def select_output_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir_var.get(),
            title="Select Output Directory"
        )

        if directory:  # If a directory was selected
            self.output_dir_var.set(directory)

    def create_balloon_parameters_tab(self, parent):
        """Create tab for balloon parameters that apply to all experiment types"""
        balloon_frame = ttk.Frame(parent, padding=15)
        parent.add(balloon_frame, text="Balloon Parameters")

        # Title and description
        ttk.Label(
            balloon_frame,
            text="Block Configuration",
            font=('Helvetica', 14, 'bold')
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            balloon_frame,
            text="Configure the blocks and balloon parameters for all experiment types.",
            font=('Helvetica', 10)
        ).pack(anchor="w", pady=(0, 15))

        # Create a frame for block counts
        count_frame = ttk.LabelFrame(balloon_frame, text="Block Structure", padding=10)
        count_frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        count_frame.columnconfigure(0, weight=1)
        count_frame.columnconfigure(1, weight=1)

        # Variables for block counts
        self.balloon_params = {}

        # Number of blocks
        ttk.Label(count_frame, text="Number of blocks:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.balloon_params['num_blocks'] = tk.StringVar(
            value=str(self.settings.get('balloon_parameters', {}).get('num_blocks', 3)))
        num_blocks_entry = ttk.Entry(count_frame, textvariable=self.balloon_params['num_blocks'])
        num_blocks_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Balloons per block
        ttk.Label(count_frame, text="Balloons per block:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.balloon_params['balloons_per_block'] = tk.StringVar(
            value=str(self.settings.get('balloon_parameters', {}).get('balloons_per_block', 10)))
        ttk.Entry(count_frame, textvariable=self.balloon_params['balloons_per_block']).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5)

        # Create a frame for the block-specific settings
        self.block_settings_frame = ttk.LabelFrame(balloon_frame, text="Block-Specific Settings", padding=10)
        self.block_settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Configure columns for the headers (updated to match our UI changes)
        self.block_settings_frame.columnconfigure(0, weight=1)  # Block label
        self.block_settings_frame.columnconfigure(1, weight=1)  # Max pop label
        self.block_settings_frame.columnconfigure(2, weight=1)  # Max pop entry
        self.block_settings_frame.columnconfigure(3, weight=1)  # Color label
        self.block_settings_frame.columnconfigure(4, weight=1)  # Color dropdown

        # Add headers
        ttk.Label(self.block_settings_frame, text="Block", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky="w", padx=5, pady=(0, 5))
        ttk.Label(self.block_settings_frame, text="Maximum Pop", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=1, columnspan=2, sticky="w", padx=5, pady=(0, 5))
        ttk.Label(self.block_settings_frame, text="Balloon Color", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=3, columnspan=2, sticky="w", padx=5, pady=(0, 5))

        # Separator after headers
        ttk.Separator(self.block_settings_frame, orient='horizontal').grid(
            row=1, column=0, columnspan=5, sticky="ew", pady=(0, 5))

        # Store references to block setting variables
        self.block_vars = []

        # Create UI for each block
        self.update_block_settings_ui()

        # Bind to update block UI when num_blocks changes
        num_blocks_entry.bind("<KeyRelease>", lambda e: self.schedule_block_ui_update())

        # Help text
        ttk.Label(
            balloon_frame,
            text="These settings determine the balloon behavior across all experiment types.",
            font=('Helvetica', 9, 'italic'),
            foreground='#666666'
        ).pack(anchor="w", pady=(0, 5))

        # Add explanatory text for the probability model
        ttk.Label(
            balloon_frame,
            text="Balloon explosion probability follows a 'drawing without replacement' model.",
            font=('Helvetica', 9),
            foreground='#666666'
        ).pack(anchor="w", pady=(0, 2))

        ttk.Label(
            balloon_frame,
            text="For a balloon with Maximum Pop of 128, the probability starts at 1/128 and increases with each pump.",
            font=('Helvetica', 9),
            foreground='#666666'
        ).pack(anchor="w", pady=(0, 5))

    # 4. Add helper functions for dynamic block UI
    def schedule_block_ui_update(self):
        """Schedule an update to the block settings UI (to avoid multiple rapid updates)"""
        # Cancel any existing scheduled update
        if hasattr(self, '_block_update_after_id'):
            self.master.after_cancel(self._block_update_after_id)

        # Schedule a new update
        self._block_update_after_id = self.master.after(500, self.update_block_settings_ui)

    def update_block_settings_ui(self):
        """Update the block settings UI based on the current number of blocks"""
        try:
            # Get the number of blocks
            num_blocks = int(self.balloon_params['num_blocks'].get())

            # Clear existing entries
            for widget in self.block_settings_frame.winfo_children():
                if widget.grid_info().get('row', 0) > 1:  # Skip headers and separator
                    widget.destroy()

            # Clear the block vars list
            self.block_vars = []

            # Get current block settings or default empty list
            block_settings = self.settings.get('balloon_parameters', {}).get('block_settings', [])

            # Create UI for each block
            for i in range(num_blocks):
                # Get settings for this block or use defaults
                block_setting = block_settings[i] if i < len(block_settings) else {
                    'max_pop': 128,
                    'balloon_color': ['blue', 'red', 'green'][i % 3]
                }

                # Block label
                ttk.Label(self.block_settings_frame, text=f"Block {i + 1}").grid(
                    row=i + 2, column=0, sticky="w", padx=5, pady=2)

                # Block variables
                block_var = {
                    'max_pop': tk.StringVar(value=str(block_setting.get('max_pop', 128))),
                    'balloon_color': tk.StringVar(value=block_setting.get('balloon_color', 'blue'))
                }
                self.block_vars.append(block_var)

                # Max pop entry
                ttk.Label(self.block_settings_frame, text="Max Pop:").grid(
                    row=i + 2, column=1, sticky="e", padx=5, pady=2)
                ttk.Entry(self.block_settings_frame, textvariable=block_var['max_pop'], width=10).grid(
                    row=i + 2, column=2, sticky="w", padx=5, pady=2)

                # Balloon color selector
                ttk.Label(self.block_settings_frame, text="Color:").grid(
                    row=i + 2, column=3, sticky="e", padx=5, pady=2)
                ttk.Combobox(
                    self.block_settings_frame,
                    textvariable=block_var['balloon_color'],
                    values=['blue', 'red', 'green', 'yellow', 'random'],
                    state='readonly',
                    width=10
                ).grid(row=i + 2, column=4, sticky="w", padx=5, pady=2)

        except ValueError:
            # If the number of blocks is not a valid integer, do nothing
            pass

    def create_standard_settings_tab(self, parent):
        """Create settings tab for Standard BART"""
        standard_frame = ttk.Frame(parent, padding=15)
        parent.add(standard_frame, text="Standard BART")

        # Title and description
        ttk.Label(
            standard_frame,
            text="Standard BART Settings",
            font=('Helvetica', 14, 'bold')
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            standard_frame,
            text="Configure settings for the classic BART experiment.",
            font=('Helvetica', 10)
        ).pack(anchor="w", pady=(0, 15))

        # Create sections
        self.create_standard_basic_section(standard_frame)
        self.create_standard_visual_section(standard_frame)

    def create_standard_basic_section(self, parent):
        """Create basic settings section for Standard BART"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Basic Parameters", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        std_settings = self.settings.get('standard', self.default_settings['standard'])

        # Variables for settings
        self.std_vars = {}

        # Cents per pump
        ttk.Label(frame, text="Cents per pump:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.std_vars['cents_per_pump'] = tk.StringVar(value=str(std_settings.get('cents_per_pump', 5)))
        ttk.Entry(frame, textvariable=self.std_vars['cents_per_pump']).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)

    def create_standard_visual_section(self, parent):
        """Create visual settings section for Standard BART"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Visual Settings", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        std_settings = self.settings.get('standard', self.default_settings['standard'])

        # Checkboxes
        self.std_vars['fullscreen'] = tk.BooleanVar(value=std_settings.get('fullscreen', False))
        ttk.Checkbutton(
            frame,
            text="Fullscreen Mode",
            variable=self.std_vars['fullscreen']
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.std_vars['fun_mode'] = tk.BooleanVar(value=std_settings.get('fun_mode', True))
        ttk.Checkbutton(
            frame,
            text="Fun Mode (animations & sounds)",
            variable=self.std_vars['fun_mode']
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.std_vars['show_container'] = tk.BooleanVar(value=std_settings.get('show_container', True))
        ttk.Checkbutton(
            frame,
            text="Show Balloon Container",
            variable=self.std_vars['show_container']
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

    def create_standard_block_section(self, parent):
        """Create block settings section for Standard BART"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Block Settings", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        std_settings = self.settings.get('standard', self.default_settings['standard'])
        blocks_data = std_settings.get('blocks', {})

        # Variables for settings
        if 'num_blocks' not in self.std_vars:
            # Number of blocks
            ttk.Label(frame, text="Number of blocks:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            self.std_vars['num_blocks'] = tk.StringVar(value=str(blocks_data.get('num_blocks', 3)))
            ttk.Entry(frame, textvariable=self.std_vars['num_blocks']).grid(
                row=0, column=1, sticky="ew", padx=5, pady=5)

            # Balloons per block
            ttk.Label(frame, text="Balloons per block:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            self.std_vars['balloons_per_block'] = tk.StringVar(value=str(blocks_data.get('balloons_per_block', 10)))
            ttk.Entry(frame, textvariable=self.std_vars['balloons_per_block']).grid(
                row=1, column=1, sticky="ew", padx=5, pady=5)

        # Explosion point settings
        ttk.Label(frame, text="Minimum explosion point:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.std_vars['min_explosion_point'] = tk.StringVar(value=str(std_settings.get('min_explosion_point', 1)))
        ttk.Entry(frame, textvariable=self.std_vars['min_explosion_point']).grid(
            row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Maximum explosion point:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.std_vars['max_explosion_point'] = tk.StringVar(value=str(std_settings.get('max_explosion_point', 128)))
        ttk.Entry(frame, textvariable=self.std_vars['max_explosion_point']).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5)

        # Description text
        ttk.Label(
            frame,
            text="The mean explosion point will be halfway between min and max explosion points.",
            font=('Helvetica', 9, 'italic'),
            foreground='#666666'
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 0))

    def create_preset_settings_tab(self, parent):
        """Create settings tab for Preset BART"""
        preset_frame = ttk.Frame(parent, padding=15)
        parent.add(preset_frame, text="Preset BART")

        # Title and description
        ttk.Label(
            preset_frame,
            text="Preset Pumps BART Settings",
            font=('Helvetica', 14, 'bold')
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            preset_frame,
            text="Configure settings for the Preset Pumps BART variant.",
            font=('Helvetica', 10)
        ).pack(anchor="w", pady=(0, 15))

        # Create sections
        self.create_preset_basic_section(preset_frame)
        self.create_preset_visual_section(preset_frame)

    def create_preset_basic_section(self, parent):
        """Create basic settings section for Preset BART"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Basic Parameters", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        preset_settings = self.settings.get('preset', self.default_settings['preset'])

        # Variables for settings
        self.preset_vars = {}

        # Cents per pump
        ttk.Label(frame, text="Cents per pump:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.preset_vars['cents_per_pump'] = tk.StringVar(value=str(preset_settings.get('cents_per_pump', 5)))
        ttk.Entry(frame, textvariable=self.preset_vars['cents_per_pump']).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)

        # Input timeout
        ttk.Label(frame, text="Input timeout (seconds):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.preset_vars['input_timeout'] = tk.StringVar(value=str(preset_settings.get('input_timeout', 10)))
        ttk.Entry(frame, textvariable=self.preset_vars['input_timeout']).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5)

    def create_preset_visual_section(self, parent):
        """Create visual settings section for Preset BART"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Visual Settings", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        preset_settings = self.settings.get('preset', self.default_settings['preset'])

        # Checkboxes
        self.preset_vars['fullscreen'] = tk.BooleanVar(value=preset_settings.get('fullscreen', False))
        ttk.Checkbutton(
            frame,
            text="Fullscreen Mode",
            variable=self.preset_vars['fullscreen']
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.preset_vars['fun_mode'] = tk.BooleanVar(value=preset_settings.get('fun_mode', True))
        ttk.Checkbutton(
            frame,
            text="Fun Mode (animations & sounds)",
            variable=self.preset_vars['fun_mode']
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.preset_vars['show_container'] = tk.BooleanVar(value=preset_settings.get('show_container', True))
        ttk.Checkbutton(
            frame,
            text="Show Balloon Container",
            variable=self.preset_vars['show_container']
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

    def create_auto_settings_tab(self, parent):
        """Create settings tab for Auto-Inflate BART"""
        auto_frame = ttk.Frame(parent, padding=15)
        parent.add(auto_frame, text="Auto-Inflate BART")

        # Title and description
        ttk.Label(
            auto_frame,
            text="Auto-Inflate BART Settings",
            font=('Helvetica', 14, 'bold')
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            auto_frame,
            text="Configure settings for the Auto-Inflate BART variant.",
            font=('Helvetica', 10)
        ).pack(anchor="w", pady=(0, 15))

        # Create sections
        self.create_auto_basic_section(auto_frame)
        self.create_auto_visual_section(auto_frame)

    def create_auto_basic_section(self, parent):
        """Create basic settings section for Auto-Inflate BART"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Basic Parameters", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        auto_settings = self.settings.get('auto', self.default_settings['auto'])

        # Variables for settings
        self.auto_vars = {}

        # Cents per pump
        ttk.Label(frame, text="Cents per pump:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.auto_vars['cents_per_pump'] = tk.StringVar(value=str(auto_settings.get('cents_per_pump', 5)))
        ttk.Entry(frame, textvariable=self.auto_vars['cents_per_pump']).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)

        # Inflation speed
        ttk.Label(frame, text="Inflation speed (seconds):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.auto_vars['inflation_speed'] = tk.StringVar(value=str(auto_settings.get('inflation_speed', 1.5)))
        ttk.Entry(frame, textvariable=self.auto_vars['inflation_speed']).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5)

    def create_auto_visual_section(self, parent):
        """Create visual settings section for Auto-Inflate BART"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Visual Settings", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        auto_settings = self.settings.get('auto', self.default_settings['auto'])

        # Checkboxes
        self.auto_vars['fullscreen'] = tk.BooleanVar(value=auto_settings.get('fullscreen', False))
        ttk.Checkbutton(
            frame,
            text="Fullscreen Mode",
            variable=self.auto_vars['fullscreen']
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.auto_vars['fun_mode'] = tk.BooleanVar(value=auto_settings.get('fun_mode', True))
        ttk.Checkbutton(
            frame,
            text="Fun Mode (animations & sounds)",
            variable=self.auto_vars['fun_mode']
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.auto_vars['show_container'] = tk.BooleanVar(value=auto_settings.get('show_container', True))
        ttk.Checkbutton(
            frame,
            text="Show Balloon Container",
            variable=self.auto_vars['show_container']
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

    def create_barty_settings_tab(self, parent):
        """Create settings tab for BART-Y"""
        barty_frame = ttk.Frame(parent, padding=15)
        parent.add(barty_frame, text="BART-Y")

        # Title and description
        ttk.Label(
            barty_frame,
            text="BART-Y Settings",
            font=('Helvetica', 14, 'bold')
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            barty_frame,
            text="Configure settings for the child-friendly BART-Y variant.",
            font=('Helvetica', 10)
        ).pack(anchor="w", pady=(0, 15))

        # Create sections
        self.create_barty_basic_section(barty_frame)
        self.create_barty_visual_section(barty_frame)
        self.create_barty_prizes_section(barty_frame)

    def create_barty_basic_section(self, parent):
        """Create basic settings section for BART-Y"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Basic Parameters", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        barty_settings = self.settings.get('bart_y', self.default_settings['bart_y'])

        # Variables for settings
        self.barty_vars = {}

        # Points per pump
        ttk.Label(frame, text="Points per pump:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.barty_vars['points_per_pump'] = tk.StringVar(value=str(barty_settings.get('points_per_pump', 100)))
        ttk.Entry(frame, textvariable=self.barty_vars['points_per_pump']).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)

    def create_barty_visual_section(self, parent):
        """Create visual settings section for BART-Y"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Visual Settings", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        barty_settings = self.settings.get('bart_y', self.default_settings['bart_y'])

        # Checkboxes
        self.barty_vars['fullscreen'] = tk.BooleanVar(value=barty_settings.get('fullscreen', False))
        ttk.Checkbutton(
            frame,
            text="Fullscreen Mode",
            variable=self.barty_vars['fullscreen']
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.barty_vars['fun_mode'] = tk.BooleanVar(value=barty_settings.get('fun_mode', True))
        ttk.Checkbutton(
            frame,
            text="Fun Mode (animations & sounds)",
            variable=self.barty_vars['fun_mode']
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.barty_vars['show_container'] = tk.BooleanVar(value=barty_settings.get('show_container', True))
        ttk.Checkbutton(
            frame,
            text="Show Balloon Container",
            variable=self.barty_vars['show_container']
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

    def create_barty_prizes_section(self, parent):
        """Create prize settings section for BART-Y"""
        # Create labeled frame
        frame = ttk.LabelFrame(parent, text="Prize Thresholds", padding=10)
        frame.pack(fill=tk.X, pady=(0, 15))

        # Configure grid
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Get settings
        barty_settings = self.settings.get('bart_y', self.default_settings['bart_y'])
        prize_thresholds = barty_settings.get('prize_thresholds', self.default_settings['bart_y']['prize_thresholds'])

        # Variables for prize thresholds
        self.barty_prize_vars = {}

        # Small prize
        ttk.Label(frame, text="Small Prize Threshold:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.barty_prize_vars['small'] = tk.StringVar(value=str(prize_thresholds.get('small', 5000)))
        ttk.Entry(frame, textvariable=self.barty_prize_vars['small']).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)

        # Medium prize
        ttk.Label(frame, text="Medium Prize Threshold:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.barty_prize_vars['medium'] = tk.StringVar(value=str(prize_thresholds.get('medium', 10000)))
        ttk.Entry(frame, textvariable=self.barty_prize_vars['medium']).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5)

        # Large prize
        ttk.Label(frame, text="Large Prize Threshold:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.barty_prize_vars['large'] = tk.StringVar(value=str(prize_thresholds.get('large', 15000)))
        ttk.Entry(frame, textvariable=self.barty_prize_vars['large']).grid(
            row=2, column=1, sticky="ew", padx=5, pady=5)

        # Bonus prize
        ttk.Label(frame, text="Bonus Prize Threshold:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.barty_prize_vars['bonus'] = tk.StringVar(value=str(prize_thresholds.get('bonus', 20000)))
        ttk.Entry(frame, textvariable=self.barty_prize_vars['bonus']).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5)

    def create_data_tab(self):
        """Create the Data tab for viewing experimental data"""
        data_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(data_frame, text="Data")

        # Title
        ttk.Label(
            data_frame,
            text="BART Data Viewer",
            font=('Helvetica', 18, 'bold')
        ).pack(pady=(0, 10))

        # Create control area
        control_frame = ttk.Frame(data_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # File selection
        ttk.Label(control_frame, text="Data File:").pack(side=tk.LEFT, padx=(0, 5))

        self.data_file_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.data_file_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                                 padx=(0, 5))

        ttk.Button(control_frame, text="Browse...", command=self.select_data_file).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(control_frame, text="Load Data", command=self.load_data_file).pack(side=tk.LEFT)

        # Create notebook for data views
        self.data_notebook = ttk.Notebook(data_frame)
        self.data_notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create tabs for data views
        self.create_data_table_tab()
        self.create_data_summary_tab()
        self.create_data_chart_tab()

    def create_data_table_tab(self):
        """Create tab for data table view with expanded columns"""
        table_frame = ttk.Frame(self.data_notebook, padding=10)
        self.data_notebook.add(table_frame, text="Raw Data")

        # Create a treeview for data display with expanded columns
        columns = [
            'balloon_num', 'block_num', 'num_pumps', 'exploded', 'money_earned',
            'max_pop', 'cents_per_pump', 'explosion_point',
            'balloon_color', 'subject_id', 'age', 'sex', 'session'
        ]

        self.data_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Set column headings
        for col in columns:
            # Convert column name to title case with spaces
            heading = col.replace('_', ' ').title()
            self.data_tree.heading(col, text=heading)

            # Set column width based on content
            if col in ['balloon_num', 'block_num', 'num_pumps', 'exploded', 'age', 'sex', 'session']:
                width = 80
            elif col in ['max_pop', 'cents_per_pump']:
                width = 100
            else:
                width = 120

            self.data_tree.column(col, width=width, minwidth=width)

        # Add scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Place tree and scrollbars
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_data_summary_tab(self):
        """Create tab for data summary statistics"""
        summary_frame = ttk.Frame(self.data_notebook, padding=10)
        self.data_notebook.add(summary_frame, text="Summary Stats")

        # Empty label for summary (will be filled when data is loaded)
        self.summary_text = tk.Text(summary_frame, wrap=tk.WORD, width=60, height=20, font=('Courier', 10))
        self.summary_text.pack(fill=tk.BOTH, expand=True)

    def create_data_chart_tab(self):
        """Create tab for data visualization with block analysis"""
        chart_frame = ttk.Frame(self.data_notebook, padding=10)
        self.data_notebook.add(chart_frame, text="Charts")

        # Controls for chart type
        controls_frame = ttk.Frame(chart_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(controls_frame, text="Chart Type:").pack(side=tk.LEFT, padx=(0, 5))

        self.chart_type_var = tk.StringVar(value="pumps_per_balloon")
        chart_type_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.chart_type_var,
            values=[
                'pumps_per_balloon',
                'pumps_by_block',
                'adjusted_pumps_by_block',
                'earnings_per_balloon',
                'earnings_by_block',
                'explosion_histogram',
                'average_pumps'
            ],
            state='readonly',
            width=25
        )
        chart_type_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Bind chart type change
        chart_type_combo.bind('<<ComboboxSelected>>', lambda e: self.update_chart())

        # Create frame for matplotlib figure
        self.chart_display_frame = ttk.Frame(chart_frame)
        self.chart_display_frame.pack(fill=tk.BOTH, expand=True)

        # Create empty chart
        self.create_empty_chart()

    def create_empty_chart(self):
        """Create an empty matplotlib chart"""
        # Clear existing widgets
        for widget in self.chart_display_frame.winfo_children():
            widget.destroy()

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title("No Data Loaded")
        ax.text(0.5, 0.5, "Please load a data file to view charts",
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12)

        # Create canvas for matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master=self.chart_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def select_data_file(self):
        """Open file dialog to select data file"""
        file_path = filedialog.askopenfilename(
            initialdir=self.settings.get('output_directory'),
            title="Select Data File",
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            self.data_file_var.set(file_path)

    def load_data_file(self):
        """Load and process the selected data file"""
        file_path = self.data_file_var.get()

        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid data file")
            return

        try:
            # Load data
            self.data_df = pd.read_csv(file_path)

            # Update data table
            self.update_data_table()

            # Update summary statistics
            self.update_summary_stats()

            # Update chart
            self.update_chart()

            messagebox.showinfo("Success", "Data loaded successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def update_data_table(self):
        """Update the data table with loaded data"""
        # Clear existing items
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

        # Add new data
        for _, row in self.data_df.iterrows():
            values = [row.get(col, '') for col in self.data_tree['columns']]
            self.data_tree.insert('', 'end', values=values)

    def update_summary_stats(self):
        """Update the summary statistics display with block-specific analysis"""
        if not hasattr(self, 'data_df'):
            return

        # Clear existing text
        self.summary_text.delete(1.0, tk.END)

        # Add title
        self.summary_text.insert(tk.END, "=== BART EXPERIMENT SUMMARY ===\n\n", "title")
        self.summary_text.tag_configure("title", font=("Helvetica", 12, "bold"), justify="center")

        # GENERAL STATISTICS SECTION
        self.summary_text.insert(tk.END, "GENERAL STATISTICS\n", "section")
        self.summary_text.tag_configure("section", font=("Helvetica", 11, "bold"), foreground="#000099")

        # Calculate overall statistics
        stats = [
            f"Total records: {len(self.data_df)}",
            f"Total balloons: {self.data_df['balloon_num'].max()}",
            f"Total blocks: {self.data_df['block_num'].max()}",
            f"Average pumps per balloon: {self.data_df['num_pumps'].mean():.2f}",
            f"Total explosions: {self.data_df['exploded'].sum()}",
            f"Explosion rate: {self.data_df['exploded'].mean():.2%}",
            f"Total earnings: ${self.data_df['money_earned'].sum() / 100:.2f}",
            f"Average earnings per balloon: ${self.data_df['money_earned'].mean() / 100:.2f}"
        ]

        # Add overall statistics
        for stat in stats:
            self.summary_text.insert(tk.END, stat + "\n")

        # Calculate and add average adjusted pumps
        # Adjusted pumps = average number of pumps on balloons that didn't explode
        non_exploded = self.data_df[self.data_df['exploded'] == 0]
        if len(non_exploded) > 0:
            avg_adjusted_pumps = non_exploded['num_pumps'].mean()
            self.summary_text.insert(tk.END, f"\nAverage Adjusted Pumps (non-exploded): {avg_adjusted_pumps:.2f}\n")

        # BLOCK ANALYSIS SECTION
        self.summary_text.insert(tk.END, "\n\nBLOCK ANALYSIS\n", "section")

        # Group by block_num
        block_groups = self.data_df.groupby('block_num')

        for block_num, block_data in block_groups:
            # Get the first row to extract block parameters
            block_info = block_data.iloc[0]

            # Block header
            self.summary_text.insert(tk.END, f"\nBlock {int(block_num)} Statistics:\n", "block_header")
            self.summary_text.tag_configure("block_header", font=("Helvetica", 10, "bold"), foreground="#006600")

            # Block parameters
            self.summary_text.insert(tk.END,
                                     f" Max Pop: {block_info['max_pop']}, Cents Per Pump: {block_info['cents_per_pump']}\n")
            self.summary_text.insert(tk.END, f"  Balloon Color: {block_info['balloon_color']}\n\n")

            # Block statistics
            total_balloons = len(block_data)
            avg_pumps = block_data['num_pumps'].mean()
            explosion_count = block_data['exploded'].sum()
            explosion_rate = explosion_count / total_balloons if total_balloons > 0 else 0
            total_earnings = block_data['money_earned'].sum()
            avg_earnings = total_earnings / total_balloons if total_balloons > 0 else 0

            # Adjusted pumps (non-exploded balloons only)
            non_exploded_block = block_data[block_data['exploded'] == 0]
            avg_adjusted_pumps_block = non_exploded_block['num_pumps'].mean() if len(non_exploded_block) > 0 else 0

            # Add block statistics
            self.summary_text.insert(tk.END, f"  Total Balloons: {total_balloons}\n")
            self.summary_text.insert(tk.END, f"  Average Pumps: {avg_pumps:.2f}\n")
            self.summary_text.insert(tk.END, f"  Explosions: {explosion_count} ({explosion_rate:.2%})\n")
            self.summary_text.insert(tk.END, f"  Average Adjusted Pumps: {avg_adjusted_pumps_block:.2f}\n")
            self.summary_text.insert(tk.END, f"  Total Earnings: ${total_earnings / 100:.2f}\n")
            self.summary_text.insert(tk.END, f"  Average Earnings: ${avg_earnings / 100:.2f}\n")

        # SUBJECT ANALYSIS SECTION (if applicable)
        if 'subject_id' in self.data_df.columns and len(self.data_df['subject_id'].unique()) > 1:
            self.summary_text.insert(tk.END, "\n\nSUBJECT ANALYSIS\n", "section")

            # Group by subject
            subject_stats = self.data_df.groupby('subject_id').agg({
                'num_pumps': 'mean',
                'exploded': 'mean',
                'money_earned': 'sum'
            })

            # Format for display
            for subject, row in subject_stats.iterrows():
                self.summary_text.insert(tk.END, f"\nSubject: {subject}\n", "subject_header")
                self.summary_text.tag_configure("subject_header", font=("Helvetica", 10, "bold"), foreground="#990000")
                self.summary_text.insert(tk.END, f"  Avg pumps: {row['num_pumps']:.2f}\n")
                self.summary_text.insert(tk.END, f"  Explosion rate: {row['exploded']:.2%}\n")
                self.summary_text.insert(tk.END, f"  Total earnings: ${row['money_earned'] / 100:.2f}\n")

                # Calculate adjusted pumps for each subject
                subject_data = self.data_df[self.data_df['subject_id'] == subject]
                non_exploded_subject = subject_data[subject_data['exploded'] == 0]
                if len(non_exploded_subject) > 0:
                    subject_adj_pumps = non_exploded_subject['num_pumps'].mean()
                    self.summary_text.insert(tk.END, f"  Avg adjusted pumps: {subject_adj_pumps:.2f}\n")

    def update_chart(self):
        """Update the chart based on loaded data and chart type with block-specific analysis"""
        if not hasattr(self, 'data_df'):
            return

        # Clear chart frame
        for widget in self.chart_display_frame.winfo_children():
            widget.destroy()

        # Create appropriate chart based on selection
        chart_type = self.chart_type_var.get()

        fig, ax = plt.subplots(figsize=(8, 6))

        if chart_type == 'pumps_per_balloon':
            # Filter out rows with balloon_num = -1 (summary rows) if any
            valid_data = self.data_df[self.data_df['balloon_num'] > 0]

            # Plot pumps per balloon colored by block
            blocks = valid_data['block_num'].unique()
            for block in blocks:
                block_data = valid_data[valid_data['block_num'] == block]
                ax.plot(block_data['balloon_num'], block_data['num_pumps'], 'o-',
                        label=f'Block {int(block)}')

            ax.set_xlabel('Balloon Number')
            ax.set_ylabel('Number of Pumps')
            ax.set_title('Pumps Per Balloon (By Block)')
            ax.legend()

            # Set integer ticks for balloons
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

        elif chart_type == 'pumps_by_block':
            # Group by block and calculate average pumps
            block_pumps = self.data_df.groupby('block_num')['num_pumps'].mean().reset_index()

            # Plot average pumps by block as bar chart
            ax.bar(block_pumps['block_num'], block_pumps['num_pumps'], color='blue')

            # Add data labels on top of bars
            for i, v in enumerate(block_pumps['num_pumps']):
                ax.text(block_pumps['block_num'][i], v + 0.5, f'{v:.1f}',
                        ha='center', va='bottom', fontsize=10)

            ax.set_xlabel('Block Number')
            ax.set_ylabel('Average Pumps')
            ax.set_title('Average Pumps by Block')
            ax.set_xticks(block_pumps['block_num'])
            ax.set_xticklabels([f'Block {int(b)}' for b in block_pumps['block_num']])

        elif chart_type == 'adjusted_pumps_by_block':
            # Get non-exploded balloons only
            non_exploded = self.data_df[self.data_df['exploded'] == 0]

            # Group by block and calculate average adjusted pumps
            if len(non_exploded) > 0:
                block_adj_pumps = non_exploded.groupby('block_num')['num_pumps'].mean().reset_index()

                # Plot average adjusted pumps by block as bar chart
                ax.bar(block_adj_pumps['block_num'], block_adj_pumps['num_pumps'], color='green')

                # Add data labels on top of bars
                for i, v in enumerate(block_adj_pumps['num_pumps']):
                    ax.text(block_adj_pumps['block_num'][i], v + 0.5, f'{v:.1f}',
                            ha='center', va='bottom', fontsize=10)

                ax.set_xlabel('Block Number')
                ax.set_ylabel('Average Adjusted Pumps')
                ax.set_title('Average Adjusted Pumps by Block (Non-Exploded Balloons)')
                ax.set_xticks(block_adj_pumps['block_num'])
                ax.set_xticklabels([f'Block {int(b)}' for b in block_adj_pumps['block_num']])
            else:
                ax.text(0.5, 0.5, "No non-exploded balloons data available",
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12)

        elif chart_type == 'earnings_per_balloon':
            # Filter out rows with balloon_num = -1 (summary rows)
            valid_data = self.data_df[self.data_df['balloon_num'] > 0]

            # Convert cents to dollars for display
            valid_data['dollars_earned'] = valid_data['money_earned'] / 100

            # Plot earnings per balloon colored by block
            blocks = valid_data['block_num'].unique()
            bar_width = 0.8 / len(blocks)

            for i, block in enumerate(blocks):
                block_data = valid_data[valid_data['block_num'] == block]
                offset = (i - len(blocks) / 2 + 0.5) * bar_width
                ax.bar(block_data['balloon_num'] + offset, block_data['dollars_earned'],
                       width=bar_width, label=f'Block {int(block)}')

            ax.set_xlabel('Balloon Number')
            ax.set_ylabel('Earnings ($)')
            ax.set_title('Earnings Per Balloon (By Block)')
            ax.legend()

            # Set integer ticks for balloons
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

        elif chart_type == 'earnings_by_block':
            # Group by block and calculate total earnings
            block_earnings = self.data_df.groupby('block_num')['money_earned'].sum().reset_index()
            block_earnings['dollars_earned'] = block_earnings['money_earned'] / 100

            # Plot total earnings by block as bar chart
            ax.bar(block_earnings['block_num'], block_earnings['dollars_earned'], color='green')

            # Add data labels on top of bars
            for i, v in enumerate(block_earnings['dollars_earned']):
                ax.text(block_earnings['block_num'][i], v + 0.2, f'${v:.2f}',
                        ha='center', va='bottom', fontsize=10)

            ax.set_xlabel('Block Number')
            ax.set_ylabel('Total Earnings ($)')
            ax.set_title('Total Earnings by Block')
            ax.set_xticks(block_earnings['block_num'])
            ax.set_xticklabels([f'Block {int(b)}' for b in block_earnings['block_num']])

        elif chart_type == 'explosion_histogram':
            # Filter only explosions
            explosions = self.data_df[self.data_df['exploded'] == 1]

            if len(explosions) > 0:
                # Create histogram of explosions by pump count for each block
                blocks = explosions['block_num'].unique()

                if len(blocks) > 1:
                    # If multiple blocks, create histograms side by side
                    for block in blocks:
                        block_explosions = explosions[explosions['block_num'] == block]
                        label = f'Block {int(block)}'
                        ax.hist(block_explosions['num_pumps'], bins=8, alpha=0.6, label=label)
                    ax.legend()
                else:
                    # If only one block, use a single histogram
                    ax.hist(explosions['num_pumps'], bins=10, color='red', alpha=0.7)

                ax.set_xlabel('Number of Pumps')
                ax.set_ylabel('Frequency')
                ax.set_title('Explosion Distribution (By Block)')
            else:
                ax.text(0.5, 0.5, "No explosion data available",
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12)

        elif chart_type == 'average_pumps':
            # Group by subject if available
            if 'subject_id' in self.data_df.columns and len(self.data_df['subject_id'].unique()) > 1:
                # Group by subject and block
                grouped = self.data_df.groupby(['subject_id', 'block_num'])['num_pumps'].mean().reset_index()

                # Pivot to get subjects as rows and blocks as columns
                pivot_df = grouped.pivot(index='subject_id', columns='block_num', values='num_pumps')

                # Plot as a grouped bar chart
                pivot_df.plot(kind='bar', ax=ax)

                ax.set_xlabel('Subject')
                ax.set_ylabel('Average Pumps')
                ax.set_title('Average Pumps by Subject and Block')
                ax.legend(title='Block', labels=[f'Block {int(b)}' for b in pivot_df.columns])
            else:
                # Just show average pumps by block
                block_pumps = self.data_df.groupby('block_num')['num_pumps'].mean()
                block_pumps.plot(kind='bar', ax=ax, color='purple')

                # Add data labels on top of bars
                for i, v in enumerate(block_pumps):
                    ax.text(i, v + 0.5, f'{v:.1f}', ha='center', va='bottom', fontsize=10)

                ax.set_xlabel('Block')
                ax.set_ylabel('Average Pumps')
                ax.set_title('Average Pumps Across Blocks')
                ax.set_xticklabels([f'Block {int(b)}' for b in block_pumps.index])

        # Create canvas for matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master=self.chart_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_all_settings(self):
        """Save all settings from UI to settings dictionary"""
        # Update subject settings
        for key, var in self.subject_vars.items():
            self.settings['subject'][key] = var.get()

        # Update output directory
        self.settings['output_directory'] = self.output_dir_var.get()

        # Update balloon parameters (new)
        self.update_balloon_parameters()

        # Update Standard BART settings
        self.update_standard_settings()

        # Update Preset BART settings
        self.update_preset_settings()

        # Update Auto BART settings
        self.update_auto_settings()

        # Update BART-Y settings
        self.update_barty_settings()

        # Save settings to file
        if self.save_settings():
            messagebox.showinfo("Success", "Settings saved successfully")

    def update_balloon_parameters(self):
        """Update balloon parameters from UI variables"""
        try:
            # Ensure balloon_parameters section exists
            if 'balloon_parameters' not in self.settings:
                self.settings['balloon_parameters'] = {}

            # Basic structure parameters
            self.settings['balloon_parameters']['num_blocks'] = int(self.balloon_params['num_blocks'].get())
            self.settings['balloon_parameters']['balloons_per_block'] = int(
                self.balloon_params['balloons_per_block'].get())

            # Block-specific settings
            block_settings = []
            for i, block_var in enumerate(self.block_vars):
                max_pop = int(block_var['max_pop'].get())

                # Validate max_pop is positive
                if max_pop <= 0:
                    messagebox.showerror("Error", f"Block {i + 1}: Maximum pop must be a positive integer")
                    return False

                # Add to block settings list
                block_settings.append({
                    'max_pop': max_pop,
                    'balloon_color': block_var['balloon_color'].get()
                })

            self.settings['balloon_parameters']['block_settings'] = block_settings
            return True

        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid value in Balloon Parameters: {e}")
            return False

    def update_standard_settings(self):
        """Update Standard BART settings from UI variables"""
        try:
            # Only basic settings remain
            self.settings['standard']['cents_per_pump'] = int(self.std_vars['cents_per_pump'].get())

            # Visual settings
            self.settings['standard']['fullscreen'] = self.std_vars['fullscreen'].get()
            self.settings['standard']['fun_mode'] = self.std_vars['fun_mode'].get()
            self.settings['standard']['show_container'] = self.std_vars['show_container'].get()

            return True
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid value in Standard BART settings: {e}")
            return False

    def update_preset_settings(self):
        """Update Preset BART settings from UI variables"""
        try:
            # Basic settings
            self.settings['preset']['cents_per_pump'] = int(self.preset_vars['cents_per_pump'].get())
            self.settings['preset']['input_timeout'] = int(self.preset_vars['input_timeout'].get())

            # Visual settings
            self.settings['preset']['fullscreen'] = self.preset_vars['fullscreen'].get()
            self.settings['preset']['fun_mode'] = self.preset_vars['fun_mode'].get()
            self.settings['preset']['show_container'] = self.preset_vars['show_container'].get()

            return True
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid value in Preset BART settings: {e}")
            return False

    def update_auto_settings(self):
        """Update Auto-Inflate BART settings from UI variables"""
        try:
            # Basic settings
            self.settings['auto']['cents_per_pump'] = int(self.auto_vars['cents_per_pump'].get())
            self.settings['auto']['inflation_speed'] = float(self.auto_vars['inflation_speed'].get())

            # Visual settings
            self.settings['auto']['fullscreen'] = self.auto_vars['fullscreen'].get()
            self.settings['auto']['fun_mode'] = self.auto_vars['fun_mode'].get()
            self.settings['auto']['show_container'] = self.auto_vars['show_container'].get()

            return True
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid value in Auto-Inflate BART settings: {e}")
            return False

    def update_barty_settings(self):
        """Update BART-Y settings from UI variables"""
        try:
            # Basic settings
            self.settings['bart_y']['points_per_pump'] = int(self.barty_vars['points_per_pump'].get())

            # Visual settings
            self.settings['bart_y']['fullscreen'] = self.barty_vars['fullscreen'].get()
            self.settings['bart_y']['fun_mode'] = self.barty_vars['fun_mode'].get()
            self.settings['bart_y']['show_container'] = self.barty_vars['show_container'].get()

            # Prize thresholds
            prize_thresholds = {}
            for key, var in self.barty_prize_vars.items():
                prize_thresholds[key] = int(var.get())

            self.settings['bart_y']['prize_thresholds'] = prize_thresholds

            return True
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid value in BART-Y settings: {e}")
            return False

    def launch_experiment(self, experiment_type):
        """Launch the selected experiment type"""
        # Save settings first
        self.save_all_settings()

        # Create experiment window
        experiment_window = tk.Toplevel(self.master)
        experiment_window.protocol("WM_DELETE_WINDOW", lambda: self.on_experiment_close(experiment_window))

        # Get appropriate settings
        experiment_settings = self.settings[experiment_type].copy()

        # Add balloon parameters to experiment settings
        experiment_settings['blocks'] = {
            'num_blocks': self.settings['balloon_parameters']['num_blocks'],
            'balloons_per_block': self.settings['balloon_parameters']['balloons_per_block']
        }
        experiment_settings['block_settings'] = self.settings['balloon_parameters']['block_settings']

        # Add subject info and output directory
        experiment_settings['subject'] = self.settings['subject']
        experiment_settings['output_directory'] = self.settings['output_directory']

        # Create experiment instance based on type
        if experiment_type == 'standard':
            experiment = StandardBART(experiment_window, experiment_settings)
        elif experiment_type == 'preset':
            experiment = PresetBART(experiment_window, experiment_settings)
        elif experiment_type == 'auto':
            experiment = AutoBART(experiment_window, experiment_settings)
        elif experiment_type == 'bart_y':
            experiment = BARTY(experiment_window, experiment_settings)

        # Override return_to_hub method to properly close the window and return to hub
        experiment.return_to_hub = lambda: self.on_experiment_close(experiment_window)

        # Minimize the main window
        self.master.iconify()

    def on_experiment_close(self, experiment_window):
        """Handle experiment window closing"""
        # Close experiment window
        experiment_window.destroy()

        # Restore the main window
        self.master.deiconify()

        # Refresh the data tab
        self.refresh_data_tab()

    def refresh_data_tab(self):
        """Refresh data tab to show new data files"""
        # Nothing to do yet - could auto-load newest file in the future
        pass

def main():
    """Main function to start the application"""
    root = tk.Tk()
    app = BARTHub(root)
    root.mainloop()

if __name__ == "__main__":
    main()