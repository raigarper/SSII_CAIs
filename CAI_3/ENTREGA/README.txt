CAI 3 - Parte 1 - Security Team 2 (ST-2)
Consulta sobre Identificacion, Autenticacion y Autorizacion en una Entidad
Hospitalaria

Contenido de esta entrega:

1. ST-2-CAI3-Parte1.pdf
   Informe tecnico completo: arquitectura, metodologia, los 9 ataques de
   la Fase 1 (Red Team) con su evidencia, las correcciones de la Fase 3
   (Blue Team), la verificacion antes/despues (Fase 4), y las
   recomendaciones para el Hospital.

2. SourceCode_hardened/
   Proyecto corregido, listo para instalar y ejecutar (ver su propio
   Leeme.txt dentro de esta misma carpeta). No incluye venv ni
   __pycache__: hay que crear el entorno virtual e instalar
   requirements.txt antes de arrancar.

3. evidencias/
   - auditoria_codigo/hallazgos.md        -> tabla completa de las 16
     vulnerabilidades encontradas (Fase 2), con fichero y linea de codigo.
   - red_team/                            -> capturas, respuestas HTTP y
     scripts de cada ataque de la Fase 1 (caja negra, sobre el proyecto
     ORIGINAL, sin modificar).
   - blue_team/                           -> logs de arranque del
     proyecto corregido y notas de las incidencias detectadas durante su
     propia verificacion.
   - pruebas_despues/                     -> capturas, scripts y tabla
     comparativa de la Fase 4 (verificacion de que los mismos ataques ya
     no funcionan contra SourceCode_hardened).

Para probar el proyecto corregido, sigue las instrucciones de
SourceCode_hardened/Leeme.txt.
