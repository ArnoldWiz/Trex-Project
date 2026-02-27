-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema TREX
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema TREX
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `TREX` DEFAULT CHARACTER SET utf8 ;
USE `TREX` ;

-- -----------------------------------------------------
-- Table `TREX`.`Empleado`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`Empleado` (
  `idEmpleado` INT NOT NULL AUTO_INCREMENT,
  `Area` VARCHAR(45) NOT NULL,
  `Nombre` VARCHAR(45) NOT NULL,
  `Apellidos` VARCHAR(45) NOT NULL,
  `Estatus` TINYINT NOT NULL,
  PRIMARY KEY (`idEmpleado`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `TREX`.`Maquina`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`Maquina` (
  `idMaquina` INT NOT NULL AUTO_INCREMENT,
  `Area` VARCHAR(45) NOT NULL,
  `Numero` INT NOT NULL,
  `Estatus` TINYINT NOT NULL,
  PRIMARY KEY (`idMaquina`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `TREX`.`Modelo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`Modelo` (
  `idModelo` INT NOT NULL AUTO_INCREMENT,
  `Folio` VARCHAR(45) NOT NULL,
  `Modelo` VARCHAR(45) NOT NULL,
  `CantidadHilo` INT NOT NULL,
  `Estatus` TINYINT NOT NULL,
  PRIMARY KEY (`idModelo`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `TREX`.`Cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`Cliente` (
  `idCliente` INT NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(45) NOT NULL,
  `Contacto` VARCHAR(45) NOT NULL,
  `Estatus` TINYINT NOT NULL,
  PRIMARY KEY (`idCliente`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `TREX`.`OrdenDePedido`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`OrdenDePedido` (
  `idOrdenDePedido` INT NOT NULL AUTO_INCREMENT,
  `NumeroOrden` VARCHAR(45) NOT NULL,
  `idCliente` INT NOT NULL,
  `FechaInicio` DATETIME NOT NULL,
  `FechaFin` DATETIME NULL,
  PRIMARY KEY (`idOrdenDePedido`),
  INDEX `foreign_ordenes_clientes_idx` (`idCliente` ASC) VISIBLE,
  CONSTRAINT `foreign_ordenes_clientes`
    FOREIGN KEY (`idCliente`)
    REFERENCES `TREX`.`Cliente` (`idCliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `TREX`.`Pedido`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`Pedido` (
  `idPedido` INT NOT NULL AUTO_INCREMENT,
  `idOrdenPedido` INT NOT NULL,
  `idModelo` INT NOT NULL,
  `Talla` INT NOT NULL,
  `Cantidad` INT NOT NULL,
  `Color` VARCHAR(45) NOT NULL,
  `TotalLotes` INT NOT NULL,
  `LoteTerminado` INT NOT NULL,
  `FechaInicio` DATETIME NOT NULL,
  `FechaFin` DATETIME NULL,
  `FechaPrevista` DATETIME NOT NULL,
  PRIMARY KEY (`idPedido`),
  INDEX `Foreign_Modelo_idx` (`idModelo` ASC) VISIBLE,
  INDEX `Foreign_Orden_idx` (`idOrdenPedido` ASC) VISIBLE,
  CONSTRAINT `Foreign_Modelo`
    FOREIGN KEY (`idModelo`)
    REFERENCES `TREX`.`Modelo` (`idModelo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_OrdenPedido`
    FOREIGN KEY (`idOrdenPedido`)
    REFERENCES `TREX`.`OrdenDePedido` (`idOrdenDePedido`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `TREX`.`Lote`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`Lote` (
  `idLote` INT NOT NULL AUTO_INCREMENT,
  `idPedido` INT NOT NULL,
  `idEmpTejido` INT NULL,
  `idEmpPlancha` INT NULL,
  `idEmpCorte` INT NULL,
  `idMquTejido` INT NULL,
  `idMaqPlancha` INT NULL,
  `idMaqCorte` INT NULL,
  `Cantidad` INT NOT NULL,
  `FechaTermTejido` DATETIME NULL,
  `FechaTermPlancha` DATETIME NULL,
  `FechaTermCorte` DATETIME NULL,
  `FechaEmpa` DATETIME NULL,
  PRIMARY KEY (`idLote`),
  INDEX `Orden_idx` (`idPedido` ASC) VISIBLE,
  INDEX `Foreign_Empleado_idx` (`idEmpTejido` ASC) VISIBLE,
  INDEX `Foreign_Maquina_idx` (`idMquTejido` ASC) VISIBLE,
  INDEX `Foreign_EmpPlancha_idx` (`idEmpPlancha` ASC) VISIBLE,
  INDEX `Foreign_EmpCorte_idx` (`idEmpCorte` ASC) VISIBLE,
  INDEX `Foreign_MaqPlancha_idx` (`idMaqPlancha` ASC) VISIBLE,
  INDEX `Foreign_MaqCorte_idx` (`idMaqCorte` ASC) VISIBLE,
  CONSTRAINT `Foreign_Orden`
    FOREIGN KEY (`idPedido`)
    REFERENCES `TREX`.`Pedido` (`idPedido`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_EmpTejido`
    FOREIGN KEY (`idEmpTejido`)
    REFERENCES `TREX`.`Empleado` (`idEmpleado`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_MaqTejido`
    FOREIGN KEY (`idMquTejido`)
    REFERENCES `TREX`.`Maquina` (`idMaquina`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_EmpPlancha`
    FOREIGN KEY (`idEmpPlancha`)
    REFERENCES `TREX`.`Empleado` (`idEmpleado`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_EmpCorte`
    FOREIGN KEY (`idEmpCorte`)
    REFERENCES `TREX`.`Empleado` (`idEmpleado`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_MaqPlancha`
    FOREIGN KEY (`idMaqPlancha`)
    REFERENCES `TREX`.`Maquina` (`idMaquina`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_MaqCorte`
    FOREIGN KEY (`idMaqCorte`)
    REFERENCES `TREX`.`Maquina` (`idMaquina`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `TREX`.`ComentariosMaquinas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TREX`.`ComentariosMaquinas` (
  `idComentariosMaquinas` INT NOT NULL AUTO_INCREMENT,
  `idMaquina` INT NOT NULL,
  `idEmpleado` INT NOT NULL,
  `Comentario` TEXT NOT NULL,
  `FechaRegistro` DATETIME NOT NULL,
  `Solucionado` TINYINT NOT NULL,
  PRIMARY KEY (`idComentariosMaquinas`),
  INDEX `Foreign_Maquina_idx` (`idMaquina` ASC) VISIBLE,
  INDEX `Foreign_Empleado_idx` (`idEmpleado` ASC) VISIBLE,
  CONSTRAINT `Foreign_MaquinaCom`
    FOREIGN KEY (`idMaquina`)
    REFERENCES `TREX`.`Maquina` (`idMaquina`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Foreign_EmpleadoCom`
    FOREIGN KEY (`idEmpleado`)
    REFERENCES `TREX`.`Empleado` (`idEmpleado`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
