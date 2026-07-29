import random

import numpy as np
import pytest

from coursekit.seed import set_global_seed


def test_seed_repeats_python_and_numpy_sequences() -> None:
    report = set_global_seed(17)
    first = (random.random(), np.random.random())
    set_global_seed(17)
    second = (random.random(), np.random.random())

    assert first == second
    assert report["seed"] == 17
    assert {"python", "numpy"}.issubset(report["configured"])


@pytest.mark.parametrize("seed", [-1, 2**32])
def test_seed_rejects_out_of_range_values(seed: int) -> None:
    with pytest.raises(ValueError, match="диапазоне"):
        set_global_seed(seed)


def test_seed_rejects_boolean() -> None:
    with pytest.raises(TypeError, match="целым"):
        set_global_seed(True)
