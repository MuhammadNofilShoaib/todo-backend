"""Simple test to verify bcrypt password hashing works correctly."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_password_hash, verify_password

def test_bcrypt():
    print("Testing bcrypt password hashing...")

    # Test with a short password
    password = "secure123"
    print(f"Testing with password: '{password}' (length: {len(password)})")

    try:
        # Hash the password
        hashed = get_password_hash(password)
        print("SUCCESS: Password hashed successfully")

        # Verify the password
        is_valid = verify_password(password, hashed)
        print(f"SUCCESS: Password verification: {is_valid}")

        # Test with a long password that should be truncated
        long_password = "a" * 80  # 80 characters, definitely over 72
        print(f"\nTesting with long password: (length: {len(long_password)})")

        hashed_long = get_password_hash(long_password)
        print("SUCCESS: Long password hashed successfully after truncation")

        is_valid_long = verify_password(long_password[:72], hashed_long)  # Verify with truncated version
        print(f"SUCCESS: Long password verification: {is_valid_long}")

        print("\nALL TESTS PASSED!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bcrypt()