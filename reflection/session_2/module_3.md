# Module 3 — Transfer to Python
Question: Give at least three concrete reasons why a notebook alone is not enough here — what does moving this pipeline to src/air_quality/ actually solve that the notebook could not? What is a dataclass, and what does it save you from writing by hand for PipelineConfig? And what is the point of splitting responsibilities across data.py, features.py and evaluation.py instead of one long script?

## Answer

A notebook is useful for exploration, but it is not enough to maintain this pipeline reliably. First, cells can be run out of order and share persistent global state, so results may depend on hidden earlier executions. Functions in `src/air_quality/` make the execution order, inputs, and outputs explicit. Second, notebook code is difficult to reuse without copying cells; Python functions can be called from the workflow, scripts, and other projects. Third, testing notebook cells individually is awkward. Functions can be tested separately, while integration tests can verify that the full pipeline works. This also makes debugging and code review easier.

A dataclass is a Python class for holding structured data. For `PipelineConfig`, `@dataclass` generates the constructor and assigns its fields, so there is no need to write an `__init__` method by hand for settings such as the cities, columns, sample limit, and random seed. The `default_factory` for `columns` creates a fresh list for each configuration instance, avoiding accidental sharing of one mutable list.

The modules are split by responsibility: `data.py` loads, filters, samples, and cleans data; `features.py` creates model features and selects feature columns; `evaluation.py` fits and evaluates models and computes metrics. This keeps each part focused, easier to test, and easier to change independently. `workflows.py` assembles these functions in the order needed for the complete pipeline.

