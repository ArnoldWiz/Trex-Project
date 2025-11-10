use trex;

INSERT INTO `TREX`.`Empleado` (`Area`, `Nombre`, `Apellidos`, `Estatus`)
VALUES
('Tejido', 'Ana', 'Gomez Perez', 1),
('Corte', 'Luis', 'Hernandez Lopez', 1),
('Plancha', 'Marta', 'Ramirez Salas', 1),
('Empaque', 'Javier', 'Flores Castillo', 1),
('Tejido', 'Sofia', 'Mendez Ruiz', 0);

INSERT INTO `TREX`.`Maquina` (`Area`, `Numero`, `Estatus`)
VALUES
('Tejido', 1,1),
('Tejido', 2,1),
('Plancha', 1,1),
('Corte', 1,1),
('Corte', 2,1);

INSERT INTO `TREX`.`Modelo` (`Folio`, `Modelo`, `CantidadHilo`, `Estatus`)
VALUES
('A-001', 'Camiseta Basica', 150,1),
('B-002', 'Sudadera Deportiva', 350,1),
('C-003', 'Pantalón Casual', 280,1),
('D-004', 'Chamarra Ligera', 500,1),
('E-005', 'Vestido de Verano', 200,1);

INSERT INTO `TREX`.`Cliente` (`Nombre`, `Contacto`, `Estatus`)
VALUES
('Modas Express S.A. de C.V.', 'Carlos Garcia (CEO)',1),
('Textiles del Sur', 'Elena Ramirez (Jefa de Compras)',1),
('Ropa Infantil Feliz', 'Laura Montes (Dueña)',1),
('Distribuidora Norte', 'Pedro Vazquez (Gerente)',1),
('Tienda La Moda', 'Ana Torres (Contacto Comercial)',1);

INSERT INTO `TREX`.`OrdenDePedido` (`idCliente`, `NumeroOrden`, `FechaInicio`, `FechaFin`)
VALUES
(1, 'N1', '2025-10-20 09:00:00', NULL), 
(2, 'N2', '2025-10-21 14:30:00', NULL), 
(3, 'N3', '2025-10-22 10:00:00', '2025-11-15 17:00:00'), 
(4, 'N4', '2025-10-23 08:00:00', NULL), 
(1, 'N5', '2025-10-24 11:15:00', NULL);

INSERT INTO `TREX`.`Pedido` (`idOrdenPedido`, `idModelo`, `Talla`, `Cantidad`, `Color`, `TotalLotes`, `LoteTerminado`, `FechaInicio`, `FechaFin`, `FechaPrevista`)
VALUES
(1, 1, 30, 1000, 'Rojo', 10, 3, '2025-10-20 09:00:00', '2025-11-30 17:00:00', '2025-11-25 00:00:00'),
(1, 2, 32, 500, 'Azul Marino', 5, 0, '2025-10-20 09:00:00', '2025-12-15 17:00:00', '2025-12-10 00:00:00'),
(2, 3, 34, 2000, 'Negro', 20, 20, '2025-10-21 14:30:00', '2025-11-10 17:00:00', '2025-11-10 00:00:00'),
(4, 4, 36, 800, 'Gris', 8, 0, '2025-10-23 08:00:00', '2025-12-20 17:00:00', '2025-12-18 00:00:00'),
(5, 5, 30, 300, 'Blanco', 3, 3, '2025-10-24 11:15:00', '2025-11-05 17:00:00', '2025-11-03 00:00:00');

INSERT INTO `TREX`.`Lote` (`idPedido`, `idEmpTejido`, `idEmpPlancha`, `idEmpCorte`, `idMquTejido`, `idMaqPlancha`, `idMaqCorte`, `Cantidad`, `FechaTermTejido`, `FechaTermPlancha`, `FechaTermCorte`, `FechaEmpa`)
VALUES
(1, 1, 3, 2, 1, 3, 4, 100, '2025-10-25 10:00:00', '2025-10-26 12:00:00', '2025-10-27 15:00:00', '2025-10-28 09:00:00'),
(1, 1, 3, 2, 2, 3, 4, 100, '2025-10-26 11:00:00', NULL, NULL, NULL),
(3, 1, 3, 2, 1, 3, 4, 100, '2025-10-23 15:00:00', '2025-10-24 10:00:00', '2025-10-25 12:00:00', '2025-10-25 18:00:00'),
(5, 5, 3, NULL, 5, 3, NULL, 100, '2025-10-27 08:00:00', '2025-10-28 11:00:00', NULL, NULL),
(4, NULL, NULL, 2, NULL, NULL, 5, 100, NULL, NULL, '2025-10-29 14:00:00', NULL);

INSERT INTO `TREX`.`ComentariosMaquinas` (`idMaquina`, `idEmpleado`, `Comentario`, `FechaRegistro`, `Solucionado`)
VALUES
(1, 1, 'La máquina 1 de tejido hace un ruido extraño en el motor principal.', '2025-10-28 10:00:00', 0),
(2, 5, 'El alimentador de hilo está fallando en la máquina 2.', '2025-10-28 14:30:00', 0),
(3, 3, 'Se ajustó la presión de la plancha 1, funciona correctamente.', '2025-10-27 09:15:00', 1),
(4, 2, 'El sensor de seguridad de la máquina de corte 1 está muy sensible.', '2025-10-26 16:00:00', 0),
(1, 1, 'Revisión periódica completada en la 2. Sin problemas graves.', '2025-10-25 12:00:00', 1);