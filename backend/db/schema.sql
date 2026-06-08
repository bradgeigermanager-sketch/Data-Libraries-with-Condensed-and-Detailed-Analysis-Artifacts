`sql
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
`
