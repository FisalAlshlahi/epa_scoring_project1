-- EPA Scoring System Data Population
-- Framework-aligned data with corrected EPA weights totaling 100%
-- File: database/data.sql

USE epa_scoring;

-- Insert Core EPAs with corrected weights
INSERT INTO core_epas (epa_id, epa_name, epa_description, total_weight, version, status) VALUES
('EPA_001', 'Comprehensive Patient Assessment and Health History', 'Conduct systematic and comprehensive patient assessments including health history, physical examination, and psychosocial evaluation across diverse populations and care settings.', 19.00, '2.0', 'implementation_ready'),
('EPA_002', 'Nursing Diagnoses and Clinical Reasoning', 'Formulate evidence-based nursing diagnoses through systematic clinical reasoning, critical thinking, and integration of assessment data with theoretical knowledge.', 16.00, '2.0', 'implementation_ready'),
('EPA_003', 'Care Planning and Implementation', 'Develop, implement, and evaluate comprehensive, individualized care plans that integrate evidence-based practice, patient preferences, and interdisciplinary collaboration.', 15.00, '2.0', 'implementation_ready'),
('EPA_004', 'Therapeutic Procedures and Interventions', 'Perform complex therapeutic nursing procedures and interventions safely and competently while maintaining patient dignity and comfort.', 14.00, '2.0', 'implementation_ready'),
('EPA_005', 'Emergency Recognition and Response', 'Recognize patient deterioration and emergency situations, initiate appropriate interventions, and coordinate emergency response activities.', 14.00, '2.0', 'implementation_ready'),
('EPA_006', 'Mental Health and Palliative Care', 'Provide compassionate, evidence-based mental health and palliative care interventions while supporting patients and families through challenging health experiences.', 8.00, '2.0', 'implementation_ready'),
('EPA_007', 'Health Promotion and Community Care', 'Design and implement health promotion strategies and community-based interventions that address population health needs and social determinants of health.', 8.00, '2.0', 'implementation_ready'),
('EPA_008', 'Informatics and Leadership', 'Utilize healthcare informatics and demonstrate leadership skills in quality improvement, interprofessional collaboration, and healthcare innovation.', 6.00, '2.0', 'implementation_ready');

-- Insert Context Types
INSERT INTO context_types (context_id, context_name, context_description, base_multiplier, trigger_conditions) VALUES
('STD_CARE', 'Standard Care', 'Standard hospital or clinic care environment', 1.00, 'Standard patient care settings'),
('PED_CARE', 'Pediatric Care', 'Specialized pediatric care environment', 1.20, 'Patients under 18 years old'),
('GER_CARE', 'Geriatric Care', 'Specialized geriatric care environment', 1.15, 'Patients over 65 years old'),
('CRIT_CARE', 'Critical Care', 'Intensive care or critical care environment', 1.40, 'ICU, CCU, or critical care units'),
('EMERG_CARE', 'Emergency Care', 'Emergency department or urgent care', 1.30, 'Emergency department or urgent care'),
('MENT_HEALTH', 'Mental Health', 'Mental health or psychiatric care setting', 1.25, 'Mental health or psychiatric patients'),
('HOME_CARE', 'Home Care', 'Home health or community care setting', 1.10, 'Home health or community care'),
('SURG_CARE', 'Surgical Care', 'Perioperative or surgical care environment', 1.20, 'Surgical or perioperative care'),
('REHAB_CARE', 'Rehabilitation', 'Rehabilitation or long-term care setting', 1.15, 'Rehabilitation or long-term care'),
('DISASTER', 'Disaster Response', 'Disaster or mass casualty response', 1.60, 'Disaster or mass casualty events');

-- Insert Technology Levels
INSERT INTO technology_levels (tech_level_id, level_name, level_description, multiplier) VALUES
('BASIC_TECH', 'Basic Technology', 'Basic healthcare technology and equipment', 1.00),
('ADV_TECH', 'Advanced Technology', 'Advanced healthcare technology and informatics', 1.20),
('INNOV_TECH', 'Innovative Technology', 'Cutting-edge technology and AI-assisted care', 1.40);

-- Insert Sample Students
INSERT INTO students (student_id, student_name, student_email, program, year_level, enrollment_date, status) VALUES
('STU_001', 'أحمد محمد علي', 'ahmed.ali@university.edu', 'BSN', 3, '2022-09-01', 'Active'),
('STU_002', 'فاطمة حسن محمود', 'fatima.hassan@university.edu', 'BSN', 3, '2022-09-01', 'Active'),
('STU_003', 'محمد عبدالله سالم', 'mohammed.salem@university.edu', 'BSN', 4, '2021-09-01', 'Active'),
('STU_004', 'نورا أحمد خالد', 'nora.khalid@university.edu', 'BSN', 2, '2023-09-01', 'Active'),
('STU_005', 'عبدالرحمن يوسف', 'abdulrahman.youssef@university.edu', 'BSN', 4, '2021-09-01', 'Active');

-- Insert Sample Faculty
INSERT INTO faculty (faculty_id, faculty_name, faculty_email, department, position, specialization, status) VALUES
('FAC_001', 'د. سارة أحمد الزهراني', 'sara.alzahrani@university.edu', 'Nursing', 'Professor', 'Critical Care Nursing', 'Active'),
('FAC_002', 'د. محمد عبدالعزيز القحطاني', 'mohammed.alqahtani@university.edu', 'Nursing', 'Associate Professor', 'Emergency Nursing', 'Active'),
('FAC_003', 'د. نوال سليمان العتيبي', 'nawal.alotaibi@university.edu', 'Nursing', 'Assistant Professor', 'Pediatric Nursing', 'Active'),
('FAC_004', 'د. خالد محمد الشهري', 'khalid.alshahri@university.edu', 'Nursing', 'Professor', 'Mental Health Nursing', 'Active'),
('FAC_005', 'د. هند عبدالله المطيري', 'hind.almutairi@university.edu', 'Nursing', 'Associate Professor', 'Community Health Nursing', 'Active');

-- Insert Smaller EPAs for EPA 1
INSERT INTO smaller_epas (smaller_epa_id, core_epa_id, smaller_epa_name, smaller_epa_description, weight_percentage, sequence_order) VALUES
('EPA_001_1', 'EPA_001', 'Health History and Interview', 'Conduct comprehensive health history interviews using therapeutic communication and cultural sensitivity.', 25.00, 1),
('EPA_001_2', 'EPA_001', 'Physical Assessment', 'Perform systematic physical examinations using appropriate techniques and equipment.', 35.00, 2),
('EPA_001_3', 'EPA_001', 'Psychosocial Assessment', 'Evaluate psychosocial factors, mental health status, and social determinants affecting patient health.', 25.00, 3),
('EPA_001_4', 'EPA_001', 'Documentation and Communication', 'Document assessment findings accurately and communicate effectively with healthcare team members.', 15.00, 4);

-- Insert Activities for EPA 1.1
INSERT INTO activities (activity_id, smaller_epa_id, activity_name, activity_description, weight_percentage, sequence_order) VALUES
('EPA_001_1_1', 'EPA_001_1', 'Therapeutic Communication', 'Establish therapeutic relationships and conduct interviews using effective communication techniques.', 40.00, 1),
('EPA_001_1_2', 'EPA_001_1', 'Cultural Assessment', 'Assess cultural factors and adapt communication approaches for diverse populations.', 35.00, 2),
('EPA_001_1_3', 'EPA_001_1', 'Health History Documentation', 'Document comprehensive health histories accurately and systematically.', 25.00, 3);

-- Insert Performance Indicators for EPA 1.1.1
INSERT INTO performance_indicators (indicator_id, activity_id, indicator_name, indicator_description, competency_type, weight_percentage, sequence_order) VALUES
('EPA_001_1_1_1', 'EPA_001_1_1', 'Establishes Rapport', 'Demonstrates ability to establish therapeutic rapport with patients and families.', 'Communicator', 25.00, 1),
('EPA_001_1_1_2', 'EPA_001_1_1', 'Active Listening Skills', 'Uses active listening techniques and responds appropriately to patient concerns.', 'Communicator', 25.00, 2),
('EPA_001_1_1_3', 'EPA_001_1_1', 'Therapeutic Questioning', 'Asks appropriate therapeutic questions to gather comprehensive health information.', 'Critical_Thinker', 25.00, 3),
('EPA_001_1_1_4', 'EPA_001_1_1', 'Professional Boundaries', 'Maintains appropriate professional boundaries while demonstrating empathy and compassion.', 'Nurse_Expert', 25.00, 4);

-- Insert Sample Assessments
INSERT INTO student_assessments (assessment_id, student_id, indicator_id, assessor_id, base_score, context_id, tech_level_id, evidence_type, notes) VALUES
('ASS_001_001', 'STU_001', 'EPA_001_1_1_1', 'FAC_001', 4.2, 'STD_CARE', 'BASIC_TECH', 'Direct_Observation', 'Excellent rapport building with elderly patient'),
('ASS_001_002', 'STU_001', 'EPA_001_1_1_2', 'FAC_001', 3.8, 'STD_CARE', 'BASIC_TECH', 'Direct_Observation', 'Good listening skills, needs improvement in follow-up questions'),
('ASS_001_003', 'STU_001', 'EPA_001_1_1_3', 'FAC_002', 4.0, 'EMERG_CARE', 'ADV_TECH', 'Simulation', 'Effective questioning in emergency scenario'),
('ASS_001_004', 'STU_001', 'EPA_001_1_1_4', 'FAC_001', 4.5, 'STD_CARE', 'BASIC_TECH', 'Direct_Observation', 'Excellent professional boundaries maintained'),
('ASS_002_001', 'STU_002', 'EPA_001_1_1_1', 'FAC_003', 3.5, 'PED_CARE', 'BASIC_TECH', 'Direct_Observation', 'Good rapport with pediatric patient and family'),
('ASS_002_002', 'STU_002', 'EPA_001_1_1_2', 'FAC_003', 4.1, 'PED_CARE', 'BASIC_TECH', 'Direct_Observation', 'Excellent listening skills with child patient'),
('ASS_002_003', 'STU_002', 'EPA_001_1_1_3', 'FAC_001', 3.9, 'STD_CARE', 'BASIC_TECH', 'Portfolio', 'Well-structured questions documented'),
('ASS_002_004', 'STU_002', 'EPA_001_1_1_4', 'FAC_003', 4.3, 'PED_CARE', 'BASIC_TECH', 'Direct_Observation', 'Appropriate boundaries with pediatric family');

-- Verify data integrity
SELECT 'Core EPAs Total Weight' as Check_Type, SUM(total_weight) as Total_Weight FROM core_epas;
SELECT 'EPA 1 Smaller EPAs Weight' as Check_Type, SUM(weight_percentage) as Total_Weight FROM smaller_epas WHERE core_epa_id = 'EPA_001';
SELECT 'EPA 1.1 Activities Weight' as Check_Type, SUM(weight_percentage) as Total_Weight FROM activities WHERE smaller_epa_id = 'EPA_001_1';
SELECT 'EPA 1.1.1 Indicators Weight' as Check_Type, SUM(weight_percentage) as Total_Weight FROM performance_indicators WHERE activity_id = 'EPA_001_1_1';

