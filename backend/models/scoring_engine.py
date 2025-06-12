"""
EPA Scoring Engine - Core Models
File: backend/models/scoring_engine.py
"""

import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)

class EPAScoringEngine:
    """
    Complete EPA scoring engine with algorithmic calculations
    """
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.connection = None
        
    def connect_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            logger.info("Database connection established successfully")
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
            
    def disconnect_database(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
            
    def calculate_indicator_score(self, assessment_id: str) -> Dict:
        """
        Calculate performance indicator score with context and technology adjustments
        """
        if not self.connection:
            self.connect_database()
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Get assessment details
            query = """
            SELECT sa.*, pi.weight_percentage as indicator_weight,
                   ct.base_multiplier as context_multiplier,
                   tl.multiplier as tech_multiplier,
                   pi.competency_type
            FROM student_assessments sa
            JOIN performance_indicators pi ON sa.indicator_id = pi.indicator_id
            LEFT JOIN context_types ct ON sa.context_id = ct.context_id
            LEFT JOIN technology_levels tl ON sa.tech_level_id = tl.tech_level_id
            WHERE sa.assessment_id = %s
            """
            
            cursor.execute(query, (assessment_id,))
            assessment = cursor.fetchone()
            
            if not assessment:
                return {'error': 'Assessment not found'}
            
            # Calculate scores
            base_score = float(assessment['base_score'])
            context_multiplier = float(assessment['context_multiplier'] or 1.0)
            tech_multiplier = float(assessment['tech_multiplier'] or 1.0)
            indicator_weight = float(assessment['indicator_weight'])
            
            # Apply adjustments
            context_adjusted_score = base_score * context_multiplier
            tech_adjusted_score = context_adjusted_score * tech_multiplier
            final_score = min(tech_adjusted_score, 5.0)  # Cap at 5.0
            final_weighted_score = (final_score * indicator_weight) / 100.0
            
            return {
                'assessment_id': assessment_id,
                'base_score': base_score,
                'context_multiplier': context_multiplier,
                'tech_multiplier': tech_multiplier,
                'context_adjusted_score': context_adjusted_score,
                'tech_adjusted_score': tech_adjusted_score,
                'final_score': final_score,
                'indicator_weight': indicator_weight,
                'final_weighted_score': final_weighted_score,
                'competency_type': assessment['competency_type'],
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Error as e:
            logger.error(f"Error calculating indicator score: {e}")
            return {'error': str(e)}
        finally:
            cursor.close()
            
    def calculate_activity_score(self, student_id: str, activity_id: str) -> Dict:
        """
        Calculate activity-level score from multiple performance indicators
        """
        if not self.connection:
            self.connect_database()
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Get all assessments for this student and activity
            query = """
            SELECT sa.assessment_id, sa.base_score, pi.indicator_id, pi.weight_percentage,
                   ct.base_multiplier as context_multiplier,
                   tl.multiplier as tech_multiplier
            FROM student_assessments sa
            JOIN performance_indicators pi ON sa.indicator_id = pi.indicator_id
            LEFT JOIN context_types ct ON sa.context_id = ct.context_id
            LEFT JOIN technology_levels tl ON sa.tech_level_id = tl.tech_level_id
            WHERE sa.student_id = %s AND pi.activity_id = %s
            ORDER BY sa.assessment_date DESC
            """
            
            cursor.execute(query, (student_id, activity_id))
            assessments = cursor.fetchall()
            
            if not assessments:
                return {'error': 'No assessments found for this activity'}
            
            # Calculate indicator scores
            indicator_scores = []
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for assessment in assessments:
                base_score = float(assessment['base_score'])
                context_multiplier = float(assessment['context_multiplier'] or 1.0)
                tech_multiplier = float(assessment['tech_multiplier'] or 1.0)
                weight = float(assessment['weight_percentage'])
                
                # Apply adjustments
                adjusted_score = min(base_score * context_multiplier * tech_multiplier, 5.0)
                weighted_score = adjusted_score * weight / 100.0
                
                indicator_scores.append({
                    'indicator_id': assessment['indicator_id'],
                    'base_score': base_score,
                    'adjusted_score': adjusted_score,
                    'weight': weight,
                    'weighted_score': weighted_score
                })
                
                total_weighted_score += weighted_score
                total_weight += weight / 100.0
            
            # Calculate activity score
            activity_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            return {
                'student_id': student_id,
                'activity_id': activity_id,
                'activity_score': activity_score,
                'indicator_count': len(indicator_scores),
                'indicator_scores': indicator_scores,
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Error as e:
            logger.error(f"Error calculating activity score: {e}")
            return {'error': str(e)}
        finally:
            cursor.close()
            
    def calculate_integration_bonus(self, student_id: str, primary_epa: str, secondary_epa: str) -> Dict:
        """
        Calculate cross-EPA integration bonus
        """
        # Integration matrix with bonus values
        integration_matrix = {
            ('EPA_001', 'EPA_002'): {'type': 'Assessment_to_Diagnosis', 'bonus': 0.2},
            ('EPA_002', 'EPA_003'): {'type': 'Diagnosis_to_Planning', 'bonus': 0.2},
            ('EPA_003', 'EPA_004'): {'type': 'Planning_to_Implementation', 'bonus': 0.15},
            ('EPA_001', 'EPA_005'): {'type': 'Assessment_to_Emergency', 'bonus': 0.25},
            ('EPA_004', 'EPA_006'): {'type': 'Intervention_to_Specialized_Care', 'bonus': 0.15},
            ('EPA_007', 'EPA_003'): {'type': 'Community_to_Individual_Care', 'bonus': 0.1},
            ('EPA_008', 'EPA_001'): {'type': 'Technology_Enhanced_Assessment', 'bonus': 0.1},
            ('EPA_008', 'EPA_002'): {'type': 'Technology_Enhanced_Diagnosis', 'bonus': 0.1},
            ('EPA_008', 'EPA_003'): {'type': 'Technology_Enhanced_Planning', 'bonus': 0.1},
            ('EPA_008', 'EPA_004'): {'type': 'Technology_Enhanced_Implementation', 'bonus': 0.1},
            ('EPA_008', 'EPA_005'): {'type': 'Technology_Enhanced_Emergency', 'bonus': 0.15},
            ('EPA_008', 'EPA_006'): {'type': 'Technology_Enhanced_Specialized', 'bonus': 0.1},
            ('EPA_008', 'EPA_007'): {'type': 'Technology_Enhanced_Community', 'bonus': 0.1}
        }
        
        integration_key = (primary_epa, secondary_epa)
        if integration_key not in integration_matrix:
            return {
                'student_id': student_id,
                'primary_epa': primary_epa,
                'secondary_epa': secondary_epa,
                'integration_level': 'None',
                'bonus_points': 0.0,
                'calculation_timestamp': datetime.now().isoformat()
            }
        
        integration_info = integration_matrix[integration_key]
        
        if not self.connection:
            self.connect_database()
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Get student performance in both EPAs
            score_query = """
            SELECT AVG(final_score) as avg_score
            FROM calculated_scores
            WHERE student_id = %s AND epa_id = %s AND score_level = 'Core_EPA'
            """
            
            cursor.execute(score_query, (student_id, primary_epa))
            primary_result = cursor.fetchone()
            primary_score = float(primary_result['avg_score'] or 0.0)
            
            cursor.execute(score_query, (student_id, secondary_epa))
            secondary_result = cursor.fetchone()
            secondary_score = float(secondary_result['avg_score'] or 0.0)
            
            # Calculate integration level
            min_score = min(primary_score, secondary_score)
            
            if min_score >= 4.0:
                integration_level = 'High'
                bonus_multiplier = 1.0
            elif min_score >= 3.5:
                integration_level = 'Moderate'
                bonus_multiplier = 0.75
            elif min_score >= 3.0:
                integration_level = 'Basic'
                bonus_multiplier = 0.5
            else:
                integration_level = 'Insufficient'
                bonus_multiplier = 0.0
            
            bonus_points = integration_info['bonus'] * bonus_multiplier
            
            return {
                'student_id': student_id,
                'primary_epa': primary_epa,
                'secondary_epa': secondary_epa,
                'integration_type': integration_info['type'],
                'integration_level': integration_level,
                'primary_score': primary_score,
                'secondary_score': secondary_score,
                'base_bonus': integration_info['bonus'],
                'bonus_multiplier': bonus_multiplier,
                'bonus_points': bonus_points,
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Error as e:
            logger.error(f"Error calculating integration bonus: {e}")
            return {'error': str(e)}
        finally:
            cursor.close()
            
    def calculate_entrustment_level(self, epa_score: float) -> Dict:
        """
        Calculate entrustment level based on EPA score
        """
        if epa_score >= 4.5:
            level = 5
            description = "Expert - Able to supervise others"
            supervision = "Independent practice with teaching responsibilities"
        elif epa_score >= 3.5:
            level = 4
            description = "Proficient - Independent practice"
            supervision = "Independent practice with minimal oversight"
        elif epa_score >= 3.0:
            level = 3
            description = "Competent - Minimal guidance needed"
            supervision = "Independent practice with available supervision"
        elif epa_score >= 2.0:
            level = 2
            description = "Advanced Beginner - Moderate guidance"
            supervision = "Direct supervision with guided practice"
        else:
            level = 1
            description = "Novice - Significant guidance needed"
            supervision = "Close supervision with extensive guidance"
        
        return {
            'epa_score': epa_score,
            'entrustment_level': level,
            'description': description,
            'supervision_type': supervision,
            'calculation_timestamp': datetime.now().isoformat()
        }

