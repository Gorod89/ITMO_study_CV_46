# Актуализация университетского курса по компьютерному зрению

## Обзор работ CORE A/A* и проект воспроизводимых лабораторных

**Дата среза:** 29 июля 2026 года  
**Язык курса:** русский  
**Цель:** не перечислить модные модели, а выделить идеи и эксперименты, которые можно честно и воспроизводимо преподавать студентам с неодинаковым аппаратным обеспечением.

---

## 1. Как проводился отбор

В обзор включены прежде всего статьи 2022–2026 годов и фундаментальные более ранние работы, без которых невозможно объяснить современное состояние области. Для утверждений о публикации использованы первичные источники:

- официальные proceedings CVF, ECVA, NeurIPS, PMLR/ICML и ICLR/OpenReview;
- страницы авторов и официальные project pages;
- официальные репозитории авторов;
- портал ICORE (продолжение рейтинга CORE) для проверки уровня площадки.

Приоритет получали работы, для которых возможно хотя бы одно из следующего:

1. повторить центральную идею на малой модели или подвыборке;
2. провести inference/linear probe на опубликованных весах;
3. проверить заявленное свойство контролируемым экспериментом;
4. воспроизвести протокол оценки без закрытых API;
5. использовать код и данные с явно указанными условиями.

Критерий «статья опубликована на A*» не означает, что ее полный эксперимент следует переносить в лабораторную. Масштабные pretraining-рецепты часто требуют сотен GPU и закрытых данных. В таких случаях в курс переносится **научный вопрос, абляция и протокол проверки**, а не попытка повторить число из leaderboard.

---

## 2. Проверка рейтинга площадок

Текущий источник — **ICORE2026**. Портал прямо сообщает, что CORE rankings продолжены как международная коллаборация ICORE. Рейтинг может меняться между выпусками, поэтому в библиографии курса следует хранить поле `ranking_source: ICORE2026`, а не писать просто «A* навсегда».

| Площадка | ICORE2026 | Первичный источник | Что важно для курса |
|---|---:|---|---|
| CVPR | A* | [карточка CVPR в ICORE](https://portal.core.edu.au/conf-ranks/604/) | Основная площадка по 2D/3D vision, detection, segmentation, generation |
| ICCV | A* | [карточка ICCV в ICORE](https://portal.core.edu.au/conf-ranks/638/) | Основная площадка по computer vision; проводится по нечётным годам |
| ECCV | A* | [карточка ECCV в ICORE](https://portal.core.edu.au/conf-ranks/479/) | В ICORE2026 — A*; в CORE2020 была A, что показывает изменяемость рейтинга |
| NeurIPS | A* | [карточка NeurIPS в ICORE](https://portal.core.edu.au/conf-ranks/98/) | Representation learning, foundation models, benchmarks |
| ICML | A* | [карточка ICML в ICORE](https://portal.core.edu.au/conf-ranks/1121/) | Общие методы ML, VLM, ускорение генеративных моделей |
| ICLR | A* | [карточка ICLR в ICORE](https://portal.core.edu.au/conf-ranks/2273/) | Representation learning, архитектуры и современные foundation models |
| AAAI | A* | [карточка AAAI в ICORE](https://portal.core.edu.au/conf-ranks/1629/) | В базе записана под историческим названием; использовать только явно vision-релевантные работы |
| SIGGRAPH | A* | [карточка SIGGRAPH в ICORE](https://portal.core.edu.au/conf-ranks/38/) | Neural rendering, 3D representations, graphics/vision boundary |
| WACV | A | [карточка WACV в ICORE](https://portal.core.edu.au/conf-ranks/763/) | Полезна для прикладных работ, но не следует выдавать за A* |

Для статей CVPR/ICCV официальный open-access архив CVF сообщает, что размещенные версии идентичны принятым версиям за исключением watermark; для ECCV использован архив ECVA. Для NeurIPS Datasets and Benchmarks следует учитывать, что с 2022 года работы этого трека входят в основные proceedings; это зафиксировано на [официальной странице proceedings](https://proceedings.neurips.cc/).

---

## 3. Главные изменения области, которые должен отражать курс

К 2026 году базовая схема «обучить CNN на одном закрытом наборе классов и посчитать accuracy/mAP» уже недостаточна. Современный курс должен системно показывать пять сдвигов:

1. **От task-specific моделей к переносимым представлениям и promptable-моделям.**
2. **От закрытого словаря к vision-language и open-vocabulary постановкам.**
3. **От одного IID test set к оценке сдвига, калибровки и стоимости ошибок.**
4. **От максимальной точности к Pareto-анализу качество–задержка–память–энергия.**
5. **От «данные даны» к инженерии данных: лицензии, происхождение, synthetic-to-real gap, leakage и документация датасета.**

При этом классическая геометрия, свертки, аугментации, метрики, NMS, camera model и оптимизация не устарели. Они стали необходимым языком, на котором объясняются ограничения foundation-моделей.

---

## 4. Тема A. Foundation models и vision-language models

### Зачем включать

VLM превращают классификацию и поиск из задачи с фиксированным числом классов в сопоставление изображений и текста. Promptable segmentation и open-vocabulary detection расширяют эту идею на локализацию. Для русскоязычного курса особенно важно показать, что качество зависит от языка prompt, шаблона, словаря и состава pretraining-данных.

### Учебные результаты

Студент должен уметь:

- объяснить contrastive image–text objective и отличие dual encoder от generative VLM;
- построить zero-shot classifier через текстовые прототипы;
- сравнить русский и английский prompt, единичный prompt и prompt ensemble;
- измерить retrieval Recall@K и zero-shot balanced accuracy;
- объяснить open-vocabulary detection и promptable segmentation;
- документировать неизвестный состав pretraining-данных как угрозу валидности;
- отличать лицензию кода, весов и датасета.

### Обязательное чтение

| Работа | Площадка | Что взять в курс |
|---|---|---|
| [CLIP: Learning Transferable Visual Models From Natural Language Supervision](https://proceedings.mlr.press/v139/radford21a.html) | ICML 2021, A* | Dual encoder, contrastive loss, zero-shot через текстовые шаблоны; фундаментальная работа |
| [Flamingo: a Visual Language Model for Few-Shot Learning](https://proceedings.neurips.cc/paper_files/paper/2022/hash/960a172bc7fbf0177ccccbb411a7d800-Abstract-Conference.html) | NeurIPS 2022, A* | Связка замороженных vision/LM-компонентов, few-shot через interleaved контекст; читать архитектурно, не пытаться обучать |
| [BLIP-2](https://proceedings.mlr.press/v202/li23q.html) | ICML 2023, A* | Замороженные энкодер и LLM плюс обучаемый Q-Former; хороший пример parameter-efficient bridge |
| [Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://openaccess.thecvf.com/content/ICCV2023/html/Zhai_Sigmoid_Loss_for_Language_Image_Pre-Training_ICCV_2023_paper.html) | ICCV 2023, A* | Сравнение sigmoid и global softmax contrastive objective, влияние batch size |
| [Segment Anything](https://openaccess.thecvf.com/content/ICCV2023/html/Kirillov_Segment_Anything_ICCV_2023_paper.html) | ICCV 2023, A* | Promptable segmentation, data engine, zero-shot перенос и границы постановки |
| [Grounding DINO](https://eccv.ecva.net/virtual/2024/poster/395) | ECCV 2024, A* | Связь текста и detector queries, open-set detection, referring expressions |
| [SAM 2: Segment Anything in Images and Videos](https://proceedings.iclr.cc/paper_files/paper/2025/file/45c1f6a8cbf2da59ebf2c802b4f742cd-Paper-Conference.pdf) | ICLR 2025, A* | Streaming memory и unified image/video segmentation |
| [SAM 3: Segment Anything with Concepts](https://iclr.cc/virtual/2026/poster/10007181) | ICLR 2026, A* | Тренд 2026: promptable concept segmentation; пока использовать как семинар, не как стабильную лабораторную основу |

### Воспроизводимая лабораторная A1: zero-shot и языковой сдвиг

**Основной режим, CPU:**

- 100–500 изображений, 5–10 классов;
- замороженный CLIP/OpenCLIP или SigLIP-base;
- batch 8, изображения 224 px;
- 1 английский, 1 русский и 3–5 ensemble-шаблонов на класс;
- метрики: top-1, macro-F1, balanced accuracy, confusion matrix;
- обязательный bootstrap 95% CI по изображениям;
- один и тот же кеш image embeddings используется всеми вариантами.

**Ограниченный GPU (4–8 GB):**

- до 5 тыс. изображений;
- linear probe поверх замороженных embeddings;
- сравнение zero-shot, k-NN и linear probe на одном split;
- 3 seed для probe, но embedding извлекается один раз.

**Научный вопрос:** является ли выигрыш нового prompt статистически различимым и переносится ли он на все классы, а не только на среднее?

**Не делать:** не использовать облачный закрытый VLM как единственную реализацию; не посылать студенческие/персональные изображения во внешний API.

### Воспроизводимая лабораторная A2: promptable segmentation

- 5–20 изображений с малыми ground-truth masks;
- SAM ViT-B или компактный EfficientSAM;
- prompts: центр объекта, случайная положительная точка, box, positive+negative points;
- метрики: IoU/Dice, число взаимодействий до достижения IoU 0.8, время encoder и decoder отдельно;
- CPU smoke — 3–5 изображений; GPU — весь малый набор;
- фиксировать координаты prompts в JSON, а не кликать вручную при итоговом прогоне.

### Код, веса и данные

- [Официальный SAM](https://github.com/facebookresearch/segment-anything): код и модель заявлены под Apache-2.0; **SA-1B отдельно** требует принятия SA-1B Dataset Research License. Не помещать SA-1B в репозиторий курса.
- [Официальный Grounding DINO](https://github.com/IDEA-Research/GroundingDINO): репозиторий помечен Apache-2.0.
- [Big Vision, официальный код SigLIP](https://github.com/google-research/big_vision): Apache-2.0. Использованный WebLI не опубликован как воспроизводимый учебный датасет, поэтому курс воспроизводит inference/objective, но не заявляет повторение pretraining.
- [OpenCLIP](https://github.com/mlfoundations/open_clip): удобен для inference и сравнений; условия конкретного checkpoint и исходного датасета проверяются отдельно.
- [EfficientSAM](https://github.com/yformer/EfficientSAM): использовать только после фиксации commit и записи лицензии в `THIRD_PARTY.yml`.
- Для открытого smoke-набора предпочтительнее подготовить 20–50 собственных/CC0 изображений с явным `sources.csv`. COCO нельзя описывать одной общей лицензией: лицензия аннотаций и лицензии исходных Flickr-изображений различаются.

---

## 5. Тема B. Self-supervised learning и masked prediction

### Зачем включать

SSL дает общий язык для DINO/DINOv2-подобных признаков, MAE, data2vec, I-JEPA и VideoMAE. Главный учебный результат — не «получить ImageNet SOTA», а понять, **какое представление индуцирует objective**, как его проверять и как отделять качество pretraining от мощности downstream classifier.

### Учебные результаты

- различать contrastive, distillation, reconstruction и latent-prediction objectives;
- объяснить collapse и роль teacher/EMA, centering, masking;
- выполнить k-NN и linear evaluation без утечки test;
- сравнить frozen и fine-tuned режимы при одинаковом бюджете;
- анализировать влияние masking ratio и augmentations;
- строить embedding-визуализации только как дополнение к численным метрикам.

### Обязательное чтение

| Работа | Площадка | Учебный акцент |
|---|---|---|
| [DINO: Emerging Properties in Self-Supervised Vision Transformers](https://openaccess.thecvf.com/content/ICCV2021/html/Caron_Emerging_Properties_in_Self-Supervised_Vision_Transformers_ICCV_2021_paper) | ICCV 2021, A* | Self-distillation, momentum teacher, emergent attention maps |
| [Masked Autoencoders Are Scalable Vision Learners](https://openaccess.thecvf.com/content/CVPR2022/html/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.html) | CVPR 2022, A* | Асимметричный encoder/decoder и высокий masking ratio |
| [iBOT](https://openreview.net/pdf?id=ydopy-e6Dg) | ICLR 2022, A* | Online tokenizer и masked self-distillation |
| [data2vec](https://proceedings.mlr.press/v162/baevski22a) | ICML 2022, A* | Предсказание contextualized latent targets единым методом для модальностей |
| [I-JEPA](https://openaccess.thecvf.com/content/CVPR2023/html/Assran_Self-Supervised_Learning_From_Images_With_a_Joint-Embedding_Predictive_Architecture_CVPR_2023_paper.html) | CVPR 2023, A* | Предсказание представлений target blocks, а не пикселей |

### Лабораторная B1: objective против downstream-качества

**CPU smoke:**

- CIFAR-10 или собственный CC0-набор, 1–5 тыс. изображений;
- encoder: ResNet-18 ширины 0.5 или tiny ViT;
- 1 эпоха toy SimCLR/MAE на 500–1000 изображениях;
- основная проверка — готовые DINO/MAE embeddings и один общий linear probe;
- сравнение: random init, supervised weights, DINO/MAE weights.

**GPU 6–8 GB:**

- 5–10 тыс. изображений, 10–20 эпох toy SSL;
- masking ratio 0.5/0.75/0.9 либо 2 силы augmentation;
- downstream subset неизменен;
- сохранять `split.json`, seed, checkpoint hash и CSV метрик.

**Метрики:** k-NN accuracy, linear-probe macro-F1, время извлечения embeddings, peak VRAM/RSS. Reconstruction loss нельзя выдавать за качество representation.

### Лицензионная оговорка

- [DINO code](https://github.com/facebookresearch/dino) — Apache-2.0.
- [MAE code](https://github.com/facebookresearch/mae) — **CC BY-NC 4.0**, то есть это не обычная permissive-лицензия. Для открытого образовательного курса допустимо ссылаться и запускать по условиям лицензии, но не следует бездумно копировать код в проект под MIT/Apache.
- Для каждого checkpoint нужно сохранять URL, SHA256, дату загрузки и условия использования. Лицензия репозитория не автоматически покрывает сторонние данные и веса.

---

## 6. Тема C. Detection и segmentation после DETR

### Учебные результаты

- сравнить anchor/NMS pipeline и set prediction;
- объяснить Hungarian matching, object queries и причины медленной сходимости раннего DETR;
- различать semantic, instance, panoptic и promptable segmentation;
- считать AP/mAP, IoU, Dice и boundary metrics без подбора по test;
- проводить open-vocabulary эксперимент с позитивными и негативными prompts;
- измерять robustness detector по доменам, а не только COCO-style average.

### Чтение

| Работа | Площадка | Роль |
|---|---|---|
| [DETR](https://www.ecva.net/papers/eccv_2020/papers_ECCV/html/832_ECCV_2020_paper.php) | ECCV 2020, тогда CORE A; ICORE2026 для ECCV — A* | Фундамент set prediction и отказ от NMS |
| [Mask2Former](https://openaccess.thecvf.com/content/CVPR2022/html/Cheng_Masked-Attention_Mask_Transformer_for_Universal_Image_Segmentation_CVPR_2022_paper.html) | CVPR 2022, A* | Унификация semantic/instance/panoptic через mask classification |
| [DINO: DETR with Improved DeNoising Anchor Boxes](https://openreview.net/pdf?id=3mRwyG5one) | ICLR 2023, A* | Denoising training и улучшенная инициализация queries |
| [RT-DETR](https://openaccess.thecvf.com/content/CVPR2024/html/Zhao_DETRs_Beat_YOLOs_on_Real-time_Object_Detection_CVPR_2024_paper.html) | CVPR 2024, A* | NMS-free real-time detector и честная связь архитектуры с latency |
| [Grounding DINO](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/06319.pdf) | ECCV 2024, A* | Open-set detector с текстом |
| [Efficient Track Anything](https://openaccess.thecvf.com/content/ICCV2025/html/Xiong_Efficient_Track_Anything_ICCV_2025_paper.html) | ICCV 2025, A* | Компактная promptable video segmentation |

### Лабораторная C1: NMS и set prediction

Поскольку обучение DETR с нуля не является разумным smoke-тестом:

- взять готовые компактные detector checkpoints;
- 20–100 изображений с 2–5 классами;
- сравнить классический detector до/после NMS при сетке IoU threshold;
- сопоставить с RT-DETR inference;
- для каждого режима измерить AP50, recall, дубликаты на объект, p50/p95 latency;
- разобрать crowd/occlusion и small-object failures.

**CPU smoke:** 10 изображений, модели с input 320–640 px.  
**GPU 6–8 GB:** до 500 изображений, batch 1/4, FP32/FP16.

Цель не доказать универсальное превосходство одного семейства, а показать, что NMS threshold является частью алгоритма и что FPS из статьи не переносится между устройствами.

### Лабораторная C2: open vocabulary

- 10 изображений и заранее заданные списки positive/near-negative prompts;
- Grounding DINO tiny/base только в inference;
- метрики отдельно для известных, перефразированных и отсутствующих категорий;
- зафиксировать text threshold и box threshold до просмотра test;
- выполнить анализ ложных срабатываний на атрибутах и частях объектов.

### Репозитории и данные

- [Mask2Former](https://github.com/facebookresearch/Mask2Former): основная часть MIT, но есть заимствованные компоненты MIT/Apache; сохранять notices.
- [RT-DETR](https://github.com/lyuwenyu/RT-DETR): Apache-2.0; компактный R18 — предпочтительный full-profile.
- [Grounding DINO](https://github.com/IDEA-Research/GroundingDINO): Apache-2.0, но полный training mix неоднороден и не воспроизводим только из этого repo.
- COCO annotations распространяются под CC BY 4.0, а исходные изображения сохраняют индивидуальные Flickr-лицензии. ADE20K, Cityscapes и Objects365 требуют отдельной проверки/регистрации; не зеркалировать их в Git.

---

## 7. Тема D. Diffusion и генеративное зрение

### Учебные результаты

- вывести forward noising и denoising objective DDPM;
- объяснить связь score prediction, noise prediction и sampling schedule;
- сравнить pixel-space и latent diffusion;
- измерить качество–скорость при разном числе шагов;
- объяснить classifier-free guidance и ее влияние на diversity;
- оценивать генерацию не по нескольким «красивым» примерам;
- обсуждать memorization, происхождение данных, авторские права и недопустимость synthetic test leakage.

### Чтение

| Работа | Площадка | Учебный акцент |
|---|---|---|
| [Denoising Diffusion Probabilistic Models](https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html) | NeurIPS 2020, A* | Базовый probabilistic formulation |
| [Latent Diffusion Models](https://openaccess.thecvf.com/content/CVPR2022/html/Rombach_High-Resolution_Image_Synthesis_With_Latent_Diffusion_Models_CVPR_2022_paper.html) | CVPR 2022, A* | Компромисс detail–compute и conditioning через cross-attention |
| [Diffusion Transformers (DiT)](https://openaccess.thecvf.com/content/ICCV2023/html/Peebles_Scalable_Diffusion_Models_with_Transformers_ICCV_2023_paper.html) | ICCV 2023, A* | Transformer backbone и scaling с compute |
| [Consistency Models](https://proceedings.mlr.press/v202/song23a.html) | ICML 2023, A* | One/few-step generation и distillation |
| [DreamBooth](https://openaccess.thecvf.com/content/CVPR2023/papers/Ruiz_DreamBooth_Fine_Tuning_Text-to-Image_Diffusion_Models_for_Subject-Driven_Generation_CVPR_2023_paper.pdf) | CVPR 2023, A* | Персонализация и риск overfitting/memorization |

### Лабораторная D1: шаги sampling как контролируемый фактор

**CPU smoke, обязательный:**

- маленький DDPM для MNIST/Fashion-MNIST либо готовый `ddpm-cifar10-32`;
- 16–64 samples, одинаковые initial noise tensors;
- 10/25/50/100 шагов;
- wall time, samples/sec, diversity proxy и небольшой FID/KID только с явной оговоркой о высокой дисперсии малого sample;
- визуальная сетка генерируется из фиксированного списка seed.

**GPU 6–8 GB:**

- toy U-Net, 5–20 тыс. train samples, 10–30 эпох;
- абляция schedule или guidance;
- не обучать Stable Diffusion с нуля.

Рекомендуемый стек — [Hugging Face diffusers](https://github.com/huggingface/diffusers) с фиксацией версии и model card. Код библиотеки Apache-2.0, но лицензия конкретных весов проверяется отдельно. [Официальный latent-diffusion repo](https://github.com/CompVis/latent-diffusion) полезен как reference implementation, а не как основное студенческое окружение.

### Что считать корректным выводом

Нельзя делать вывод «модель A лучше» по 16 картинкам. Допустимый вывод для smoke: «при фиксированных seed сокращение числа шагов уменьшило время в X раз и изменило выбранные метрики/артефакты в наблюдаемом диапазоне». Для серьезного проекта требуются достаточный sample size, доверительные интервалы и независимый real test set.

---

## 8. Тема E. Эффективный инференс и измерение системной стоимости

### Почему это не факультатив

FLOPs, число параметров и FPS из статьи не взаимозаменяемы. Реальная задержка зависит от batch, разрешения, precision, warm-up, числа потоков CPU, версии runtime и устройства. Студент должен уметь не только экспортировать модель, но и спроектировать корректный benchmark.

### Учебные результаты

- различать parameter count, MACs/FLOPs, latency, throughput, RSS и peak VRAM;
- объяснить distillation, pruning, quantization и structural re-parameterization;
- экспортировать модель в ONNX и проверить численную эквивалентность;
- измерять p50/p95, а не единичный «лучший» запуск;
- строить Pareto frontier качество–задержка–размер;
- не сравнивать FP16 GPU с FP32 CPU как свойство архитектуры.

### Чтение

| Работа | Площадка | Что проверять |
|---|---|---|
| [DeiT](https://proceedings.mlr.press/v139/touvron21a) | ICML 2021, A* | Distillation token и data-efficient training |
| [EfficientViT: Lightweight Multi-Scale Attention](https://openaccess.thecvf.com/content/ICCV2023/html/Cai_EfficientViT_Lightweight_Multi-Scale_Attention_for_High-Resolution_Dense_Prediction_ICCV_2023_paper.html) | ICCV 2023, A* | Hardware-efficient операции для dense prediction |
| [I-ViT: Integer-only Quantization](https://openaccess.thecvf.com/content/ICCV2023/html/Li_I-ViT_Integer-only_Quantization_for_Efficient_Vision_Transformer_Inference_ICCV_2023_paper.html) | ICCV 2023, A* | Ограничения integer-only inference для nonlinear ViT blocks |
| [RepViT](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_RepViT_Revisiting_Mobile_CNN_From_ViT_Perspective_CVPR_2024_paper.html) | CVPR 2024, A* | Почему хорошо спроектированный CNN остается конкурентен на mobile |
| [EfficientSAM](https://openaccess.thecvf.com/content/CVPR2024/html/Xiong_EfficientSAM_Leveraged_Masked_Image_Pretraining_for_Efficient_Segment_Anything_CVPR_2024_paper.html) | CVPR 2024, A* | Distillation/предобучение компактного encoder для promptable task |

### Лабораторная E1: честный ONNX benchmark

**Модели:** MobileNetV3 / RepViT / EfficientViT малого размера.  
**Данные:** 100–500 изображений; один фиксированный preprocessing.

Обязательный протокол:

1. eager PyTorch FP32 как baseline;
2. экспорт ONNX с фиксированной и, отдельно, dynamic batch shape;
3. проверка `max_abs_diff` logits и совпадения top-1;
4. 20–50 warm-up итераций;
5. не менее 200 timed итераций;
6. batch 1 и один дополнительный batch;
7. фиксированные `intra_op_num_threads` и `inter_op_num_threads`;
8. p50, p95, throughput, RSS, размер файла;
9. accuracy до/после оптимизации на одной и той же подвыборке.

**CPU:** основной обязательный режим.  
**GPU:** опционально FP16 и TensorRT, но в отдельной таблице.

Результат — Pareto-график и вывод в границах конкретного hardware/software stack. Репозиторий [MIT HAN Lab EfficientViT](https://github.com/mit-han-lab/efficientvit) заявлен под Apache-2.0; [FastViT](https://github.com/apple/ml-fastvit) использует собственный лицензионный текст Apple, поэтому его `LICENSE` и `ACKNOWLEDGEMENTS` нужно сохранять.

---

## 9. Тема F. Robust evaluation, OOD и калибровка

### Главный методический вывод

Robustness должна быть не одной лекцией в конце, а обязательным слоем каждой лабораторной. Современная модель может повысить IID accuracy и одновременно сохранить большой провал на редких условиях, natural shift или отдельных группах.

### Учебные результаты

- различать corruption, perturbation, adversarial и natural distribution shift;
- не обучаться на test corruptions;
- считать ECE/NLL/Brier score вместе с accuracy;
- строить performance-by-severity и subgroup breakdown;
- использовать AUROC/FPR95 для OOD detection и понимать их ограничения;
- применять paired bootstrap и несколько seed;
- регистрировать failure taxonomy до чтения test.

### Чтение

| Работа | Площадка | Роль |
|---|---|---|
| [ImageNet-C/P: Benchmarking Neural Network Robustness](https://openreview.net/pdf?id=HJz6tiCqYm) | ICLR 2019, A* | Стандартизованные common corruptions и severity |
| [ObjectNet](https://proceedings.neurips.cc/paper/2019/hash/97af07a14cacba681feacf3012730892-Abstract.html) | NeurIPS 2019, A* | Контролируемые background/viewpoint/rotation shifts |
| [WILDS](https://proceedings.mlr.press/v139/koh21a) | ICML 2021, A* | Реальные сдвиги по месту, времени, устройству и организации |
| [RobustBench](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/a3c65c2974270fd093ee8a9bf8ae7d0b-Abstract-round2.html) | NeurIPS Datasets & Benchmarks 2021, A* | Стандартизация adversarial evaluation |
| [COCO-O](https://openaccess.thecvf.com/content/ICCV2023/html/Mao_COCO-O_A_Benchmark_for_Object_Detectors_under_Natural_Distribution_Shifts_ICCV_2023_paper.html) | ICCV 2023, A* | Natural OOD для detector, а не только classifier |
| [DataComp](https://proceedings.neurips.cc/paper_files/paper/2023/hash/56332d41d55ad7ad8024aac625881be7-Abstract-Datasets_and_Benchmarks.html) | NeurIPS 2023, A* | Dataset curation как измеряемая часть multimodal pipeline |
| [COUNTS](https://openaccess.thecvf.com/content/CVPR2025/html/Li_COUNTS_Benchmarking_Object_Detectors_and_Multimodal_Large_Language_Models_under_CVPR_2025_paper.html) | CVPR 2025, A* | Fine-grained OOD для detector/grounding, 14 типов natural shift |

### Лабораторная F1: corruption + calibration

**CPU:**

- CIFAR-10-C subset либо локально сгенерированные blur/noise/JPEG/brightness;
- 500–2000 примеров, 4–5 corruptions × 3 severity;
- pretrained ResNet-18/MobileNet;
- accuracy, macro-F1, NLL, ECE, confidence–accuracy gap;
- temperature scaling обучается **только на validation**.

**GPU 4–8 GB:**

- добавить FGSM/PGD на 200–1000 примерах;
- clean и corrupted/adversarial результаты держать отдельно;
- adaptive attack — обязательная оговорка при оценке защиты.

**Вариант без данных/GPU:** преподаватель публикует logits, labels и group metadata; студенты полностью воспроизводят метрики, bootstrap CI и calibration. Это полезнее, чем исключать robustness из-за размера ImageNet.

### Инструменты и лицензии

- [RobustBench](https://github.com/RobustBench/robustbench) — официальный benchmark/repo.
- [OpenOOD](https://github.com/Jingkang50/OpenOOD) — MIT, но лицензии подключаемых датасетов независимы.
- [ImageNet-X](https://github.com/facebookresearch/imagenetx) — BSD-3-Clause для кода/аннотаций; базовые ImageNet images остаются под условиями ImageNet.
- [easyrobust / COCO-O](https://github.com/alibaba/easyrobust/tree/main/benchmarks/coco_o) — использовать через manifest, не зеркалировать данные автоматически.

---

## 10. Тема G. Синтетические данные

### Чему следует учить

Синтетические данные дают точную разметку и контроль факторов, но не отменяют domain gap. Курс должен учить проводить эксперимент `real-only / synthetic-only / mixed`, а также хранить provenance генератора, assets, prompts и seed.

### Чтение

| Работа | Площадка | Что переносится в курс |
|---|---|---|
| [Kubric](https://openaccess.thecvf.com/content/CVPR2022/html/Greff_Kubric_A_Scalable_Dataset_Generator_CVPR_2022_paper.html) | CVPR 2022, A* | Программируемая генерация сцен и богатой ground truth |
| [Infinigen](https://openaccess.thecvf.com/content/CVPR2023/html/Raistrick_Infinite_Photorealistic_Worlds_Using_Procedural_Generation_CVPR_2023_paper.html) | CVPR 2023, A* | Полностью процедурные 3D-миры без внешних assets |
| [StableRep](https://proceedings.neurips.cc/paper_files/paper/2023/hash/971f1e59cd956cc094da4e2f78c6ea7c-Abstract-Conference.html) | NeurIPS 2023, A* | Synthetic positives для representation learning |
| [Learning Vision from Models Rivals Learning Vision from Data](https://openaccess.thecvf.com/content/CVPR2024/html/Tian_Learning_Vision_from_Models_Rivals_Learning_Vision_from_Data_CVPR_2024_paper.html) | CVPR 2024, A* | Синтетический pretraining как исследовательская гипотеза, а не универсальная замена real data |

### Лабораторная G1: domain randomization

**CPU smoke без Blender:**

- генератор простых 2D-сцен (формы, текстуры, фон, occlusion);
- автоматически получить class/mask/bbox;
- 1–5 тыс. изображений генерируются по seed;
- обучить малый CNN/UNet в трех режимах: synthetic-only, small-real-only, mixed;
- test состоит только из независимых real/hand-crafted изображений;
- изменять один фактор: диапазон фона, освещения или occlusion.

**Расширение с Blender/Kubric:**

- 30–100 низкоразрешенных сцен, headless render;
- сохранить Blender/Kubric version, asset IDs и scene configs;
- CPU render допустим как ночной/pre-generated этап; GPU не обязателен для обучения маленькой модели.

**Метрики:** target real mIoU/accuracy, gap synthetic→real, performance по фактору, стоимость генерации. Запрещено включать generated test views из тех же scene seeds.

### Лицензии и provenance

- [Kubric](https://github.com/google-research/kubric) — официальный framework; лицензии внешних assets учитываются отдельно.
- [Infinigen](https://github.com/princeton-vl/infinigen) — процедурный подход уменьшает зависимость от внешних assets, но `LICENSE` фиксируется вместе с commit.
- [StableRep/SynCLR code](https://github.com/google-research/syn-rep-learn) — Apache-2.0; prompts, генеративные веса и outputs имеют отдельные условия.
- LAION metadata под открытой лицензией не превращает изображения по URL в свободно лицензированный датасет.
- Если в официальном repo нет явной лицензии, его код нельзя копировать в открытый курс по умолчанию. Допустимы ссылка на статью и собственная реализация идеи.

---

## 11. Тема H. 3D vision и видео

Эта тема уместна как один обязательный компактный модуль и один проектный трек. Полное обучение 3D foundation model или video transformer не является воспроизводимым обязательным заданием.

### Чтение по 3D

| Работа | Площадка | Учебный акцент |
|---|---|---|
| [NeRF](https://www.ecva.net/papers/eccv_2020/papers_ECCV/html/1473_ECCV_2020_paper.php) | ECCV 2020 | Differentiable volume rendering и implicit scene representation |
| [Instant-NGP](https://doi.org/10.1145/3528223.3530127) | SIGGRAPH/TOG 2022, SIGGRAPH A* | Multiresolution hash encoding и реальная hardware-aware реализация |
| [3D Gaussian Splatting](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) | SIGGRAPH/TOG 2023, SIGGRAPH A* | Explicit primitives и real-time rendering |
| [DUSt3R](https://openaccess.thecvf.com/content/CVPR2024/papers/Wang_DUSt3R_Geometric_3D_Vision_Made_Easy_CVPR_2024_paper.pdf) | CVPR 2024, A* | Feed-forward pointmaps и унификация геометрических задач |
| [VGGT](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html) | CVPR 2025, A* | Единый feed-forward прогноз камер, depth, pointmaps и tracks |
| [QVGGT](https://openaccess.thecvf.com/content/CVPR2026/html/Pan_QVGGT_Post-Training_Quantized_Visual_Geometry_Grounded_Transformer_CVPR_2026_paper.html) | CVPR 2026, A* | Тренд: mixed-precision quantization 3D foundation model; семинар/watchlist |

### Чтение по видео

| Работа | Площадка | Учебный акцент |
|---|---|---|
| [VideoMAE](https://proceedings.neurips.cc/paper_files/paper/2022/hash/416f9cb3276121c42eebb86352a4354a-Abstract-Conference.html) | NeurIPS 2022, A* | Tube masking 90–95% и temporal redundancy |
| [XMem](https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/568_ECCV_2022_paper.php) | ECCV 2022, A* | Несколько типов memory для long video segmentation |
| [CoTracker](https://eccv.ecva.net/virtual/2024/poster/1074) | ECCV 2024, A* | Совместная оценка множества point tracks |
| [SAM 2](https://proceedings.iclr.cc/paper_files/paper/2025/file/45c1f6a8cbf2da59ebf2c802b4f742cd-Paper-Conference.pdf) | ICLR 2025, A* | Streaming memory для promptable video segmentation |

### Лабораторная H1: две фотографии → 3D

**CPU-обязательная часть:**

- две синтетические/собственные пары с известной камерой;
- оценка correspondences, fundamental/essential matrix, triangulation;
- reprojection error и отказ при малом baseline/плохом overlap;
- готовые DUSt3R outputs можно анализировать без запуска модели.

**GPU 8 GB, опционально:**

- DUSt3R на 2–4 изображениях 512 px;
- сравнить overlap/resolution;
- depth/pointmap confidence и согласованность reprojection.

[DUSt3R code](https://github.com/naver/dust3r) — CC BY-NC-SA 4.0; training datasets скачиваются у первоисточников. [3D Gaussian Splatting code](https://github.com/graphdeco-inria/gaussian-splatting) имеет собственные research/evaluation non-commercial условия, поэтому 3DGS нельзя вендорить как permissive dependency.

### Лабораторная H2: temporal memory

- собственный или CC0-клип 5–15 секунд, 240–480p;
- 20–50 кадров, одна стартовая маска/точки;
- сравнить frame-independent propagation и XMem/CoTracker/компактный SAM2-like inference;
- метрики: J&F/IoU по кадрам, trajectory error, survival после occlusion, время/кадр, рост памяти;
- CPU smoke — 10–20 кадров и мало точек; GPU — полный короткий клип.

Данные Kinetics/YouTube и многие video benchmarks нельзя надежно зеркалировать: ссылки исчезают, а условия исходных платформ сохраняются. Для курса лучше иметь маленький собственный CC0/generated video pack с checksums.

---

## 12. Рекомендуемое обязательное ядро лабораторных

Ниже — минимальный набор, который одновременно отражает современную область и остается передаваемым другому преподавателю.

| № | Лабораторная | Обязательный CPU smoke | Расширение на малой GPU | Основной результат |
|---:|---|---|---|---|
| 1 | VLM zero-shot и язык prompt | 100–500 изображений, кеш embeddings | linear probe до 5 тыс. | prompt sensitivity, Recall@K/F1, CI |
| 2 | SSL representations | frozen DINO/MAE + k-NN/probe | toy MAE/SSL 10–20 эпох | objective → downstream |
| 3 | Detection после NMS | 10–50 изображений | RT-DETR + до 500 изображений | AP/recall/latency |
| 4 | Promptable segmentation | 3–10 изображений | SAM/EfficientSAM на 20–50 | IoU на тип prompt и interaction cost |
| 5 | Diffusion sampling | tiny/pretrained 32×32 | toy training | качество–число шагов–время |
| 6 | ONNX/quantization benchmark | обязателен полностью | FP16/TensorRT опционально | Pareto quality–latency–size |
| 7 | Robustness/calibration | logits или CIFAR-C subset | FGSM/PGD | severity curves, ECE, CI |
| 8 | Synthetic-to-real | 2D procedural generator | Kubric/Blender | real/synthetic/mixed |
| 9 | 3D или video mini-project | classical geometry / готовые outputs | DUSt3R, CoTracker, XMem | failure-aware system analysis |

Если учебного времени недостаточно, лабораторные 3 и 4 можно объединить в pipeline `Grounding DINO/RT-DETR → box prompt → SAM`, но оценивать detection и segmentation следует раздельно.

### Что оставить только проектным треком

- полное pretraining VLM, DINOv2/MAE-B, VideoMAE;
- fine-tuning больших LLM/VLM;
- Stable Diffusion training и DreamBooth на персональных лицах;
- 3DGS/NeRF benchmark-scale training;
- полный SA-1B, ImageNet, Objects365, Kinetics;
- сравнение закрытых API как основная научная работа.

Причина — не «слишком сложно», а невозможность гарантировать одинаковый доступ к compute, данным и сервисам.

---

## 13. Единый контракт воспроизводимости для каждой лабораторной

Каждая работа должна иметь два профиля:

### `smoke`

- CPU-first, без обязательного CUDA;
- не более 10–15 минут после установки;
- маленькие данные с checksum;
- полный проход от загрузки до `results.json`;
- используется в CI хотя бы на одном примере;
- не требует аккаунта, API key или ручного клика.

### `full`

- одна GPU 6–8 GB либо явно помеченная более высокая потребность;
- время и VRAM указаны как измеренный диапазон на эталонной машине;
- тот же код и config schema, меняются только параметры;
- CPU fallback сохраняет смысл эксперимента, даже если не достигает paper-scale качества.

### Минимальный набор файлов

```text
lab_x/
├── README.md                  # цель, бюджет, команды, ожидаемые артефакты
├── configs/
│   ├── smoke.yaml
│   └── full.yaml
├── data/
│   ├── README.md              # откуда брать данные и почему их нельзя/можно хранить
│   ├── manifest.csv           # url/source/license/checksum/split
│   └── tiny/                  # только если перераспространение разрешено
├── src/
├── tests/
│   ├── test_shapes.py
│   ├── test_metrics.py
│   └── test_smoke.py
├── expected/
│   └── smoke_schema.json
└── THIRD_PARTY.yml
```

### Обязательные поля одного запуска

```json
{
  "experiment_id": "uuid-or-stable-name",
  "git_commit": "...",
  "config_sha256": "...",
  "data_manifest_sha256": "...",
  "model_id": "...",
  "weights_sha256": "...",
  "seed": 42,
  "device": "cpu",
  "precision": "fp32",
  "library_versions": {},
  "metrics": {},
  "wall_time_s": 0.0,
  "peak_rss_mb": 0.0,
  "status": "ok"
}
```

### Научный протокол

1. Split фиксируется до эксперимента.
2. Test не используется для выбора prompt, threshold, epoch или temperature.
3. Baseline запускается тем же evaluator.
4. Меняется один основной фактор.
5. Для stochastic training — не менее 3 seed либо честная оговорка о smoke-only.
6. Для сравнений по объектам/изображениям — paired bootstrap CI.
7. Наряду со средним приводится breakdown по классам/условиям.
8. Неудачные случаи выбираются по фиксированному правилу, а не вручную.
9. Время включает четко указанные стадии; preprocessing и data transfer не прячутся.
10. Вывод не выходит за пределы данных, устройства и sample size.

---

## 14. Политика лицензий и внешних ресурсов

Этот раздел не является юридической консультацией, но задает безопасную инженерную дисциплину.

### Три независимых объекта

Для любого внешнего метода отдельно проверяются:

1. **код**;
2. **веса**;
3. **данные/изображения/аннотации**.

Наличие `Apache-2.0` в GitHub repository не означает, что все weights и datasets автоматически Apache-2.0.

### Светофор включения

| Статус | Условия | Действие |
|---|---|---|
| Зеленый | Явная permissive license; redistribution разрешен | Можно зависеть/вендорить с notices |
| Желтый | CC BY-NC, research-only, custom data license, регистрация | Не вендорить без необходимости; downloader + принятие условий |
| Красный | Нет LICENSE, неизвестное происхождение, запрет redistribution | Только ссылка/цитирование или собственная реализация |

### Примеры, критичные для этого курса

| Ресурс | Проверенный статус | Практическое решение |
|---|---|---|
| SAM code/model | Apache-2.0 | Можно использовать; сохранить notice |
| SA-1B | отдельная Research License | Только downloader/инструкция; не зеркалировать |
| DINO | Apache-2.0 | Допустим как dependency/reference |
| MAE | CC BY-NC 4.0 | Не смешивать как будто это MIT/Apache |
| Grounding DINO | Apache-2.0 | Допустим; training data все равно неоднородны |
| Mask2Former | преимущественно MIT, есть заимствованные части | Проверить notices конкретного commit |
| RT-DETR | Apache-2.0 | Хороший кандидат для обязательной работы |
| latent-diffusion | MIT | Веса/LAION отдельно |
| DiT | CC BY-NC | Reference/inference по условиям |
| consistency_models | MIT | Хороший компактный учебный reference |
| OpenOOD | MIT | Датасеты отдельно |
| DUSt3R | CC BY-NC-SA 4.0 | Опциональный некоммерческий project track |
| 3DGS official | custom research/evaluation, non-commercial | Не считать open-source permissive |
| VideoMAE/CoTracker official | CC BY-NC в основной части | Не вендорить под несовместимой лицензией |

`THIRD_PARTY.yml` должен содержать: имя, upstream URL, commit/tag, license SPDX или `LicenseRef-*`, scope (`code|weights|data`), redistribution, required notice, download date, checksum.

---

## 15. Данные, которые реально выдержат несколько потоков студентов

### Предпочтительный порядок

1. маленький собственный CC0/CC BY набор курса;
2. процедурно генерируемые данные;
3. downloader к официальному источнику с checksum;
4. institutional/full dataset как необязательный профиль;
5. закрытый API — только демонстрация, не условие сдачи.

### Обязательные документы

- `DATA_CARD.md`: назначение, сбор, состав, ограничения, риски;
- `manifest.csv`: источник каждого файла, лицензия, hash;
- `splits/v1.json`: неизменяемое разбиение;
- `download.py --verify-only`;
- `make_tiny.py`: детерминированная подвыборка, если лицензия допускает;
- список удаленных/недоступных URL и fallback.

### Что нельзя обещать

- Полную воспроизводимость pretraining CLIP/SigLIP, если WebLI/исходная web-выборка закрыта.
- Полную воспроизводимость DINOv2 pretraining, если LVD-142M не опубликован.
- Стабильность Kinetics/YouTube downloads.
- Единую лицензию для COCO images.
- Право публиковать outputs генеративной модели только потому, что код генератора открыт.

---

## 16. Оценивание студенческой работы

Предлагаемая рубрика на 100 баллов:

| Компонент | Баллы |
|---|---:|
| Выполнимость `smoke` из чистого клона | 15 |
| Корректность данных и split | 10 |
| Baseline и контролируемый фактор | 15 |
| Корректность метрик и evaluator | 15 |
| Reproducibility artifacts/config/checksums | 15 |
| Robustness или subgroup analysis | 10 |
| Анализ ошибок и границ вывода | 15 |
| Лицензии/provenance/этика | 5 |

Нельзя ставить основную часть баллов за абсолютное значение leaderboard metric: это стимулирует compute race, утечку test и невоспроизводимые трюки. Качество модели оценивается относительно заранее заданного baseline при фиксированном бюджете.

---

## 17. Рекомендуемая последовательность лекций и семинаров

1. **Классическая база:** imaging, фильтрация, features, geometry, CNN.
2. **ViT и representation learning:** DINO, MAE, latent prediction.
3. **VLM:** CLIP/SigLIP, retrieval, русский prompt.
4. **Detection:** NMS, DETR, DINO, RT-DETR.
5. **Segmentation:** Mask2Former, SAM, prompt interaction.
6. **Generative vision:** DDPM, latent diffusion, DiT, consistency.
7. **Efficient inference:** distillation, quantization, ONNX, Pareto.
8. **Robust evaluation:** shift, calibration, confidence, failure taxonomy.
9. **Synthetic data:** procedural generation, provenance, sim-to-real.
10. **Video/3D:** temporal memory, tracking, NeRF/3DGS, DUSt3R/VGGT.
11. **Responsible CV:** privacy, licensing, bias, synthetic media.
12. **Reproducible capstone:** preregistered hypothesis, model/data cards, release.

Для русскоязычности следует переводить объяснение и задания, но сохранять оригинальные английские термины при первом употреблении: «сдвиг распределения (distribution shift)», «замороженный энкодер (frozen encoder)», «поиск соответствий (matching)». Названия статей, APIs и метрик не переводятся.

---

## 18. Политика актуализации 2026+

Стабильный курс не должен менять обязательный стек каждую неделю. Нужны три кольца:

### Stable

Работа опубликована, официальный код имеет лицензию, есть фиксированный checkpoint, smoke прошел в CI. Используется в обязательной лабораторной.

### Candidate

Работа опубликована на A/A*, код есть, но еще не проверены license/data/compute или нет стабильного релиза. Используется на семинаре/в проекте.

### Watchlist

Новая статья 2026 года или preprint; важна концептуально, но не влияет на оценивание.

На срезе 2026 года:

- **Stable/Candidate:** SAM 2, EfficientTAM, VGGT, COUNTS — после локальной проверки checkpoint и бюджета;
- **Watchlist:** SAM 3, QVGGT, OmniVGGT и другие CVPR/ICLR 2026 работы;
- DINOv2/DINOv3 допустимы как background/current baseline, но в отчете нужно честно указывать, если конкретная работа опубликована не на рассматриваемой CORE-конференции.

Обновление рекомендуется раз в семестр:

1. проверить ICORE source/year;
2. проверить upstream release и license diff;
3. прогнать smoke на чистой машине;
4. обновить model/data checksum;
5. добавить не более одной новой обязательной идеи;
6. сохранить прежний семестровый tag.

---

## 19. Приоритет внедрения

### P0 — необходимо до следующего публичного релиза

- единый CPU `smoke` для каждой лабораторной;
- manifests/checksums и лицензионный реестр;
- VLM zero-shot с русским/английским prompt;
- frozen-feature SSL lab;
- RT-DETR/SAM inference вместо пустых или гигантских training-заданий;
- единый latency benchmark;
- corruption/calibration block во всех deep-learning labs;
- фиксированный CC0/generated tiny dataset.

### P1 — в течение семестра

- toy diffusion с контролем числа шагов;
- synthetic-to-real lab;
- logits-only robustness package;
- 3D/video mini-project;
- model cards и data cards студентов;
- CI для notebook execution и metric tests.

### P2 — проектные треки

- Grounding DINO → pseudo-labeling → compact detector;
- EfficientSAM/SAM2 video;
- DUSt3R/VGGT;
- Kubric/Infinigen;
- 3DGS/NeRF;
- StableRep-подобный synthetic representation learning.

---

## 20. Официальные архивы для дальнейшего ежегодного обзора

- CVPR: [2022](https://openaccess.thecvf.com/CVPR2022?day=all), [2023](https://openaccess.thecvf.com/CVPR2023?day=all), [2024](https://openaccess.thecvf.com/CVPR2024?day=all), [2025](https://openaccess.thecvf.com/CVPR2025?day=all).
- ICCV: [2023](https://openaccess.thecvf.com/ICCV2023?day=all), [2025](https://openaccess.thecvf.com/ICCV2025?day=all). Конференция проходит по нечётным годам.
- ECCV: [архив ECVA](https://www.ecva.net/papers.php), [официальная страница 2024](https://eccv.ecva.net/Conferences/2024). Конференция проходит по чётным годам.
- NeurIPS: [общий архив](https://proceedings.neurips.cc/), [2022](https://proceedings.neurips.cc/paper_files/paper/2022), [2023](https://proceedings.neurips.cc/paper_files/paper/2023), [2024](https://proceedings.neurips.cc/paper_files/paper/2024), [2025](https://proceedings.neurips.cc/paper_files/paper/2025).
- ICML/PMLR: [2022, v162](https://proceedings.mlr.press/v162/), [2023, v202](https://proceedings.mlr.press/v202/), [2024, v235](https://proceedings.mlr.press/v235/), [2025, v267](https://proceedings.mlr.press/v267/).
- ICLR/OpenReview: [2022](https://openreview.net/group?id=ICLR.cc%2F2022%2FConference), [2023](https://openreview.net/group?id=ICLR.cc%2F2023%2FConference), [2024](https://openreview.net/group?id=ICLR.cc%2F2024%2FConference), [2025](https://openreview.net/group?id=ICLR.cc%2F2025%2FConference). Venue page содержит также reject/withdrawn; проверять статус Accept.
- AAAI: [официальный архив выпусков](https://ojs.aaai.org/index.php/AAAI/issue/archive). Год разбит на несколько issues, искать нужно по всему тому.
- SIGGRAPH: [2022](https://s2022.siggraph.org/program/technical-papers/), [2023](https://s2023.siggraph.org/program/technical-papers/index.html), [2024](https://s2024.siggraph.org/program/technical-papers/), [2025](https://s2025.siggraph.org/program/technical-papers/). Указывать фактический Journal или Conference track.

---

## Итоговый вывод

Курс мирового уровня в 2026 году должен учить не запускать очередную большую модель, а **формулировать проверяемый вопрос, воспроизводить pipeline на доступном профиле, измерять качество вместе со стоимостью и robustness, документировать происхождение данных и не выходить за границы лицензий и эксперимента**.

Оптимальная актуализация состоит из:

- foundation/VLM и promptable vision;
- SSL и frozen representations;
- DETR/open-vocabulary/promptable segmentation;
- diffusion с акцентом на sampling и оценивание;
- обязательного efficient inference;
- обязательного OOD/calibration слоя;
- synthetic-to-real;
- компактного 3D/video трека.

Такой дизайн сохраняет научную актуальность A/A* работ, но не делает успех студента функцией доступа к дорогой GPU или закрытому датасету.
