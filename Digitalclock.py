from tkinter import *
from tkinter import ttk, simpledialog
from tkinter import font, scrolledtext, filedialog, messagebox
import time
import datetime
import math
import winson
import threading

class ClockApp:
    def __init__(self, root, user_name):
        self.root = root
        self.root.title("Advanced Clock App")
        self.root.geometry("800x600")
        self.root.configure(background='black')

        self.user_name = user_name

        self.digital_frame = ttk.Frame(self.root)
        self.analog_frame = ttk.Frame(self.root)
        self.events_frame = ttk.Frame(self.root)

        self.mode = StringVar()
        self.mode.set("digital")

        self.alarm_times = []
        self.alarm_sounds = []
        self.alarm_labels = []

        self.countdown_var = StringVar()
        self.countdown_var.set("Set countdown time (MM:SS)")

        self.world_clock_var = StringVar()
        self.world_clock_var.set("Select time zone")

        self.create_widgets()

    def create_widgets(self):
        self.digital_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.analog_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.events_frame.place(relx=1.0, rely=1.0, anchor=SE)

        fnt_digital = font.Font(family='Helvetica', size=60, weight='bold')
        fnt_analog = font.Font(family='Helvetica', size=12, weight='bold')

        self.greeting_label = ttk.Label(self.root, text=f"Hi, {self.user_name}!", font=('Helvetica', 14, 'bold'), foreground="white", background="black")
        self.greeting_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.digital_label = ttk.Label(self.digital_frame, font=fnt_digital, foreground="white", background="black")
        self.digital_label.pack()

        self.analog_canvas = Canvas(self.analog_frame, width=400, height=400, background="black")
        self.analog_canvas.pack()

        self.mode_button = ttk.Button(self.root, text="Switch Mode", command=self.switch_mode)
        self.mode_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Countdown and set countdown widgets
        self.countdown_entry = ttk.Entry(self.root, textvariable=self.countdown_var, font=('Helvetica', 12))
        self.countdown_entry.grid(row=2, column=0, pady=10)

        self.set_countdown_button = ttk.Button(self.root, text="Set Countdown", command=self.set_countdown)
        self.set_countdown_button.grid(row=2, column=1, pady=10)

        # Set alarm widgets
        self.alarm_entry = ttk.Entry(self.root, font=('Helvetica', 12))
        self.alarm_entry.insert(0, "Set alarm time (HH:MM)")
        self.alarm_entry.grid(row=3, column=0, pady=10)

        self.set_alarm_button = ttk.Button(self.root, text="Set Alarm", command=self.set_alarm)
        self.set_alarm_button.grid(row=3, column=1, pady=10)

        # Set event widgets
        self.set_event_button = ttk.Button(self.root, text="Set Event", command=self.set_event)
        self.set_event_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.quit_button = ttk.Button(self.root, text="Quit", command=self.quit_app)
        self.quit_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.events_text = scrolledtext.ScrolledText(self.events_frame, wrap=WORD, width=30, height=10, font=('Helvetica', 12))
        self.events_text.grid(row=0, column=2, rowspan=6, padx=10, pady=10)

        self.update_clock()

    def update_clock(self):
        current_time = self.get_current_time()

        if self.mode.get() == "digital":
            time_str = current_time.strftime("%H:%M:%S")
            self.digital_label.config(text=time_str)
        elif self.mode.get() == "analog":
            self.draw_analog_clock(current_time)

        self.check_alarms(current_time)
        self.check_events_alarm(current_time)
        self.root.after(1000, self.update_clock)

    def get_current_time(self):
        return datetime.datetime.now()

    def draw_analog_clock(self, current_time):
        self.analog_canvas.delete("all")

        hours = current_time.hour % 12
        minutes = current_time.minute
        seconds = current_time.second

        # Draw clock circle
        self.analog_canvas.create_oval(50, 50, 350, 350, outline="white", width=4)

        # Draw hour hand
        hour_angle = math.radians(90 - hours * 30 - minutes * 0.5)
        self.draw_hand(hour_angle, 100, "white", 8)

        # Draw minute hand
        minute_angle = math.radians(90 - minutes * 6)
        self.draw_hand(minute_angle, 150, "white", 4)

        # Draw second hand
        second_angle = math.radians(90 - seconds * 6)
        self.draw_hand(second_angle, 170, "red", 2)

    def draw_hand(self, angle, length, color, width):
        x = 200 + length * math.cos(angle)
        y = 200 - length * math.sin(angle)
        self.analog_canvas.create_line(200, 200, x, y, fill=color, width=width)

    def switch_mode(self):
        if self.mode.get() == "digital":
            self.digital_frame.pack_forget()
            self.analog_frame.pack()
            self.mode.set("analog")
        elif self.mode.get() == "analog":
            self.analog_frame.pack_forget()
            self.digital_frame.pack()
            self.mode.set("digital")

    def set_alarm(self):
        try:
            alarm_time = datetime.datetime.strptime(self.alarm_entry.get(), "%H:%M")
            messagebox.showinfo("Alarm Set", f"Alarm set for {alarm_time.strftime('%H:%M')}")
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a valid time in HH:MM format.")

    def check_alarms(self, current_time):
        alarm_time_str = self.alarm_entry.get()

        if alarm_time_str != "Set alarm time (HH:MM)":
            try:
                alarm_time = datetime.datetime.strptime(alarm_time_str, "%H:%M")
                if current_time.hour == alarm_time.hour and current_time.minute == alarm_time.minute:
                    messagebox.showinfo("Alarm", "Wake up!")

            except ValueError:
                pass

    def set_event(self):
        event_text = simpledialog.askstring("Set Event", "Enter event description:")
        if event_text:
            event_time = self.get_current_time().strftime("%H:%M")
            self.events_text.insert(END, f"\n{event_text} - {event_time}")

    def set_countdown(self):
        try:
            countdown_time = datetime.datetime.strptime(self.countdown_var.get(), "%M:%S")
            end_time = self.get_current_time() + datetime.timedelta(minutes=countdown_time.minute, seconds=countdown_time.second)
            self.countdown(end_time)
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a valid time in MM:SS format.")

    def countdown(self, end_time):
        remaining_time = end_time - datetime.datetime.now()

        if remaining_time.total_seconds() > 0:
            countdown_str = remaining_time.strftime("%M:%S")
            self.countdown_var.set(countdown_str)
            self.root.after(1000, self.countdown, end_time)
        else:
            self.countdown_var.set("Set countdown time (MM:SS)")

    def show_world_clock(self):
        selected_timezone = self.world_clock_var.get()

        if selected_timezone == "UTC":
            world_time = datetime.datetime.utcnow()
        elif selected_timezone == "GMT":
            world_time = datetime.datetime.now(datetime.timezone.utc)
        elif selected_timezone == "EST":
            world_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))
        elif selected_timezone == "CST":
            world_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6)))
        elif selected_timezone == "PST":
            world_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8)))
        else:
            world_time = self.get_current_time()

        messagebox.showinfo(f"World Clock ({selected_timezone})", f"The current time in {selected_timezone} is {world_time.strftime('%H:%M:%S')}")

    def check_events_alarm(self, current_time):
        events = self.events_text.get("1.0", END).strip().split("\n")

        for event in events:
            if event:
                event_data = event.split(" - ")
                event_time = datetime.datetime.strptime(event_data[1], "%H:%M")
                if current_time.hour == event_time.hour and current_time.minute == event_time.minute:
                    messagebox.showinfo("Event Reminder", f"Don't forget: {event_data[0]}")

    def quit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    # Ask for user's name before starting the application
    user_name = simpledialog.askstring("Name", "Please enter your name:")

    if user_name:
        root = Tk()
        app = ClockApp(root, user_name)
        root.mainloop()
    else:
        messagebox.showinfo("Goodbye", "Thanks for using the Clock App. Goodbye!")
