"""
BART Experiments - Implementation of BART experiment variants
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import math
import random
from datetime import datetime
import pygame

# Import utilities
from BART_utils import ModernButton, SimpleDataLogger, create_rounded_rectangle


class BARTExperiment:
    """Base class for all BART experiment variants"""

    def __init__(self, master, settings):
        self.master = master
        self.settings = settings

        # Configure window
        self.master.title(f"BART Experiment - {self.__class__.__name__}")
        if self.settings.get('fullscreen', False):
            self.master.attributes('-fullscreen', True)
        else:
            self.master.geometry("900x700")

        # Initialize pygame for sound if available
        self.init_sound()

        # Set up common parameters
        self.setup_common_parameters()

        # Set up experiment state
        self.setup_experiment_state()

        # Set up data logging
        self.logger = SimpleDataLogger(
            self.__class__.__name__,
            self.settings.get('subject', {}),
            self.settings.get('output_directory')
        )

        # Start with instructions
        self.show_instructions()

    def init_sound(self):
        """Initialize sound system"""
        try:
            pygame.mixer.init()
            self.sound_enabled = True
            self.sounds = {}
            # Load common sounds if fun mode is enabled
            if self.settings.get('fun_mode', True):
                self.sounds = {
                    'pump': self.load_sound('pump.wav'),
                    'pop': self.load_sound('pop.wav'),
                    'cashout': self.load_sound('cashout.wav')
                }
        except:
            self.sound_enabled = False

    def load_sound(self, filename):
        """Load a sound file"""
        try:
            filepath = os.path.join(os.path.dirname(__file__), 'assets', filename)
            if os.path.exists(filepath):
                return pygame.mixer.Sound(filepath)
            return None
        except:
            return None

    def play_sound(self, sound_name):
        """Play a sound with error handling"""
        if self.sound_enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def setup_common_parameters(self):
        """Set up parameters common to all BART variants"""
        # Common visual settings
        self.fullscreen = self.settings.get('fullscreen', False)
        self.fun_mode = self.settings.get('fun_mode', True)
        self.show_container = self.settings.get('show_container', True)

        # Get block structure settings
        self.blocks = self.settings.get('blocks', {
            'num_blocks': 3,
            'balloons_per_block': 10
        })

        # Get block-specific settings
        self.block_settings = self.settings.get('block_settings', [
            {'max_pop': 128, 'balloon_color': 'blue'},
            {'max_pop': 128, 'balloon_color': 'red'},
            {'max_pop': 128, 'balloon_color': 'green'}
        ])

        # Calculate total balloons from blocks
        self.max_balloons = self.blocks['num_blocks'] * self.blocks['balloons_per_block']

        # Other common parameters
        self.cents_per_pump = self.settings.get('cents_per_pump', 5)

        # Balloon colors dict
        self.balloon_colors = {
            'blue': {"base": "#000080", "gradient": ["#000080", "#0000A0", "#0000C0", "#0000FF", "#4040FF", "#6060FF"]},
            'red': {"base": "#800000", "gradient": ["#800000", "#A00000", "#C00000", "#FF0000", "#FF4040", "#FF6060"]},
            'green': {"base": "#008000",
                      "gradient": ["#008000", "#00A000", "#00C000", "#00FF00", "#40FF40", "#60FF60"]},
            'yellow': {"base": "#808000",
                       "gradient": ["#808000", "#A0A000", "#C0C000", "#FFFF00", "#FFFF40", "#FFFF60"]}
        }

    # Update setup_experiment_state to track current block
    def setup_experiment_state(self):
        """Initialize experiment state variables"""
        self.current_balloon = 1
        self.current_block = 1  # Start with block 1
        self.current_pumps = 0
        self.total_earned = 0
        self.temp_bank = 0
        self.last_balloon_earnings = 0
        self.is_exploded = False
        self.animation_complete = True

        # Get min/max explosion points for the current block
        self.update_current_block_settings()

        # Data collection arrays
        self.pumps_history = []

    def calculate_explosion_probability(self):
        """
        Calculate explosion probability using a drawing without replacement model.
        The probability on the nth pump is 1/(max_explosion_point - (n-1))
        For example, with max_explosion_point=128:
        - First pump: 1/128
        - Second pump: 1/127
        - Third pump: 1/126
        - ...and so on until pump 128 which has probability 1/1 (100%)
        """
        # If we've already reached max pumps, explosion is certain
        if self.current_pumps >= self.max_explosion_point:
            return 1.0

        # Calculate probability based on drawing without replacement
        # For pump n, probability is 1 / (max_explosion_point - (n-1))
        denominator = self.max_explosion_point - (self.current_pumps - 1)

        # Ensure denominator is at least 1 to avoid division by zero
        denominator = max(1, denominator)

        # Return the probability
        return 1 / denominator

    def update_current_block_settings(self):
        """Update settings based on the current block"""
        # Get index in block_settings (zero-based)
        block_index = self.current_block - 1

        # Get settings for this block (use first block as fallback if index is out of range)
        if block_index < len(self.block_settings):
            block_setting = self.block_settings[block_index]
        else:
            block_setting = self.block_settings[0]

        self.max_explosion_point = block_setting.get('max_pop', 128)

        # Set balloon color if specified and not random
        balloon_color = block_setting.get('balloon_color', 'blue')
        if balloon_color != 'random':
            self.current_balloon_color = balloon_color
        else:
            self.current_balloon_color = random.choice(list(self.balloon_colors.keys()))

    def show_instructions(self):
        """Show experiment instructions"""
        # Clear screen
        self.clear_screen()

        # Create instruction frame
        instruction_frame = ttk.Frame(self.master, padding=20)
        instruction_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            instruction_frame,
            text=f"{self.__class__.__name__} Instructions",
            font=('Helvetica', 16, 'bold')
        ).pack(pady=(0, 20))

        # Instructions - to be implemented by subclasses
        instruction_text = self.get_instruction_text()

        instruction_label = ttk.Label(
            instruction_frame,
            text=instruction_text,
            wraplength=600,
            justify=tk.LEFT
        )
        instruction_label.pack(pady=20, fill=tk.BOTH, expand=True)

        # Start button
        start_button = ModernButton(
            instruction_frame,
            text="Start Experiment",
            command=self.setup_gui,
            height=50,
            font=('Helvetica', 14, 'bold')
        )
        start_button.pack(pady=20)

    def get_instruction_text(self):
        """Get the instruction text - to be overridden by subclasses"""
        return "Default instructions. This should be overridden by subclasses."

    def clear_screen(self):
        """Clear all widgets from the screen"""
        for widget in self.master.winfo_children():
            widget.destroy()

    def setup_gui(self):
        """Set up the main experiment GUI - to be implemented by subclasses"""
        pass

    def draw_balloon(self, animation_factor=1.0):
        """Draw the balloon on the canvas with size limited by container"""
        if not hasattr(self, 'canvas'):
            return

        self.canvas.delete("all")  # Clear canvas

        if not self.is_exploded:
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Draw container if enabled
            container_width = 0
            container_height = 0

            if self.show_container:
                # Calculate container dimensions
                box_width = min(canvas_width * 0.85, canvas_height * 0.85)
                box_height = box_width

                # Store container dimensions for balloon sizing
                container_width = box_width
                container_height = box_height

                self.draw_container()

            # Calculate balloon position and size
            x = canvas_width / 2
            y = canvas_height / 2

            # Base size and maximum growth
            max_size = min(canvas_width, canvas_height) / 3

            # If container is shown, set max_size to fit within container
            if self.show_container:
                # Maximum balloon diameter should be slightly less than container width/height
                max_size = min(container_width, container_height) * 0.45

            base_size = max_size * 0.2

            # Fixed reference point of 128 pumps for full size
            fixed_max_pumps = 128

            # Calculate size based on pumps with fixed reference to 128 max pumps
            growth_per_pump = (max_size - base_size) / fixed_max_pumps
            size = base_size + (self.current_pumps * growth_per_pump)

            # Apply animation factor in fun mode
            if self.fun_mode:
                size *= animation_factor

            # Draw the balloon based on mode
            if self.fun_mode:
                self.draw_fancy_balloon(x, y, size)
            else:
                self.draw_simple_balloon(x, y, size)

    def draw_container(self):
        """Draw the balloon container on the canvas"""
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate container dimensions
        box_width = min(canvas_width * 0.85, canvas_height * 0.85)
        box_height = box_width
        box_left = (canvas_width - box_width) / 2
        box_top = (canvas_height - box_height) / 2

        if self.fun_mode:
            # Draw rounded rectangle container with grid lines
            corner_radius = 20

            # Create points for rounded rectangle
            points = [
                box_left + corner_radius, box_top,
                box_left + box_width - corner_radius, box_top,
                box_left + box_width, box_top,
                box_left + box_width, box_top + corner_radius,
                box_left + box_width, box_top + box_height - corner_radius,
                box_left + box_width, box_top + box_height,
                box_left + box_width - corner_radius, box_top + box_height,
                box_left + corner_radius, box_top + box_height,
                box_left, box_top + box_height,
                box_left, box_top + box_height - corner_radius,
                box_left, box_top + corner_radius,
                box_left, box_top
            ]

            self.canvas.create_polygon(
                points,
                smooth=True,
                fill="#F8F8F8",
                outline="#AAAAAA",
                width=2
            )

            # Add grid lines
            for i in range(1, 4):
                # Horizontal lines
                y = box_top + (box_height * i / 4)
                self.canvas.create_line(
                    box_left + 10, y,
                    box_left + box_width - 10, y,
                    fill="#DDDDDD", dash=(2, 4)
                )

                # Vertical lines
                x = box_left + (box_width * i / 4)
                self.canvas.create_line(
                    x, box_top + 10,
                    x, box_top + box_height - 10,
                    fill="#DDDDDD", dash=(2, 4)
                )
        else:
            # Simple rectangle in non-fun mode
            self.canvas.create_rectangle(
                box_left, box_top,
                box_left + box_width, box_top + box_height,
                outline="#888888",
                width=2,
                fill="#F8F8F8"
            )

    def draw_fancy_balloon(self, x, y, size):
        """Draw a fancy balloon with gradients and highlights"""
        # Get the color gradient for the current balloon color
        colors = self.balloon_colors[self.current_balloon_color]["gradient"]

        # Main balloon (largest)
        self.canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=colors[0], outline=colors[1], width=2
        )

        # Inner balloon layers for gradient effect
        for i in range(1, len(colors) - 1):
            smaller_size = size * (1 - (i * 0.15))
            self.canvas.create_oval(
                x - smaller_size, y - smaller_size,
                x + smaller_size, y + smaller_size,
                fill=colors[i], outline=""
            )

        # Highlight/reflection (small white oval near top-left)
        highlight_size = size * 0.2
        self.canvas.create_oval(
            x - size * 0.5, y - size * 0.5,
            x - size * 0.1, y - size * 0.1,
            fill="#FFFFFF", outline=""
        )

        # Draw enhanced string with knot
        string_length = size * 1.5
        string_width = max(2, size * 0.02)
        self.canvas.create_line(
            x, y + size,
            x, y + size + string_length,
            width=string_width, fill="#888888"
        )

        # Knot at the bottom of the balloon
        knot_size = size * 0.1
        self.canvas.create_oval(
            x - knot_size, y + size - knot_size,
            x + knot_size, y + size + knot_size,
            fill="#666666", outline="#444444"
        )

        # Balloon tie effect
        self.canvas.create_arc(
            x - knot_size * 1.5, y + size - knot_size,
            x + knot_size * 1.5, y + size + knot_size * 2,
            start=30, extent=120, style="arc", width=string_width,
            outline="#666666"
        )

    def draw_simple_balloon(self, x, y, size):
        """Draw a simple balloon without fancy effects"""
        # Use the base color for the current balloon color
        color = self.balloon_colors[self.current_balloon_color]["base"]

        # Simple balloon with single color
        self.canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=color, outline="black", width=1
        )

        # Simple string
        self.canvas.create_line(
            x, y + size,
            x, y + size + (size * 1.2),
            width=1, fill="black"
        )

    def handle_explosion(self):
        """Handle balloon explosion with animation"""
        # Set balloon state
        self.is_exploded = True
        self.temp_bank = 0

        # Play explosion sound
        self.play_sound('pop')

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Clear canvas
        self.canvas.delete("all")

        # Calculate balloon size for explosion
        max_size = min(canvas_width, canvas_height) / 3
        base_size = max_size * 0.2
        size = base_size + (self.current_pumps * (max_size * 0.05))

        # Show simple or fancy explosion based on mode
        if self.fun_mode:
            self.show_fancy_explosion(canvas_width / 2, canvas_height / 2, size)
        else:
            self.show_simple_explosion(canvas_width / 2, canvas_height / 2, size)

        # Log the trial with updated block information
        self.logger.log_trial(
            self.current_balloon,
            self.current_block,
            self.current_pumps,
            True,  # exploded
            0,  # money earned (0 for explosion)
            None,  # reaction time
            self.current_balloon_color,
            self.max_explosion_point,  # Max pop
            self.cents_per_pump  # $ per pump
        )

        # Move to next balloon after delay
        self.master.after(2000, self.next_balloon)

    def show_simple_explosion(self, x, y, size):
        """Show a simple explosion animation"""
        # Create "POP!" text
        self.canvas.create_text(
            x, y,
            text="POP!",
            font=("Arial", int(size / 2), "bold"),
            fill="#FF0000",
            anchor="center"
        )

    def show_fancy_explosion(self, x, y, size):
        """Show a fancy explosion with particles"""
        # Number of particles
        num_particles = 20
        explosion_colors = ["#FF0000", "#FF4500", "#FF6347", "#FF8C00", "#FFA500"]

        # Create particles
        for _ in range(num_particles):
            # Random angle and distance
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, size * 1.5)

            # Calculate position
            px = x + math.cos(angle) * distance
            py = y + math.sin(angle) * distance

            # Random size and color
            p_size = random.uniform(size * 0.05, size * 0.2)
            color = random.choice(explosion_colors)

            # Create particle
            self.canvas.create_oval(
                px - p_size, py - p_size,
                px + p_size, py + p_size,
                fill=color, outline=""
            )

        # Create "POP!" text
        self.canvas.create_text(
            x, y,
            text="POP!",
            font=("Arial Black", int(max(24, size * 0.4))),
            fill="#FF0000",
            anchor="center"
        )

    def collect(self):
        """Handle collection of money"""
        if self.is_exploded:
            return

        # Calculate earnings
        earned_amount = self.current_pumps * self.cents_per_pump
        self.total_earned += earned_amount
        self.last_balloon_earnings = earned_amount

        # Add to history
        self.pumps_history.append(self.current_pumps)

        # Log the trial with updated block information
        self.logger.log_trial(
            self.current_balloon,
            self.current_block,  # Block number
            self.current_pumps,
            False,  # not exploded
            earned_amount,
            None,  # reaction time
            self.current_balloon_color,
            self.max_explosion_point,  # Max pop
            self.cents_per_pump  # $ per pump
        )

        # Play collection sound
        self.play_sound('cashout')

        # Show collection feedback
        self.show_collection_feedback(earned_amount)

        # Move to next balloon after delay
        self.master.after(2000, self.next_balloon)

    def show_collection_feedback(self, amount):
        """Show feedback when money is collected"""
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Clear canvas
        self.canvas.delete("all")

        # Show amount collected
        self.canvas.create_text(
            canvas_width / 2, canvas_height / 2,
            text=f"+${amount / 100:.2f}",
            font=("Arial", 24, "bold"),
            fill="#008800",
            anchor="center"
        )

    def next_balloon(self):
        """Prepare for the next balloon"""
        # Check if we've reached maximum balloons
        if self.current_balloon >= self.max_balloons:
            self.end_experiment()
            return

        # Increment balloon counter
        self.current_balloon += 1

        # Check if we need to move to the next block
        if (self.current_balloon - 1) % self.blocks['balloons_per_block'] == 0:
            self.current_block += 1
            # Update settings for the new block
            self.update_current_block_settings()

        # Reset balloon state
        self.current_pumps = 0
        self.temp_bank = 0
        self.is_exploded = False

        # Update the UI
        self.update_ui_for_next_balloon()

    def update_ui_for_next_balloon(self):
        """Update UI elements for the next balloon - implemented by subclasses"""
        # Update balloon display
        self.draw_balloon()

        # Update labels with current values
        self.update_labels()

    def update_labels(self):
        """Update display labels with current values"""
        self.balloon_label.config(text=f"Balloon: {self.current_balloon}/{self.max_balloons}")
        self.block_label.config(text=f"Block: {self.current_block}/{self.blocks['num_blocks']}")  # New label
        self.pump_label.config(text=f"Pumps: {self.current_pumps}")
        self.total_label.config(text=f"Total: ${self.total_earned / 100:.2f}")

    def end_experiment(self):
        """End the experiment and show results"""
        # Clear the screen
        self.clear_screen()

        # Create results frame
        results_frame = ttk.Frame(self.master, padding=20)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Show completion message
        ttk.Label(
            results_frame,
            text="Experiment Complete!",
            font=("Arial", 20, "bold")
        ).pack(pady=(0, 20))

        # Show earnings
        ttk.Label(
            results_frame,
            text=f"Total Earned: ${self.total_earned / 100:.2f}",
            font=("Arial", 16)
        ).pack(pady=10)

        # Show some statistics
        if self.pumps_history:
            avg_pumps = sum(self.pumps_history) / len(self.pumps_history)
            ttk.Label(
                results_frame,
                text=f"Average Pumps Per Balloon: {avg_pumps:.1f}",
                font=("Arial", 14)
            ).pack(pady=5)

        # Back to hub button
        back_button = ModernButton(
            results_frame,
            text="Return to Hub",
            command=self.return_to_hub,
            height=50,
            font=('Helvetica', 14, 'bold')
        )
        back_button.pack(pady=30)

    def return_to_hub(self):
        """Return to the main hub - overridden by the hub"""
        self.master.destroy()  # Default behavior is to close the window


class StandardBART(BARTExperiment):
    """Standard BART experiment implementation"""

    def get_instruction_text(self):
        return (
            "In this task, you will see a series of balloons on the screen. "
            "For each balloon, you can earn money by clicking the 'Pump' button to inflate it. "
            "Each pump earns 5 cents, but be careful! The balloon will pop at some point if you pump too much. "
            "If the balloon pops, you earn nothing for that balloon.\n\n"
            "You can click 'Collect' at any time to add your earnings for the current balloon to your total and move on to the next one.\n\n"
            f"You will see {self.max_balloons} balloons in total. Try to earn as much money as possible!"
        )

    def setup_gui(self):
        """Set up the main experiment GUI for Standard BART"""
        self.clear_screen()

        # Configure the layout
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=0)  # Info area
        self.master.grid_rowconfigure(1, weight=1)  # Canvas area
        self.master.grid_rowconfigure(2, weight=0)  # Button area

        # Create info frame
        info_frame = ttk.Frame(self.master, padding=10)
        info_frame.grid(row=0, column=0, sticky="ew")

        # Configure info frame columns
        info_frame.columnconfigure(0, weight=1)  # Left info
        info_frame.columnconfigure(1, weight=1)  # Center info
        info_frame.columnconfigure(2, weight=1)  # Right info

        # Create info labels
        self.balloon_label = ttk.Label(
            info_frame,
            text=f"Balloon: {self.current_balloon}/{self.max_balloons}",
            font=("Arial", 14, "bold")
        )
        self.balloon_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.pump_label = ttk.Label(
            info_frame,
            text=f"Pumps: {self.current_pumps}",
            font=("Arial", 14)
        )
        self.pump_label.grid(row=0, column=1, sticky="n", padx=20, pady=10)

        self.total_label = ttk.Label(
            info_frame,
            text=f"Total: ${self.total_earned / 100:.2f}",
            font=("Arial", 14, "bold")
        )
        self.total_label.grid(row=0, column=2, sticky="e", padx=20, pady=10)

        # Create canvas for balloon
        canvas_frame = ttk.Frame(self.master)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create button frame
        button_frame = ttk.Frame(self.master, padding=10)
        button_frame.grid(row=2, column=0, sticky="ew")

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Create pump and collect buttons
        self.pump_button = ModernButton(
            button_frame,
            text="Pump",
            command=self.pump,
            height=60,
            font=('Helvetica', 16, 'bold')
        )
        self.pump_button.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        self.collect_button = ModernButton(
            button_frame,
            text="Collect",
            command=self.collect,
            height=60,
            bg_color="#4CAF50",  # Green
            hover_color="#388E3C",  # Darker green
            font=('Helvetica', 16, 'bold')
        )
        self.collect_button.grid(row=0, column=1, sticky="ew", padx=20, pady=10)

        # Draw initial balloon
        self.master.update_idletasks()  # Force update to get correct dimensions
        self.draw_balloon()

    def pump(self):
        """Handle pump button click"""
        if self.is_exploded:
            return

        # Play pump sound
        self.play_sound('pump')

        # Calculate explosion probability using drawing without replacement model
        explosion_prob = self.calculate_explosion_probability()

        # Determine if explosion occurs
        if random.random() < explosion_prob:
            self.handle_explosion()
            return

        # Increment pumps and money
        self.current_pumps += 1
        self.temp_bank += self.cents_per_pump

        # Update pump label
        self.pump_label.config(text=f"Pumps: {self.current_pumps}")

        # Update balloon display with animation
        if self.fun_mode:
            self.animate_pump()
        else:
            self.draw_balloon()

    def animate_pump(self):
        """Animate the balloon pump with expansion and contraction"""
        # Animation parameters
        steps = 6
        duration = 300  # milliseconds

        def animate_step(step=0):
            if step <= steps:
                # Calculate animation factor
                if step <= steps // 2:
                    # First half - expand
                    factor = 1.0 + 0.1 * (step / (steps // 2))
                else:
                    # Second half - contract
                    factor = 1.1 - 0.1 * ((step - steps // 2) / (steps // 2))

                # Draw with animation factor
                self.draw_balloon(animation_factor=factor)

                # Schedule next step
                self.master.after(duration // steps, lambda: animate_step(step + 1))
            else:
                # Animation complete
                self.draw_balloon()

        # Start animation
        animate_step()

    def update_labels(self):
        """Update display labels with current values"""
        self.balloon_label.config(text=f"Balloon: {self.current_balloon}/{self.max_balloons}")
        self.pump_label.config(text=f"Pumps: {self.current_pumps}")
        self.total_label.config(text=f"Total: ${self.total_earned / 100:.2f}")


class PresetBART(BARTExperiment):
    """Preset Pumps BART experiment implementation"""

    def setup_experiment_state(self):
        """Initialize experiment state variables"""
        super().setup_experiment_state()
        self.preset_pumps = 0
        self.input_timeout = self.settings.get('input_timeout', 10)

    def get_instruction_text(self):
        return (
            "In this version of BART, you will decide how many times to pump each balloon before seeing it inflate.\n\n"
            "For each balloon, enter the number of pumps you want, then click 'Submit'. "
            "The balloon will automatically inflate to that size if it doesn't pop first.\n\n"
            "Each pump earns 5 cents, but if the balloon pops, you earn nothing for that balloon.\n\n"
            f"You have {self.input_timeout} seconds to enter your decision for each balloon.\n\n"
            f"You will see {self.max_balloons} balloons in total. Try to earn as much money as possible!"
        )

    def setup_gui(self):
        """Set up the main experiment GUI for Preset BART"""
        self.clear_screen()

        # Configure the layout
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=0)  # Info area
        self.master.grid_rowconfigure(1, weight=0)  # Input area
        self.master.grid_rowconfigure(2, weight=1)  # Canvas area

        # Create info frame
        info_frame = ttk.Frame(self.master, padding=10)
        info_frame.grid(row=0, column=0, sticky="ew")

        # Configure info frame columns
        info_frame.columnconfigure(0, weight=1)  # Left info
        info_frame.columnconfigure(1, weight=1)  # Right info

        # Create info labels
        self.balloon_label = ttk.Label(
            info_frame,
            text=f"Balloon: {self.current_balloon}/{self.max_balloons}",
            font=("Arial", 14, "bold")
        )
        self.balloon_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.total_label = ttk.Label(
            info_frame,
            text=f"Total: ${self.total_earned / 100:.2f}",
            font=("Arial", 14, "bold")
        )
        self.total_label.grid(row=0, column=1, sticky="e", padx=20, pady=10)

        self.last_label = ttk.Label(
            info_frame,
            text=f"Last: ${self.last_balloon_earnings / 100:.2f}",
            font=("Arial", 14)
        )
        self.last_label.grid(row=1, column=1, sticky="e", padx=20, pady=10)

        # Create input frame
        input_frame = ttk.Frame(self.master, padding=10)
        input_frame.grid(row=1, column=0, sticky="ew")

        input_frame.columnconfigure(0, weight=2)  # Label
        input_frame.columnconfigure(1, weight=3)  # Entry
        input_frame.columnconfigure(2, weight=2)  # Button

        # Input label
        # Input label
        ttk.Label(
            input_frame,
            text="Enter number of pumps:",
            font=("Arial", 14)
        ).grid(row=0, column=0, sticky="e", padx=10, pady=10)

        # Entry field
        vcmd = (self.master.register(self.validate_input), '%P')
        self.pump_entry = ttk.Entry(
            input_frame,
            font=("Arial", 14),
            width=10,
            validate="key",
            validatecommand=vcmd
        )
        self.pump_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        # Submit button
        self.submit_button = ModernButton(
            input_frame,
            text="Submit",
            command=self.process_preset_pumps,
            height=40,
            font=('Helvetica', 14, 'bold')
        )
        self.submit_button.grid(row=0, column=2, sticky="w", padx=10, pady=10)

        # Create canvas for balloon
        canvas_frame = ttk.Frame(self.master)
        canvas_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Set focus to entry field
        self.pump_entry.focus_set()

        # Bind Enter key to submit
        self.pump_entry.bind("<Return>", lambda e: self.process_preset_pumps())

        # Draw initial balloon
        self.master.update_idletasks()
        self.draw_balloon()

    def validate_input(self, value):
        """Validate input to ensure it's numeric"""
        if value == "":
            return True
        try:
            num = int(value)
            return 0 <= num <= 150  # Reasonable upper limit
        except ValueError:
            return False

    def process_preset_pumps(self):
        """Process the preset pump entry"""
        try:
            # Get the number of pumps from entry
            pumps = int(self.pump_entry.get())

            # Validate the number
            if pumps <= 0:
                return False

            # Store the preset pumps
            self.preset_pumps = pumps

            # Disable entry and button during animation
            self.pump_entry.configure(state='disabled')
            self.submit_button.state(['disabled'])

            # Animate the pumping process
            self.animate_preset_pumps(0)

            return True
        except ValueError:
            # Invalid input
            return False

    def animate_preset_pumps(self, current_pump):
        """Animate the preset pumps with explosion check"""
        if current_pump >= self.preset_pumps:
            # All pumps completed without explosion
            self.current_pumps = self.preset_pumps
            self.temp_bank = self.preset_pumps * self.cents_per_pump

            # Successful completion - collect
            self.collect()
            return

        # Set current pumps for probability calculation
        self.current_pumps = current_pump

        # Calculate explosion probability using standardized method
        explosion_prob = self.calculate_explosion_probability()

        if random.random() < explosion_prob:
            # Balloon exploded
            self.handle_explosion()
            return

        # Play pump sound
        self.play_sound('pump')

        # Update current pump count
        self.current_pumps = current_pump + 1

        # Animate this pump
        if self.fun_mode:
            steps = 6
            duration = 300  # milliseconds

            def animate_step(step=0):
                if step <= steps:
                    # Calculate animation factor
                    if step <= steps // 2:
                        # First half - expand
                        factor = 1.0 + 0.1 * (step / (steps // 2))
                    else:
                        # Second half - contract
                        factor = 1.1 - 0.1 * ((step - steps // 2) / (steps // 2))

                    # Draw with animation factor
                    self.draw_balloon(animation_factor=factor)

                    # Schedule next step
                    self.master.after(duration // steps, lambda: animate_step(step + 1))
                else:
                    # Animation complete for this pump, proceed to next
                    self.master.after(100, lambda: self.animate_preset_pumps(current_pump + 1))

            # Start animation for this pump
            animate_step()
        else:
            # Simpler animation in non-fun mode
            self.draw_balloon()

            # Schedule next pump with delay
            self.master.after(200, lambda: self.animate_preset_pumps(current_pump + 1))

    def update_ui_for_next_balloon(self):
        """Update UI for next balloon"""
        super().update_ui_for_next_balloon()

        # Clear and re-enable entry and button
        self.pump_entry.configure(state='normal')
        self.pump_entry.delete(0, tk.END)
        self.submit_button.state(['!disabled'])

        # Set focus to entry
        self.pump_entry.focus_set()

    def update_labels(self):
        """Update display labels with current values"""
        self.balloon_label.config(text=f"Balloon: {self.current_balloon}/{self.max_balloons}")
        self.total_label.config(text=f"Total: ${self.total_earned / 100:.2f}")
        self.last_label.config(text=f"Last: ${self.last_balloon_earnings / 100:.2f}")


class AutoBART(BARTExperiment):
    """Auto-Inflate BART experiment implementation"""

    def setup_experiment_state(self):
        """Initialize experiment state variables"""
        super().setup_experiment_state()
        self.is_inflating = False
        self.inflation_speed = self.settings.get('inflation_speed', 1.5)
        self.inflation_timer = None

    def get_instruction_text(self):
        return (
            "In this version of BART, the balloon will inflate automatically.\n\n"
            "Click 'Start Inflation' to begin inflating the balloon. "
            "Each pump earns 5 cents, but the balloon will pop at some point if you let it inflate too much.\n\n"
            "Press the SPACE BAR at any time to stop the inflation and collect your money.\n\n"
            "If the balloon pops, you earn nothing for that balloon.\n\n"
            f"You will see {self.max_balloons} balloons in total. Try to earn as much money as possible!"
        )

    def setup_gui(self):
        """Set up the main experiment GUI for Auto-Inflate BART"""
        self.clear_screen()

        # Configure the layout
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=0)  # Info area
        self.master.grid_rowconfigure(1, weight=1)  # Canvas area
        self.master.grid_rowconfigure(2, weight=0)  # Instruction area
        self.master.grid_rowconfigure(3, weight=0)  # Button area

        # Create info frame
        info_frame = ttk.Frame(self.master, padding=10)
        info_frame.grid(row=0, column=0, sticky="ew")

        # Configure info frame columns
        info_frame.columnconfigure(0, weight=1)  # Left info
        info_frame.columnconfigure(1, weight=1)  # Right info

        # Create info labels
        self.balloon_label = ttk.Label(
            info_frame,
            text=f"Balloon: {self.current_balloon}/{self.max_balloons}",
            font=("Arial", 14, "bold")
        )
        self.balloon_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.total_label = ttk.Label(
            info_frame,
            text=f"Total: ${self.total_earned / 100:.2f}",
            font=("Arial", 14, "bold")
        )
        self.total_label.grid(row=0, column=1, sticky="e", padx=20, pady=10)

        self.last_label = ttk.Label(
            info_frame,
            text=f"Last: ${self.last_balloon_earnings / 100:.2f}",
            font=("Arial", 14)
        )
        self.last_label.grid(row=1, column=1, sticky="e", padx=20, pady=10)

        # Create canvas for balloon
        canvas_frame = ttk.Frame(self.master)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Instruction label
        instruction_frame = ttk.Frame(self.master, padding=5)
        instruction_frame.grid(row=2, column=0, sticky="ew")

        ttk.Label(
            instruction_frame,
            text="Press SPACE BAR to stop inflation and collect money",
            font=("Arial", 12, "bold")
        ).pack()

        # Button frame
        button_frame = ttk.Frame(self.master, padding=10)
        button_frame.grid(row=3, column=0, sticky="ew")

        # Center the button
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # Start inflation button
        self.start_button = ModernButton(
            button_frame,
            text="Start Inflation",
            command=self.start_inflation,
            height=50,
            font=('Helvetica', 16, 'bold')
        )
        self.start_button.grid(row=0, column=1, padx=20, pady=10)

        # Bind spacebar to stop inflation
        self.master.bind('<space>', lambda e: self.stop_inflation())

        # Draw initial balloon
        self.master.update_idletasks()
        self.draw_balloon()

    def start_inflation(self):
        """Start automatic balloon inflation"""
        if self.is_exploded or self.is_inflating:
            return

        # Set inflating state
        self.is_inflating = True

        # Disable start button
        self.start_button.state(['disabled'])

        # Start inflation process
        self.inflate_balloon()

    def inflate_balloon(self):
        """Inflate the balloon automatically"""
        if not self.is_inflating or self.is_exploded:
            return

        # Calculate explosion probability using standardized method
        explosion_prob = self.calculate_explosion_probability()

        if random.random() < explosion_prob:
            # Balloon exploded
            self.handle_explosion()
            return

        # Play pump sound
        self.play_sound('pump')

        # Increment pumps and money
        self.current_pumps += 1
        self.temp_bank += self.cents_per_pump

        # Animate the pump
        if self.fun_mode:
            steps = 6
            duration = 300  # milliseconds

            def animate_step(step=0):
                if step <= steps:
                    # Calculate animation factor
                    if step <= steps // 2:
                        # First half - expand
                        factor = 1.0 + 0.1 * (step / (steps // 2))
                    else:
                        # Second half - contract
                        factor = 1.1 - 0.1 * ((step - steps // 2) / (steps // 2))

                    # Draw with animation factor
                    self.draw_balloon(animation_factor=factor)

                    # Schedule next step
                    self.master.after(duration // steps, lambda: animate_step(step + 1))
                else:
                    # Animation complete, schedule next inflation after delay
                    self.inflation_timer = self.master.after(
                        int(self.inflation_speed * 1000),
                        self.inflate_balloon
                    )

            # Start animation
            animate_step()
        else:
            # Simpler animation in non-fun mode
            self.draw_balloon()

            # Schedule next inflation
            self.inflation_timer = self.master.after(
                int(self.inflation_speed * 1000),
                self.inflate_balloon
            )

    def stop_inflation(self):
        """Stop inflation and collect earnings"""
        if not self.is_inflating or self.is_exploded:
            return

        # Cancel any pending inflation
        if self.inflation_timer:
            self.master.after_cancel(self.inflation_timer)
            self.inflation_timer = None

        # Stop inflation
        self.is_inflating = False

        # Collect earnings
        self.collect()

    def update_ui_for_next_balloon(self):
        """Update UI for next balloon"""
        super().update_ui_for_next_balloon()

        # Re-enable start button
        self.start_button.state(['!disabled'])

    def update_labels(self):
        """Update display labels with current values"""
        self.balloon_label.config(text=f"Balloon: {self.current_balloon}/{self.max_balloons}")
        self.total_label.config(text=f"Total: ${self.total_earned / 100:.2f}")
        self.last_label.config(text=f"Last: ${self.last_balloon_earnings / 100:.2f}")

class BARTY(BARTExperiment):
    """BART-Y (child-friendly version) experiment implementation"""

    def setup_experiment_state(self):
        """Initialize experiment state variables"""
        super().setup_experiment_state()

        # Points instead of cents
        self.points_per_pump = self.settings.get('points_per_pump', 100)

        # Prize thresholds
        self.prize_thresholds = self.settings.get('prize_thresholds', {
            'small': 5000,
            'medium': 10000,
            'large': 15000,
            'bonus': 20000
        })

    def get_instruction_text(self):
        return (
            "Welcome to the Balloon Game!\n\n"
            "In this game, you will see a series of balloons on the screen. "
            "For each balloon, you can earn points by clicking the 'Pump' button to inflate it. "
            f"Each pump earns {self.points_per_pump} points, but be careful! "
            "The balloon will pop at some point if you pump too much. "
            "If the balloon pops, you earn no points for that balloon.\n\n"
            "You can click 'Collect' at any time to add your points for the current balloon "
            "to your total and move on to the next one.\n\n"
            f"You will see {self.max_balloons} balloons in total. Try to earn as many points as possible!\n\n"
            "Prizes:\n"
            f"• Small Prize: {self.prize_thresholds['small']} points\n"
            f"• Medium Prize: {self.prize_thresholds['medium']} points\n"
            f"• Large Prize: {self.prize_thresholds['large']} points\n"
            f"• Bonus Prize: {self.prize_thresholds['bonus']} points"
        )

    def setup_gui(self):
        """Set up the main experiment GUI for BART-Y"""
        self.clear_screen()

        # Configure the layout
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=0)  # Info area
        self.master.grid_rowconfigure(1, weight=1)  # Canvas area
        self.master.grid_rowconfigure(2, weight=0)  # Button area

        # Create info frame
        info_frame = ttk.Frame(self.master, padding=10)
        info_frame.grid(row=0, column=0, sticky="ew")

        # Configure info frame columns
        info_frame.columnconfigure(0, weight=1)  # Left info
        info_frame.columnconfigure(1, weight=1)  # Center info
        info_frame.columnconfigure(2, weight=1)  # Right info

        # Create info labels with more colorful and child-friendly fonts
        self.balloon_label = ttk.Label(
            info_frame,
            text=f"Balloon: {self.current_balloon}/{self.max_balloons}",
            font=("Comic Sans MS", 14, "bold"),
            foreground="#0066CC"
        )
        self.balloon_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.pump_label = ttk.Label(
            info_frame,
            text=f"Pumps: {self.current_pumps}",
            font=("Comic Sans MS", 14),
            foreground="#CC6600"
        )
        self.pump_label.grid(row=0, column=1, sticky="n", padx=20, pady=10)

        self.points_label = ttk.Label(
            info_frame,
            text=f"Points: {self.total_earned}",
            font=("Comic Sans MS", 14, "bold"),
            foreground="#009900"
        )
        self.points_label.grid(row=0, column=2, sticky="e", padx=20, pady=10)

        # Create progress bar for visual feedback on prize thresholds
        progress_frame = ttk.Frame(info_frame)
        progress_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 10))

        # Prize level indicators
        prize_labels_frame = ttk.Frame(progress_frame)
        prize_labels_frame.pack(fill=tk.X, pady=(5, 0))

        # Configure columns for prize labels
        for i in range(4):
            prize_labels_frame.columnconfigure(i, weight=1)

        # Create prize threshold labels
        prizes = [
            ("Small", self.prize_thresholds['small']),
            ("Medium", self.prize_thresholds['medium']),
            ("Large", self.prize_thresholds['large']),
            ("Bonus", self.prize_thresholds['bonus'])
        ]

        for i, (name, threshold) in enumerate(prizes):
            ttk.Label(
                prize_labels_frame,
                text=f"{name}\n{threshold}",
                font=("Comic Sans MS", 10),
                foreground="#555555",
                justify=tk.CENTER
            ).grid(row=0, column=i, sticky="n")

        # Create canvas for balloon
        canvas_frame = ttk.Frame(self.master)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create button frame
        button_frame = ttk.Frame(self.master, padding=10)
        button_frame.grid(row=2, column=0, sticky="ew")

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Create pump and collect buttons with more child-friendly appearance
        self.pump_button = ModernButton(
            button_frame,
            text="Pump",
            command=self.pump,
            height=60,
            font=('Comic Sans MS', 16, 'bold'),
            bg_color="#FF9900",  # Orange
            hover_color="#FF6600"  # Darker orange
        )
        self.pump_button.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        self.collect_button = ModernButton(
            button_frame,
            text="Collect",
            command=self.collect,
            height=60,
            font=('Comic Sans MS', 16, 'bold'),
            bg_color="#66CC00",  # Green
            hover_color="#339900"  # Darker green
        )
        self.collect_button.grid(row=0, column=1, sticky="ew", padx=20, pady=10)

        # Draw initial balloon
        self.master.update_idletasks()
        self.draw_balloon()

    def pump(self):
        """Handle pump button click"""
        if self.is_exploded:
            return

        # Play pump sound
        self.play_sound('pump')

        # Calculate explosion probability using standardized method
        explosion_prob = self.calculate_explosion_probability()

        if random.random() < explosion_prob:
            self.handle_explosion()
            return

        # Increment pumps and points
        self.current_pumps += 1
        self.temp_bank += self.points_per_pump

        # Update pump label
        self.pump_label.config(text=f"Pumps: {self.current_pumps}")

        # Update balloon display with animation
        if self.fun_mode:
            self.animate_pump()
        else:
            self.draw_balloon()

    def animate_pump(self):
        """Animate the balloon pump with expansion and contraction"""
        # Animation parameters
        steps = 6
        duration = 300  # milliseconds

        def animate_step(step=0):
            if step <= steps:
                # Calculate animation factor
                if step <= steps // 2:
                    # First half - expand
                    factor = 1.0 + 0.1 * (step / (steps // 2))
                else:
                    # Second half - contract
                    factor = 1.1 - 0.1 * ((step - steps // 2) / (steps // 2))

                # Draw with animation factor
                self.draw_balloon(animation_factor=factor)

                # Schedule next step
                self.master.after(duration // steps, lambda: animate_step(step + 1))
            else:
                # Animation complete
                self.draw_balloon()

        # Start animation
        animate_step()

    def update_labels(self):
        """Update display labels with current values"""
        self.balloon_label.config(text=f"Balloon: {self.current_balloon}/{self.max_balloons}")
        self.pump_label.config(text=f"Pumps: {self.current_pumps}")
        self.points_label.config(text=f"Points: {self.total_earned}")

    def show_collection_feedback(self, amount):
        """Show feedback when points are collected"""
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Clear canvas
        self.canvas.delete("all")

        # Show amount collected
        self.canvas.create_text(
            canvas_width / 2, canvas_height / 2,
            text=f"+{amount} points!",
            font=("Comic Sans MS", 24, "bold"),
            fill="#008800",
            anchor="center"
        )

    def end_experiment(self):
        """End the experiment and show results with prize information"""
        # Clear the screen
        self.clear_screen()

        # Create results frame
        results_frame = ttk.Frame(self.master, padding=20)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Show completion message
        ttk.Label(
            results_frame,
            text="Game Complete!",
            font=("Comic Sans MS", 20, "bold"),
            foreground="#0066CC"
        ).pack(pady=(0, 20))

        # Show points earned
        ttk.Label(
            results_frame,
            text=f"Total Points: {self.total_earned}",
            font=("Comic Sans MS", 16, "bold"),
            foreground="#009900"
        ).pack(pady=10)

        # Determine prize level
        prize_level = "None"
        if self.total_earned >= self.prize_thresholds['bonus']:
            prize_level = "BONUS PRIZE!!"
            prize_color = "#FF00FF"  # Magenta
        elif self.total_earned >= self.prize_thresholds['large']:
            prize_level = "LARGE PRIZE!"
            prize_color = "#FF9900"  # Orange
        elif self.total_earned >= self.prize_thresholds['medium']:
            prize_level = "MEDIUM PRIZE!"
            prize_color = "#3399FF"  # Blue
        elif self.total_earned >= self.prize_thresholds['small']:
            prize_level = "SMALL PRIZE"
            prize_color = "#66CC00"  # Green

        # Show prize earned
        ttk.Label(
            results_frame,
            text=f"You earned a: {prize_level}",
            font=("Comic Sans MS", 18, "bold"),
            foreground=prize_color
        ).pack(pady=20)

        # Back to hub button
        back_button = ModernButton(
            results_frame,
            text="Return to Hub",
            command=self.return_to_hub,
            height=50,
            font=('Comic Sans MS', 14, 'bold'),
            bg_color="#4a86e8"
        )
        back_button.pack(pady=30)