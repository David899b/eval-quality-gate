# Cómo se comprueban y evalúan proyectos de ingeniería de IA

Documento de análisis (no de presentación comercial). Responde a tres preguntas:
(1) qué principios tienen las pruebas, (2) cómo una multinacional comprueba
proyectos y conocimientos, y (3) cómo lo hacen otros evaluadores / competidores.
Al final, qué cubre y qué no cubre `eval-quality-gate`, y qué se propone como
suite adicional.

---

## 1. Principios de las pruebas (qué separa a un senior de un junior)

1. **Probar comportamiento, no cobertura.** La cobertura es un piso, no una meta.
   Umbral de referencia: ≥80% global, **100% en rutas críticas**. ADVERTENCIA:
   100% de cobertura no implica calidad; un test que ejecuta una línea sin
   aserciones no prueba nada.
2. **Deterministas primero, semánticas después.** Barato y sin red (schema,
   frases prohibidas, JSON) antes de lo caro (similitud, LLM-as-judge). Un fallo
   duro cortocircuita el gate.
3. **Aislar lo no determinista.** Los tests unitarios mockean modelo y red; los
   tests de integración se marcan (`@pytest.mark.longrunning`) y corren aparte.
   El loop de desarrollo tiene que ser rápido.
4. **Property-based testing** (Hypothesis) para bordes que los ejemplos no ven:
   genera miles de entradas y reduce el fallo a un caso mínimo.
5. **`xfail(strict=True)` para límites conocidos.** Si un fallo documentado deja
   de fallar, **el build rompe**: así las regresiones silenciosas no se escapan.
6. **Mutation testing** (mutmut) para comprobar que los tests *muerden*. Que un
   test pase no significa que detecte un bug.
7. **Rigor estadístico.** Medir la varianza run-to-run y anclar toda cifra a un
   baseline medible. Nunca un solo número: banda pesimista / base / optimista.
8. **Reproducibilidad no negociable.** Si el evaluador no puede reproducir tu
   resultado, tu resultado no cuenta: semillas fijas, dependencias pinneadas,
   rutas relativas, comando único en el README.
9. **Provenance / trazabilidad.** Cada resultado ligado al run, al código y al
   dataset que lo produjeron (run IDs, artifacts).

---

## 2. Cómo comprueba una multinacional (rúbricas de take-home y de plataforma)

Las rúbricas de contratación de IA (ML Engineer / AI Evaluator, 2026) suelen
puntuar en **4 dimensiones ponderadas**:

| Dimensión | Peso típico | Ancla nivel alto |
|---|---|---|
| Problem framing & métricas | 20% | Conecta target, cortes y umbrales con la decisión de negocio |
| Modelado & calidad de código | 30% | Pipeline reproducible, testeado; explica por qué ese enfoque |
| Diseño de sistema / producción | 30% | Presupuestos explícitos (costo, latencia), observabilidad, rollback |
| Colaboración & comunicación | 20% | Expone incertidumbre, documenta trade-offs y riesgos |

Artefactos que **exigen** y que se puntúan por separado (para que un modelo
brillante en código inseguro no pase, y viceversa):

- README con supuestos, decisiones y qué cambiaría con más tiempo.
- **Pipeline reproducible** (preparación / inferencia / evaluación separadas).
- **Model card**: uso previsto, límites, riesgos, procedencia de datos.
- **Eval harness** más allá del accuracy: slices, calibración, error analysis.
- Medición de **latencia** en una VM modesta y nota de **costo**.
- **Failure probes**: qué pasa si el índice está viejo, el modelo alucina, el
  redactor de PII falla, o un modelo nuevo va mal en un subgrupo. El camino
  "de vuelta a una versión segura" se sub-diseña siempre.

Además: rebajan el riesgo del "ask" aprobando un **piloto** con downside acotado.
La conversación de defensa pide **una decisión de modelado, una de fiabilidad y
un riesgo aceptado a conciencia**.

---

## 3. Cómo lo hacen otros evaluadores / competidores

### Herramientas estándar (contra las que te comparan)

| Herramienta | Categoría | Fuerte en | Forma |
|---|---|---|---|
| **promptfoo** (OpenAI) | runner CI | regresión de prompts, red-teaming OWASP | CLI/YAML |
| **DeepEval** | runner CI | 50+ métricas, "pytest para LLMs" | SDK Python |
| **Inspect AI** (UK AISI) | harness | evals de seguridad/capacidad, agentes sandbox | lib + UI |
| **Ragas** | métricas RAG | faithfulness, context precision/recall | librería |
| **Braintrust / LangSmith / Langfuse / Phoenix / Opik** | plataforma | tracing, datasets, dashboards | SaaS/self-host |
| **lm-evaluation-harness / HELM** | benchmarks | comparar modelos base | CLI |
| **Giskard** | red-team | escaneo de vulnerabilidades | librería |

**Patrón de facto = "eval CI gate":** un runner code-first que corre en CI, con
umbrales en el README, artifacts con el caso fallido / salida real / esperado /
score, smoke en cada PR y suite completa nightly (control de costo).

### Qué suelen mirar los evaluadores en un portfolio

- Un **comando → resultado pass/fail** reproducible (no una captura de pantalla).
- Dataset + regla de scoring + **badge de CI** + análisis de fallas en lenguaje
  llano. Hacer visible el riesgo, no esconderlo.

---

## 4. Qué cubre `eval-quality-gate` (y qué no)

| Dimensión | Cubierto | Cómo |
|---|---|---|
| Quality | ✅ | golden set + token-F1 + citations + grounding |
| Safety | ⚠️ parcial | frases prohibidas + firmas de prompt-injection (no es el OWASP completo) |
| Cost | ✅ | tokens × precio vs presupuesto |
| Latency | ✅ | p95 vs presupuesto |
| Governance | ⚠️ parcial | disclaimers obligatorios + PII regex; model card; evidencia audit-ready |
| Rigor estadístico | ✅ | banda pesimista/base/optimista (IC 95%) |
| Reproducibilidad | ✅ | determinista, sin red en el run de referencia |
| CI gate | ✅ | GitHub Actions, exit code, artifacts |

**Brechas identificadas** (fuera de este repo, candidatas a suite adicional):

1. **Red-teaming completo OWASP LLM Top 10** (inyección directa/indirecta, tool
   hijacking, exfiltración, denial-of-wallet) y **Attack Success Rate**.
2. **Agentic evals**: corrección de tool-calls, uso indebido de herramientas,
   loops, goal completion.
3. **LLM-as-judge con calibración** (acuerdo con humanos, control de sesgo y
   drift del juez) y **energía determinista vs semántica**.
4. **Fairness / bias por subgrupos** (slices por demografía proxy, lenguaje).
5. **Drift / monitoreo en producción** y **A/B online** (es problema de
   plataforma, no de un repo).

Recomendación: mantener `eval-quality-gate` como el **núcleo de gate** y añadir
**una suite de seguridad/red-team** como segundo repo (`eval-redteam-suite`),
reutilizando el mismo contrato de datos y el mismo modelo de decisión.
