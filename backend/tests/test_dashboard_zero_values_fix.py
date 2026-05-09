"""
Property-Based Tests for Dashboard Zero Values Fix

This test file contains bug condition exploration tests that demonstrate
the bug exists in the unfixed code. These tests are EXPECTED TO FAIL
on unfixed code (confirming the bug) and PASS after the fix is implemented.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
"""
import os
import sys

# Set environment variables BEFORE importing app
os.environ["DATABASE_URL"] = "mysql+pymysql://root:@localhost/test_dashboard_bugfix"
os.environ["SECRET_KEY"] = "test-secret-key-for-dashboard-bugfix-tests"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, Phase
from hypothesis import assume

from app.main import app
from app.database import Base, get_db
from app.models import Patient, Consultation, Diagnostic, DossierMedical

# Test database setup - Use MySQL test database instead of SQLite
# to avoid ENUM compatibility issues
SQLALCHEMY_TEST_DATABASE_URL = "mysql+pymysql://root:@localhost/test_dashboard_bugfix"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create test database tables"""
    # Drop and recreate test database
    from sqlalchemy import create_engine as create_temp_engine, text
    temp_engine = create_temp_engine("mysql+pymysql://root:@localhost/")
    with temp_engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS test_dashboard_bugfix"))
        conn.execute(text("CREATE DATABASE test_dashboard_bugfix"))
        conn.commit()
    temp_engine.dispose()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    temp_engine = create_temp_engine("mysql+pymysql://root:@localhost/")
    with temp_engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS test_dashboard_bugfix"))
        conn.commit()
    temp_engine.dispose()


@pytest.fixture(autouse=True)
def clean_database():
    """Clean database before each test"""
    db = TestingSessionLocal()
    try:
        # Delete in correct order to respect foreign keys
        db.query(Diagnostic).delete()
        db.query(Consultation).delete()
        db.query(DossierMedical).delete()
        db.query(Patient).delete()
        db.commit()
    finally:
        db.close()
    yield


# ══════════════════════════════════════════════════════════════════════════════
# Property 1: Bug Condition - Dashboard Statistics Missing Fields
# ══════════════════════════════════════════════════════════════════════════════

class TestBugConditionExploration:
    """
    Bug Condition Exploration Tests
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
    
    These tests demonstrate the bug exists by generating random database states
    and verifying that the API fails to return the required fields or returns
    incorrect values.
    
    EXPECTED OUTCOME ON UNFIXED CODE: FAIL (confirms bug exists)
    EXPECTED OUTCOME ON FIXED CODE: PASS (confirms bug is fixed)
    """
    
    @given(
        num_consultations_today=st.integers(min_value=0, max_value=20),
        num_consultations_yesterday=st.integers(min_value=0, max_value=10),
        num_diagnostics_confirmes=st.integers(min_value=0, max_value=30),
        num_diagnostics_rejetes=st.integers(min_value=0, max_value=15),
        num_diagnostics_provisoires=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=50, phases=[Phase.generate, Phase.target])
    def test_property_dashboard_statistics_completeness(
        self,
        num_consultations_today,
        num_consultations_yesterday,
        num_diagnostics_confirmes,
        num_diagnostics_rejetes,
        num_diagnostics_provisoires,
    ):
        """
        Property 1: Bug Condition - Dashboard Statistics Completeness
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**
        
        FOR ALL dashboard requests with random database states:
          - The API response SHALL contain consultations_aujourd_hui field
          - The API response SHALL contain diagnostics_approuves field
          - The API response SHALL contain diagnostics_rejetes field
          - The values SHALL match actual database counts
        
        This test generates random database states and verifies the API
        returns correct counts for all three statistics.
        """
        db = TestingSessionLocal()
        
        try:
            # Clean database before each example to avoid data pollution
            db.query(Diagnostic).delete()
            db.query(Consultation).delete()
            db.query(DossierMedical).delete()
            db.query(Patient).delete()
            db.commit()
            # Generate random database state
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            
            # Create a patient and dossier for foreign key constraints
            patient = Patient(
                nom="TEST",
                prenoms="Patient",
                date_naissance=datetime(1990, 1, 1),
                sexe="M",
                telephone="0000000000",
                adresse="Test Address"
            )
            db.add(patient)
            db.flush()
            
            dossier = DossierMedical(
                patient_id=patient.patient_id,
                numero_dossier=f"DOSS-{patient.patient_id}",
                allergies="None"
            )
            db.add(dossier)
            db.flush()
            
            # Create consultations for today
            consultations_today = []
            for i in range(num_consultations_today):
                # Random time today between 00:00 and 23:59
                hours = i % 24
                minutes = (i * 13) % 60
                consultation_time = today.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                
                consultation = Consultation(
                    patient_id=patient.patient_id,
                    nom_patient=f"Patient {i}",
                    date_heure=consultation_time,
                    motif=f"Test motif {i}",
                    statut="en attente"
                )
                db.add(consultation)
                consultations_today.append(consultation)
            
            # Create consultations for yesterday (should NOT be counted)
            for i in range(num_consultations_yesterday):
                hours = i % 24
                minutes = (i * 17) % 60
                consultation_time = yesterday.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                
                consultation = Consultation(
                    patient_id=patient.patient_id,
                    nom_patient=f"Patient Yesterday {i}",
                    date_heure=consultation_time,
                    motif=f"Test motif yesterday {i}",
                    statut="terminée"
                )
                db.add(consultation)
            
            db.flush()
            
            # Create diagnostics with various statuses
            # We need at least one consultation for diagnostics
            extra_consultation_created = False
            if len(consultations_today) > 0:
                consultation_for_diagnostics = consultations_today[0]
            else:
                # Create a consultation for diagnostics if none exist
                # This consultation will be counted in consultations_aujourd_hui
                consultation_for_diagnostics = Consultation(
                    patient_id=patient.patient_id,
                    nom_patient="Patient for Diagnostics",
                    date_heure=today,
                    motif="Test motif for diagnostics",
                    statut="en cours"
                )
                db.add(consultation_for_diagnostics)
                db.flush()
                extra_consultation_created = True
            
            # Create CONFIRMÉ diagnostics
            for i in range(num_diagnostics_confirmes):
                diagnostic = Diagnostic(
                    consultation_id=consultation_for_diagnostics.consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Maladie Confirmée {i}",
                    statut="CONFIRMÉ",
                    certitude=0.9
                )
                db.add(diagnostic)
            
            # Create REJETÉ diagnostics
            for i in range(num_diagnostics_rejetes):
                diagnostic = Diagnostic(
                    consultation_id=consultation_for_diagnostics.consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Maladie Rejetée {i}",
                    statut="REJETÉ",
                    certitude=0.3
                )
                db.add(diagnostic)
            
            # Create PROVISOIRE diagnostics (should NOT be counted in approuvés or rejetés)
            for i in range(num_diagnostics_provisoires):
                diagnostic = Diagnostic(
                    consultation_id=consultation_for_diagnostics.consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Maladie Provisoire {i}",
                    statut="PROVISOIRE",
                    certitude=0.5
                )
                db.add(diagnostic)
            
            db.commit()
            
            # Call the API endpoint
            response = client.get("/api/analytics/dashboard")
            
            # Verify response status
            assert response.status_code == 200, f"API returned status {response.status_code}"
            
            data = response.json()
            
            # Verify response structure
            assert "kpis" in data, "Response missing 'kpis' object"
            kpis = data["kpis"]
            
            # ═══════════════════════════════════════════════════════════════════
            # BUG CONDITION CHECKS - These will FAIL on unfixed code
            # ═══════════════════════════════════════════════════════════════════
            
            # Check 1: consultations_aujourd_hui field exists
            assert "consultations_aujourd_hui" in kpis, (
                f"BUG DETECTED: API response missing 'consultations_aujourd_hui' field. "
                f"Expected field in kpis object. This confirms Requirement 1.5 violation."
            )
            
            # Check 2: diagnostics_approuves field exists
            assert "diagnostics_approuves" in kpis, (
                f"BUG DETECTED: API response missing 'diagnostics_approuves' field. "
                f"Expected field in kpis object. This confirms Requirement 1.5 violation."
            )
            
            # Check 3: diagnostics_rejetes field exists
            assert "diagnostics_rejetes" in kpis, (
                f"BUG DETECTED: API response missing 'diagnostics_rejetes' field. "
                f"Expected field in kpis object. This confirms Requirement 1.5 violation."
            )
            
            # Check 4: consultations_aujourd_hui has correct value
            # Account for the extra consultation created for diagnostics if needed
            expected_consultations_today = num_consultations_today
            if extra_consultation_created:
                expected_consultations_today += 1
            
            actual_consultations_today = kpis["consultations_aujourd_hui"]
            assert actual_consultations_today == expected_consultations_today, (
                f"BUG DETECTED: consultations_aujourd_hui = {actual_consultations_today}, "
                f"expected {expected_consultations_today}. "
                f"Database has {expected_consultations_today} consultations created today, "
                f"but API returns {actual_consultations_today}. "
                f"This confirms Requirements 1.1, 2.1, 2.6 violation."
            )
            
            # Check 5: diagnostics_approuves has correct value
            actual_diagnostics_approuves = kpis["diagnostics_approuves"]
            assert actual_diagnostics_approuves == num_diagnostics_confirmes, (
                f"BUG DETECTED: diagnostics_approuves = {actual_diagnostics_approuves}, "
                f"expected {num_diagnostics_confirmes}. "
                f"Database has {num_diagnostics_confirmes} diagnostics with status CONFIRMÉ, "
                f"but API returns {actual_diagnostics_approuves}. "
                f"This confirms Requirements 1.2, 2.2, 2.7 violation."
            )
            
            # Check 6: diagnostics_rejetes has correct value
            actual_diagnostics_rejetes = kpis["diagnostics_rejetes"]
            assert actual_diagnostics_rejetes == num_diagnostics_rejetes, (
                f"BUG DETECTED: diagnostics_rejetes = {actual_diagnostics_rejetes}, "
                f"expected {num_diagnostics_rejetes}. "
                f"Database has {num_diagnostics_rejetes} diagnostics with status REJETÉ, "
                f"but API returns {actual_diagnostics_rejetes}. "
                f"This confirms Requirements 1.3, 2.3, 2.8 violation."
            )
            
            # Check 7: Values are non-negative
            assert actual_consultations_today >= 0, "consultations_aujourd_hui must be >= 0"
            assert actual_diagnostics_approuves >= 0, "diagnostics_approuves must be >= 0"
            assert actual_diagnostics_rejetes >= 0, "diagnostics_rejetes must be >= 0"
            
        finally:
            db.close()
    
    def test_bug_condition_with_specific_counterexample(self):
        """
        Specific counterexample demonstrating the bug
        
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
        
        This test uses a concrete example from the bugfix.md:
        - 5 consultations created today
        - 12 diagnostics with status "CONFIRMÉ"
        - 3 diagnostics with status "REJETÉ"
        
        EXPECTED ON UNFIXED CODE:
        - API response missing the three fields OR
        - Frontend displays 0 for all three statistics
        
        EXPECTED ON FIXED CODE:
        - API returns consultations_aujourd_hui: 5
        - API returns diagnostics_approuves: 12
        - API returns diagnostics_rejetes: 3
        """
        db = TestingSessionLocal()
        
        try:
            today = datetime.now()
            
            # Create patient and dossier
            patient = Patient(
                nom="KOUASSI",
                prenoms="Jean",
                date_naissance=datetime(1985, 5, 15),
                sexe="M",
                telephone="0123456789",
                adresse="Abidjan"
            )
            db.add(patient)
            db.flush()
            
            dossier = DossierMedical(
                patient_id=patient.patient_id,
                numero_dossier=f"DOSS-{patient.patient_id}",
                allergies="None"
            )
            db.add(dossier)
            db.flush()
            
            # Create 5 consultations today
            consultations = []
            for i in range(5):
                consultation = Consultation(
                    patient_id=patient.patient_id,
                    nom_patient=f"Patient {i}",
                    date_heure=today.replace(hour=8+i, minute=0, second=0, microsecond=0),
                    motif=f"Consultation {i}",
                    statut="terminée"
                )
                db.add(consultation)
                consultations.append(consultation)
            
            db.flush()
            
            # Create 12 diagnostics CONFIRMÉ
            for i in range(12):
                diagnostic = Diagnostic(
                    consultation_id=consultations[i % 5].consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Maladie Confirmée {i}",
                    statut="CONFIRMÉ",
                    certitude=0.85
                )
                db.add(diagnostic)
            
            # Create 3 diagnostics REJETÉ
            for i in range(3):
                diagnostic = Diagnostic(
                    consultation_id=consultations[i].consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Maladie Rejetée {i}",
                    statut="REJETÉ",
                    certitude=0.25
                )
                db.add(diagnostic)
            
            db.commit()
            
            # Call API
            response = client.get("/api/analytics/dashboard")
            assert response.status_code == 200
            
            data = response.json()
            assert "kpis" in data
            kpis = data["kpis"]
            
            # Verify the three fields exist and have correct values
            assert "consultations_aujourd_hui" in kpis, (
                "BUG: API response missing 'consultations_aujourd_hui' field. "
                "This is the concrete counterexample from bugfix.md."
            )
            assert kpis["consultations_aujourd_hui"] == 5, (
                f"BUG: Expected consultations_aujourd_hui=5, got {kpis['consultations_aujourd_hui']}"
            )
            
            assert "diagnostics_approuves" in kpis, (
                "BUG: API response missing 'diagnostics_approuves' field. "
                "This is the concrete counterexample from bugfix.md."
            )
            assert kpis["diagnostics_approuves"] == 12, (
                f"BUG: Expected diagnostics_approuves=12, got {kpis['diagnostics_approuves']}"
            )
            
            assert "diagnostics_rejetes" in kpis, (
                "BUG: API response missing 'diagnostics_rejetes' field. "
                "This is the concrete counterexample from bugfix.md."
            )
            assert kpis["diagnostics_rejetes"] == 3, (
                f"BUG: Expected diagnostics_rejetes=3, got {kpis['diagnostics_rejetes']}"
            )
            
        finally:
            db.close()
    
    def test_bug_condition_edge_case_zero_values(self):
        """
        Edge case: Zero values should be legitimate when no data exists
        
        **Validates: Requirements 3.8**
        
        When no consultations exist today and no diagnostics exist,
        the system should return 0 for all three statistics.
        This is NOT a bug - it's the correct behavior.
        """
        db = TestingSessionLocal()
        
        try:
            # Database is empty (cleaned by fixture)
            
            # Call API
            response = client.get("/api/analytics/dashboard")
            assert response.status_code == 200
            
            data = response.json()
            assert "kpis" in data
            kpis = data["kpis"]
            
            # Fields must exist even when values are 0
            assert "consultations_aujourd_hui" in kpis, (
                "BUG: API response missing 'consultations_aujourd_hui' field even with empty database"
            )
            assert "diagnostics_approuves" in kpis, (
                "BUG: API response missing 'diagnostics_approuves' field even with empty database"
            )
            assert "diagnostics_rejetes" in kpis, (
                "BUG: API response missing 'diagnostics_rejetes' field even with empty database"
            )
            
            # Values should be 0 (this is correct, not a bug)
            assert kpis["consultations_aujourd_hui"] == 0
            assert kpis["diagnostics_approuves"] == 0
            assert kpis["diagnostics_rejetes"] == 0
            
        finally:
            db.close()
    
    def test_bug_condition_consultations_time_boundary(self):
        """
        Test time boundary for "today" calculation
        
        **Validates: Requirements 2.6**
        
        Consultations created at 00:00:00 and 23:59:59 today should be counted.
        Consultations created yesterday at 23:59:59 should NOT be counted.
        """
        db = TestingSessionLocal()
        
        try:
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            
            # Create patient
            patient = Patient(
                nom="TEST",
                prenoms="Boundary",
                date_naissance=datetime(1990, 1, 1),
                sexe="F",
                telephone="0000000000",
                adresse="Test"
            )
            db.add(patient)
            db.flush()
            
            # Consultation at start of today (00:00:00)
            consultation_start = Consultation(
                patient_id=patient.patient_id,
                nom_patient="Patient Start",
                date_heure=today.replace(hour=0, minute=0, second=0, microsecond=0),
                motif="Start of day",
                statut="en attente"
            )
            db.add(consultation_start)
            
            # Consultation at end of today (23:59:59)
            consultation_end = Consultation(
                patient_id=patient.patient_id,
                nom_patient="Patient End",
                date_heure=today.replace(hour=23, minute=59, second=59, microsecond=999999),
                motif="End of day",
                statut="en attente"
            )
            db.add(consultation_end)
            
            # Consultation yesterday (should NOT be counted)
            consultation_yesterday = Consultation(
                patient_id=patient.patient_id,
                nom_patient="Patient Yesterday",
                date_heure=yesterday.replace(hour=23, minute=59, second=59, microsecond=999999),
                motif="Yesterday",
                statut="terminée"
            )
            db.add(consultation_yesterday)
            
            db.commit()
            
            # Call API
            response = client.get("/api/analytics/dashboard")
            assert response.status_code == 200
            
            data = response.json()
            kpis = data["kpis"]
            
            # Should count exactly 2 consultations (start and end of today)
            assert "consultations_aujourd_hui" in kpis, (
                "BUG: API response missing 'consultations_aujourd_hui' field"
            )
            assert kpis["consultations_aujourd_hui"] == 2, (
                f"BUG: Expected 2 consultations today (00:00:00 and 23:59:59), "
                f"got {kpis['consultations_aujourd_hui']}. "
                f"Yesterday's consultation should NOT be counted."
            )
            
        finally:
            db.close()


# ══════════════════════════════════════════════════════════════════════════════
# Property 2: Preservation - Existing Dashboard Statistics Unchanged
# ══════════════════════════════════════════════════════════════════════════════

class TestPreservationProperty:
    """
    Preservation Property Tests
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**
    
    These tests observe and capture the behavior of existing dashboard statistics
    on UNFIXED code. They verify that after the fix, all existing statistics
    continue to work exactly as before (no regressions).
    
    EXPECTED OUTCOME ON UNFIXED CODE: PASS (confirms baseline behavior)
    EXPECTED OUTCOME ON FIXED CODE: PASS (confirms no regressions)
    """
    
    @given(
        num_patients=st.integers(min_value=1, max_value=20),  # At least 1 patient to avoid edge cases
        num_consultations_attente=st.integers(min_value=0, max_value=10),
        num_consultations_cours=st.integers(min_value=0, max_value=10),
        num_consultations_terminees=st.integers(min_value=0, max_value=10),
        num_diagnostics_confirmes=st.integers(min_value=0, max_value=10),
        num_diagnostics_rejetes=st.integers(min_value=0, max_value=5),
        num_diagnostics_provisoires=st.integers(min_value=0, max_value=5),
    )
    @settings(max_examples=20, phases=[Phase.generate, Phase.target], deadline=timedelta(seconds=2))
    def test_property_existing_statistics_unchanged(
        self,
        num_patients,
        num_consultations_attente,
        num_consultations_cours,
        num_consultations_terminees,
        num_diagnostics_confirmes,
        num_diagnostics_rejetes,
        num_diagnostics_provisoires,
    ):
        """
        Property 2: Preservation - Existing Dashboard Statistics Unchanged
        
        **Validates: Requirements 3.1, 3.2, 3.6**
        
        FOR ALL dashboard requests with random database states:
          - All existing KPI fields SHALL return correct values
          - The response structure SHALL match the expected schema
          - All calculations SHALL use the same logic as before
        
        This test generates random database states and verifies that existing
        statistics are calculated correctly and consistently.
        """
        db = TestingSessionLocal()
        
        try:
            today = datetime.now()
            first_day_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Create patients (some this month, some before)
            patients_this_month = 0
            for i in range(num_patients):
                # 70% chance patient was created this month
                if i < int(num_patients * 0.7):
                    created_at = today - timedelta(days=i % 28)
                    if created_at >= first_day_month:
                        patients_this_month += 1
                else:
                    # Created before this month
                    created_at = today - timedelta(days=35 + i)
                
                patient = Patient(
                    nom=f"Patient{i}",
                    prenoms=f"Test{i}",
                    date_naissance=datetime(1980 + (i % 40), 1 + (i % 12), 1 + (i % 28)),
                    sexe="M" if i % 2 == 0 else "F",
                    telephone=f"0{i:09d}",
                    adresse=f"Address {i}",
                    created_at=created_at
                )
                db.add(patient)
            
            db.flush()
            
            # Get all patients for foreign keys
            all_patients = db.query(Patient).all()
            
            # Only create a default patient if we need consultations but have no patients
            if not all_patients and (num_consultations_attente > 0 or num_consultations_cours > 0 or num_consultations_terminees > 0):
                patient = Patient(
                    nom="DefaultPatient",
                    prenoms="Test",
                    date_naissance=datetime(1990, 1, 1),
                    sexe="M",
                    telephone="0000000000",
                    adresse="Default Address"
                )
                db.add(patient)
                db.flush()
                all_patients = [patient]
                # Adjust expected count since we created a patient
                expected_total_patients = 1
                # Check if this patient was created this month
                if patient.created_at >= first_day_month:
                    patients_this_month = 1
            
            # Create dossiers for patients (only if they don't already exist)
            for patient in all_patients:
                existing_dossier = db.query(DossierMedical).filter(
                    DossierMedical.patient_id == patient.patient_id
                ).first()
                
                if not existing_dossier:
                    dossier = DossierMedical(
                        patient_id=patient.patient_id,
                        numero_dossier=f"DOSS-{patient.patient_id}",
                        allergies="None"
                    )
                    db.add(dossier)
            
            db.flush()
            
            # Create consultations with different statuses
            consultations = []
            
            # Only create consultations if we have patients
            if all_patients:
                # Consultations en attente
                for i in range(num_consultations_attente):
                    patient = all_patients[i % len(all_patients)]
                    consultation = Consultation(
                        patient_id=patient.patient_id,
                        nom_patient=f"{patient.nom} {patient.prenoms}",
                        date_heure=today - timedelta(hours=i),
                        motif=f"Motif attente {i}",
                        statut="en attente"
                    )
                    db.add(consultation)
                    consultations.append(consultation)
                
                # Consultations en cours
                for i in range(num_consultations_cours):
                    patient = all_patients[i % len(all_patients)]
                    consultation = Consultation(
                        patient_id=patient.patient_id,
                        nom_patient=f"{patient.nom} {patient.prenoms}",
                        date_heure=today - timedelta(hours=i + num_consultations_attente),
                        motif=f"Motif en cours {i}",
                        statut="en cours"
                    )
                    db.add(consultation)
                    consultations.append(consultation)
                
                # Consultations terminées
                for i in range(num_consultations_terminees):
                    patient = all_patients[i % len(all_patients)]
                    consultation = Consultation(
                        patient_id=patient.patient_id,
                        nom_patient=f"{patient.nom} {patient.prenoms}",
                        date_heure=today - timedelta(days=i % 30),
                        motif=f"Motif terminée {i}",
                        statut="terminée"
                    )
                    db.add(consultation)
                    consultations.append(consultation)
            
            db.flush()
            
            # Create diagnostics with various statuses
            total_diagnostics = num_diagnostics_confirmes + num_diagnostics_rejetes + num_diagnostics_provisoires
            certitudes = []
            
            if consultations:
                # Create CONFIRMÉ diagnostics
                for i in range(num_diagnostics_confirmes):
                    consultation = consultations[i % len(consultations)]
                    dossier = db.query(DossierMedical).filter(
                        DossierMedical.patient_id == consultation.patient_id
                    ).first()
                    
                    certitude = 0.7 + (i % 30) / 100  # 0.7 to 0.99
                    certitudes.append(certitude)
                    
                    diagnostic = Diagnostic(
                        consultation_id=consultation.consultation_id,
                        dossier_id=dossier.dossier_id,
                        nom_maladie=f"Maladie Confirmée {i}",
                        statut="CONFIRMÉ",
                        certitude=certitude
                    )
                    db.add(diagnostic)
                
                # Create REJETÉ diagnostics
                for i in range(num_diagnostics_rejetes):
                    consultation = consultations[i % len(consultations)]
                    dossier = db.query(DossierMedical).filter(
                        DossierMedical.patient_id == consultation.patient_id
                    ).first()
                    
                    certitude = 0.2 + (i % 30) / 100  # 0.2 to 0.49
                    certitudes.append(certitude)
                    
                    diagnostic = Diagnostic(
                        consultation_id=consultation.consultation_id,
                        dossier_id=dossier.dossier_id,
                        nom_maladie=f"Maladie Rejetée {i}",
                        statut="REJETÉ",
                        certitude=certitude
                    )
                    db.add(diagnostic)
                
                # Create PROVISOIRE diagnostics
                for i in range(num_diagnostics_provisoires):
                    consultation = consultations[i % len(consultations)]
                    dossier = db.query(DossierMedical).filter(
                        DossierMedical.patient_id == consultation.patient_id
                    ).first()
                    
                    certitude = 0.5 + (i % 30) / 100  # 0.5 to 0.79
                    certitudes.append(certitude)
                    
                    diagnostic = Diagnostic(
                        consultation_id=consultation.consultation_id,
                        dossier_id=dossier.dossier_id,
                        nom_maladie=f"Maladie Provisoire {i}",
                        statut="PROVISOIRE",
                        certitude=certitude
                    )
                    db.add(diagnostic)
            
            db.commit()
            
            # Calculate expected values by querying the actual database state
            # This ensures we're comparing against what's actually in the DB
            expected_total_patients = db.query(func.count(Patient.patient_id)).scalar() or 0
            expected_patients_ce_mois = db.query(func.count(Patient.patient_id)).filter(
                Patient.created_at >= first_day_month
            ).scalar() or 0
            expected_total_consultations = db.query(func.count(Consultation.consultation_id)).scalar() or 0
            expected_consultations_en_attente = db.query(func.count(Consultation.consultation_id)).filter(
                Consultation.statut == "en attente"
            ).scalar() or 0
            expected_consultations_en_cours = db.query(func.count(Consultation.consultation_id)).filter(
                Consultation.statut == "en cours"
            ).scalar() or 0
            expected_consultations_terminees = db.query(func.count(Consultation.consultation_id)).filter(
                Consultation.statut == "terminée"
            ).scalar() or 0
            expected_total_diagnostics = db.query(func.count(Diagnostic.diagnostic_id)).scalar() or 0
            
            diagnostics_confirmes_count = db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.statut == "CONFIRMÉ"
            ).scalar() or 0
            expected_taux_approbation = (diagnostics_confirmes_count / expected_total_diagnostics * 100) if expected_total_diagnostics > 0 else 0
            
            avg_certitude = db.query(func.avg(Diagnostic.certitude)).scalar() or 0
            expected_confiance_moyenne = float(avg_certitude) * 100
            
            # Call the API endpoint
            response = client.get("/api/analytics/dashboard")
            
            # Verify response status
            assert response.status_code == 200, f"API returned status {response.status_code}"
            
            data = response.json()
            
            # ═══════════════════════════════════════════════════════════════════
            # PRESERVATION CHECKS - These should PASS on both unfixed and fixed code
            # ═══════════════════════════════════════════════════════════════════
            
            # Check 1: Response structure
            assert "kpis" in data, "Response missing 'kpis' object"
            assert "tendance_patients" in data, "Response missing 'tendance_patients' array"
            assert "top_diagnostics" in data, "Response missing 'top_diagnostics' array"
            
            kpis = data["kpis"]
            
            # Check 2: All existing KPI fields exist
            assert "total_patients" in kpis, "Missing 'total_patients' field"
            assert "patients_ce_mois" in kpis, "Missing 'patients_ce_mois' field"
            assert "total_consultations" in kpis, "Missing 'total_consultations' field"
            assert "consultations_en_attente" in kpis, "Missing 'consultations_en_attente' field"
            assert "consultations_en_cours" in kpis, "Missing 'consultations_en_cours' field"
            assert "consultations_terminees" in kpis, "Missing 'consultations_terminees' field"
            assert "total_diagnostics" in kpis, "Missing 'total_diagnostics' field"
            assert "taux_approbation" in kpis, "Missing 'taux_approbation' field"
            assert "confiance_moyenne" in kpis, "Missing 'confiance_moyenne' field"
            
            # Check 3: Existing KPI values are correct
            assert kpis["total_patients"] == expected_total_patients, (
                f"total_patients mismatch: expected {expected_total_patients}, got {kpis['total_patients']}"
            )
            
            assert kpis["patients_ce_mois"] == expected_patients_ce_mois, (
                f"patients_ce_mois mismatch: expected {expected_patients_ce_mois}, got {kpis['patients_ce_mois']}"
            )
            
            assert kpis["total_consultations"] == expected_total_consultations, (
                f"total_consultations mismatch: expected {expected_total_consultations}, got {kpis['total_consultations']}"
            )
            
            assert kpis["consultations_en_attente"] == expected_consultations_en_attente, (
                f"consultations_en_attente mismatch: expected {expected_consultations_en_attente}, got {kpis['consultations_en_attente']}"
            )
            
            assert kpis["consultations_en_cours"] == expected_consultations_en_cours, (
                f"consultations_en_cours mismatch: expected {expected_consultations_en_cours}, got {kpis['consultations_en_cours']}"
            )
            
            assert kpis["consultations_terminees"] == expected_consultations_terminees, (
                f"consultations_terminees mismatch: expected {expected_consultations_terminees}, got {kpis['consultations_terminees']}"
            )
            
            assert kpis["total_diagnostics"] == expected_total_diagnostics, (
                f"total_diagnostics mismatch: expected {expected_total_diagnostics}, got {kpis['total_diagnostics']}"
            )
            
            # Check taux_approbation with tolerance for rounding
            assert abs(kpis["taux_approbation"] - round(expected_taux_approbation, 2)) < 0.01, (
                f"taux_approbation mismatch: expected {round(expected_taux_approbation, 2)}, got {kpis['taux_approbation']}"
            )
            
            # Check confiance_moyenne with tolerance for rounding
            assert abs(kpis["confiance_moyenne"] - round(expected_confiance_moyenne, 2)) < 0.01, (
                f"confiance_moyenne mismatch: expected {round(expected_confiance_moyenne, 2)}, got {kpis['confiance_moyenne']}"
            )
            
            # Check 4: tendance_patients structure
            assert isinstance(data["tendance_patients"], list), "tendance_patients should be a list"
            for item in data["tendance_patients"]:
                assert "date" in item, "tendance_patients item missing 'date' field"
                assert "count" in item, "tendance_patients item missing 'count' field"
            
            # Check 5: top_diagnostics structure
            assert isinstance(data["top_diagnostics"], list), "top_diagnostics should be a list"
            for item in data["top_diagnostics"]:
                assert "diagnostic" in item, "top_diagnostics item missing 'diagnostic' field"
                assert "count" in item, "top_diagnostics item missing 'count' field"
            
        finally:
            db.close()
    
    def test_preservation_empty_database(self):
        """
        Test preservation with empty database
        
        **Validates: Requirements 3.8**
        
        When the database is empty, all existing statistics should return 0
        or empty arrays. This is the correct behavior and should be preserved.
        """
        db = TestingSessionLocal()
        
        try:
            # Database is empty (cleaned by fixture)
            
            # Call API
            response = client.get("/api/analytics/dashboard")
            assert response.status_code == 200
            
            data = response.json()
            assert "kpis" in data
            kpis = data["kpis"]
            
            # All existing statistics should be 0 or empty
            assert kpis["total_patients"] == 0
            assert kpis["patients_ce_mois"] == 0
            assert kpis["total_consultations"] == 0
            assert kpis["consultations_en_attente"] == 0
            assert kpis["consultations_en_cours"] == 0
            assert kpis["consultations_terminees"] == 0
            assert kpis["total_diagnostics"] == 0
            assert kpis["taux_approbation"] == 0
            assert kpis["confiance_moyenne"] == 0
            
            # Arrays should be empty
            assert isinstance(data["tendance_patients"], list)
            assert isinstance(data["top_diagnostics"], list)
            
        finally:
            db.close()
    
    def test_preservation_response_structure(self):
        """
        Test that response structure is preserved
        
        **Validates: Requirements 3.2**
        
        The API response should have the expected structure with all
        required fields. This structure should be preserved after the fix.
        """
        db = TestingSessionLocal()
        
        try:
            # Create minimal data
            patient = Patient(
                nom="TEST",
                prenoms="Structure",
                date_naissance=datetime(1990, 1, 1),
                sexe="M",
                telephone="0000000000",
                adresse="Test"
            )
            db.add(patient)
            db.commit()
            
            # Call API
            response = client.get("/api/analytics/dashboard")
            assert response.status_code == 200
            
            data = response.json()
            
            # Verify top-level structure
            assert "kpis" in data, "Response missing 'kpis' object"
            assert "tendance_patients" in data, "Response missing 'tendance_patients' array"
            assert "top_diagnostics" in data, "Response missing 'top_diagnostics' array"
            
            # Verify kpis structure (existing fields only)
            kpis = data["kpis"]
            required_fields = [
                "total_patients",
                "patients_ce_mois",
                "total_consultations",
                "consultations_en_attente",
                "consultations_en_cours",
                "consultations_terminees",
                "total_diagnostics",
                "taux_approbation",
                "confiance_moyenne"
            ]
            
            for field in required_fields:
                assert field in kpis, f"Response missing required field '{field}'"
                assert isinstance(kpis[field], (int, float)), f"Field '{field}' should be numeric"
            
            # Verify arrays are lists
            assert isinstance(data["tendance_patients"], list)
            assert isinstance(data["top_diagnostics"], list)
            
        finally:
            db.close()
    
    def test_preservation_taux_approbation_calculation(self):
        """
        Test that taux_approbation calculation is preserved
        
        **Validates: Requirements 3.6**
        
        The taux_approbation should be calculated as:
        (diagnostics_confirmes / total_diagnostics * 100)
        
        This calculation logic should be preserved after the fix.
        """
        db = TestingSessionLocal()
        
        try:
            today = datetime.now()
            
            # Create patient and dossier
            patient = Patient(
                nom="TEST",
                prenoms="Taux",
                date_naissance=datetime(1990, 1, 1),
                sexe="M",
                telephone="0000000000",
                adresse="Test"
            )
            db.add(patient)
            db.flush()
            
            dossier = DossierMedical(
                patient_id=patient.patient_id,
                numero_dossier=f"DOSS-{patient.patient_id}",
                allergies="None"
            )
            db.add(dossier)
            db.flush()
            
            # Create consultation
            consultation = Consultation(
                patient_id=patient.patient_id,
                nom_patient="Test Patient",
                date_heure=today,
                motif="Test",
                statut="terminée"
            )
            db.add(consultation)
            db.flush()
            
            # Create 7 CONFIRMÉ diagnostics and 3 REJETÉ diagnostics
            # Expected taux_approbation = 7/10 * 100 = 70.0
            for i in range(7):
                diagnostic = Diagnostic(
                    consultation_id=consultation.consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Confirmé {i}",
                    statut="CONFIRMÉ",
                    certitude=0.9
                )
                db.add(diagnostic)
            
            for i in range(3):
                diagnostic = Diagnostic(
                    consultation_id=consultation.consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Rejeté {i}",
                    statut="REJETÉ",
                    certitude=0.3
                )
                db.add(diagnostic)
            
            db.commit()
            
            # Call API
            response = client.get("/api/analytics/dashboard")
            assert response.status_code == 200
            
            data = response.json()
            kpis = data["kpis"]
            
            # Verify taux_approbation calculation
            expected_taux = 70.0
            assert abs(kpis["taux_approbation"] - expected_taux) < 0.01, (
                f"taux_approbation calculation incorrect: expected {expected_taux}, got {kpis['taux_approbation']}"
            )
            
        finally:
            db.close()
    
    def test_preservation_confiance_moyenne_calculation(self):
        """
        Test that confiance_moyenne calculation is preserved
        
        **Validates: Requirements 3.6**
        
        The confiance_moyenne should be calculated as:
        AVG(certitude) * 100
        
        This calculation logic should be preserved after the fix.
        """
        db = TestingSessionLocal()
        
        try:
            today = datetime.now()
            
            # Create patient and dossier
            patient = Patient(
                nom="TEST",
                prenoms="Confiance",
                date_naissance=datetime(1990, 1, 1),
                sexe="M",
                telephone="0000000000",
                adresse="Test"
            )
            db.add(patient)
            db.flush()
            
            dossier = DossierMedical(
                patient_id=patient.patient_id,
                numero_dossier=f"DOSS-{patient.patient_id}",
                allergies="None"
            )
            db.add(dossier)
            db.flush()
            
            # Create consultation
            consultation = Consultation(
                patient_id=patient.patient_id,
                nom_patient="Test Patient",
                date_heure=today,
                motif="Test",
                statut="terminée"
            )
            db.add(consultation)
            db.flush()
            
            # Create diagnostics with specific certitudes
            # certitudes: 0.8, 0.9, 0.7 -> average = 0.8 -> 80.0%
            certitudes = [0.8, 0.9, 0.7]
            for i, cert in enumerate(certitudes):
                diagnostic = Diagnostic(
                    consultation_id=consultation.consultation_id,
                    dossier_id=dossier.dossier_id,
                    nom_maladie=f"Diagnostic {i}",
                    statut="CONFIRMÉ",
                    certitude=cert
                )
                db.add(diagnostic)
            
            db.commit()
            
            # Call API
            response = client.get("/api/analytics/dashboard")
            assert response.status_code == 200
            
            data = response.json()
            kpis = data["kpis"]
            
            # Verify confiance_moyenne calculation
            expected_confiance = 80.0  # (0.8 + 0.9 + 0.7) / 3 * 100
            assert abs(kpis["confiance_moyenne"] - expected_confiance) < 0.01, (
                f"confiance_moyenne calculation incorrect: expected {expected_confiance}, got {kpis['confiance_moyenne']}"
            )
            
        finally:
            db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
