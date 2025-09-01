CREATE SCHEMA IF NOT EXISTS `trex` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `trex` ;

-- -----------------------------------------------------
-- Table `trex`.`empleado`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `trex`.`empleado` (
  `idEMPLEADO` INT NOT NULL,
  `NOMBRE` VARCHAR(45) NOT NULL,
  `APELLIDO` VARCHAR(45) NOT NULL,
  `ESTATUS` TINYINT NOT NULL,
  PRIMARY KEY (`idEMPLEADO`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `trex`.`maquina`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `trex`.`maquina` (
  `idMAQUINA` INT NOT NULL,
  `AREA` VARCHAR(45) NOT NULL,
  `NUMERO` INT NOT NULL,
  PRIMARY KEY (`idMAQUINA`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `trex`.`orden`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `trex`.`orden` (
  `idORDEN` INT NOT NULL,
  `FOLIO` VARCHAR(45) NOT NULL,
  `TALLA` INT NOT NULL,
  `CANTIDAD` INT NOT NULL,
  `COLOR` VARCHAR(45) NOT NULL,
  `MODELO` VARCHAR(45) NOT NULL,
  `TOTAL_LOTES` INT NOT NULL,
  `LOTE_TERMI` INT NOT NULL,
  `FECHA_INICIO` DATETIME NOT NULL,
  `FECHA_FIN` DATETIME NOT NULL,
  PRIMARY KEY (`idORDEN`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `trex`.`lote`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `trex`.`lote` (
  `idLOTE` INT NOT NULL,
  `idORDEN` INT NOT NULL,
  `idEMPLEADO` INT NOT NULL,
  `idMAQUINA` INT NOT NULL,
  `CANTIDAD` INT NOT NULL,
  `FECHA_REALIZADO` DATETIME NOT NULL,
  PRIMARY KEY (`idLOTE`),
  INDEX `Orden_idx` (`idORDEN` ASC) VISIBLE,
  INDEX `Foreign_Empleado_idx` (`idEMPLEADO` ASC) VISIBLE,
  INDEX `Foreign_Maquina_idx` (`idMAQUINA` ASC) VISIBLE,
  CONSTRAINT `Foreign_Empleado`
    FOREIGN KEY (`idEMPLEADO`)
    REFERENCES `trex`.`empleado` (`idEMPLEADO`),
  CONSTRAINT `Foreign_Maquina`
    FOREIGN KEY (`idMAQUINA`)
    REFERENCES `trex`.`maquina` (`idMAQUINA`),
  CONSTRAINT `Foreign_Orden`
    FOREIGN KEY (`idORDEN`)
    REFERENCES `trex`.`orden` (`idORDEN`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
