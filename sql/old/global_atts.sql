DROP VIEW IF EXISTS global_attributes CASCADE;
CREATE OR REPLACE VIEW global_attributes AS
SELECT c.global_attribute_id as id,  
       c.global_attribute_name as att_name, 
       SUM(CASE WHEN a.is_match and ba.question_id = bc.question_id THEN 1 ELSE 0 END) frequency
FROM ui_schemamapchoice c 
     LEFT JOIN ( 
     	  ui_schemamapanswer a
	  JOIN ui_baseanswer ba ON a.baseanswer_ptr_id = ba.id  
     ) ON c.global_attribute_id = a.global_attribute_id
     JOIN ui_basechoice bc ON c.basechoice_ptr_id = bc.id
GROUP BY c.global_attribute_name, c.global_attribute_id;

DROP VIEW IF EXISTS schemamapquestion_priors CASCADE;
CREATE VIEW schemamapquestion_priors AS
SELECT a.id, a.att_name, a.frequency::FLOAT/count(a2.id) AS prior
FROM global_attributes as a, global_attributes as a2
GROUP BY a.id, a.att_name, a.frequency; 
