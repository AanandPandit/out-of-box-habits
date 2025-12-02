import sys
import os

# Add current directory to path to find the compiled module if it's here
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import hacker_utils
    HAS_CPP = True
    print("✅ C++ Module 'hacker_utils' loaded successfully.")
except ImportError as e:
    HAS_CPP = False
    print(f"⚠️ C++ Module 'hacker_utils' not found. Using Python fallbacks. Error: {e}")

class CppBridge:
    @staticmethod
    def find_primes(limit: int):
        if HAS_CPP:
            return hacker_utils.find_primes(limit)
        else:
            # Python fallback
            primes = []
            for num in range(2, limit + 1):
                if all(num % i != 0 for i in range(2, int(num ** 0.5) + 1)):
                    primes.append(num)
            return primes

    @staticmethod
    def generate_matrix_rain(width: int, height: int, frame_count: int):
        if HAS_CPP:
            return hacker_utils.generate_matrix_rain(width, height, frame_count)
        else:
            # Python fallback (simplified)
            import random
            chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*"
            lines = []
            for _ in range(height):
                line = "".join(random.choice(chars) if random.random() > 0.8 else " " for _ in range(width))
                lines.append(line)
            return "\n".join(lines)

    @staticmethod
    def fast_fibonacci(n: int):
        if HAS_CPP:
            return hacker_utils.fast_fibonacci(n)
        else:
            if n <= 1: return n
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
