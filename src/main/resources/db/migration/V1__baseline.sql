-- V1: tabla minima para demostrar que Flyway funciona.
-- Las tablas reales de tandas se definen en el Sprint 2.
CREATE TABLE tanda (
    id         BIGSERIAL    PRIMARY KEY,
    nombre     VARCHAR(120) NOT NULL,
    estado     VARCHAR(30)  NOT NULL DEFAULT 'BORRADOR',
    creado_en  TIMESTAMPTZ  NOT NULL DEFAULT now()
);
