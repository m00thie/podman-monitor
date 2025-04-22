import logging
from services.logger_service import get_logger

# Test basic logger creation
print("Testing basic logger creation...")
logger1 = get_logger("test-logger-1")
logger1.info("This is a test message from logger1")

# Test logger with custom level
print("\nTesting logger with custom level...")
logger2 = get_logger("test-logger-2", level=logging.DEBUG)
logger2.debug("This is a debug message from logger2")
logger2.info("This is an info message from logger2")

# Test error handling for empty name
print("\nTesting error handling for empty name...")
try:
    logger3 = get_logger("")
    print("ERROR: Empty name was accepted")
except ValueError as e:
    print(f"SUCCESS: Caught expected error: {e}")

print("\nAll tests completed.")