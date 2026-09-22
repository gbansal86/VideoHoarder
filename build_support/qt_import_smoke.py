"""Console diagnostic for validating frozen PySide6/Qt DLL loading."""

from PySide6.QtCore import qVersion

print(f"PySide6 QtCore imported successfully; Qt {qVersion()}")
