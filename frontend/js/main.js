// EPA Scoring System - Main JavaScript
// File: frontend/js/main.js

// Global variables
let currentSection = 'dashboard';
let studentsData = [];
let facultyData = [];
let epasData = [];
let contextsData = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('EPA Scoring System initialized');
    
    // Initialize navigation
    initializeNavigation();
    
    // Load initial data
    loadInitialData();
    
    // Initialize forms
    initializeForms();
    
    // Show loading
    showLoading();
});

// Navigation handling
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sectionId = this.getAttribute('data-section');
            showSection(sectionId);
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Show specific section
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
        
        // Load section-specific data
        loadSectionData(sectionId);
    }
}

// Load section-specific data
function loadSectionData(sectionId) {
    switch(sectionId) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'assessment':
            loadAssessmentFormData();
            break;
        case 'students':
            loadStudentsData();
            break;
        case 'reports':
            loadReportsData();
            break;
    }
}

// Load initial application data
async function loadInitialData() {
    try {
        showLoading();
        
        // Load all required data
        await Promise.all([
            loadStudents(),
            loadFaculty(),
            loadEPAs(),
            loadContexts()
        ]);
        
        // Load dashboard by default
        loadDashboardData();
        
        hideLoading();
        showMessage('تم تحميل البيانات بنجاح', 'success');
        
    } catch (error) {
        console.error('Error loading initial data:', error);
        hideLoading();
        showMessage('خطأ في تحميل البيانات: ' + error.message, 'error');
    }
}

// Load students data
async function loadStudents() {
    try {
        const response = await apiRequest('/students');
        studentsData = response.students || [];
        
        // Update students count
        document.getElementById('total-students').textContent = studentsData.length;
        
        return studentsData;
    } catch (error) {
        console.error('Error loading students:', error);
        throw error;
    }
}

// Load faculty data
async function loadFaculty() {
    try {
        const response = await apiRequest('/faculty');
        facultyData = response.faculty || [];
        return facultyData;
    } catch (error) {
        console.error('Error loading faculty:', error);
        throw error;
    }
}

// Load EPAs data
async function loadEPAs() {
    try {
        const response = await apiRequest('/epas');
        epasData = response.epas || [];
        return epasData;
    } catch (error) {
        console.error('Error loading EPAs:', error);
        throw error;
    }
}

// Load contexts data
async function loadContexts() {
    try {
        const response = await apiRequest('/contexts');
        contextsData = response.contexts || [];
        return contextsData;
    } catch (error) {
        console.error('Error loading contexts:', error);
        throw error;
    }
}

// Initialize forms
function initializeForms() {
    // Assessment form
    const assessmentForm = document.getElementById('assessment-form');
    if (assessmentForm) {
        assessmentForm.addEventListener('submit', handleAssessmentSubmit);
        
        // EPA selection change handler
        const epaSelect = document.getElementById('epa-select');
        if (epaSelect) {
            epaSelect.addEventListener('change', handleEPASelectionChange);
        }
    }
}

// Handle assessment form submission
async function handleAssessmentSubmit(e) {
    e.preventDefault();
    
    try {
        showLoading();
        
        const formData = new FormData(e.target);
        const assessmentData = Object.fromEntries(formData.entries());
        
        // Convert score to number
        assessmentData.base_score = parseFloat(assessmentData.base_score);
        
        // Remove empty optional fields
        if (!assessmentData.context_id) delete assessmentData.context_id;
        if (!assessmentData.tech_level_id) delete assessmentData.tech_level_id;
        if (!assessmentData.notes) delete assessmentData.notes;
        
        const response = await apiRequest('/assessments', 'POST', assessmentData);
        
        hideLoading();
        showMessage('تم حفظ التقييم بنجاح', 'success');
        
        // Reset form
        e.target.reset();
        
        // Refresh dashboard data
        if (currentSection === 'dashboard') {
            loadDashboardData();
        }
        
    } catch (error) {
        console.error('Error submitting assessment:', error);
        hideLoading();
        showMessage('خطأ في حفظ التقييم: ' + error.message, 'error');
    }
}

// Handle EPA selection change
async function handleEPASelectionChange(e) {
    const epaId = e.target.value;
    const indicatorSelect = document.getElementById('indicator-select');
    
    // Clear indicator options
    indicatorSelect.innerHTML = '<option value="">اختر مؤشر الأداء</option>';
    
    if (!epaId) return;
    
    try {
        showLoading();
        
        // Get EPA details with indicators
        const response = await apiRequest(`/epas/${epaId}`);
        const epa = response.epa;
        
        // Populate indicators
        if (epa.smaller_epas) {
            epa.smaller_epas.forEach(smallerEpa => {
                if (smallerEpa.activities) {
                    smallerEpa.activities.forEach(activity => {
                        // For demo, we'll use activity IDs as indicator IDs
                        // In real implementation, you'd fetch actual indicators
                        const option = document.createElement('option');
                        option.value = activity.activity_id + '_IND_1'; // Demo indicator ID
                        option.textContent = activity.activity_name;
                        indicatorSelect.appendChild(option);
                    });
                }
            });
        }
        
        hideLoading();
        
    } catch (error) {
        console.error('Error loading EPA details:', error);
        hideLoading();
        showMessage('خطأ في تحميل تفاصيل النشاط المهني', 'error');
    }
}

// Load dashboard data
function loadDashboardData() {
    // Update stats
    updateDashboardStats();
    
    // Load EPA overview
    loadEPAOverview();
    
    // Load recent activity
    loadRecentActivity();
}

// Update dashboard statistics
function updateDashboardStats() {
    // Update total students (already updated in loadStudents)
    
    // Update total assessments (demo data)
    document.getElementById('total-assessments').textContent = '156';
    
    // Update average score (demo data)
    document.getElementById('avg-score').textContent = '3.8';
}

// Load EPA overview for dashboard
function loadEPAOverview() {
    const epaGrid = document.getElementById('epa-grid');
    if (!epaGrid) return;
    
    epaGrid.innerHTML = '';
    
    epasData.forEach(epa => {
        const epaCard = createEPACard(epa);
        epaGrid.appendChild(epaCard);
    });
}

// Create EPA card element
function createEPACard(epa) {
    const card = document.createElement('div');
    card.className = 'card epa-card';
    
    // Demo score data
    const demoScore = (Math.random() * 2 + 3).toFixed(1); // Random score between 3.0-5.0
    const demoCount = Math.floor(Math.random() * 20 + 5); // Random count between 5-25
    
    card.innerHTML = `
        <div class="epa-header">
            <h4>${epa.epa_name}</h4>
            <span class="epa-weight">${epa.total_weight}%</span>
        </div>
        <div class="epa-stats">
            <div class="epa-stat">
                <span class="stat-label">متوسط النقاط</span>
                <span class="stat-value">${demoScore}</span>
            </div>
            <div class="epa-stat">
                <span class="stat-label">عدد التقييمات</span>
                <span class="stat-value">${demoCount}</span>
            </div>
        </div>
        <div class="epa-progress">
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${(demoScore / 5) * 100}%"></div>
            </div>
        </div>
    `;
    
    return card;
}

// Load recent activity
function loadRecentActivity() {
    const activityList = document.getElementById('recent-activity');
    if (!activityList) return;
    
    // Demo recent activities
    const recentActivities = [
        { student: 'أحمد محمد علي', epa: 'EPA 1', score: 4.2, date: '2024-01-15' },
        { student: 'فاطمة حسن محمود', epa: 'EPA 3', score: 3.8, date: '2024-01-15' },
        { student: 'محمد عبدالله سالم', epa: 'EPA 5', score: 4.5, date: '2024-01-14' },
        { student: 'نورا أحمد خالد', epa: 'EPA 2', score: 3.9, date: '2024-01-14' },
        { student: 'عبدالرحمن يوسف', epa: 'EPA 4', score: 4.1, date: '2024-01-13' }
    ];
    
    activityList.innerHTML = '';
    
    recentActivities.forEach(activity => {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        
        activityItem.innerHTML = `
            <div class="activity-content">
                <div class="activity-main">
                    <span class="student-name">${activity.student}</span>
                    <span class="epa-name">${activity.epa}</span>
                </div>
                <div class="activity-meta">
                    <span class="score">النقاط: ${activity.score}</span>
                    <span class="date">${activity.date}</span>
                </div>
            </div>
        `;
        
        activityList.appendChild(activityItem);
    });
}

// Load assessment form data
function loadAssessmentFormData() {
    populateStudentSelect();
    populateFacultySelect();
    populateEPASelect();
    populateContextSelect();
}

// Populate student select options
function populateStudentSelect() {
    const studentSelect = document.getElementById('student-select');
    if (!studentSelect) return;
    
    studentSelect.innerHTML = '<option value="">اختر الطالب</option>';
    
    studentsData.forEach(student => {
        const option = document.createElement('option');
        option.value = student.student_id;
        option.textContent = student.student_name;
        studentSelect.appendChild(option);
    });
}

// Populate faculty select options
function populateFacultySelect() {
    const facultySelect = document.getElementById('assessor-select');
    if (!facultySelect) return;
    
    facultySelect.innerHTML = '<option value="">اختر المقيم</option>';
    
    facultyData.forEach(faculty => {
        const option = document.createElement('option');
        option.value = faculty.faculty_id;
        option.textContent = faculty.faculty_name;
        facultySelect.appendChild(option);
    });
}

// Populate EPA select options
function populateEPASelect() {
    const epaSelect = document.getElementById('epa-select');
    if (!epaSelect) return;
    
    epaSelect.innerHTML = '<option value="">اختر النشاط المهني</option>';
    
    epasData.forEach(epa => {
        const option = document.createElement('option');
        option.value = epa.epa_id;
        option.textContent = `${epa.epa_id} - ${epa.epa_name}`;
        epaSelect.appendChild(option);
    });
}

// Populate context select options
function populateContextSelect() {
    const contextSelect = document.getElementById('context-select');
    if (!contextSelect) return;
    
    contextSelect.innerHTML = '<option value="">اختر بيئة الرعاية</option>';
    
    contextsData.forEach(context => {
        const option = document.createElement('option');
        option.value = context.context_id;
        option.textContent = context.context_name;
        contextSelect.appendChild(option);
    });
}

// Load students section data
function loadStudentsData() {
    const studentsGrid = document.getElementById('students-grid');
    if (!studentsGrid) return;
    
    studentsGrid.innerHTML = '';
    
    studentsData.forEach(student => {
        const studentCard = createStudentCard(student);
        studentsGrid.appendChild(studentCard);
    });
}

// Create student card element
function createStudentCard(student) {
    const card = document.createElement('div');
    card.className = 'card student-card';
    
    // Demo data for student
    const demoAvgScore = (Math.random() * 2 + 3).toFixed(1);
    const demoAssessments = Math.floor(Math.random() * 15 + 5);
    
    card.innerHTML = `
        <div class="student-header">
            <div class="student-avatar">
                <i class="fas fa-user-graduate"></i>
            </div>
            <div class="student-info">
                <h4>${student.student_name}</h4>
                <p>${student.program} - السنة ${student.year_level}</p>
            </div>
        </div>
        <div class="student-stats">
            <div class="stat">
                <span class="stat-label">متوسط النقاط</span>
                <span class="stat-value">${demoAvgScore}</span>
            </div>
            <div class="stat">
                <span class="stat-label">عدد التقييمات</span>
                <span class="stat-value">${demoAssessments}</span>
            </div>
        </div>
        <div class="student-actions">
            <button class="btn btn-primary btn-sm" onclick="viewStudentProfile('${student.student_id}')">
                <i class="fas fa-eye"></i>
                عرض الملف
            </button>
        </div>
    `;
    
    return card;
}

// Load reports section data
function loadReportsData() {
    // Populate report selects
    populateReportStudentSelect();
    populateReportEPASelect();
}

// Populate report student select
function populateReportStudentSelect() {
    const reportStudentSelect = document.getElementById('report-student-select');
    if (!reportStudentSelect) return;
    
    reportStudentSelect.innerHTML = '<option value="">اختر الطالب</option>';
    
    studentsData.forEach(student => {
        const option = document.createElement('option');
        option.value = student.student_id;
        option.textContent = student.student_name;
        reportStudentSelect.appendChild(option);
    });
}

// Populate report EPA select
function populateReportEPASelect() {
    const reportEPASelect = document.getElementById('report-epa-select');
    if (!reportEPASelect) return;
    
    reportEPASelect.innerHTML = '<option value="">اختر النشاط المهني</option>';
    
    epasData.forEach(epa => {
        const option = document.createElement('option');
        option.value = epa.epa_id;
        option.textContent = `${epa.epa_id} - ${epa.epa_name}`;
        reportEPASelect.appendChild(option);
    });
}

// Utility functions
function showLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.add('show');
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('show');
    }
}

function showMessage(message, type = 'success') {
    const messageContainer = document.getElementById('message-container');
    if (!messageContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'exclamation-triangle'}"></i>
        ${message}
    `;
    
    messageContainer.appendChild(messageElement);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}

// Report generation functions
function generateStudentReport() {
    const studentId = document.getElementById('report-student-select').value;
    if (!studentId) {
        showMessage('يرجى اختيار الطالب', 'warning');
        return;
    }
    
    showMessage('جاري إنشاء تقرير الطالب...', 'success');
    // Implementation would call API to generate report
}

function generateEPAReport() {
    const epaId = document.getElementById('report-epa-select').value;
    if (!epaId) {
        showMessage('يرجى اختيار النشاط المهني', 'warning');
        return;
    }
    
    showMessage('جاري إنشاء تقرير النشاط المهني...', 'success');
    // Implementation would call API to generate report
}

function generateQualityReport() {
    showMessage('جاري إنشاء تقرير الجودة...', 'success');
    // Implementation would call API to generate quality report
}

function viewStudentProfile(studentId) {
    showMessage(`عرض ملف الطالب: ${studentId}`, 'success');
    // Implementation would show detailed student profile
}

