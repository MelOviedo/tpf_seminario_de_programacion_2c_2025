import unittest
import random
from src.arith.divider import divide

class TestDivider(unittest.TestCase):
  def check_case(self, A, B, n_bits):
    if B == 0:
      with self.assertRaises(ZeroDivisionError):
        divide(A, B, n_bits)
      return
    q, r, _ = divide(A, B, n_bits)
    self.assertEqual(q, A // B, f'Q mal: {A}//{B} con n={n_bits}')
    self.assertEqual(r, A % B,  f'R mal: {A}%{B} con n={n_bits}')
    # Propiedades básicas
    self.assertTrue(0 <= r < B)
    self.assertEqual(A, q * B + r)

  def test_known(self):
    self.check_case(14, 3, 4)    # 1110 / 0011 => Q=4, R=2
    self.check_case(13, 13, 4)   # Q=1, R=0
    self.check_case(7, 2, 4)     # Q=3, R=1
    self.check_case(0, 5, 4)     # Q=0, R=0
    self.check_case(9, 1, 4)     # Q=9, R=0

  def test_random_4bits(self):
    n = 4
    for _ in range(30):
      A = random.randrange(1 << n)
      B = random.randrange(1, 1 << n)  # B != 0
      self.check_case(A, B, n)

  def test_zero_division(self):
    with self.assertRaises(ZeroDivisionError):
      divide(5, 0, 4)

if __name__ == '__main__':
  unittest.main()
