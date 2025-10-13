import unittest
from src.arith.adder import add

class TestAdder(unittest.TestCase):
  def test_simple_no_carry(self):
    res, _ = add(0b0011, 0b0001, n_bits=4)
    self.assertEqual(res, 0b0100)

  def test_with_carry(self):
    res, _ = add(0b1011, 0b0101, n_bits=4)
    self.assertEqual(res, 0b10000)  # 11 + 5 = 16

  def test_zero(self):
    res, _ = add(0, 0, n_bits=4)
    self.assertEqual(res, 0)

  def test_full_range_small(self):
    for a in range(16):
      for b in range(16):
        res, _ = add(a, b, n_bits=4)
        self.assertEqual(res, a + b)

  def test_carry_in(self):
    res, _ = add(0b0001, 0b0001, n_bits=2, carry_in=1)
    self.assertEqual(res, 0b0011)

if __name__ == '__main__':
  unittest.main()
