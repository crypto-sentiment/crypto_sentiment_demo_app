import numpy as np


class TestClass:
    def test_dummy(self):
        np.testing.assert_allclose(0.1, 0.1, rtol=0.001)
