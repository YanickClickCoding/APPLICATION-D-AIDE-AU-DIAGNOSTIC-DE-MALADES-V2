import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, User, Phone, Mail, Calendar, Activity, AlertCircle, FileText } from 'lucide-react';
import { patientsAPI } from '../services/api';

interface Patient {
  patient_id: number;
  nom: string;
  prenoms: string;
  date_naissance: string;
  sexe: 'M' | 'F';
  telephone?: string;
  email?: string;
  groupe_sanguin?: string;
  created_at: string;
}

const MesPatients = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filtered, setFiltered] = useState<Patient[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await patientsAPI.list(0, 200);
      setPatients(data);
      setFiltered(data);
    } catch (err: any) {
      setError(err.message || 'Impossible de charger les patients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPatients(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(
      patients.filter(p =>
        p.nom.toLowerCase().includes(q) ||
        p.prenoms.toLowerCase().includes(q) ||
        (p.telephone ?? '').includes(q) ||
        (p.email ?? '').toLowerCase().includes(q)
      )
    );
  }, [search, patients]);

  const calculateAge = (birthDate: string) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
    return age;
  };

  const getInitials = (nom: string, prenoms: string) =>
    `${prenoms.charAt(0)}${nom.charAt(0)}`.toUpperCase();

  const bloodGroupColor = (bg?: string) => {
    if (!bg) return { bg: '#F3F4F6', text: '#6B7280' };
    if (bg.includes('A')) return { bg: '#FEE2E2', text: '#DC2626' };
    if (bg.includes('B')) return { bg: '#DBEAFE', text: '#2563EB' };
    if (bg.includes('AB')) return { bg: '#EDE9FE', text: '#7C3AED' };
    return { bg: '#D1FAE5', text: '#065F46' };
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', flexDirection: 'column', gap: '16px' }}>
        <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        <p style={{ color: '#6B7280' }}>Chargement des patients...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto 16px' }} />
        <h3 style={{ color: '#1F2937', marginBottom: '8px' }}>Erreur de chargement</h3>
        <p style={{ color: '#6B7280', marginBottom: '16px' }}>{error}</p>
        <button onClick={fetchPatients} className="sp-btn sp-btn-primary">Réessayer</button>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Mes Patients</h1>
          <p className="sp-page-subtitle">{patients.length} patient{patients.length > 1 ? 's' : ''} enregistré{patients.length > 1 ? 's' : ''}</p>
        </div>
      </div>

      {/* Search */}
      <div className="sp-card sp-fade-in" style={{ padding: '16px 20px', marginBottom: '20px' }}>
        <div style={{ position: 'relative', maxWidth: '400px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
          <input
            type="text"
            placeholder="Rechercher par nom, prénom, téléphone..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="sp-input"
            style={{ paddingLeft: '38px' }}
          />
        </div>
      </div>

      {/* Patient Grid */}
      {filtered.length === 0 ? (
        <div className="sp-card sp-fade-in" style={{ padding: '60px', textAlign: 'center' }}>
          <User size={48} style={{ color: '#D1D5DB', margin: '0 auto 16px' }} />
          <h3 style={{ color: '#1F2937', marginBottom: '8px' }}>Aucun patient trouvé</h3>
          <p style={{ color: '#6B7280' }}>
            {search ? `Aucun résultat pour "${search}"` : 'Aucun patient enregistré dans le système.'}
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }} className="sp-fade-in">
          {filtered.map(patient => {
            const bgColor = bloodGroupColor(patient.groupe_sanguin);
            return (
              <div key={patient.patient_id} className="sp-card" style={{ padding: '20px', transition: 'box-shadow 0.2s' }}>
                {/* Header patient */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
                  <div style={{
                    width: '52px', height: '52px', borderRadius: '14px',
                    background: patient.sexe === 'M'
                      ? 'linear-gradient(135deg, #3B82F6, #1D4ED8)'
                      : 'linear-gradient(135deg, #EC4899, #BE185D)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: '#fff', fontSize: '18px', fontWeight: 700, flexShrink: 0
                  }}>
                    {getInitials(patient.nom, patient.prenoms)}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, color: '#1F2937', fontSize: '15px' }}>
                      {patient.prenoms} {patient.nom}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                      #{patient.patient_id.toString().padStart(4, '0')} · {patient.sexe === 'M' ? '♂ Masculin' : '♀ Féminin'}
                    </div>
                  </div>
                  {patient.groupe_sanguin && (
                    <span style={{
                      padding: '3px 8px', background: bgColor.bg, color: bgColor.text,
                      borderRadius: '6px', fontSize: '12px', fontWeight: 700, flexShrink: 0
                    }}>
                      {patient.groupe_sanguin}
                    </span>
                  )}
                </div>

                {/* Infos */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#4B5563' }}>
                    <Calendar size={13} style={{ color: '#9CA3AF', flexShrink: 0 }} />
                    <span>{new Date(patient.date_naissance).toLocaleDateString('fr-FR')} ({calculateAge(patient.date_naissance)} ans)</span>
                  </div>
                  {patient.telephone && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#4B5563' }}>
                      <Phone size={13} style={{ color: '#9CA3AF', flexShrink: 0 }} />
                      <span>{patient.telephone}</span>
                    </div>
                  )}
                  {patient.email && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#4B5563' }}>
                      <Mail size={13} style={{ color: '#9CA3AF', flexShrink: 0 }} />
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{patient.email}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '8px', paddingTop: '12px', borderTop: '1px solid #F3F4F6' }}>
                  <Link
                    to={`/dossier-patient/${patient.patient_id}`}
                    className="sp-btn sp-btn-primary"
                    style={{ flex: 1, justifyContent: 'center', fontSize: '13px', padding: '8px' }}
                  >
                    <FileText size={14} /> Dossier
                  </Link>
                  <Link
                    to="/consultation/nouvelle"
                    className="sp-btn sp-btn-outline"
                    style={{ flex: 1, justifyContent: 'center', fontSize: '13px', padding: '8px' }}
                  >
                    <Calendar size={14} /> Consulter
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
};

export default MesPatients;
