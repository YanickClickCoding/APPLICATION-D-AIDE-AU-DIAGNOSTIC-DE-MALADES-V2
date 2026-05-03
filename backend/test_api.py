"""
Script de test de l'API
Teste les endpoints principaux

Usage:
    python test_api.py
"""
import requests
import json
from datetime import date, datetime

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check"""
    print("\n" + "="*80)
    print("🏥 TEST: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_model_info():
    """Test model info"""
    print("\n" + "="*80)
    print("🤖 TEST: Model Info")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/ml/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_create_patient():
    """Test création patient"""
    print("\n" + "="*80)
    print("👤 TEST: Créer un patient")
    print("="*80)
    
    patient_data = {
        "nom": "Test",
        "prenom": "Patient",
        "date_naissance": "1985-03-20",
        "sexe": "M",
        "numero_securite_sociale": "185032012345678",
        "telephone": "0612345678",
        "email": "test.patient@email.com",
        "adresse": "123 Rue Test",
        "ville": "Paris",
        "code_postal": "75001"
    }
    
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        patient = response.json()
        print(f"✅ Patient créé: {patient['prenom']} {patient['nom']}")
        print(f"   ID: {patient['id']}")
        return patient['id']
    else:
        print(f"❌ Erreur: {response.json()}")
        return None


def test_create_consultation(patient_id):
    """Test création consultation"""
    print("\n" + "="*80)
    print("📋 TEST: Créer une consultation")
    print("="*80)
    
    consultation_data = {
        "patient_id": patient_id,
        "medecin_id": 1,
        "motif": "Fièvre et toux depuis 3 jours",
        "symptomes": [
            {
                "nom": "fievre",
                "present": True,
                "severite": "modere",
                "duree_jours": 3
            },
            {
                "nom": "toux",
                "present": True,
                "severite": "leger",
                "duree_jours": 3
            },
            {
                "nom": "mal_gorge",
                "present": True,
                "severite": "leger",
                "duree_jours": 2
            }
        ],
        "signes_vitaux": {
            "saturation_o2": 97.0,
            "frequence_cardiaque": 85,
            "temperature": 38.5,
            "tension_arterielle_systolique": 125,
            "tension_arterielle_diastolique": 80
        }
    }
    
    response = requests.post(f"{BASE_URL}/consultations", json=consultation_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        consultation = response.json()
        print(f"✅ Consultation créée")
        print(f"   ID: {consultation['id']}")
        print(f"   Motif: {consultation['motif']}")
        return consultation['id']
    else:
        print(f"❌ Erreur: {response.json()}")
        return None


def test_predict(consultation_id):
    """Test prédiction"""
    print("\n" + "="*80)
    print("🔮 TEST: Prédiction diagnostic")
    print("="*80)
    
    prediction_data = {
        "consultation_id": consultation_id
    }
    
    response = requests.post(f"{BASE_URL}/ml/predict", json=prediction_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        prediction = response.json()
        print(f"✅ Prédiction effectuée")
        print(f"   Diagnostic: {prediction['diagnostic_propose']}")
        print(f"   Confiance: {prediction['confiance']*100:.2f}%")
        print(f"   Niveau: {prediction['niveau_confiance']}")
        print(f"   Temps: {prediction['temps_prediction_secondes']:.3f}s")
        
        if prediction['diagnostics_alternatifs']:
            print(f"\n   Alternatives:")
            for alt in prediction['diagnostics_alternatifs']:
                print(f"   - {alt['diagnostic']}: {alt['confiance']*100:.2f}%")
        
        return True
    else:
        print(f"❌ Erreur: {response.json()}")
        return False


def test_explain(consultation_id):
    """Test explication"""
    print("\n" + "="*80)
    print("💡 TEST: Explication diagnostic")
    print("="*80)
    
    explanation_data = {
        "consultation_id": consultation_id
    }
    
    response = requests.post(f"{BASE_URL}/ml/explain", json=explanation_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        explanation = response.json()
        print(f"✅ Explication générée")
        print(f"   Diagnostic: {explanation['diagnostic']}")
        print(f"   Confiance: {explanation['confiance']*100:.2f}%")
        
        if 'features_importantes' in explanation:
            print(f"\n   Features importantes:")
            for feat in explanation['features_importantes'][:5]:
                print(f"   - {feat['feature']}: {feat['importance']:.4f}")
        
        return True
    else:
        print(f"❌ Erreur: {response.json()}")
        return False


def test_dashboard():
    """Test dashboard"""
    print("\n" + "="*80)
    print("📊 TEST: Dashboard Analytics")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/analytics/dashboard")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        dashboard = response.json()
        print(f"✅ Dashboard récupéré")
        print(f"\n   KPIs:")
        for key, value in dashboard['kpis'].items():
            print(f"   - {key}: {value}")
        
        return True
    else:
        print(f"❌ Erreur: {response.json()}")
        return False


def main():
    """
    Exécute tous les tests
    """
    print("\n" + "="*80)
    print("🧪 TESTS DE L'API - Medical Diagnostic AI System")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    # Test 2: Model info
    results.append(("Model Info", test_model_info()))
    
    # Test 3: Créer patient
    patient_id = test_create_patient()
    results.append(("Create Patient", patient_id is not None))
    
    if patient_id:
        # Test 4: Créer consultation
        consultation_id = test_create_consultation(patient_id)
        results.append(("Create Consultation", consultation_id is not None))
        
        if consultation_id:
            # Test 5: Prédiction
            results.append(("Predict Diagnosis", test_predict(consultation_id)))
            
            # Test 6: Explication
            results.append(("Explain Diagnosis", test_explain(consultation_id)))
    
    # Test 7: Dashboard
    results.append(("Dashboard Analytics", test_dashboard()))
    
    # Résumé
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*80)
    
    passed = sum([1 for _, result in results if result])
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés!")
    else:
        print(f"\n⚠️ {total - passed} test(s) échoué(s)")
    
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter à l'API")
        print("   Vérifiez que l'API est démarrée: python -m app.main")
        print(f"   URL: {BASE_URL}")
