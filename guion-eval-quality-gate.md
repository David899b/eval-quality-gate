# Guion — defensa de `eval-quality-gate`

Guía para presentar el proyecto a un evaluador técnico, a un hiring manager o a
un stakeholder de negocio. Pensado para leerse casi literal en una demo de 5–8
minutos.

---

## 0. Apertura (30 s) — liderar con el problema, no con la tecnología

> "Hoy, para saber si un sistema de IA mejoró o empeoró, la mayoría de los
> equipos mira un número promedio. Eso no es una decisión: no dice nada sobre el
> peor caso, ni sobre costo, latencia o cumplimiento. `eval-quality-gate` toma un
> golden set y devuelve **un comando, un veredicto y la evidencia adjunta**. Si
> el veredicto es `NO_GO`, CI bloquea el merge."

---

## 1. Demo (2 min) — el comando y el veredicto

```bash
python -m eval_quality_gate --golden data/golden_set.json \
  --outputs data/outputs.json --pricing data/pricing.json --report-dir reports
```

Salida real del run de referencia:

```
decision=REVIEW  pessimistic=0.705 base=0.823 optimistic=0.940
  - quality: REVIEW   safety: GO   cost: GO   latency: GO   governance: GO
```

**Qué decir:** "Cinco dimensiones, cinco gates. La decisión global es la peor
dimensión. Acá la calidad está en `REVIEW` (base 0.823 no alcanza el 0.85 del
caso pesimista) y todo lo demás está en `GO`. El resultado no es un número:
es una **banda** pesimista / base / optimista."

---

## 2. Análisis detrás del dato (2 min)

- **Base 0.823** = promedio de token-F1 por ejemplo sobre el golden set.
- **Pesimista 0.705 / optimista 0.940** = **intervalo de confianza del 95%** al
  estilo one-sided. La cifra es reproducible en cualquier máquina: el run de
  referencia no usa red ni claves.
- **Calidad en REVIEW** porque el umbral GO exige que el *pesimista* ≥ 0.85.
  Es deliberado: si el peor caso no es bueno, no es un `GO`.
- **Costo $0.0030 vs presupuesto $0.05** = tokens × precio publicado.
- **Latencia p95 1388 ms vs 2000 ms.** Ambos presupuestos explícitos.
- **Seguridad/gobernanza en GO:** sin frases prohibidas, sin eco de inyección,
> disclaimer presente, sin PII.

**Rigor estadístico:** el veredicto se calcula sobre la variabilidad del set, no
sobre un run único — la banda es un intervalo de confianza al 95%.

---

## 2. Evidencia detrás del dato (2 min)

- `reports/report.md` y `report.json`: por ejemplo, **qué check falló y por qué**
  (input, esperado, real, score). No solo un número.
- **Provenance:** el JSON del reporte incluye umbrales, política y cada medición.
- Los tests: `pytest --cov` con piso de 80% de branch; **property-based** con
  Hypothesis; **mutation testing** con mutmut; límites conocidos fijados con
  `xfail(strict=True)`.

---

## 3. Preguntas posibles (con respuestas fundamentadas)

- **"¿Por qué no usar promptfoo/DeepEval directamente?"**
  Son runners excelentes y el patrón es el mismo. Este repo implementa el
  patrón *como referencia* con cero dependencias (stdlib), para mostrar que
  entiendo el diseño — no para reemplazarlos. En producción elegiría la
  herramienta según el stack del cliente.
- **"Tu scorer es token-F1, es débil."**
  Correcto y **documentado**: no detecta negación ni orden de palabras. Está
  fijado con `xfail(strict=True)` para que ese límite no cambie en silencio; la
  registry permite enchufar similitud por embeddings o LLM-as-judge.
- **"¿Cómo evitas el sesgo del juez?"**
  Con el run de referencia determinista + banda de confianza + checks
  deterministas *antes* del scoring semántico. La calibración del juez es la
  siguiente suite (declarada como brecha).
- **"¿Esto es governance o compliance?"**
  Es **evidencia**, no política. Enforzo disclaimers y PII mecánicamente y
  genero model card y traceabilidad; la firma de política queda en legal/risk.
- **"¿Aguanta a escala?"**
  Cambiá el proveedor por uno real; el resto del pipeline no cambia. El control
  de costo (smoke en PR, full nightly) es parte del diseño del CI.

---

## 4. Bloqueadores / decisiones abiertas

| Tema | Estado | Depende de |
|---|---|---|
| Red-team OWASP completo + ASR | Fuera de alcance (suite siguiente) | Prioridad del equipo |
| Agentic evals (tool-calls) | Fuera de alcance | Framework del cliente (ADK/otros) |
| LLM-as-judge con calibración | Pendiente | Acceso a modelo + humanos para acuerdo |
| Fairness por subgrupos | Pendiente | Dataset con atributos protegidos |
| Monitoring/drift en prod | Fuera de un repo | Plataforma (Langfuse/Braintrust) |

**Próximo paso propuesto:** publicar `eval-quality-gate` como repo anónimo +
aprobar un **piloto** sobre una feature real (downside acotado: 1 comando, 1
semana) antes de invertir en la suite de red-teaming.
