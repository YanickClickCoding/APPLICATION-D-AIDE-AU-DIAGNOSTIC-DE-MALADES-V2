import { useState } from 'react';
import { getUtilisateurs, saveUtilisateurs } from '../db';
import type { Utilisateur } from '../types';
import { useAuth } from '../context/AuthContext';
import { Users, Search, Trash2, Shield, User, Grid, List, Mail, Calendar, Lock, X } from 'lucide-react';

const Utilisateurs = () => {
  const { user: currentUser } = useAuth();
  const [utilisateurs, setUtilisateurs] = useState<Utilisateur[]>(() => getUtilisateurs());
  const [search, setSearch] = useState('');
  const [view, setView] = useState<'grid' | 'table'>(() => (localStorage.getItem('sp_usr_view') as 'grid' | 'table') || 'grid');
  
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<{id: number, name: string} | null>(null);

  const handleViewChange = (v: 'grid' | 'table') => {
    setView(v);
    localStorage.setItem('sp_usr_view', v);
  };

  const filtered = utilisateurs.filter(u => {
    if (!u) return false;
    const term = search.toLowerCase();
    const nom = (u.nom || '').toLowerCase();
    const prenoms = (u.prenoms || '').toLowerCase();
    const email = (u.email || '').toLowerCase();
    return nom.includes(term) || prenoms.includes(term) || email.includes(term);
  });

  const handleDelete = () => {
    if (!userToDelete) return;
    const updated = utilisateurs.filter(u => u.utilisateur_id !== userToDelete.id);
    saveUtilisateurs(updated);
    setUtilisateurs(updated);
    setDeleteModalOpen(false);
  };

  const toggleRole = (id: number) => {
    const updated = utilisateurs.map(u => {
      if (u.utilisateur_id === id) {
        return { ...u, role: u.role === 'admin' ? 'medecin' as const : 'admin' as const };
      }
      return u;
    });
    saveUtilisateurs(updated);
    setUtilisateurs(updated);
  };

  return (
    <div>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Utilisateurs</h1>
          <p className="sp-page-subtitle">{filtered.length} compte(s) enregistré(s)</p>
        </div>
      </div>

      <div className="sp-card sp-fade-in">
        <div className="sp-card-header">
          <div className="sp-card-title">
            <Users size={20} /> Gestion des comptes
          </div>
          <div className="sp-toolbar">
              <div className="sp-search-box">
                <Search size={18} />
                <input 
                  type="text" 
                  placeholder="Rechercher nom, email..." 
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
                {search && <X size={14} style={{cursor:'pointer'}} onClick={() => setSearch('')} />}
              </div>
              <div className="sp-view-toggle">
                <button className={`sp-view-btn ${view === 'grid' ? 'active' : ''}`} onClick={() => handleViewChange('grid')} title="Vue cartes">
                    <Grid size={18} />
                </button>
                <button className={`sp-view-btn ${view === 'table' ? 'active' : ''}`} onClick={() => handleViewChange('table')} title="Vue tableau">
                    <List size={18} />
                </button>
              </div>
          </div>
        </div>

        {/* VUE CARTE */}
        {view === 'grid' && (
          <div id="view-grid" style={{padding:'20px'}}>
            {filtered.length === 0 ? (
              <div className="sp-empty">
                <Users size={48} style={{margin:'0 auto 1rem', opacity:0.3}} />
                <div className="sp-empty-title">Aucun utilisateur trouvé</div>
              </div>
            ) : (
              <div className="sp-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
                {filtered.map(u => {
                  const initiales = ((u.prenoms || '?').substring(0, 1) + (u.nom || '?').substring(0, 1)).toUpperCase();
                  const isAdmin = u.role === 'admin';
                  const isCurrentUser = u.utilisateur_id === currentUser?.utilisateur_id;

                  return (
                    <div className="sp-item-card" key={u.utilisateur_id} style={{ padding: '16px', position: 'relative' }}>
                      <div className="sp-item-card-header" style={{ marginBottom: '12px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                        <div className="sp-item-avatar" style={{ width: '38px', height: '38px', fontSize: '13px', borderRadius: '8px', flexShrink: 0, background: isAdmin ? 'linear-gradient(135deg, #0A4B8C, #00B4D8)' : 'linear-gradient(135deg, #7C3AED, #A78BFA)' }}>
                          {initiales}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div className="sp-item-name" style={{ fontSize: '14px', fontWeight: 700, marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {u.prenoms} {u.nom}
                            {isCurrentUser && (
                              <span style={{ fontSize: '9px', background: '#dbeafe', color: 'var(--sp-primary)', padding: '1px 5px', borderRadius: '4px', fontWeight: 600, marginLeft: '4px' }}>Vous</span>
                            )}
                          </div>
                          <div className="sp-item-meta" style={{ fontSize: '10.5px' }}>
                            <Mail size={11} />
                            <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', display: 'block' }}>
                              {u.email}
                            </span>
                          </div>
                        </div>
                        <span className={`sp-role-badge ${isAdmin ? 'admin' : 'operator'}`} style={{ fontSize: '9px', position: 'absolute', top: '16px', right: '16px' }}>
                          {isAdmin ? 'Admin' : 'Opérateur'}
                        </span>
                      </div>

                      <div className="sp-item-details" style={{ gap: '6px', marginBottom: '14px' }}>
                        <div className="sp-item-detail-row" style={{ fontSize: '11.5px' }}>
                          <Calendar size={12} style={{ color: 'var(--sp-gray-400)' }} />
                          <span>Inscrit le {new Date(u.created_at).toLocaleDateString('fr-FR')}</span>
                        </div>
                        <div className="sp-item-detail-row" style={{ fontSize: '11.5px' }}>
                          <Shield size={12} style={{ color: 'var(--sp-gray-400)' }} />
                          <span>Rôle : {u.role === 'admin' ? 'Administrateur' : 'Opérateur'}</span>
                        </div>
                      </div>

                      <div className="sp-item-actions" style={{ paddingTop: '14px', borderTop: '1px solid var(--sp-gray-100)', display: 'flex', gap: '8px', alignItems: 'center' }}>
                        {!isCurrentUser ? (
                          <>
                            <button 
                              onClick={() => toggleRole(u.utilisateur_id)}
                              className="sp-btn sp-btn-outline sp-btn-sm"
                              style={{ padding: '6px 12px', fontSize: '12px', height: '32px' }}
                            >
                              {isAdmin ? <User size={14} /> : <Shield size={14} />}
                              {isAdmin ? 'Rétrograder' : 'Promouvoir Admin'}
                            </button>
                            <button 
                              className="sp-btn sp-btn-ghost sp-btn-sm" 
                              style={{ color: 'var(--sp-danger)', padding: '6px', marginLeft: 'auto' }}
                              onClick={() => { setUserToDelete({ id: u.utilisateur_id, name: `${u.prenoms} ${u.nom}` }); setDeleteModalOpen(true); }}
                            >
                              <Trash2 size={14} />
                            </button>
                          </>
                        ) : (
                          <div style={{ padding: '4px 0', fontSize: '12px', color: 'var(--sp-gray-400)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <Lock size={12} /> Compte courant — non modifiable ici
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* VUE TABLEAU */}
        {view === 'table' && (
          <div id="view-table">
            <div className="sp-table-wrap">
              <table className="sp-table">
                <thead>
                  <tr>
                    <th>#ID</th>
                    <th>Utilisateur</th>
                    <th>Email</th>
                    <th>Rôle</th>
                    <th>Date inscription</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(u => {
                    const isAdmin = u.role === 'admin';
                    const isCurrentUser = u.utilisateur_id === currentUser?.utilisateur_id;
                    return (
                      <tr key={u.utilisateur_id}>
                        <td style={{ color: 'var(--sp-gray-400)', fontSize: '12px' }}>#{String(u.utilisateur_id).padStart(4, '0')}</td>
                        <td>
                          <div style={{ fontWeight: 600 }}>
                            {u.prenoms} {u.nom}
                            {isCurrentUser && (
                              <span style={{ fontSize: '10px', background: '#dbeafe', color: 'var(--sp-primary)', padding: '2px 7px', borderRadius: '10px', fontWeight: 600, marginLeft: '4px' }}>Vous</span>
                            )}
                          </div>
                        </td>
                        <td style={{ color: 'var(--sp-gray-500)' }}>{u.email}</td>
                        <td>
                          <span className={`sp-role-badge ${isAdmin ? 'admin' : 'operator'}`} style={{ fontSize: '10.5px' }}>
                            {isAdmin ? 'Admin' : 'Opérateur'}
                          </span>
                        </td>
                        <td>{new Date(u.created_at).toLocaleDateString('fr-FR')}</td>
                        <td>
                          {!isCurrentUser ? (
                            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                              <button 
                                onClick={() => toggleRole(u.utilisateur_id)}
                                className="sp-btn sp-btn-outline sp-btn-sm"
                                title={isAdmin ? 'Rétrograder' : 'Promouvoir Admin'}
                              >
                                {isAdmin ? <User size={14} /> : <Shield size={14} />}
                              </button>
                              <button 
                                className="sp-btn sp-btn-ghost sp-btn-sm" 
                                style={{ color: 'var(--sp-danger)' }}
                                onClick={() => { setUserToDelete({ id: u.utilisateur_id, name: `${u.prenoms} ${u.nom}` }); setDeleteModalOpen(true); }}
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          ) : (
                            <span style={{ fontSize: '11.5px', color: 'var(--sp-gray-300)' }}>—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={6} className="sp-no-results">Aucun utilisateur trouvé.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Delete Modal */}
      {deleteModalOpen && (
        <div className="sp-modal-overlay open">
          <div className="sp-modal" style={{ textAlign: 'center' }}>
            <div className="sp-modal-icon">
              <Trash2 size={26} />
            </div>
            <h3>Supprimer cet utilisateur ?</h3>
            <p>Le compte de <strong>{userToDelete?.name}</strong> sera définitivement supprimé. Cette action est irréversible.</p>
            <div className="sp-modal-actions">
              <button className="sp-btn sp-btn-ghost" onClick={() => setDeleteModalOpen(false)}>Annuler</button>
              <button className="sp-btn sp-btn-danger" onClick={handleDelete}><Trash2 size={16} /> Supprimer</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Utilisateurs;
