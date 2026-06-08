/*
  MODULE: LogicArtifact Schema
  LOCATION: backend/db/schema.sql
  NOTATION: Core atomic node table for the immutable logic graph.
  USE: Stores all logic nodes, machine-readable templates, and fillable schemas.
*/

CREATE TABLE IF NOT EXISTS LogicArtifact (
    artifact_id UUID PRIMARY KEY,

    -- Human-readable identifier
    title VARCHAR(255) NOT NULL,

    -- Core representations
    condensed_logic TEXT NOT NULL,
    verbose_desc TEXT NOT NULL,
    foundational_data JSONB,

    -- Polymorphic classification
    artifactcategory VARCHAR(50) NOT NULL DEFAULT 'logicnode',
    syntax_language VARCHAR(50) NOT NULL DEFAULT 'text',

    -- Metadata
    createdat TIMESTAMP DEFAULT CURRENTTIMESTAMP,
    updatedat TIMESTAMP DEFAULT CURRENTTIMESTAMP
);

-- Category index for fast filtering in browse.html
CREATE INDEX IF NOT EXISTS idxartifactcategory
    ON LogicArtifact(artifact_category);

/*
  MODULE: LogicRelationship Schema
  LOCATION: backend/db/schema.sql
  NOTATION: Directed edge table for the immutable logic graph.
  USE: Stores all inter-artifact relationships (implies, contradicts, supersedes, implements, etc.).
*/

CREATE TABLE IF NOT EXISTS LogicRelationship (
    relationship_id UUID PRIMARY KEY,

    -- Directed edge endpoints
    source_id UUID NOT NULL,
    target_id UUID NOT NULL,

    -- Relationship classification
    relationship_type VARCHAR(100) NOT NULL,

    -- Foreign key constraints (append-only)
    CONSTRAINT fk_source
        FOREIGN KEY (source_id)
        REFERENCES LogicArtifact(artifact_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_target
        FOREIGN KEY (target_id)
        REFERENCES LogicArtifact(artifact_id)
        ON DELETE RESTRICT
);

-- Indexes for fast graph traversal
CREATE INDEX IF NOT EXISTS idx_source
    ON LogicRelationship(source_id);

CREATE INDEX IF NOT EXISTS idx_target
    ON LogicRelationship(target_id);

CREATE INDEX IF NOT EXISTS idx_relationship_type
    ON LogicRelationship(relationship_type);
