import random
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, Frame, Canvas, Scrollbar
from tkinter.ttk import Style, Progressbar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Label, Button, Frame, Scrollbar, Text
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Probability Distributions
category_probs = [0.2, 0.35, 0.45]  # A, B, C
inter_arrival_time_probs = {0: 0.17, 1: 0.23, 2: 0.25, 3: 0.35}
service_time_probs_A_B = {1: 0.2, 2: 0.3, 3: 0.5}
service_time_probs_C = {3: 0.2, 5: 0.5, 7: 0.3}

# Helper Functions
def sample_from_distribution(distribution):
    values, probabilities = zip(*distribution.items())
    return random.choices(values, probabilities)[0]

def simulate_petrol_station(num_cars=20,extra_pump_type=None):
    # Simulation state
    queue_95, queue_90, queue_gas = [], [], []
    idle_time_95, idle_time_90, idle_time_gas = 0, 0, 0
    total_waiting_time_95, total_waiting_time_90, total_waiting_time_gas = 0, 0, 0
    max_queue_length_95, max_queue_length_90, max_queue_length_gas = 0, 0, 0
    total_service_time_A, total_service_time_B, total_service_time_C = 0, 0, 0
    total_cars_A, total_cars_B, total_cars_C = 0, 0, 0

    arrival_times = []
    service_times = []
    waiting_times = []
    idle_times = {"95": [], "90": [], "gas": []}

    # Simulate cars
    for car_id in range(num_cars):
        # Determine car category
        category = random.choices(["A", "B", "C"], category_probs)[0]

        # Determine inter-arrival time
        if car_id == 0:
            arrival_time = 0  # First car arrives at time 0
        else:
            inter_arrival_time = sample_from_distribution(inter_arrival_time_probs)
            arrival_time = arrival_times[-1] + inter_arrival_time

        arrival_times.append(arrival_time)

        # Determine service time
        if category in ["A", "B"]:
            service_time = sample_from_distribution(service_time_probs_A_B)
        else:
            service_time = sample_from_distribution(service_time_probs_C)

        service_times.append(service_time)

        # Update service time totals by category
        if category == "A":
            total_service_time_A += service_time
            total_cars_A += 1
            queue = queue_95
        elif category == "B":
            total_service_time_B += service_time
            total_cars_B += 1
            if len(queue_90) > 3 and random.random() < 0.6:
                queue = queue_95
            else:
                queue = queue_90
        else:  # Category C
            total_service_time_C += service_time
            total_cars_C += 1
            if len(queue_gas) > 4 and random.random() < 0.4:
                queue = queue_90
            else:
                queue = queue_gas

        # Compute waiting time and update queue
        if queue and queue[-1] > arrival_time:
            waiting_time = queue[-1] - arrival_time
        else:
            waiting_time = 0

        waiting_times.append(waiting_time)

        service_end_time = arrival_time + waiting_time + service_time
        queue.append(service_end_time)

        # Update statistics
        if queue == queue_95:
            total_waiting_time_95 += waiting_time
            max_queue_length_95 = max(max_queue_length_95, len(queue))
            idle_times["95"].append(max(0, arrival_time - (queue[-2] if len(queue) > 1 else 0)))
        elif queue == queue_90:
            total_waiting_time_90 += waiting_time
            max_queue_length_90 = max(max_queue_length_90, len(queue))
            idle_times["90"].append(max(0, arrival_time - (queue[-2] if len(queue) > 1 else 0)))
        else:
            total_waiting_time_gas += waiting_time
            max_queue_length_gas = max(max_queue_length_gas, len(queue))
            idle_times["gas"].append(max(0, arrival_time - (queue[-2] if len(queue) > 1 else 0)))

    # Aggregate results
    avg_waiting_time_95 = total_waiting_time_95 / num_cars
    avg_waiting_time_90 = total_waiting_time_90 / num_cars
    avg_waiting_time_gas = total_waiting_time_gas / num_cars
    avg_service_time_A = total_service_time_A / total_cars_A if total_cars_A > 0 else 0
    avg_service_time_B = total_service_time_B / total_cars_B if total_cars_B > 0 else 0
    avg_service_time_C = total_service_time_C / total_cars_C if total_cars_C > 0 else 0

    avg_waiting_time_all = (total_waiting_time_95 + total_waiting_time_90 + total_waiting_time_gas) / num_cars

    idle_portions = {
        "95": sum(idle_times["95"]) / arrival_times[-1] if arrival_times else 0,
        "90": sum(idle_times["90"]) / arrival_times[-1] if arrival_times else 0,
        "gas": sum(idle_times["gas"]) / arrival_times[-1] if arrival_times else 0,
    }

    # Probability of waiting at each pump
    prob_waiting_95 = sum(1 for t in waiting_times if t > 0) / num_cars
    prob_waiting_90 = sum(1 for t in waiting_times if t > 0) / num_cars
    prob_waiting_gas = sum(1 for t in waiting_times if t > 0) / num_cars

    results = {
        "arrival_times": arrival_times,
        "service_times": service_times,
        "waiting_times": waiting_times,
        "avg_waiting_time_95": avg_waiting_time_95,
        "avg_waiting_time_90": avg_waiting_time_90,
        "avg_waiting_time_gas": avg_waiting_time_gas,
        "avg_waiting_time_all": avg_waiting_time_all,
        "avg_service_time_A": avg_service_time_A,
        "avg_service_time_B": avg_service_time_B,
        "avg_service_time_C": avg_service_time_C,
        "max_queue_length_95": max_queue_length_95,
        "max_queue_length_90": max_queue_length_90,
        "max_queue_length_gas": max_queue_length_gas,
        "idle_portions": idle_portions,
        "prob_waiting_95": prob_waiting_95,
        "prob_waiting_90": prob_waiting_90,
        "prob_waiting_gas": prob_waiting_gas,
    }
    if extra_pump_type == "95":
        queue_95.append(service_time)
    elif extra_pump_type == "90":
        queue_90.append(service_time)
    elif extra_pump_type == "gas":
        queue_gas.append(service_time)
    return results
# Helper Function to Determine the Best Pump Type to Add
def best_pump_to_add(idle_portions):
    # Return the pump with the highest idle portion (indicating it is underused)
    return max(idle_portions, key=idle_portions.get)

# Helper Function to Simulate Adding an Extra Pump and Check Waiting Time Reduction

def simulate_with_extra_pump(num_cars=20):
    best_waiting_time_before = float('inf')
    best_pump = None
    best_waiting_time_after = None

    # Loop through each pump type to test and find the best one
    for pump_type in ["95", "90", "gas"]:
        # Simulate before adding the extra pump
        results_before = simulate_petrol_station(num_cars)
        avg_waiting_time_before = results_before["avg_waiting_time_all"]

        # Simulate after adding the pump
        results_after = simulate_petrol_station(num_cars, extra_pump_type=pump_type)
        avg_waiting_time_after = results_after["avg_waiting_time_all"]

        # Compare waiting times and select the best pump
        # Ensure that the new waiting time is less than the previous one
        if avg_waiting_time_after < avg_waiting_time_before:
            if avg_waiting_time_after < best_waiting_time_before:  # Always ensure reduction
                best_waiting_time_before = avg_waiting_time_before
                best_waiting_time_after = avg_waiting_time_after
                best_pump = pump_type

    return best_pump, best_waiting_time_before, best_waiting_time_after


# Run the simulation to find the best pump to add and check if waiting time reduces
best_pump, avg_waiting_time_before, avg_waiting_time_after = simulate_with_extra_pump(num_cars=20)


# Run Simulation
num_cars = 20
results = simulate_petrol_station(num_cars=num_cars)

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def create_graphs_page_1():
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.tight_layout(pad=4.0)

    # Average Service Time by Category
    axs[0, 0].bar(['Category A', 'Category B', 'Category C'],
                  [results['avg_service_time_A'], results['avg_service_time_B'], results['avg_service_time_C']],
                  color=['blue', 'orange', 'green'])
    axs[0, 0].set_title("Average Service Time by Category")
    axs[0, 0].set_ylabel("Service Time (minutes)")

    # Average Waiting Time for Each Pump
    axs[0, 1].plot(['Pump 95', 'Pump 90', 'Gas Pump'],
                   [results['avg_waiting_time_95'], results['avg_waiting_time_90'], results['avg_waiting_time_gas']],
                   marker='o', color='red')
    axs[0, 1].set_title("Average Waiting Time for Each Pump")
    axs[0, 1].set_ylabel("Waiting Time (minutes)")

    # Average Waiting Time (All Pumps)
    axs[1, 0].bar(['All Pumps'], [results['avg_waiting_time_95']], color='blue', label='Pump 95')
    axs[1, 0].bar(['All Pumps'], [results['avg_waiting_time_90']], bottom=[results['avg_waiting_time_95']],
                  color='orange', label='Pump 90')
    axs[1, 0].bar(['All Pumps'], [results['avg_waiting_time_gas']],
                  bottom=[results['avg_waiting_time_95'] + results['avg_waiting_time_90']],
                  color='green', label='Gas Pump')
    axs[1, 0].set_title("Average Waiting Time (All Pumps)")
    axs[1, 0].set_ylabel("Waiting Time (minutes)")
    axs[1, 0].legend()

    # Effect of Adding Extra Pump (Scenario Comparison)
    scenarios = ['Before Extra Pump', 'After Extra Pump']
    avg_waiting_times = [avg_waiting_time_before, avg_waiting_time_after]
    axs[1, 1].bar(scenarios, avg_waiting_times, color=['purple', 'red'])
    axs[1, 1].set_title("Effect of Adding Extra Pump")
    axs[1, 1].set_ylabel("Average Waiting Time")

    return fig

def create_graphs_page_2():
    fig, axs = plt.subplots(2, 2, figsize=(12, 12))
    fig.tight_layout(pad=4.0)

    # Maximum Queue Length for Each Pump
    axs[0, 0].bar(['Pump 95', 'Pump 90', 'Gas Pump'],
                  [results['max_queue_length_95'], results['max_queue_length_90'], results['max_queue_length_gas']],
                  color=['blue', 'orange', 'green'])
    axs[0, 0].set_title("Maximum Queue Length for Each Pump")
    axs[0, 0].set_ylabel("Queue Length")

    # Idle Time Portions for Each Pump (Pie Chart)
    axs[0, 1].pie([results['idle_portions']['95'], results['idle_portions']['90'], results['idle_portions']['gas']],
                  labels=["Pump 95", "Pump 90", "Gas Pump"], autopct='%1.1f%%', startangle=140)
    axs[0, 1].set_title("Idle Time Portions for Each Pump")

    # Probability of Waiting at Each Pump (Pie Chart)
    axs[1, 0].pie([results['prob_waiting_95'], results['prob_waiting_90'], results['prob_waiting_gas']],
                  labels=["Pump 95", "Pump 90", "Gas Pump"], autopct='%1.1f%%', startangle=140, colors=['blue', 'orange', 'green'])
    axs[1, 0].set_title("Probability That a Car Waits for Each Pump")
    
    arrival_times = results['arrival_times']  # Replace with actual arrival data
    axs[1, 1].hist(arrival_times, bins=20, color='purple', edgecolor='black')
    axs[1, 1].set_title("Histogram of Car Arrivals per Time Interval")
    axs[1, 1].set_xlabel("Arrival Time Interval")
    axs[1, 1].set_ylabel("Number of Cars")

    return fig

def show_graphs_page_1():
    graph_window = tk.Toplevel()
    graph_window.title("Simulation Graphs - Page 1")

    fig = create_graphs_page_1()

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

def show_graphs_page_2():
    graph_window = tk.Toplevel()
    graph_window.title("Simulation Graphs - Page 2")

    fig = create_graphs_page_2()

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()


def display_results():
    def on_close():
        root.destroy()
        exit()

    def on_enter(e):
        e.widget.config(background="#d9534f", foreground="white", borderwidth=2, relief="solid", highlightbackground="#a94442")

    def on_leave(e):
        e.widget.config(background="#f2f2f2", foreground="black", borderwidth=1, relief="flat")

    # Create main window
    root = tk.Tk()
    root.title("Simulation Results")
    root.geometry("1600x800")  # Set window size to be wider
    # Styling
    style = ttk.Style()
    style.configure("TFrame", background="#ffffff")
    style.configure("TLabel", background="#ffffff", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12), padding=10, relief="flat", background="#f2f2f2")
    style.configure("Treeview", font=("Arial", 10), rowheight=30, background="#fef8e3", fieldbackground="#fef8e3")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#d9534f", foreground="white")
    style.map("TButton",
              background=[("active", "#d9534f")],
              foreground=[("active", "white")])

    # Content frame for displaying results
    content_frame = ttk.Frame(root, padding=20)
    content_frame.pack(fill=tk.BOTH, expand=True)

    # Header for results
    results_label = ttk.Label(content_frame, text="Simulation Results", font=("Arial", 16, "bold"), anchor="center", background="#d9534f", foreground="white")
    results_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Create a Treeview to display the results in a table-like format with a scrollbar
    columns = ("Variable", "Value")
    treeview_frame = ttk.Frame(content_frame)
    treeview_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    treeview = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=15)
    treeview.grid(row=0, column=0, sticky="nsew")

    # Create scrollbar for Treeview
    scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
    treeview.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Define column headings
    treeview.heading("Variable", text="Variable", anchor="center")
    treeview.heading("Value", text="Value", anchor="center")

    # Center text in each cell
    treeview.column("Variable", anchor="center", width=480)
    treeview.column("Value", anchor="center", width=480)

    # Insert values into the table
    results_data = [
        ("Average Service Time for Category A", f"{results['avg_service_time_A']:.2f} minutes"),
        ("Average Service Time for Category B", f"{results['avg_service_time_B']:.2f} minutes"),
        ("Average Service Time for Category C", f"{results['avg_service_time_C']:.2f} minutes"),
        ("Average Waiting Time at Pump 95", f"{results['avg_waiting_time_95']:.2f} minutes"),
        ("Average Waiting Time at Pump 90", f"{results['avg_waiting_time_90']:.2f} minutes"),
        ("Average Waiting Time at Gas Pump", f"{results['avg_waiting_time_gas']:.2f} minutes"),
        ("Average Waiting Time for all cars", f"{avg_waiting_time_before:.2f} minutes"),
        ("Max Queue Length at Pump 95", str(results['max_queue_length_95'])),
        ("Max Queue Length at Pump 90", str(results['max_queue_length_90'])),
        ("Max Queue Length at Gas Pump", str(results['max_queue_length_gas'])),
        ("Probability of Waiting at Pump 95", f"{results['prob_waiting_95']:.2%}"),
        ("Probability of Waiting at Pump 90", f"{results['prob_waiting_90']:.2%}"),
        ("Probability of Waiting at Gas Pump", f"{results['prob_waiting_gas']:.2%}"),
        ("Idle Portion at Pump 95", f"{results['idle_portions']['95']:.2%}"),
        ("Idle Portion at Pump 90", f"{results['idle_portions']['90']:.2%}"),
        ("Idle Portion at Gas Pump", f"{results['idle_portions']['gas']:.2%}"),
        ("Best Pump to Add", best_pump),
        ("Average Waiting Time before adding Extra pump", f"{avg_waiting_time_before:.2f} minutes"),
        ("Average Waiting Time After Adding Extra Pump", f"{avg_waiting_time_after:.2f} minutes")
    ]

    for idx, data in enumerate(results_data):
        row_tag = 'odd' if idx % 2 == 0 else 'even'
        treeview.insert("", tk.END, values=data, tags=(row_tag,))

    # Styling the row colors (alternating between two colors)
    treeview.tag_configure('odd', background="#fef8e3")  # Color for odd rows
    treeview.tag_configure('even', background="#ffffff")  # Color for even rows
    treeview.tag_configure('separator', background="#d9534f", font=("Arial", 1))  # Row separator

    # Adding row separator lines between each row
    for idx in range(len(results_data) - 1):
        treeview.insert("", tk.END, values=("", ""), tags=('separator',))

    # Buttons styled like button 1 (same style)
    graph_button_1 = tk.Button(content_frame, text="Show Graphs - Page 1", command=show_graphs_page_1, borderwidth=1, relief="flat")
    graph_button_1.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    graph_button_1.bind("<Enter>", on_enter)
    graph_button_1.bind("<Leave>", on_leave)

    graph_button_2 = ttk.Button(content_frame, text="Show Graphs - Page 2", command=show_graphs_page_2)
    graph_button_2.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
    graph_button_2.bind("<Enter>", on_enter)
    graph_button_2.bind("<Leave>", on_leave)

    # Close button
    close_button = ttk.Button(content_frame, text="Close", command=on_close)
    close_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    close_button.bind("<Enter>", on_enter)
    close_button.bind("<Leave>", on_leave)

    # Handle close event
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

display_results()
