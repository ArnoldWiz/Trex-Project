-- Script para actualizar las restricciones de clave foránea a ON DELETE CASCADE
-- Ejecutar en MySQL en la base de datos TREX

USE `TREX`;

-- Primero, desactivar las verificaciones de clave foránea temporalmente
SET FOREIGN_KEY_CHECKS=0;

-- Eliminar las restricciones antiguas
ALTER TABLE `pedido` DROP FOREIGN KEY `Foreign_OrdenPedido`;
ALTER TABLE `lote` DROP FOREIGN KEY `Foreign_Orden`;

-- Agregar las nuevas restricciones con ON DELETE CASCADE
ALTER TABLE `pedido` ADD CONSTRAINT `Foreign_OrdenPedido`
  FOREIGN KEY (`idOrdenPedido`) REFERENCES `OrdenDePedido` (`idOrdenDePedido`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

ALTER TABLE `lote` ADD CONSTRAINT `Foreign_Orden`
  FOREIGN KEY (`idPedido`) REFERENCES `pedido` (`idPedido`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

-- Reactivar las verificaciones de clave foránea
SET FOREIGN_KEY_CHECKS=1;

-- Listo
SELECT 'Restricciones actualizadas con éxito a ON DELETE CASCADE' AS resultado;


-- Script para dividir Plancha en Pre y Post en la tabla lote
-- Ejecutar en MySQL sobre la base de datos TREX

USE `TREX`;

SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE `lote`
    ADD COLUMN `idEmpPlanchaPre` INT NULL AFTER `idEmpTejido`,
    ADD COLUMN `idEmpPlanchaPost` INT NULL AFTER `idEmpPlanchaPre`,
    ADD COLUMN `FechaTermPlanchaPre` DATETIME NULL AFTER `FechaTermTejido`,
    ADD COLUMN `FechaTermPlanchaPost` DATETIME NULL AFTER `FechaTermPlanchaPre`;

ALTER TABLE `lote`
    ADD CONSTRAINT `fk_lote_emp_plancha_pre`
        FOREIGN KEY (`idEmpPlanchaPre`) REFERENCES `empleado` (`idEmpleado`)
        ON DELETE NO ACTION ON UPDATE NO ACTION,
    ADD CONSTRAINT `fk_lote_emp_plancha_post`
        FOREIGN KEY (`idEmpPlanchaPost`) REFERENCES `empleado` (`idEmpleado`)
        ON DELETE NO ACTION ON UPDATE NO ACTION;

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Campos de Plancha Pre/Post agregados correctamente' AS resultado;

ALTER TABLE `lote`
DROP FOREIGN KEY `Foreign_EmpPlancha`;

ALTER TABLE `lote`
    DROP COLUMN `idEmpPlancha`,
    DROP COLUMN `FechaTermPlancha`;


-- =============================================
-- UPDATE: OrdenDePedido con FechaPrevista
-- y FechaFin automática por avance de pedidos
-- =============================================

USE `TREX`;

-- 1) Agregar FechaPrevista en la orden
ALTER TABLE `ordendepedido`
  ADD COLUMN `FechaPrevista` DATETIME NULL AFTER `FechaInicio`;

-- 2) Inicializar FechaPrevista en datos existentes
UPDATE `ordendepedido`
SET `FechaPrevista` = `FechaInicio`
WHERE `FechaPrevista` IS NULL;

-- 3) Permitir FechaFin nula para manejar flujo por etapas
ALTER TABLE `ordendepedido`
  MODIFY COLUMN `FechaFin` DATETIME NULL;

ALTER TABLE `pedido`
  MODIFY COLUMN `FechaFin` DATETIME NULL;

SELECT 'UPDATE orden/pedido aplicado correctamente (FechaPrevista + FechaFin nullable)' AS resultado;