# SecureCode Ground Truth — Manual Integral y Especificación Técnica del Repositorio

**Repositorio:** `Medalcode/securecode-ground-truth`  
**Repositorio Relacionado:** `Medalcode/SecureCode`  
**Versión del Benchmark:** `1.0.0`  
**Última Actualización:** 2026-10-06  
**Principio Metodológico:** `EVIDENCE BEFORE CLAIM` (Evidencia antes de Afirmación)

---

## 1. Misión, Propósito y Arquitectura

### 1.1 Objetivo Fundamental
El repositorio **`securecode-ground-truth`** constituye el **oráculo independiente, falsable, criptográficamente inmutable y reproducible** diseñado para auditar, validar y certificar la exactitud del motor de evaluación determinista de cumplimiento de seguridad **SecureCode** ([`Medalcode/SecureCode`](https://github.com/Medalcode/SecureCode)).

Responde a la pregunta fundamental de ingeniería de software:
> *"Dado un escenario de evidencia de configuración normalizada, ¿cuál DEBE ser la evaluación de seguridad esperada (`expected_status`), de manera completamente independiente de cómo esté implementado SECURECODE?"*

### 1.2 Separación Estricta de Responsabilidades

```text
┌────────────────────────────────────────────────────────┐
│               securecode-ground-truth                  │
│  - Oráculo Independiente (Expected Status)             │
│  - Datasets de Referencia Congelados (GH-001, GH-002)  │
│  - Manifiesto Criptográfico (SHA-256)                  │
│  - Harness de Métricas (Matriz 3x3, Precision, Recall) │
│  - Tests de Sensibilidad a Mutaciones                  │
└───────────┬────────────────────────────────────────────┘
            │ evidencia normalizada
            ▼
┌────────────────────────────────────────────────────────┐
│                      SecureCode                        │
│  - Adaptadores GitHub REST                             │
│  - Modelos Inmutables (GH001Evidence, GH002Evidence)   │
│  - Motor Determinista (evaluate_gh001, evaluate_gh002) │
│  - Persistencia PostgreSQL & Migraciones Alembic       │
│  - API REST FastAPI & Autenticación JWT                │
└───────────┬────────────────────────────────────────────┘
            │ predicción de cumplimiento (PASS / FAIL / UNKNOWN)
            ▼
┌────────────────────────────────────────────────────────┐
│               securecode-ground-truth                  │
│  - Comparación Expected vs Actual                      │
│  - Certificación de KPI Correctitud (ES2)              │
│  - Generación de Artefactos de Auditoría               │
└────────────────────────────────────────────────────────┘
```

### 1.3 Ley de No Circularidad (Oracle Independence)
$$\text{Expected Status} \neq f_{\text{SecureCode}}(\text{Evidence})$$

Bajo ninguna circunstancia el oráculo de Ground Truth puede invocar a `securecode.engine.evaluator` para etiquetar datasets o derivar resultados esperados. Ground Truth define las tablas de verdad a priori basándose exclusivamente en especificaciones formales y respuestas HTTP reales de GitHub.

---

## 2. Taxonomía de Estados y Filosofía de Clasificación

El oráculo opera de forma determinista con tres estados mutuamente excluyentes:

| Estado | Significado Técnico en el Oráculo | Impacto Operacional |
|---|---|---|
| **`PASS`** | La evidencia cumple estrictamente todos los requisitos de seguridad exigidos por el control. | Postura de seguridad conforme. |
| **`FAIL`** | La evidencia está completa, pero viola uno o más requisitos mandatorios. | Violación de seguridad detectada. |
| **`UNKNOWN`** | La evidencia es incompleta, ausente, inaccesible o no observable. | Indeterminación por falta de datos. |

### 2.1 El Estado `UNKNOWN` como Ciudadano de Primera Clase
- En seguridad de la información, inferir `FAIL` ante evidencia faltante crea **falsos positivos** que provocan fatiga de alertas.
- Inferir `PASS` ante evidencia faltante crea **falsos negativos críticos** que ocultan brechas de seguridad.
- Por tanto, `UNKNOWN` se aísla de las métricas binarias estándar ($TP, TN, FP, FN$) y se mide con su propia métrica de precisión:
  $$\text{UNKNOWN Accuracy} = \frac{\text{UNKNOWN Correctos}}{\text{Total de UNKNOWN Esperados}}$$

### 2.2 Definición de la Clase Positiva
Siguiendo las mejores prácticas de auditoría de seguridad y los lineamientos del informe ES2:
- **Clase Positiva = `FAIL`**: El objetivo prioritario del sistema es la detección de riesgos y no conformidades. Detectar con éxito un `FAIL` constituye un **Verdadero Positivo ($TP$)**.
- **Clase Negativa = `PASS`**: La conformidad representa la línea base negativa.

---

## 3. Especificación Formal de Controles y Tablas de Verdad

### 3.1 Control GH-001 — Política de Revisiones en Branch Protection

- **Objetivo:** Garantizar que los cambios en ramas protegidas requieran revisión obligatoria por pares y descarten aprobaciones obsoletas tras nuevos commits.
- **Modelo de Evidencia (`GH001Evidence`):**
  - `required_review_approvals` (`Optional[int]`): Cantidad mínima de aprobaciones requeridas.
  - `dismiss_stale_reviews` (`Optional[bool]`): Si se descartan aprobaciones previas al recibir nuevos commits.

#### Regla Matemática del Oráculo
$$\text{Oracle}_{\text{GH-001}}(A, D) = \begin{cases}
\text{UNKNOWN} & \text{si } A = \text{null} \lor D = \text{null} \\
\text{PASS} & \text{si } A \ge 2 \land D = \text{true} \\
\text{FAIL} & \text{en cualquier otro caso}
\end{cases}$$

#### Tabla de Verdad y Particiones de Frontera

| Aprobaciones ($A$) | Descartar Obsoletas ($D$) | Partición de Frontera | Estado Oráculo | Justificación |
|:---:|:---:|---|:---:|---|
| $\ge 2$ (2, 3, 4, 6) | `True` | Conforme | **`PASS`** | Cumple umbral ($\ge 2$) y descarta revisiones viejas. |
| 1 | `True` | Umbral Insuficiente | **`FAIL`** | Solo requiere 1 aprobación (mínimo exigido: 2). |
| 0 | `True` | Sin Aprobaciones | **`FAIL`** | No exige ninguna aprobación obligatoria. |
| $\ge 2$ | `False` | Revisiones Obsoletas | **`FAIL`** | Permite mezclar código sin re-aprobación. |
| $< 2$ | `False` | Doble Violación | **`FAIL`** | Falla umbral y no descarta revisiones obsoletas. |
| `None` | `True` / `False` | Evidencia Parcial | **`UNKNOWN`** | No se pudo leer la cantidad de aprobaciones. |
| $\ge 0$ | `None` | Evidencia Parcial | **`UNKNOWN`** | No se pudo leer la bandera de descartar obsoletas. |
| `None` | `None` | Omisión Total | **`UNKNOWN`** | Rama desprotegida o sin reglas configuradas. |

---

### 3.2 Control GH-002 — Protección Activada en Rama por Defecto

- **Objetivo:** Verificar que la rama principal (`main`/`master`) tenga la protección de rama habilitada.
- **Modelo de Evidencia (`GH002Evidence`):**
  - `default_branch` (`str`): Nombre de la rama principal (ej. `"main"`).
  - `protection_enabled` (`Optional[bool]`): Si la protección está activa en dicha rama.

#### Regla Matemática del Oráculo
$$\text{Oracle}_{\text{GH-002}}(B, P) = \begin{cases}
\text{UNKNOWN} & \text{si } B = \text{null} \lor B = \text{""} \lor P = \text{null} \\
\text{PASS} & \text{si } P = \text{true} \\
\text{FAIL} & \text{si } P = \text{false}
\end{cases}$$

#### Semántica de Adquisición en la API de GitHub (3 Pasos)
La API REST de GitHub utiliza `404 Not Found` de forma ambigua. Para evitar falsos `FAIL`, el adaptador ejecuta un flujo determinista:
1. `GET /repos/{owner}/{repo}` $\to$ Obtiene `default_branch`. Si falla (`401/403/404`), retorna **`UNKNOWN`**.
2. `GET /repos/{owner}/{repo}/branches/{default_branch}` $\to$ Confirma que la rama existe físicamente. Si falla, retorna **`UNKNOWN`**.
3. `GET /repos/{owner}/{repo}/branches/{default_branch}/protection` $\to$
   - `200 OK` $\to$ `protection_enabled = True` (**`PASS`**).
   - `404 Not Found` $\to$ Como el paso 2 confirmó la existencia de la rama, el 404 aquí significa inequívocamente desprotegida $\to$ `protection_enabled = False` (**`FAIL`**).
   - `401/403` $\to$ Falta de permisos/token $\to$ `protection_enabled = None` (**`UNKNOWN`**).

---

## 4. Datasets, Integridad Criptográfica y Manifiesto

### 4.1 Segregación: Benchmark Sintético vs Piloto Empírico
El repositorio mantiene una rigurosa separación epistemológica:
- **Benchmark Sintético ($n=205$):** Casos generados para cubrir todas las combinaciones y particiones de frontera. Se ejecuta 100% offline sin credenciales.
- **Piloto Empírico Real de GitHub ($n=6$):** Respuestas HTTP reales capturadas directamente de GitHub en branches de prueba bajo `Medalcode/securecode-ground-truth`.

```text
Flota Total Validada: 211 casos
├── Sintéticos: 205 casos (GH-001: 105, GH-002: 100)
└── Empíricos:    6 casos (GH-001: 6, GH-002: 0 / Bloqueado por token)
```

### 4.2 Inventario de Datasets y Hashes Criptográficos Congelados

Hashes registrados en [`benchmark/manifest.json`](file:///c:/Users/Jonatthan/Documents/Github/securecode-ground-truth/benchmark/manifest.json):

| Archivo | Control | Tipo | Casos | File SHA-256 | Canonical JSON SHA-256 |
|---|---|---|:---:|---|---|
| `data/ground_truth/gh001_benchmark_105.json` | **GH-001** | Sintético | 105 | `8319425d25a1b251f680282495e22a11043093397cf36afcd88a77a1529d7947` | `9fda9475134c53244c9af0d6ccdfeb9b6cafa6caa98728750b28803085338464` |
| `data/ground_truth/gh001_ground_truth.json` | **GH-001** | Empírico | 6 | `7418f0da8b8f55da1123068756650434b0ec03e20d575fba1c01e6663656832b` | `d560a93cfe2e4c31f0177853f99b044d2f81190e52b6521c5ef07357e671c045` |
| `data/ground_truth/gh002_ground_truth.json` | **GH-002** | Sintético | 100 | `c285dc542d0f97de0507f71aa601484055a80e6b34d060fb2529c5d4dfbaca13` | `8f0bd5554014f37c0206acdc1b92e53aa5bcac601265ab3dc6e92428910c6a99` |

### 4.3 Garantía de Portabilidad Multiplataforma (`.gitattributes`)
Para prevenir discrepancias de hash entre entornos Windows (`CRLF`) y Linux CI (`LF`), el archivo [`.gitattributes`](file:///c:/Users/Jonatthan/Documents/Github/securecode-ground-truth/.gitattributes) fuerza:
```gitattributes
* text=auto eol=lf
*.json text eol=lf
```
Garantizando que el cálculo de `file_sha256` sea idéntico en cualquier sistema operativo.

---

## 5. Resultados del Benchmark y Métricas Académicas (ES2)

### 5.1 Matriz de Confusión 3x3 (Benchmark Combinado, $n=205$)

```text
               ┌────────────────────────────────────────────────────────┐
               │                     PREDICCIÓN REAL                    │
               ├────────────────┬───────────────┬──────────────────────┤
               │      PASS      │     FAIL      │       UNKNOWN        │
┌──────────────┼────────────────┼───────────────┼──────────────────────┤
│ ESPERADO PASS│      69        │ 0             │ 0                    │
├──────────────┼────────────────┼───────────────┼──────────────────────┤
│ ESPERADO FAIL│      0         │ 68            │ 0                    │
├──────────────┼────────────────┼───────────────┼──────────────────────┤
│ ESPERADO UNK │      0         │ 0             │ 68                   │
└──────────────┴────────────────┴───────────────┴──────────────────────┘
```

### 5.2 Resumen de Métricas (KPI Correctitud)

| Métrica Académica | GH-001 Sintético ($n=105$) | GH-002 Sintético ($n=100$) | Combinado Sintético ($n=205$) | GH-001 Piloto Real ($n=6$) |
|---|:---:|:---:|:---:|:---:|
| **Casos Evaluados** | 105 | 100 | 205 | 6 |
| **Coincidencias / Errores**| 105 / 0 | 100 / 0 | 205 / 0 | 6 / 0 |
| **Verdaderos Positivos ($TP$)** | 35 | 33 | 68 | 3 |
| **Verdaderos Negativos ($TN$)** | 35 | 34 | 69 | 1 |
| **Falsos Positivos ($FP$)** | 0 | 0 | 0 | 0 |
| **Falsos Negativos ($FN$)** | 0 | 0 | 0 | 0 |
| **Exactitud Binaria** | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) |
| **Precisión ($TP/(TP+FP)$)** | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) |
| **Sensibilidad / Recall** | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) |
| **F1-Score** | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) |
| **UNKNOWN Accuracy** | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) |
| **Exactitud General 3 Clases** | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) | **100.0%** ($1.0$) |

---

## 6. Pruebas de Sensibilidad a Mutaciones (Falsabilidad)

Un benchmark científico no puede simplemente reportar 100% de éxito; debe demostrar fehacientemente que **es capaz de fallar** y detectar un motor defectuoso.

Se evaluaron 4 mutantes aislados contra la flota del benchmark:

| Mutación Inyectada (Test-Only) | Control | Casos Evaluados | Discrepancias Detectadas | Tasa de Detección | Estado |
|---|---|:---:|:---:|:---:|:---:|
| **Mutante 1:** Umbral subido a 3 ($2 \to 3$) | GH-001 | 105 | 15 | 14.3% | **DETECTADO** |
| **Mutante 2:** Ignorar descartar obsoletas | GH-001 | 105 | 25 | 23.8% | **DETECTADO** |
| **Mutante 3:** Lógica booleana invertida | GH-002 | 100 | 67 | 67.0% | **DETECTADO** |
| **Mutante 4:** Tratar UNKNOWN como PASS | GH-002 | 100 | 33 | 33.0% | **DETECTADO** |

**Puntaje de Sensibilidad del Benchmark:** **100.0%** (4/4 mutantes detectados y eliminados).

---

## 7. Estructura Completa del Repositorio

```text
securecode-ground-truth/
├── .github/
│   └── workflows/
│       └── ci.yml                      # Workflow automatizado en GitHub Actions
├── .gitattributes                      # Control de fin de línea unificado (LF)
├── .gitignore                          # Exclusión de cachés y entornos virtuales
├── artifacts/
│   ├── ground_truth_validation.json    # Reporte máquina exhaustivo (JSON)
│   └── ground_truth_validation.md      # Reporte humano consolidado para ES2
├── benchmark/
│   ├── __init__.py
│   ├── dataset_validator.py            # Validador de esquemas, cobertura y duplicados
│   ├── manifest.json                   # Manifiesto criptográfico maestro
│   ├── metadata.py                     # Modelo de metadatos según especificación Step 7
│   ├── metrics.py                      # Motor de cálculo de matriz 3x3 y métricas
│   ├── run_benchmark.py                # Punto de entrada CLI del benchmark
│   └── runner.py                       # Harness unificado de ejecución cruzada
├── data/
│   └── ground_truth/
│       ├── gh001_benchmark_105.json    # Dataset sintético GH-001 (105 casos)
│       ├── gh001_ground_truth.json     # Baseline empírico GH-001 (6 casos)
│       └── gh002_ground_truth.json     # Dataset sintético GH-002 (100 casos)
├── docs/
│   ├── evidence/
│   │   └── ground_truth/               # Respuestas HTTP crudas de GitHub (GT-GH001-01..06)
│   ├── specs/
│   │   ├── GH001_ORACLE.md             # Especificación matemática del oráculo GH-001
│   │   ├── GH002_ORACLE.md             # Especificación matemática del oráculo GH-002
│   │   ├── METRICS.md                  # Especificación formal de métricas académicas
│   │   └── MIGRATION.md                # Bitácora histórica de migración
│   ├── GROUND_TRUTH_PROTOCOL.md        # Protocolo de independencia de oráculos
│   └── REPOSITORY_OVERVIEW.md          # Manual integral de referencia (este archivo)
├── gen_gh002.py                        # Generador determinista de referencia GH-002
├── scripts/
│   ├── generate_gh001_benchmark.py     # Generador con seed fijo para GH-001
│   └── generate_gh002_benchmark.py     # Wrapper de generación para GH-002
├── tests/
│   ├── unit/
│   │   ├── test_dataset_validation.py  # Validación de unicidad de IDs y esquemas
│   │   ├── test_manifest.py            # Verificación de integridad de hashes
│   │   ├── test_metadata.py            # Tests de serialización de metadatos
│   │   ├── test_metrics.py             # Casos de borde A..F en métricas
│   │   └── test_mutation_sensitivity.py# Verificación de kill rate de mutaciones
│   ├── integration/
│   │   ├── test_benchmark_runner.py    # Ejecución E2E del runner contra SecureCode
│   │   ├── test_ground_truth.py        # Coincidencia con baseline empírico
│   │   └── test_metrics_ground_truth.py# Coincidencia de métricas empíricas (100%)
│   └── test_gh001_benchmark.py         # Propiedades del dataset sintético GH-001
└── README.md                           # Documentación principal del repositorio
```

---

## 8. Guía de Ejecución y Validación

### Requisitos Previos
- Python $\ge 3.11$ (probado en Python 3.12 y 3.14).
- `SecureCode` instalado en modo editable en el mismo entorno:
  ```bash
  pip install -e ../SecureCode
  ```

### Ejecución de Pruebas Automatizadas (31 Tests)
```bash
python -m pytest tests/ -v
```

### Ejecución del Benchmark y Regeneración de Artefactos
```bash
python benchmark/run_benchmark.py
```
Salidas producidas:
- `artifacts/ground_truth_validation.json`
- `artifacts/ground_truth_validation.md`

### Ejecución en CI (GitHub Actions)
El workflow `.github/workflows/ci.yml` clona `Medalcode/SecureCode` anclado al commit exacto `bbc9c27`, ejecuta los 31 tests y el runner de forma totalmente desacoplada y offline.

---

## 9. Paquete de Trazabilidad y Certificación

| Atributo | Valor Verificado en Producción |
|---|---|
| **Product Commit (SecureCode):** | `bbc9c2747373ef31a3e9ba3589ae192842d2fd52` |
| **Ground Truth Commit:** | `9d592019488b0f719fe400ea02970a273b0a7905` |
| **GitHub Actions Run ID:** | [`37410558404`](https://github.com/Medalcode/securecode-ground-truth/actions/runs/37410558404) |
| **Resultado de CI:** | `SUCCESS` (31/31 tests passed, 205/205 matched) |
| **Audit de Secretos:** | `0 secretos encontrados` (Sanitización verificada) |

---

## 10. Limitaciones Académicas

1. **Equivalencia Sintética:** Las permutaciones sintéticas validan exhaustivamente los límites lógicos de las reglas, pero no modelan desviaciones imprevistas de contratos de API externa.
2. **Alcance de Controles:** Cubre `GH-001` y `GH-002`. Controles futuros (`GH-003+`) quedan fuera del alcance actual.
3. **Muestra Empírica:** El piloto empírico real para `GH-001` es acotado ($n=6$) y tiene fines de verificación de protocolos de adquisición, no de inferencia estadística poblacional.
4. **Proveedor SCM:** GitHub es actualmente el único proveedor de control de versiones modelado.
