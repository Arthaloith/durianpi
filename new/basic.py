from gpiozero import OutputDevice
import time

# Relay pin is connected to GPIO18 (Pin 12)
relay_pin = 18
relay = OutputDevice(relay_pin, active_high=False, initial_value=False)  # Set initial state to off

try:
    print("Options:")
    print("1: Turn ON the relay")
    print("2: Turn OFF the relay")
    print("3: Quit")

    while True:
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == '1':
            relay.on()
            print("Relay ON")
        
        elif choice == '2':
            relay.off()
            print("Relay OFF")
        
        elif choice == '3':
            print("Exiting program...")
            break
        
        else:
            print("Invalid choice. Please try again.")

except KeyboardInterrupt:
    print("Exiting program...")
finally:
    relay.off()  # Ensure the relay is turned off
