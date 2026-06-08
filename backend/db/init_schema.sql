/*
  MODULE: init_schema.sql
  LOCATION: backend/db/init_schema.sql
  NOTATION: Full initialization script for the immutable logic graph database.
  USE: Bootstraps all tables, indexes, and immutability constraints.
*/

------------------------------------------------------------
-- 1. CORE TABLES
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS LogicArtifact (
    artifact_id UUID PRIMARY KEY,

    -- Human-readable identifier
    title VARCHAR(255) NOT NULL,

    -- Core representations
    condensed_logic TEXT NOT NULL,
    verbose_desc TEXT NOT NULL,
    foundational_data JSONB,

    -- Polymorphic classification
    artifact_category VARCHAR(50) NOT NULL DEFAULT 'logic_node',
    syntax_language VARCHAR(50) NOT NULL DEFAULT 'text',

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS LogicRelationship (
    relationship_id UUID PRIMARY KEY,

    -- Directed edge endpoints
    source_id UUID NOT NULL,
    target_id UUID NOT NULL,

    -- Relationship classification
    relationship_type VARCHAR(100) NOT NULL,

    CONSTRAINT fk_source
        FOREIGN KEY (source_id)
        REFERENCES LogicArtifact(artifact_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_target
        FOREIGN KEY (target_id)
        REFERENCES LogicArtifact(artifact_id)
        ON DELETE RESTRICT
);

------------------------------------------------------------
-- 2. INDEXES
------------------------------------------------------------

-- Artifact filters
CREATE INDEX IF NOT EXISTS idx_artifact_category
    ON LogicArtifact(artifact_category);

CREATE INDEX IF NOT EXISTS idx_syntax_language
    ON LogicArtifact(syntax_language);

-- Graph traversal
CREATE INDEX IF NOT EXISTS idx_source
    ON LogicRelationship(source_id);

CREATE INDEX IF NOT EXISTS idx_target
    ON LogicRelationship(target_id);

CREATE INDEX IF NOT EXISTS idx_relationship_type
    ON LogicRelationship(relationship_type);

------------------------------------------------------------
-- 3. IMMUTABILITY ENFORCEMENT
------------------------------------------------------------

-- Prevent DELETE on LogicArtifact
CREATE OR REPLACE FUNCTION prevent_artifact_deletion()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Immutability Violation: Logical artifacts cannot be deleted. Use supersedes or deprecation.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_no_delete
BEFORE DELETE ON LogicArtifact
FOR EACH ROW EXECUTE FUNCTION prevent_artifact_deletion();

-- Prevent UPDATE on core fields
CREATE OR REPLACE FUNCTION prevent_artifact_mutation()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.condensed_logic <> OLD.condensed_logic OR
       NEW.verbose_desc <> OLD.verbose_desc OR
       NEW.foundational_data <> OLD.foundational_data OR
       NEW.artifact_category <> OLD.artifact_category OR
       NEW.syntax_language <> OLD.syntax_language THEN
        RAISE EXCEPTION 'Immutability Violation: Core artifact fields cannot be mutated. Use versioning.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_no_update
BEFORE UPDATE ON LogicArtifact
FOR EACH ROW EXECUTE FUNCTION prevent_artifact_mutation();
