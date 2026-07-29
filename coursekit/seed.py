"""Единая настройка генераторов случайных чисел."""

from __future__ import annotations

import os
import random
from typing import Any

import numpy as np


def set_global_seed(seed: int = 42, *, deterministic: bool = True) -> dict[str, Any]:
    """Настроить seed для Python, NumPy, OpenCV и PyTorch, если они установлены.

    Функция не требует тяжёлых библиотек: OpenCV и PyTorch подключаются только
    при их наличии. Возвращаемый словарь удобно сохранять вместе с экспериментом.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed должен быть целым числом")
    if not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed должен находиться в диапазоне [0, 2**32 - 1]")

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    configured = ["python", "numpy"]

    try:
        import cv2
    except ImportError:
        pass
    else:
        cv2.setRNGSeed(seed if seed < 2**31 else seed - 2**32)
        configured.append("opencv")

    try:
        import torch
    except ImportError:
        pass
    else:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.use_deterministic_algorithms(True, warn_only=True)
            if hasattr(torch.backends, "cudnn"):
                torch.backends.cudnn.benchmark = False
                torch.backends.cudnn.deterministic = True
        configured.append("pytorch")

    return {
        "seed": seed,
        "deterministic": deterministic,
        "configured": configured,
        "note": (
            "PYTHONHASHSEED действует полностью только для процессов, "
            "запущенных после его установки"
        ),
    }
