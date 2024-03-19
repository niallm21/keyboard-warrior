import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import subprocess

class KeyboardLightController(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Keyboard Warrior")
        self.set_border_width(10)
        self.set_default_size(400, 200)

        self.password_entered = False  # Flag to check if password was entered

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Color chooser
        self.colorchooser = Gtk.ColorButton()
        vbox.pack_start(self.colorchooser, True, True, 0)

        # Brightness slider
        self.brightness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 3, 1)
        self.brightness_scale.set_value(1)  # Default brightness
        vbox.pack_start(self.brightness_scale, True, True, 0)

        # Apply button
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.connect("clicked", self.on_apply_clicked)
        vbox.pack_start(apply_btn, True, True, 0)

        # Cancel button
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", Gtk.main_quit)
        vbox.pack_start(cancel_btn, True, True, 0)

    def on_apply_clicked(self, widget):
        # Get the selected color
        color = self.colorchooser.get_rgba()
        hex_color = '{:02x}{:02x}{:02x}'.format(int(color.red * 255), int(color.green * 255), int(color.blue * 255))

        # Command to change the keyboard color
        color_command = f"rogauracore single_static {hex_color}"
        
        # Execute the color command
        try:
            subprocess.run(color_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to set color: {e}")

        # Get the brightness level
        brightness = int(self.brightness_scale.get_value())

        # Brightness command
        brightness_command = f"echo {brightness} | sudo -S tee /sys/class/leds/asus::kbd_backlight/brightness"

        # Check if password was entered before
        if not self.password_entered:
            # Create a dialog for password input
            dialog = Gtk.Dialog(title="Authentication Required", parent=self, flags=0)
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
            dialog.set_default_size(150, 100)

            label = Gtk.Label(label="Please enter your password:")
            password_entry = Gtk.Entry()
            password_entry.set_visibility(False)
            password_entry.set_invisible_char("*")

            box = dialog.get_content_area()
            box.add(label)
            box.add(password_entry)
            box.show_all()

            response = dialog.run()
            password = password_entry.get_text()
            dialog.destroy()

            if response == Gtk.ResponseType.OK:
                # Execute the brightness command with password prompt
                try:
                    subprocess.run(['sudo', '-S', 'bash', '-c', brightness_command], input=password.encode(), check=True)
                    self.password_entered = True  # Set the flag as password entered
                except subprocess.CalledProcessError as e:
                    print(f"Failed to set brightness: {e}")
        else:
            # Execute the brightness command without password prompt
            try:
                subprocess.run(['sudo', 'bash', '-c', brightness_command], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to set brightness: {e}")

win = KeyboardLightController()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
