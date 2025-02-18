import socket
import time
import random


def initialize_targets():
    """
    Initializes 5 targets with random positions and motion vectors.
    Each target has:
    - Position: [x, y, z] (coordinates in a 3D space)
    - Motion vector: [dx, dy, dz] (rate of change per second)
    - Speed: Scalar speed for display
    """
    targets = []
    for _ in range(5):
        x_position = random.uniform(0, 1000)
        y_position = random.uniform(0, 1000)
        z_position = random.uniform(0, 500)
        dx = random.uniform(-5, 5)
        dy = random.uniform(-5, 5)
        dz = random.uniform(-2, 2)
        speed = random.uniform(50, 300)

        targets.append({
            "position": [x_position, y_position, z_position],
            "motion": [dx, dy, dz],
            "speed": speed
        })
    return targets


def update_positions(targets):
    """
    Updates the positions of the targets based on their motion vectors
    and ensures positions stay within predefined boundaries.
    """
    for target in targets:
        target["position"][0] += target["motion"][0]  # Update x
        target["position"][1] += target["motion"][1]  # Update y
        target["position"][2] += target["motion"][2]  # Update z

        # Keep positions within boundaries
        target["position"][0] = max(0, min(1000, target["position"][0]))
        target["position"][1] = max(0, min(1000, target["position"][1]))
        target["position"][2] = max(0, min(500, target["position"][2]))
    return targets


def start_sender():
    receiver_ip = "127.0.0.1"
    receiver_port = 5000
    server_address = (receiver_ip, receiver_port)

    # Initialize 5 targets
    targets = initialize_targets()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            print(f"Sender started. Sending data to {receiver_ip}:{receiver_port}...")

            while True:
                # Update target positions
                targets = update_positions(targets)

                # Flatten data into a string for transmission
                data = ",".join(
                    map(
                        str,
                        [
                            value
                            for target in targets
                            for value in (*target["position"], target["speed"])
                        ]
                    )
                )

                # Print details for debugging and visualization
                for i, target in enumerate(targets, start=1):
                    position = target["position"]
                    speed = target["speed"]
                    print(f"Target {i}: Position={position}, Speed={speed:.2f}")

                # Send data to the receiver
                sock.sendto(data.encode("utf-8"), server_address)

                # Wait before sending the next update
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nSender stopped manually.")
    except socket.error as sock_err:
        print(f"Socket error: {sock_err}")
    except Exception as e:
        print(f"Sender error: {e}")


if __name__ == "__main__":
    start_sender()
