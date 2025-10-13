import unittest
from src.arith.subtractor import subtract

class TestSubtractor(unittest.TestCase):
  def test_no_borrow(self):
    val, borrow, _ = subtract(0b1100, 0b0011, n_bits=4)  # 12 - 3 = 9
    self.assertEqual(val, 0b1001)
    self.assertEqual(borrow, 0)

  def test_with_borrow(self):
    val, borrow, _ = subtract(0b0011, 0b1100, n_bits=4)  # 3 - 12 = -9 -> 7 mod 16
    self.assertEqual(val, 0b0111)
    self.assertEqual(borrow, 1)

  def test_mod_arithmetic_property(self):
    n = 4
    mod = 1 << n
    for A in range(mod):
      for B in range(mod):
        val, _, _ = subtract(A, B, n_bits=n)
        self.assertEqual(val, (A - B) % mod)

if __name__ == '__main__':
  unittest.main()
