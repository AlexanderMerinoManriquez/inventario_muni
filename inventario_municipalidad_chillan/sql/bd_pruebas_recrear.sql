DROP DATABASE IF EXISTS inventario_municipalidad;

CREATE DATABASE inventario_municipalidad
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE inventario_municipalidad;

CREATE TABLE departamentos (
    id_departamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre_departamento VARCHAR(150) NOT NULL,

    UNIQUE KEY uq_departamentos_nombre (nombre_departamento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE funcionarios (
    id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(15) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    id_departamento INT NULL,

    CONSTRAINT fk_funcionarios_departamentos
        FOREIGN KEY (id_departamento)
        REFERENCES departamentos(id_departamento)
        ON DELETE SET NULL,

    UNIQUE KEY uq_funcionarios_rut (rut),
    KEY idx_funcionarios_nombre (nombre),
    KEY idx_funcionarios_departamento (id_departamento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE usuarios_sistema (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(15) NOT NULL,
    nombre_usuario VARCHAR(150) NOT NULL,

    UNIQUE KEY uq_usuarios_sistema_rut (rut),
    KEY idx_usuarios_sistema_nombre (nombre_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE activos (
    id_activo INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('EQUIPO', 'MONITOR', 'IMPRESORA') NOT NULL,
    codigo_inventario VARCHAR(50) NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NULL,

    UNIQUE KEY uq_activos_codigo_inventario (codigo_inventario),
    KEY idx_activos_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE equipos (
    id_activo INT PRIMARY KEY,

    nombre_pc VARCHAR(100) NULL,
    sistema_operativo VARCHAR(150) NULL,
    procesador VARCHAR(200) NULL,
    ram_gb DECIMAL(10,2) NULL,

    tipo_disco_principal VARCHAR(20) NULL,
    capacidad_disco_principal_gb DECIMAL(10,2) NULL,

    ip VARCHAR(45) NULL,
    anydesk VARCHAR(50) NULL,
    numero_de_serie VARCHAR(100) NULL,

    CONSTRAINT fk_equipos_activos
        FOREIGN KEY (id_activo)
        REFERENCES activos(id_activo)
        ON DELETE CASCADE,

    UNIQUE KEY uq_equipos_numero_de_serie (numero_de_serie),
    KEY idx_equipos_nombre_pc (nombre_pc),
    KEY idx_equipos_ip (ip)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE monitores (
    id_activo INT PRIMARY KEY,

    marca VARCHAR(100) NULL,
    modelo VARCHAR(100) NULL,
    pulgadas DECIMAL(4,1) NULL,
    numero_de_serie VARCHAR(100) NULL,

    CONSTRAINT fk_monitores_activos
        FOREIGN KEY (id_activo)
        REFERENCES activos(id_activo)
        ON DELETE CASCADE,

    UNIQUE KEY uq_monitores_numero_de_serie (numero_de_serie),
    KEY idx_monitores_marca_modelo (marca, modelo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE impresoras (
    id_activo INT PRIMARY KEY,

    marca VARCHAR(100) NULL,
    modelo VARCHAR(100) NULL,
    tipo_impresora VARCHAR(100) NULL,
    toner_tinta VARCHAR(100) NULL,
    ip VARCHAR(45) NULL,
    numero_de_serie VARCHAR(100) NULL,

    CONSTRAINT fk_impresoras_activos
        FOREIGN KEY (id_activo)
        REFERENCES activos(id_activo)
        ON DELETE CASCADE,

    UNIQUE KEY uq_impresoras_numero_de_serie (numero_de_serie),
    KEY idx_impresoras_ip (ip),
    KEY idx_impresoras_marca_modelo (marca, modelo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE asignaciones_activo (
    id_asignacion INT AUTO_INCREMENT PRIMARY KEY,

    id_activo INT NOT NULL,
    id_funcionario INT NOT NULL,
    id_departamento INT NOT NULL,
    asignado_por INT NOT NULL,

    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NULL,

    observaciones TEXT NULL,

    asignacion_activa TINYINT
        GENERATED ALWAYS AS (
            CASE
                WHEN fecha_fin IS NULL THEN 1
                ELSE NULL
            END
        ) STORED,

    CONSTRAINT fk_asignaciones_activo
        FOREIGN KEY (id_activo)
        REFERENCES activos(id_activo)
        ON DELETE CASCADE,

    CONSTRAINT fk_asignaciones_funcionario
        FOREIGN KEY (id_funcionario)
        REFERENCES funcionarios(id_funcionario)
        ON DELETE RESTRICT,

    CONSTRAINT fk_asignaciones_departamento
        FOREIGN KEY (id_departamento)
        REFERENCES departamentos(id_departamento)
        ON DELETE RESTRICT,

    CONSTRAINT fk_asignaciones_usuario
        FOREIGN KEY (asignado_por)
        REFERENCES usuarios_sistema(id_usuario)
        ON DELETE RESTRICT,

    UNIQUE KEY uq_asignacion_activa_por_activo (id_activo, asignacion_activa),

    KEY idx_asignaciones_funcionario (id_funcionario),
    KEY idx_asignaciones_departamento (id_departamento),
    KEY idx_asignaciones_usuario (asignado_por),
    KEY idx_asignaciones_fechas (fecha_inicio, fecha_fin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

USE inventario_municipalidad;

DESCRIBE activos;
DESCRIBE equipos;
DESCRIBE monitores;
DESCRIBE impresoras;