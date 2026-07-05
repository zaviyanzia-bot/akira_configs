import sys
import traceback
from PyQt6.QtWidgets import QApplication

def test():
    app = QApplication(sys.argv)
    try:
        from main import NexusAutomatorWindow
        print("Instantiating NexusAutomatorWindow...")
        win = NexusAutomatorWindow()
        print("Instantiation SUCCESS!")
    except Exception as e:
        print("Instantiation FAILED:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
