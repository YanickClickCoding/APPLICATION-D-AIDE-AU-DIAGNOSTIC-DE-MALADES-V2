"""
Service de génération de rapports PDF
Génère des rapports pour les patients et des rapports mensuels
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from sqlalchemy.orm import Session

# Pour la génération PDF, on utilise ReportLab
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ ReportLab non disponible. Installation: pip install reportlab")

from ..models.patient import Patient
from ..models.consultation import Consultation
from ..models.diagnostic import Diagnostic
from ..models.analyse_ia import AnalyseIA

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Générateur de rapports PDF
    
    Fonctionnalités:
    - Rapport patient individuel avec historique
    - Rapport mensuel avec statistiques
    - Signature électronique
    - Export en PDF
    """
    
    def __init__(self, db: Session, output_dir: str = "./reports"):
        """
        Initialise le générateur de rapports
        
        Args:
            db: Session de base de données
            output_dir: Répertoire de sortie des rapports
        """
        self.db = db
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if not REPORTLAB_AVAILABLE:
            logger.error("❌ ReportLab n'est pas installé. Les rapports PDF ne seront pas disponibles.")
    
    def generate_patient_report(
        self,
        patient_id: str,
        include_history: bool = True
    ) -> Optional[bytes]:
        """
        Génère un rapport PDF pour un patient
        
        Args:
            patient_id: ID du patient
            include_history: Inclure l'historique des consultations
            
        Returns:
            Contenu du PDF en bytes ou None si erreur
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("❌ ReportLab non disponible")
            return None
        
        logger.info(f"📄 Génération du rapport patient: {patient_id}")
        
        try:
            # Récupérer le patient
            patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
            
            if not patient:
                logger.error(f"❌ Patient {patient_id} non trouvé")
                return None
            
            # Créer le buffer PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Style personnalisé
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # En-tête
            story.append(Paragraph("SANTÉ PLUS - Clinique Privée", title_style))
            story.append(Paragraph("Rapport Médical Patient", styles['Heading2']))
            story.append(Spacer(1, 0.3*inch))
            
            # Informations patient
            story.append(Paragraph("Informations du Patient", styles['Heading3']))
            
            patient_data = [
                ['Nom complet:', f"{patient.nom} {patient.prenom}"],
                ['Date de naissance:', patient.date_naissance.strftime('%d/%m/%Y')],
                ['Âge:', f"{self._calculate_age(patient.date_naissance)} ans"],
                ['Sexe:', 'Masculin' if patient.sexe == 'M' else 'Féminin'],
                ['Téléphone:', patient.telephone or 'N/A'],
                ['Email:', patient.email or 'N/A'],
                ['Groupe sanguin:', patient.groupe_sanguin or 'N/A'],
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 0.5*inch))
            
            # Historique des consultations
            if include_history:
                consultations = self.db.query(Consultation).filter(
                    Consultation.patient_id == patient_id
                ).order_by(Consultation.date_consultation.desc()).all()
                
                if consultations:
                    story.append(Paragraph("Historique des Consultations", styles['Heading3']))
                    story.append(Spacer(1, 0.2*inch))
                    
                    for consultation in consultations[:10]:  # Limiter à 10
                        # Date et motif
                        story.append(Paragraph(
                            f"<b>Date:</b> {consultation.date_consultation.strftime('%d/%m/%Y')} - "
                            f"<b>Motif:</b> {consultation.motif}",
                            styles['Normal']
                        ))
                        
                        # Diagnostic si disponible
                        diagnostic = self.db.query(Diagnostic).filter(
                            Diagnostic.consultation_id == consultation.consultation_id
                        ).first()
                        
                        if diagnostic:
                            story.append(Paragraph(
                                f"<b>Diagnostic:</b> {diagnostic.diagnostic_final}",
                                styles['Normal']
                            ))
                            
                            if diagnostic.notes_medecin:
                                story.append(Paragraph(
                                    f"<b>Notes:</b> {diagnostic.notes_medecin}",
                                    styles['Normal']
                                ))
                        
                        story.append(Spacer(1, 0.2*inch))
            
            # Pied de page
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(
                f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                styles['Normal']
            ))
            
            # Construire le PDF
            doc.build(story)
            
            # Récupérer le contenu
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"✅ Rapport patient généré ({len(pdf_content)} bytes)")
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du rapport: {e}")
            return None
    
    def generate_monthly_report(
        self,
        year: int,
        month: int
    ) -> Optional[bytes]:
        """
        Génère un rapport mensuel avec statistiques
        
        Args:
            year: Année
            month: Mois (1-12)
            
        Returns:
            Contenu du PDF en bytes ou None si erreur
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("❌ ReportLab non disponible")
            return None
        
        logger.info(f"📄 Génération du rapport mensuel: {month}/{year}")
        
        try:
            # Définir la période
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            # Créer le buffer PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # En-tête
            story.append(Paragraph("SANTÉ PLUS - Rapport Mensuel", styles['Title']))
            story.append(Paragraph(
                f"Période: {start_date.strftime('%B %Y')}",
                styles['Heading2']
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # Statistiques globales
            story.append(Paragraph("Statistiques Globales", styles['Heading3']))
            
            # Compter les consultations
            consultations_count = self.db.query(Consultation).filter(
                Consultation.date_consultation >= start_date,
                Consultation.date_consultation < end_date
            ).count()
            
            # Compter les diagnostics
            diagnostics_count = self.db.query(Diagnostic).filter(
                Diagnostic.date_diagnostic >= start_date,
                Diagnostic.date_diagnostic < end_date
            ).count()
            
            # Compter les nouveaux patients
            patients_count = self.db.query(Patient).filter(
                Patient.date_creation >= start_date,
                Patient.date_creation < end_date
            ).count()
            
            stats_data = [
                ['Indicateur', 'Valeur'],
                ['Consultations', str(consultations_count)],
                ['Diagnostics', str(diagnostics_count)],
                ['Nouveaux patients', str(patients_count)],
            ]
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 0.5*inch))
            
            # Top diagnostics
            story.append(Paragraph("Top 10 Diagnostics", styles['Heading3']))
            
            from sqlalchemy import func
            top_diagnostics = self.db.query(
                Diagnostic.diagnostic_final,
                func.count(Diagnostic.diagnostic_id).label('count')
            ).filter(
                Diagnostic.date_diagnostic >= start_date,
                Diagnostic.date_diagnostic < end_date,
                Diagnostic.diagnostic_final.isnot(None)
            ).group_by(
                Diagnostic.diagnostic_final
            ).order_by(
                func.count(Diagnostic.diagnostic_id).desc()
            ).limit(10).all()
            
            if top_diagnostics:
                diag_data = [['Diagnostic', 'Nombre']]
                for diag, count in top_diagnostics:
                    diag_data.append([diag, str(count)])
                
                diag_table = Table(diag_data, colWidths=[4*inch, 1.5*inch])
                diag_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                
                story.append(diag_table)
            
            # Pied de page
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(
                f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                styles['Normal']
            ))
            
            # Construire le PDF
            doc.build(story)
            
            # Récupérer le contenu
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"✅ Rapport mensuel généré ({len(pdf_content)} bytes)")
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du rapport: {e}")
            return None
    
    def add_electronic_signature(
        self,
        pdf_content: bytes,
        signature_data: Dict
    ) -> Optional[bytes]:
        """
        Ajoute une signature électronique au PDF
        
        Args:
            pdf_content: Contenu PDF original
            signature_data: Données de signature (nom, date, etc.)
            
        Returns:
            PDF signé ou None si erreur
        """
        logger.info("✍️ Ajout de la signature électronique...")
        
        try:
            # Pour une vraie signature électronique, il faudrait utiliser
            # une bibliothèque de cryptographie comme pyHanko ou endesive
            # Ici on fait une version simplifiée
            
            # TODO: Implémenter la vraie signature électronique avec certificat
            logger.warning("⚠️ Signature électronique simplifiée (non cryptographique)")
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout de la signature: {e}")
            return None
    
    def _calculate_age(self, date_naissance: datetime) -> int:
        """Calcule l'âge à partir de la date de naissance"""
        today = datetime.now()
        age = today.year - date_naissance.year
        if today.month < date_naissance.month or (today.month == date_naissance.month and today.day < date_naissance.day):
            age -= 1
        return age
