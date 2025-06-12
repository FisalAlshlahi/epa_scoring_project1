-- EPA Scoring System Database Schema
-- Complete database structure for EPA scoring system
-- File: database/schema.sql

-- Create database
CREATE DATABASE IF NOT EXISTS epa_scoring;
USE epa_scoring;

-- Core EPAs table
CREATE TABLE core_epas (
    epa_id VARCHAR(10) PRIMARY KEY,
    epa_name VARCHAR(200) NOT NULL,
    epa_description TEXT,
    total_weight DECIMAL(5,2) NOT NULL,
    version VARCHAR(10) DEFAULT '2.0',
    status VARCHAR(50) DEFAULT 'implementation_ready',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_epa_status (status),
    INDEX idx_epa_weight (total_weight)
);

-- Smaller EPAs table
CREATE TABLE smaller_epas (
    smaller_epa_id VARCHAR(15) PRIMARY KEY,
    core_epa_id VARCHAR(10) NOT NULL,
    smaller_epa_name VARCHAR(200) NOT NULL,
    smaller_epa_description TEXT,
    weight_percentage DECIMAL(5,2) NOT NULL,
    sequence_order INT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (core_epa_id) REFERENCES core_epas(epa_id) ON DELETE CASCADE,
    INDEX idx_smaller_epa_core (core_epa_id),
    INDEX idx_smaller_epa_sequence (sequence_order)
);

-- Activities table
CREATE TABLE activities (
    activity_id VARCHAR(20) PRIMARY KEY,
    smaller_epa_id VARCHAR(15) NOT NULL,
    activity_name VARCHAR(200) NOT NULL,
    activity_description TEXT,
    weight_percentage DECIMAL(5,2) NOT NULL,
    sequence_order INT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (smaller_epa_id) REFERENCES smaller_epas(smaller_epa_id) ON DELETE CASCADE,
    INDEX idx_activity_smaller_epa (smaller_epa_id),
    INDEX idx_activity_sequence (sequence_order)
);

-- Performance indicators table
CREATE TABLE performance_indicators (
    indicator_id VARCHAR(25) PRIMARY KEY,
    activity_id VARCHAR(20) NOT NULL,
    indicator_name VARCHAR(200) NOT NULL,
    indicator_description TEXT,
    competency_type ENUM('Critical_Thinker', 'Nurse_Expert', 'Communicator', 'Leader') NOT NULL,
    weight_percentage DECIMAL(5,2) NOT NULL,
    sequence_order INT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE,
    INDEX idx_indicator_activity (activity_id),
    INDEX idx_indicator_competency (competency_type),
    INDEX idx_indicator_sequence (sequence_order)
);

-- Context types table
CREATE TABLE context_types (
    context_id VARCHAR(20) PRIMARY KEY,
    context_name VARCHAR(100) NOT NULL,
    context_description TEXT,
    base_multiplier DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    trigger_conditions TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_context_multiplier (base_multiplier)
);

-- Technology levels table
CREATE TABLE technology_levels (
    tech_level_id VARCHAR(20) PRIMARY KEY,
    level_name VARCHAR(100) NOT NULL,
    level_description TEXT,
    multiplier DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tech_multiplier (multiplier)
);

-- Student assessments table
CREATE TABLE student_assessments (
    assessment_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    indicator_id VARCHAR(25) NOT NULL,
    assessor_id VARCHAR(20) NOT NULL,
    base_score DECIMAL(3,2) NOT NULL CHECK (base_score >= 1.0 AND base_score <= 5.0),
    context_id VARCHAR(20),
    tech_level_id VARCHAR(20),
    evidence_type ENUM('Direct_Observation', 'Simulation', 'Portfolio', 'Case_Study', 'Peer_Review') NOT NULL,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_id) REFERENCES performance_indicators(indicator_id),
    FOREIGN KEY (context_id) REFERENCES context_types(context_id),
    FOREIGN KEY (tech_level_id) REFERENCES technology_levels(tech_level_id),
    INDEX idx_assessment_student (student_id),
    INDEX idx_assessment_indicator (indicator_id),
    INDEX idx_assessment_date (assessment_date),
    INDEX idx_assessment_score (base_score)
);

-- Calculated scores table
CREATE TABLE calculated_scores (
    score_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    epa_id VARCHAR(10),
    smaller_epa_id VARCHAR(15),
    activity_id VARCHAR(20),
    indicator_id VARCHAR(25),
    score_level ENUM('Indicator', 'Activity', 'Smaller_EPA', 'Core_EPA', 'Framework') NOT NULL,
    base_score DECIMAL(5,3),
    context_adjusted_score DECIMAL(5,3),
    tech_adjusted_score DECIMAL(5,3),
    integration_bonus DECIMAL(5,3) DEFAULT 0.000,
    standards_bonus DECIMAL(5,3) DEFAULT 0.000,
    final_score DECIMAL(5,3) NOT NULL,
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_calculated_student (student_id),
    INDEX idx_calculated_epa (epa_id),
    INDEX idx_calculated_level (score_level),
    INDEX idx_calculated_date (calculation_date)
);

-- Integration bonuses table
CREATE TABLE integration_bonuses (
    bonus_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    primary_epa_id VARCHAR(10) NOT NULL,
    secondary_epa_id VARCHAR(10) NOT NULL,
    integration_type VARCHAR(50) NOT NULL,
    bonus_points DECIMAL(3,2) NOT NULL,
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_epa_id) REFERENCES core_epas(epa_id),
    FOREIGN KEY (secondary_epa_id) REFERENCES core_epas(epa_id),
    INDEX idx_integration_student (student_id),
    INDEX idx_integration_primary (primary_epa_id),
    INDEX idx_integration_secondary (secondary_epa_id)
);

-- Standards compliance table
CREATE TABLE standards_compliance (
    compliance_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    epa_id VARCHAR(10) NOT NULL,
    standard_type ENUM('WHO_2022', 'ICN_2023', 'AACN_2021', 'ENA_2024') NOT NULL,
    compliance_score DECIMAL(3,2) NOT NULL,
    bonus_points DECIMAL(3,2) NOT NULL,
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (epa_id) REFERENCES core_epas(epa_id),
    INDEX idx_compliance_student (student_id),
    INDEX idx_compliance_epa (epa_id),
    INDEX idx_compliance_standard (standard_type)
);

-- Quality assurance table
CREATE TABLE quality_assurance (
    qa_id VARCHAR(50) PRIMARY KEY,
    indicator_id VARCHAR(25),
    context_id VARCHAR(20),
    qa_type ENUM('Inter_Rater_Reliability', 'Context_Validation', 'Quality_Monitoring') NOT NULL,
    metric_value DECIMAL(5,3) NOT NULL,
    status VARCHAR(50) NOT NULL,
    sample_size INT,
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_id) REFERENCES performance_indicators(indicator_id),
    FOREIGN KEY (context_id) REFERENCES context_types(context_id),
    INDEX idx_qa_type (qa_type),
    INDEX idx_qa_status (status),
    INDEX idx_qa_date (calculation_date)
);

-- Students table (for reference)
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_email VARCHAR(100),
    program VARCHAR(50),
    year_level INT,
    enrollment_date DATE,
    status VARCHAR(20) DEFAULT 'Active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_program (program),
    INDEX idx_student_year (year_level),
    INDEX idx_student_status (status)
);

-- Faculty table (for reference)
CREATE TABLE faculty (
    faculty_id VARCHAR(20) PRIMARY KEY,
    faculty_name VARCHAR(100) NOT NULL,
    faculty_email VARCHAR(100),
    department VARCHAR(50),
    position VARCHAR(50),
    specialization VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_faculty_department (department),
    INDEX idx_faculty_status (status)
);

-- Create views for common queries
CREATE VIEW student_epa_summary AS
SELECT 
    s.student_id,
    s.student_name,
    ce.epa_id,
    ce.epa_name,
    AVG(cs.final_score) as avg_score,
    COUNT(cs.score_id) as assessment_count,
    MAX(cs.calculation_date) as last_assessment
FROM students s
LEFT JOIN calculated_scores cs ON s.student_id = cs.student_id
LEFT JOIN core_epas ce ON cs.epa_id = ce.epa_id
WHERE cs.score_level = 'Core_EPA'
GROUP BY s.student_id, s.student_name, ce.epa_id, ce.epa_name;

CREATE VIEW epa_performance_overview AS
SELECT 
    ce.epa_id,
    ce.epa_name,
    COUNT(DISTINCT cs.student_id) as student_count,
    AVG(cs.final_score) as avg_score,
    MIN(cs.final_score) as min_score,
    MAX(cs.final_score) as max_score,
    STDDEV(cs.final_score) as score_stddev
FROM core_epas ce
LEFT JOIN calculated_scores cs ON ce.epa_id = cs.epa_id
WHERE cs.score_level = 'Core_EPA'
GROUP BY ce.epa_id, ce.epa_name;

