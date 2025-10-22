# MÓDULO FARMACIA ODOO 18 - GUÍA DE DESARROLLO

## CONTEXTO DEL PROYECTO

Desarrollo de un módulo completo de Farmacia para Odoo 18 que extiende las capacidades estándar para adaptarse a las necesidades específicas del sector farmacéutico.

**Ruta de Odoo Core:** `~/src/odoo/core/addons`
**Repositorio Git:** Puedes crear branch, hacer commit, etc.
**Enfoque:** Incremental con entregables validables en cada fase
**Capacidad:** 2-50+ sucursales, 10,000 transacciones diarias

---

## ARQUITECTURA MODULAR

```
pharmacy_base (módulo core)
    ├── pharmacy_pos (PRIORIDAD 1)
    ├── pharmacy_insurance (PRIORIDAD 2)
    ├── pharmacy_prescription (PRIORIDAD 3)
    ├── pharmacy_delivery (PRIORIDAD 4)
    └── pharmacy_stock_enhanced (PRIORIDAD 5)
```

**Dependencias:**
- `pharmacy_pos`: point_of_sale, pharmacy_base
- `pharmacy_insurance`: pharmacy_base, pharmacy_pos
- `pharmacy_prescription`: pharmacy_base, pharmacy_pos
- `pharmacy_delivery`: sale, pharmacy_base, pharmacy_prescription
- `pharmacy_stock_enhanced`: stock, pharmacy_base
---

## DOCUMENTACIÓN MODULAR

Para evitar problemas de tamaño, la documentación está dividida en archivos específicos:

### 📋 Documentos de Especificación

1. **`PHASE_1_BASE.md`** - Módulo base con modelos fundamentales
2. **`PHASE_2_POS.md`** - POS especializado farmacéutico
3. **`PHASE_3_INSURANCE.md`** - Sistema de copago y seguros
4. **`PHASE_4_PRESCRIPTION.md`** - Gestión de recetas médicas
5. **`PHASE_5_DELIVERY.md`** - Sistema de entregas a domicilio
6. **`PHASE_6_STOCK.md`** - Mejoras de inventario farmacéutico

### 📐 Documentos Transversales

7. **`STANDARDS.md`** - Estándares de código, nomenclatura y estructura
8. **`TECHNICAL_SPECS.md`** - Especificaciones técnicas (offline, performance, seguridad)
9. **`TESTING_GUIDE.md`** - Estrategia de testing y criterios de aceptación

### 📊 Documentos de Gestión

10. **`SPRINT_PLAN.md`** - Plan de sprints y entregas
11. **`ACCEPTANCE_CRITERIA.md`** - Criterios de aceptación globales

---

## INICIO RÁPIDO

### Fase Actual: **FASE 1 - MÓDULO BASE**

**Lee primero:** `PHASE_1_BASE.md`

**Objetivo:** Crear infraestructura base con modelos fundamentales:
- Categorías farmacéuticas
- Productos farmacéuticos (extensión de product.template)
- Pacientes y prescriptores (extensión de res.partner)
- Información de seguros médicos

**Entregable:** Módulo `pharmacy_base` instalable con datos demo

**Tiempo estimado:** 1-2 semanas

---

## ORDEN DE LECTURA RECOMENDADO

Para comenzar el desarrollo, lee en este orden:

1. ✅ **Este archivo (CLAUDE.md)** - Visión general
2. 📋 **STANDARDS.md** - Estándares que aplicarás en todo el código
3. 📋 **PHASE_1_BASE.md** - Especificación detallada de la fase actual
4. 📐 **TECHNICAL_SPECS.md** - Especificaciones técnicas importantes
5. 📐 **TESTING_GUIDE.md** - Cómo testear tu código

Luego, cuando completes la Fase 1, continúa con PHASE_2_POS.md y así sucesivamente.

---

## COMANDOS ÚTILES

```bash
# Estructura básica
cd ~/src/custom/v18/addons/vertical_pharmacy
mkdir -p models views security data demo wizards reports static/description tests

# Ejecutar tests
cd ~/src/odoo/
workon v18
./odoo-bin -c conf/pharmacy.cfg -d pharmacy -i pharmacy_base --test-enable --stop-after-init
```

---
## CHECKLIST DE INICIO

Antes de comenzar, verifica:

- [ ] Odoo 18 instalado y funcionando
- [ ] Acceso a `~/src/odoo/core/addons`
- [ ] Base de datos de prueba creada
- [ ] Entorno virtual Python activado
- [ ] Git configurado para commits
- [ ] Has leído STANDARDS.md
- [ ] Has leído PHASE_1_BASE.md completamente

---

## FLUJO DE TRABAJO

```
1. Leer especificación de la fase (PHASE_X_XXX.md)
2. Crear estructura de carpetas del módulo
3. Desarrollar modelos Python
4. Crear vistas XML
5. Configurar seguridad (ir.model.access.csv)
6. Agregar datos demo
7. Escribir tests
8. Validar criterios de aceptación
9. Commit y pasar a siguiente componente
```

---

## SOPORTE Y PREGUNTAS

Si tienes dudas durante el desarrollo:

1. **Consulta primero:** El documento PHASE correspondiente
2. **Luego revisa:** STANDARDS.md para patrones de código
3. **Finalmente:** TECHNICAL_SPECS.md para detalles técnicos

Si necesitas aclaración sobre un requisito específico, pregunta directamente.

---

## ESTADO DEL PROYECTO

**Fase Actual:** 1 - MÓDULO BASE  
**Estado:** 🔴 No iniciado  
**Siguiente Hito:** pharmacy_base instalable con datos demo

**Progreso General:**
- [ ] Fase 1: pharmacy_base
- [ ] Fase 2: pharmacy_pos  
- [ ] Fase 3: pharmacy_insurance
- [ ] Fase 4: pharmacy_prescription
- [ ] Fase 5: pharmacy_delivery
- [ ] Fase 6: pharmacy_stock_enhanced

---

## NOTAS IMPORTANTES

⚠️ **CRÍTICO:**
- Cada fase debe ser completamente funcional antes de pasar a la siguiente
- Los tests son OBLIGATORIOS (coverage mínimo 70%)
- Seguridad de datos médicos es PRIORITARIA
- Modo offline debe funcionar correctamente en POS

💡 **RECOMENDACIONES:**
- Commits frecuentes con mensajes descriptivos
- Validar cada modelo en Odoo antes de continuar
- Crear datos demo realistas para testing
- Documentar decisiones de diseño importantes

---

**¡Comienza leyendo PHASE_1_BASE.md y empieza a desarrollar!**
