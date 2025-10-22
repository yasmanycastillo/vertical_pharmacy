# ÍNDICE DE DOCUMENTACIÓN - MÓDULO FARMACIA ODOO 18

## 📚 ESTRUCTURA DE LA DOCUMENTACIÓN

Esta documentación ha sido dividida en múltiples archivos para facilitar su lectura y uso en Claude Code. A continuación el índice completo:

---

## 🎯 DOCUMENTOS PRINCIPALES

### 1. **CLAUDE.md** - Inicio Aquí
**Propósito:** Visión general del proyecto y punto de entrada  
**Contenido:**
- Contexto del proyecto
- Arquitectura modular
- Referencias a otros documentos
- Checklist de inicio
- Estado del proyecto

**📌 Lee este primero para entender la estructura general**

---

### 2. **STANDARDS.md** - Estándares de Código
**Propósito:** Convenciones y mejores prácticas  
**Contenido:**
- Nomenclatura (modelos, campos, métodos, vistas)
- Estructura de carpetas
- Templates de modelos y vistas
- Seguridad (access y rules)
- Testing
- Commits y Git
- Documentación
- Performance
- Checklist de calidad

**📌 Consulta constantemente durante el desarrollo**

---

### 3. **PHASE_1_BASE.md** - Módulo Base (FASE ACTUAL)
**Propósito:** Especificación detallada del módulo pharmacy_base  
**Contenido:**
- Modelos a crear:
  - `pharmacy.product.category`
  - `product.template` (extensión)
  - `res.partner` (extensión)
  - `pharmacy.insurance.info`
- Vistas XML completas
- Menús
- Seguridad
- Datos demo
- Tests
- Criterios de aceptación

**📌 Comienza el desarrollo con este documento**

---

## 📋 DOCUMENTOS DE FASES (Próximos)

### 4. **PHASE_2_POS.md** - POS Especializado
**Contenido pendiente:**
- Extensión de pos.config, pos.order, pos.order.line
- Pantalla de selección de paciente
- Validación de recetas en POS
- Cálculo automático de copagos
- Alertas visuales
- Ticket farmacéutico
- Modo offline

### 5. **PHASE_3_INSURANCE.md** - Sistema de Seguros
**Contenido pendiente:**
- pharmacy.insurance.plan y tiers
- pharmacy.insurance.claim
- pharmacy.prior.authorization
- Dashboard de reclamaciones
- Wizard de adjudicación
- Reportes

### 6. **PHASE_4_PRESCRIPTION.md** - Gestión de Recetas
**Contenido pendiente:**
- pharmacy.prescription y líneas
- pharmacy.drug.interaction
- Wizard de validación farmacéutica
- Integración con POS
- Sistema de recordatorios
- Reportes

### 7. **PHASE_5_DELIVERY.md** - Sistema de Entregas
**Contenido pendiente:**
- pharmacy.delivery.order
- Zonas y time slots
- Rutas de entrega
- Portal de seguimiento
- Notificaciones
- Integración POS/Sale

### 8. **PHASE_6_STOCK.md** - Inventario Avanzado
**Contenido pendiente:**
- Extensiones de stock.lot y stock.picking
- FEFO (First Expired, First Out)
- Sistema de alertas de vencimiento
- Control de calidad
- Cuarentena automática
- Dashboard de inventario

---

## 📐 DOCUMENTOS TRANSVERSALES

### 9. **TECHNICAL_SPECS.md** - Especificaciones Técnicas
**Propósito:** Detalles técnicos críticos  
**Contenido:**
- **Modo Offline en POS:**
  - Caché local
  - Numeración temporal
  - Validación diferida
  - Cola de sincronización
- **Performance:**
  - Targets de tiempo de respuesta
  - Índices en BD
  - Optimizaciones
  - Queries SQL
- **Seguridad:**
  - Control de acceso
  - Auditoría
  - Encriptación
- **Multi-sucursal:**
  - Configuración
  - Sincronización
- **Servidor:**
  - Configuración Odoo
  - Tuning PostgreSQL
  - Monitoreo

**📌 Consulta para decisiones técnicas importantes**

---

### 10. **SPRINT_PLAN.md** - Plan de Desarrollo
**Propósito:** Planificación temporal del proyecto  
**Contenido:**
- Sprint 1-2: Fundamentos (pharmacy_base + pharmacy_pos)
- Sprint 3-4: Seguros y Recetas
- Sprint 5: Delivery
- Sprint 6: Inventario Avanzado
- Sprint 7: Refinamiento y Testing
- Métricas de éxito
- Riesgos y mitigación
- Daily workflow
- Ceremonies

**📌 Usa para planificar y hacer seguimiento del progreso**

---

### 11. **TESTING_GUIDE.md** - Guía de Testing
**Contenido pendiente:**
- Estrategia de testing
- Tipos de tests (unit, integration, UI)
- Coverage targets
- Ejemplos de tests
- Herramientas
- CI/CD

### 12. **ACCEPTANCE_CRITERIA.md** - Criterios de Aceptación
**Contenido pendiente:**
- Criterios funcionales por módulo
- Criterios técnicos (performance, seguridad)
- Criterios de negocio
- Checklists de validación

---

## 🚀 ORDEN DE LECTURA RECOMENDADO

### Para Comenzar el Proyecto:

1. ✅ **CLAUDE.md** - Visión general
2. 📘 **STANDARDS.md** - Aprende las convenciones
3. 📋 **PHASE_1_BASE.md** - Especificación de la fase actual
4. 📐 **TECHNICAL_SPECS.md** - Entiende aspectos técnicos críticos
5. 📊 **SPRINT_PLAN.md** - Planifica tu trabajo

### Durante el Desarrollo:

- **STANDARDS.md**: Referencia constante
- **PHASE_X_XXX.md**: Documento de la fase actual
- **TECHNICAL_SPECS.md**: Para decisiones técnicas

### Antes de Entregar:

- **ACCEPTANCE_CRITERIA.md**: Validar completitud
- **TESTING_GUIDE.md**: Ejecutar tests
- **SPRINT_PLAN.md**: Actualizar progreso

---

## 📝 NOTAS IMPORTANTES

### ⚠️ Límite de Tamaño en Claude Code

El prompt original era demasiado grande (54.2k chars > 40k límite). Por eso se dividió en múltiples archivos:

- **CLAUDE.md**: 4.5k chars ✅
- **PHASE_1_BASE.md**: 26k chars ✅
- **STANDARDS.md**: 18k chars ✅
- **TECHNICAL_SPECS.md**: 22k chars ✅
- **SPRINT_PLAN.md**: 12k chars ✅

Cada archivo es independiente y puede cargarse en Claude Code sin problemas.

### 🔄 Cómo Usar con Claude Code

1. Copia **CLAUDE.md** al archivo CLAUDE.md de tu proyecto
2. Cuando necesites detalles de una fase, abre el **PHASE_X_XXX.md** correspondiente
3. Consulta **STANDARDS.md** para dudas de código
4. Revisa **TECHNICAL_SPECS.md** para decisiones técnicas

### 📂 Ubicación Recomendada

Coloca todos estos archivos en la carpeta `docs/` de tu proyecto:

```
proyecto_farmacia/
├── docs/
│   ├── CLAUDE.md
│   ├── INDEX.md (este archivo)
│   ├── STANDARDS.md
│   ├── PHASE_1_BASE.md
│   ├── PHASE_2_POS.md
│   ├── PHASE_3_INSURANCE.md
│   ├── PHASE_4_PRESCRIPTION.md
│   ├── PHASE_5_DELIVERY.md
│   ├── PHASE_6_STOCK.md
│   ├── TECHNICAL_SPECS.md
│   ├── SPRINT_PLAN.md
│   ├── TESTING_GUIDE.md
│   └── ACCEPTANCE_CRITERIA.md
├── custom_addons/
│   ├── pharmacy_base/
│   ├── pharmacy_pos/
│   └── ...
└── README.md
```

---

## 🎯 PRÓXIMOS PASOS

1. **Lee CLAUDE.md** para entender el contexto
2. **Lee STANDARDS.md** para aprender las convenciones
3. **Lee PHASE_1_BASE.md** completamente
4. **Comienza a desarrollar** el módulo pharmacy_base
5. **Valida** con los criterios de aceptación de Phase 1
6. **Continúa** con Phase 2 cuando Phase 1 esté completa

---

## 📞 SOPORTE

Si tienes dudas durante el desarrollo:

1. **Busca en el documento apropiado:**
   - Dudas de código → STANDARDS.md
   - Dudas de funcionalidad → PHASE_X_XXX.md
   - Dudas técnicas → TECHNICAL_SPECS.md
   
2. **Si no encuentras la respuesta**, pregunta directamente mencionando:
   - Qué estás intentando hacer
   - Qué documento consultaste
   - Qué parte no está clara

---

## ✅ CHECKLIST DE DOCUMENTACIÓN

- [x] CLAUDE.md - Documento principal
- [x] INDEX.md - Este índice
- [x] STANDARDS.md - Estándares de código
- [x] PHASE_1_BASE.md - Fase 1 completa
- [x] TECHNICAL_SPECS.md - Especificaciones técnicas
- [x] SPRINT_PLAN.md - Plan de sprints
- [ ] PHASE_2_POS.md - Pendiente
- [ ] PHASE_3_INSURANCE.md - Pendiente
- [ ] PHASE_4_PRESCRIPTION.md - Pendiente
- [ ] PHASE_5_DELIVERY.md - Pendiente
- [ ] PHASE_6_STOCK.md - Pendiente
- [ ] TESTING_GUIDE.md - Pendiente
- [ ] ACCEPTANCE_CRITERIA.md - Pendiente

---

**¡Éxito en el desarrollo del módulo de farmacia!** 🚀💊
