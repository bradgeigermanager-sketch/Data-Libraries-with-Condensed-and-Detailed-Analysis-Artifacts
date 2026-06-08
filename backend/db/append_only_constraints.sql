/*
  MODULE: append_only_constraints.sql
  LOCATION: backend/db/append_only_constraints.sql
  NOTATION: Immutability enforcement for the atomic logic graph.
  USE: Prevents destructive operations and enforces versioning-only updates.
*/

------------------------------------------------------------
-- 1. PREVENT DELETE ON LogicArtifact
------------------------------------------------------------

CREATE OR REPLACE FUNCTION prevent_artifact_deletion()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 
        'Immutability Violation: Logical artifacts cannot be deleted. Use supersedes or deprecation.';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_no_delete ON LogicArtifact;

CREATE TRIGGER enforce_no_delete
BEFORE DELETE ON LogicArtifact
FOR EACH ROW EXECUTE FUNCTION prevent_artifact_deletion();


------------------------------------------------------------
-- 2. PREVENT UPDATE ON CORE FIELDS
------------------------------------------------------------

CREATE OR REPLACE FUNCTION prevent_artifact_mutation()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.condensed_logic <> OLD.condensed_logic OR
       NEW.verbose_desc <> OLD.verbose_desc OR
       NEW.foundational_data <> OLD.foundational_data OR
       NEW.artifact_category <> OLD.artifact_category OR
       NEW.syntax_language <> OLD.syntax_language THEN

        RAISE EXCEPTION 
            'Immutability Violation: Core artifact fields cannot be mutated. Use versioning.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_no_update ON LogicArtifact;

CREATE TRIGGER enforce_no_update
BEFORE UPDATE ON LogicArtifact
FOR EACH ROW EXECUTE FUNCTION prevent_artifact_mutation();


------------------------------------------------------------
-- 3. PREVENT DELETE ON LogicRelationship
--    (Relationships are also immutable; new edges must be appended)
------------------------------------------------------------

CREATE OR REPLACE FUNCTION prevent_relationship_deletion()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 
        'Immutability Violation: Relationships cannot be deleted. Append new edges instead.';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_no_delete_relationship ON LogicRelationship;

CREATE TRIGGER enforce_no_delete_relationship
BEFORE DELETE ON LogicRelationship
FOR EACH ROW EXECUTE FUNCTION prevent_relationship_deletion();


------------------------------------------------------------
-- 4. PREVENT UPDATE ON LogicRelationship
--    (Edge types and endpoints are immutable)
------------------------------------------------------------

CREATE OR REPLACE FUNCTION prevent_relationship_mutation()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.source_id <> OLD.source_id OR
       NEW.target_id <> OLD.target_id OR
       NEW.relationship_type <> OLD.relationship_type THEN

        RAISE EXCEPTION 
            'Immutability Violation: Relationship edges cannot be mutated. Append a new edge instead.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_no_update_relationship ON LogicRelationship;

CREATE TRIGGER enforce_no_update_relationship
BEFORE UPDATE ON LogicRelationship
FOR EACH ROW EXECUTE FUNCTION prevent_relationship_mutation();
