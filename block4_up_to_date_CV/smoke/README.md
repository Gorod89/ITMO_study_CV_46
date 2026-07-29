# CPU smoke блока 4

`block4_segmentation_smoke.ipynb` — технический, а не оценочный ноутбук. Он
создаёт процедурное изображение во временном каталоге, запускает открытый
NumPy-provider `lab_segmentation.py`, проверяет вероятностный выход, IoU/Dice и
JSONL-журнал.

Ноутбук не использует закрытые веса, сеть или GPU, не заменяет лабораторную
DenseCRF и не содержит решений её `TODO`. Он помечен
`metadata.course_ci.smoke=true` и предназначен для отдельного notebook-gate
`make smoke-notebooks`. Явная локальная проверка до интеграции этого target:

```bash
make smoke-notebook \
  NOTEBOOK="block4_up_to_date_CV/smoke/block4_segmentation_smoke.ipynb"
```
