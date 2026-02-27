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
