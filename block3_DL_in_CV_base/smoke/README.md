# CPU smoke блока 3

`block3_classification_smoke.ipynb` — технический, а не оценочный ноутбук. Он без
сети и GPU проверяет минимальный контракт блока:

`фиксированный seed и split → baseline → метрика → JSONL-журнал`.

Ноутбук не заменяет лабораторные работы и не содержит решений их `TODO`.
Он помечен `metadata.course_ci.smoke=true` и предназначен для отдельного
notebook-gate `make smoke-notebooks`. Явная локальная проверка до интеграции
этого target:

```bash
make smoke-notebook \
  NOTEBOOK="block3_DL_in_CV_base/smoke/block3_classification_smoke.ipynb"
```
