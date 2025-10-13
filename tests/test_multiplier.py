import os
import unittest
import random
from src.arith.multiplier import mul

class TestMultiplier(unittest.TestCase):
  def check_case(self, A, B, n_bits):
    prod, _ = mul(A, B, n_bits)
    mod = 1 << (2 * n_bits)      # producto vive en 2*n_bits
    self.assertEqual(prod, (A * B) % mod, msg=f'Fail: A={A} B={B} n={n_bits}')

  def test_zero_identity(self):
    for n in [2, 3, 4]:
      maxv = 1 << n
      for x in range(maxv):
        self.check_case(0, x, n)
        self.check_case(x, 0, n)

  def test_one_identity(self):
    for n in [2, 3, 4]:
      maxv = 1 << n
      for x in range(maxv):
        self.check_case(1, x, n)
        self.check_case(x, 1, n)

  def test_known_examples(self):
    # 11 * 3 = 33
    self.check_case(0b1011, 0b0011, 4)
    # 15 * 15 = 225
    self.check_case(0b1111, 0b1111, 4)
    # 8 * 8 = 64
    self.check_case(0b1000, 0b1000, 4)

  def test_full_range_3_bits(self):
    # Cobertura completa para 3 bits (rápido: 8x8=64 casos)
    n = 3
    for a in range(1 << n):
      for b in range(1 << n):
        self.check_case(a, b, n)

  def test_sampled_range_4_bits(self):
    # Muestra aleatoria determinística para 4 bits
    n = 4
    random.seed(0)
    pairs = [(random.randrange(16), random.randrange(16)) for _ in range(10)]
    for a, b in pairs:
      self.check_case(a, b, n)

  def test_commutativity_sampled(self):
    # Conmutatividad muestreada (rápida). Para exhaustivo ver SLOW_TESTS abajo.
    n = 4
    random.seed(42)
    for _ in range(10):
      a = random.randrange(1 << n)
      b = random.randrange(1 << n)
      val_ab, _ = mul(a, b, n)
      val_ba, _ = mul(b, a, n)
      self.assertEqual(val_ab, val_ba, msg=f'No conmutativa para {a}*{b}')

# --------- OPCIONAL: tests “lentos” si seteás la variable de entorno ---------
slow = os.getenv('SLOW_TESTS')
if slow:
  class TestMultiplierSlow(unittest.TestCase):
    def test_commutativity_full_4_bits(self):
      n = 4
      for a in range(1 << n):
        for b in range(1 << n):
          val_ab, _ = mul(a, b, n)
          val_ba, _ = mul(b, a, n)
          self.assertEqual(val_ab, val_ba, msg=f'No conmutativa para {a}*{b}')

if __name__ == '__main__':
  unittest.main()
