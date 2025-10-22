# PLAN DE SPRINTS - MÓDULOS FARMACIA ODOO 18

## OVERVIEW DEL PROYECTO

**Duración Total:** 7 semanas  
**Metodología:** Desarrollo incremental con entregables validables  
**Equipo:** Desarrollador Odoo senior  

---

## SPRINT 1-2: FUNDAMENTOS (Semanas 1-2)

### Objetivo
Establecer la base del sistema con modelos fundamentales y POS básico funcional.

### Entregables

#### 1. pharmacy_base (Semana 1)
- [ ] Estructura de módulo creada
- [ ] Modelos: pharmacy.product.category, product.template, res.partner, pharmacy.insurance.info
- [ ] Vistas: productos farmacéuticos, pacientes, prescriptores, seguros
- [ ] Menús: Maestros y Configuración
- [ ] Seguridad: grupos y permisos
- [ ] Datos demo funcionales
- [ ] Tests unitarios (10+ tests, >70% coverage)
- [ ] README.md completo

**Validación Sprint 1:**
- ✅ Instalar módulo sin errores
- ✅ Crear producto farmacéutico con todos sus campos
- ✅ Crear paciente con seguro médico
- ✅ Verificar que código de paciente se genera automáticamente
- ✅ Calcular copago correctamente con insurance_info.calculate_patient_cost()

#### 2. pharmacy_pos - Básico (Semana 2)
- [ ] Extensión de pos.config, pos.order, pos.order.line
- [ ] Pantalla de selección de paciente en POS
- [ ] Validación de productos con receta
- [ ] Cálculo básico de copagos en POS
- [ ] Alertas de productos controlados
- [ ] Ticket con información farmacéutica
- [ ] Tests de integración POS (15+ tests)

**Validación Sprint 2:**
- ✅ POS identifica si es farmacia
- ✅ Vender producto OTC sin paciente
- ✅ Vender producto con receta requiere paciente
- ✅ Calcular copago automáticamente según seguro del paciente
- ✅ Ticket incluye información farmacéutica
- ✅ Alertas visuales funcionan

**Demostración al Final de Sprint 2:**
- Configurar POS como farmacia
- Vender medicamento OTC (Ibuprofeno) sin receta
- Vender medicamento con receta (requiere paciente y validación)
- Mostrar ticket con desglose de copago

---

## SPRINT 3-4: SEGUROS Y RECETAS (Semanas 3-4)

### Objetivo
Sistema completo de gestión de seguros con copagos y recetas médicas.

### Entregables

#### 3. pharmacy_insurance (Semana 3)
- [ ] Modelos: pharmacy.insurance.plan, pharmacy.insurance.tier, pharmacy.insurance.claim, pharmacy.insurance.claim.line, pharmacy.prior.authorization
- [ ] Vistas: planes de seguro, tiers, reclamaciones, autorizaciones
- [ ] Dashboard de reclamaciones
- [ ] Integración con POS: generar claims automáticamente
- [ ] Wizard de adjudicación de claims
- [ ] Reportes: claim report, análisis de rentabilidad
- [ ] Tests de lógica de negocio (20+ tests)

**Validación Sprint 3:**
- ✅ Configurar plan de seguro con 3 tiers
- ✅ Asignar productos a diferentes tiers
- ✅ Venta en POS genera claim automáticamente
- ✅ Procesar claims en lote con wizard
- ✅ Aprobar/rechazar claims
- ✅ Dashboard muestra métricas correctas
- ✅ Calcular copago según tier del medicamento

#### 4. pharmacy_prescription (Semana 4)
- [ ] Modelos: pharmacy.prescription, pharmacy.prescription.line, pharmacy.prescription.validation, pharmacy.drug.interaction
- [ ] Vistas: receta con workflow, kanban, dashboard
- [ ] Wizard de validación farmacéutica
- [ ] Integración con POS: vincular ventas a recetas
- [ ] Control de cantidades y resurtidos
- [ ] Sistema de recordatorios (cron jobs)
- [ ] Reportes: receta dispensada
- [ ] Tests funcionales (25+ tests)

**Validación Sprint 4:**
- ✅ Crear receta con múltiples medicamentos
- ✅ Validar receta con wizard (detecta interacciones)
- ✅ Vender en POS usando receta existente
- ✅ Cantidad dispensada se resta de la receta
- ✅ No permitir dispensar más de lo prescrito
- ✅ Resurtidos funcionan correctamente
- ✅ Recordatorios se envían a pacientes

**Demostración al Final de Sprint 4:**
- Médico genera receta digital
- Paciente llega a farmacia con receta
- Farmacéutico valida receta (verifica interacciones y alergias)
- Vende productos de la receta
- Sistema genera claim al seguro
- Paciente paga solo copago
- Seguimiento de resurtidos

---

## SPRINT 5: DELIVERY (Semana 5)

### Objetivo
Sistema completo de entregas a domicilio con seguimiento.

### Entregables

#### 5. pharmacy_delivery
- [ ] Modelos: pharmacy.delivery.order, pharmacy.delivery.order.line, pharmacy.delivery.zone, pharmacy.delivery.time.slot, pharmacy.delivery.route
- [ ] Vistas: orden de entrega con workflow, kanban, dashboard
- [ ] Portal de seguimiento para clientes
- [ ] Creación de delivery desde POS
- [ ] Asignación de repartidores
- [ ] Sistema de notificaciones por estado
- [ ] Hoja de ruta imprimible
- [ ] Tests de integración (20+ tests)

**Validación Sprint 5:**
- ✅ Crear pedido con delivery desde POS
- ✅ Calcular costo de envío según zona
- ✅ Asignar repartidor a orden
- ✅ Workflow completo de estados funciona
- ✅ Cliente recibe notificaciones por email
- ✅ Portal permite seguimiento en tiempo real
- ✅ Hoja de ruta se genera correctamente
- ✅ Integración con recetas funciona

**Demostración al Final de Sprint 5:**
- Cliente pide medicamentos por teléfono
- Se crea orden de delivery vinculada a receta
- Se prepara pedido y asigna repartidor
- Cliente recibe notificaciones de progreso
- Repartidor completa entrega
- Cliente deja rating

---

## SPRINT 6: INVENTARIO AVANZADO (Semana 6)

### Objetivo
Mejoras especializadas en control de inventario farmacéutico.

### Entregables

#### 6. pharmacy_stock_enhanced
- [ ] Extensiones: stock.lot, product.template, stock.picking, stock.move.line
- [ ] Modelos: pharmacy.temperature.log, pharmacy.stock.alert, pharmacy.stock.adjustment
- [ ] Asignación automática FEFO
- [ ] Wizard de control de calidad
- [ ] Sistema de alertas de vencimiento (cron)
- [ ] Sistema de cuarentena automática
- [ ] Dashboard de inventario
- [ ] Reportes: vencimientos, pérdidas
- [ ] Integración con POS (FEFO, bloqueo vencidos)
- [ ] Tests de lógica de inventario (25+ tests)

**Validación Sprint 6:**
- ✅ Recepción con control de calidad obligatorio
- ✅ Validar vida útil mínima en recepciones
- ✅ Lotes vencidos van a cuarentena automáticamente
- ✅ Alertas de vencimiento se generan diariamente
- ✅ FEFO funciona en ventas (primero que vence, primero que sale)
- ✅ POS bloquea venta de productos vencidos
- ✅ Dashboard muestra métricas correctas
- ✅ Reporte de pérdidas mensual funciona

**Demostración al Final de Sprint 6:**
- Recibir productos con fechas de vencimiento
- Control de calidad rechaza producto
- Alertas de vencimiento próximo
- Venta en POS usa FEFO automáticamente
- Productos vencidos van a cuarentena
- Reporte de pérdidas por vencimiento

---

## SPRINT 7: REFINAMIENTO Y TESTING (Semana 7)

### Objetivo
Completar testing, corregir bugs, optimizar performance y finalizar documentación.

### Actividades

#### Testing Integral (Días 1-3)
- [ ] Ejecutar suite completa de tests
- [ ] Verificar coverage >70% en todos los módulos
- [ ] Tests de integración end-to-end
- [ ] Tests de carga (10,000 transacciones)
- [ ] Tests multi-sucursal

#### Corrección de Bugs (Días 3-4)
- [ ] Revisar y corregir todos los bugs encontrados
- [ ] Validar casos edge
- [ ] Probar flujos alternativos

#### Optimización (Día 4)
- [ ] Revisar queries lentas
- [ ] Optimizar campos computed
- [ ] Agregar índices faltantes
- [ ] Optimizar búsquedas en POS

#### Documentación (Día 5)
- [ ] Manual de usuario
- [ ] Manual de instalación
- [ ] Manual de configuración
- [ ] Documentación técnica API
- [ ] Videos demo (opcional)

**Entregables Finales:**
- ✅ Todos los módulos instalados y funcionando
- ✅ Coverage de tests >70% en cada módulo
- ✅ Performance: POS responde <2seg
- ✅ Documentación completa
- ✅ Datos demo realistas
- ✅ Sin errores en logs

**Demostración Final Completa:**
Flujo completo desde receta hasta entrega:
1. Médico genera receta
2. Paciente pide por teléfono (con delivery)
3. Farmacéutico valida receta
4. Verifica interacciones y alergias
5. Prepara pedido (FEFO automático)
6. Genera claim de seguro
7. Cobra copago al cliente
8. Asigna repartidor
9. Cliente hace seguimiento online
10. Entrega completada con firma
11. Recordatorio de resurtido programado

---

## MÉTRICAS DE ÉXITO

### Técnicas
- [ ] Cobertura de tests: >70% en cada módulo
- [ ] Tiempo de respuesta POS: <2 segundos
- [ ] Sin errores críticos en logs
- [ ] Soporte para 10,000 transacciones/día
- [ ] Funciona offline en POS

### Funcionales
- [ ] Venta de medicamentos con receta validada
- [ ] Cálculo automático de copagos
- [ ] Claims generados automáticamente
- [ ] Entregas con seguimiento
- [ ] Alertas de vencimiento operativas
- [ ] FEFO funcional en ventas

### Negocio
- [ ] Reducción de vencimientos por mejor control
- [ ] Trazabilidad completa de medicamentos
- [ ] Información de seguros integrada
- [ ] Servicio de delivery operativo
- [ ] Cumplimiento regulatorio

---

## RIESGOS Y MITIGACIÓN

### Riesgo 1: Complejidad del POS
**Probabilidad:** Media  
**Impacto:** Alto  
**Mitigación:** Comenzar con funcionalidad básica, agregar features incrementalmente

### Riesgo 2: Integración con Seguros
**Probabilidad:** Media  
**Impacto:** Medio  
**Mitigación:** Implementar sin APIs externas primero, dejar preparado para integración futura

### Riesgo 3: Performance en POS
**Probabilidad:** Baja  
**Impacto:** Alto  
**Mitigación:** Tests de carga tempranos, optimización proactiva, caché apropiado

### Riesgo 4: Modo Offline POS
**Probabilidad:** Media  
**Impacto:** Medio  
**Mitigación:** Diseño desde inicio para offline-first, sincronización robusta

---

## DAILY WORKFLOW RECOMENDADO

### Mañana (3-4 horas)
- Desarrollo de nuevas features
- Escribir código de modelos/vistas

### Tarde (2-3 horas)
- Escribir tests para código de la mañana
- Corrección de bugs
- Code review

### Final del día (30 min)
- Commit de código
- Actualizar checklist de sprint
- Planificar siguiente día

---

## CEREMONIES RECOMENDADAS

### Daily Stand-up (15 min)
- ¿Qué hice ayer?
- ¿Qué haré hoy?
- ¿Tengo algún bloqueador?

### Sprint Review (1 hora al final de cada sprint)
- Demostrar funcionalidad nueva
- Validar criterios de aceptación
- Feedback del stakeholder

### Sprint Retrospective (30 min)
- ¿Qué salió bien?
- ¿Qué mejorar?
- Acciones para próximo sprint

---

## HERRAMIENTAS RECOMENDADAS

- **IDE:** VSCode con extensiones de Odoo
- **Testing:** pytest-odoo, coverage
- **Git:** Git flow con branches por feature
- **Gestión:** Trello/Jira para seguimiento de tareas
- **Comunicación:** Slack/Discord para daily updates

---

**Este plan es flexible. Ajusta según avance real y feedback del stakeholder.**
