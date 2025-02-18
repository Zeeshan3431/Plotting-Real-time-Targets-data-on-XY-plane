import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import threading
from queue import Queue

# To keep track of the paths of each target
target_paths = {i: {"x": [], "y": []} for i in range(5)}
target_colors = ['blue', 'red', 'green', 'orange', 'purple']  # Unique colors for each target

# For thread-safe communication between threads
data_queue = Queue()

def start_receiver_thread():
    """
    Starts a UDP receiver in a separate thread to receive target data and put it in a queue.
    """
    receiver_ip = "127.0.0.1"
    receiver_port = 5000
    buffer_size = 1024
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((receiver_ip, receiver_port))
            print(f"Receiver started. Listening on {receiver_ip}:{receiver_port}...")
            
            # Set the socket to non-blocking mode
            sock.setblocking(0)
            
            while True:
                try:
                    data, _ = sock.recvfrom(buffer_size)
                    decoded_data = data.decode("utf-8")
                    data_queue.put(decoded_data)  # Put data in queue for the main thread
                except socket.error:
                    pass  # No data received yet, continue looping
                except Exception as e:
                    print(f"Error while receiving data: {e}")
                    break
    except KeyboardInterrupt:
        print("\nReceiver stopped manually.")
    except Exception as e:
        print(f"Receiver error: {e}")

def start_receiver():
    """
    Starts the receiver and sets up the plot for visualization.
    """
    # Initialize the receiver thread
    receiver_thread = threading.Thread(target=start_receiver_thread, daemon=True)
    receiver_thread.start()

    # Set up the plot
    fig, ax = plt.subplots()
    ax.set_xlim(0, 1000)  # X-axis limits
    ax.set_ylim(0, 1000)  # Y-axis limits
    ax.set_title("Target Movement")
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")

    # Initialize scatter plot for the targets with unique colors, with empty data initially
    scat = ax.scatter([], [], c=[], label="Targets")

    # Initialize lines for each target's path
    target_lines = [ax.plot([], [], color=color, label=f"Target {i+1} Path")[0] for i, color in enumerate(target_colors)]

    def update_plot(frame):
        # Check if new data is available from the queue
        if not data_queue.empty():
            data = data_queue.get()
            targets = parse_data(data)

            # Clear the previous paths and add the current position
            for idx, target in enumerate(targets):
                target_paths[idx]["x"].append(target["position"][0])
                target_paths[idx]["y"].append(target["position"][1])

            # Update scatter plot (targets as dots) with target colors
            target_positions = [target["position"][:2] for target in targets]
            scat.set_offsets(target_positions)  # Update target positions

            # Update paths (lines)
            for idx in range(5):
                target_lines[idx].set_data(target_paths[idx]["x"], target_paths[idx]["y"])

            # Update the color of the scatter plot based on target color list
            scat.set_edgecolors(target_colors)

        return scat, *target_lines

    def on_move(event):
        """
        This function is no longer needed because we're not showing mouse position on the plot.
        """
        pass

    # Animation update
    ani = animation.FuncAnimation(fig, update_plot, frames=100, interval=1000, blit=True)

    # Display the plot
    plt.legend()
    plt.show()

def parse_data(data):
    """
    Parses the received data string into a list of target dictionaries and prints each target's values.
    """
    values = list(map(float, data.split(",")))
    targets = []
    for i in range(0, len(values), 4):  # Each target has x, y, z, speed
        position = values[i:i+3]  # x, y, z
        speed = values[i+3]       # speed
        target = {"position": position, "speed": speed}
        targets.append(target)

        # Print the received values for each target
        print(f"Received Target {len(targets)} - Position: {position}, Speed: {speed}")

    return targets

if __name__ == "__main__":
    start_receiver()
