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