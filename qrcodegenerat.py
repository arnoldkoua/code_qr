import streamlit as st
import qrcode
from fpdf import FPDF
from PIL import Image
import pandas as pd
import os
import zipfile
from io import BytesIO
import shutil  # Ajout pour la suppression récursive des dossiers

# Titre de l'application
st.title("Generate Calendars with QR codes")

# Charger le fichier Excel
uploaded_file = st.file_uploader("Download Excel file", type=["xlsx"], key="excel_uploader_unique")

if uploaded_file is not None:
    # Lire les données depuis le fichier Excel
    df = pd.read_excel(uploaded_file)

    # Vérifier les colonnes nécessaires
    required_columns = ["Community", "SchoolID", "School", "Class", "Child's Name", "ID"]
    if not all(column in df.columns for column in required_columns):
        st.error(f"The Excel file must contain the following columns : {required_columns}")
    else:
        # Téléchargement de l'image du calendrier
        calendar_image = st.file_uploader("Download calendar image", type=["png", "jpg", "jpeg"], key="calendar_image_uploader_unique")
        
        if calendar_image is not None:
            # Bouton pour générer les QR codes
            if st.button("Generate calendars with QR Code"):
                # Convertir l'image téléchargée en un chemin temporaire
                calendar_image_path = f"temp_calendar_image.{calendar_image.name.split('.')[-1]}"
                with open(calendar_image_path, "wb") as f:
                    f.write(calendar_image.getbuffer())
                
                # Générer les QR codes et créer les fichiers PDF
                pdf_files = []
                qr_code_dir = "qr_code_outputs"
                if not os.path.exists(qr_code_dir):
                    os.makedirs(qr_code_dir)

                for i, row in df.iterrows():
                    # Extraire les données de l'enfant
                    community = row["Community"]
                    schoolid = row["SchoolID"]
                    school = row["School"]
                    child_class = row["Class"]
                    child_name = row["Child's Name"]
                    code = row["ID"]

                    # Convertir les données en une chaîne de caractères séparée par des virgules
                    data_str = f"{community},{schoolid},{school},{child_class},{child_name},{code}"

                    # Générer le QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(data_str)
                    qr.make(fit=True)

                    # Créer une image du QR code
                    qr_image = qr.make_image(fill_color="blue", back_color="white")
                    qr_image_path = os.path.join(qr_code_dir, f'qr_code_{i + 1}.png')
                    qr_image.save(qr_image_path)

                    # Créer le fichier PDF
                    pdf = FPDF(orientation='L', unit='mm', format='A4')
                    pdf.add_page()

                    # Ajouter l'en-tête avec l'école et le nom de l'enfant
                    pdf.set_font("Helvetica", 'B', size=12)
                    pdf.cell(25, 0, f"        School : {school}", ln=True, align='L')
                    pdf.cell(25, 20, f"        Name of the child : {child_name}", ln=True, align='L')

                    # Insérer le QR code dans le coin supérieur droit
                    pdf.image(qr_image_path, x=235, y=4, w=35, h=35)

                    # Insérer l'image du calendrier dans le PDF
                    pdf.image(calendar_image_path, x=20, y=35, w=250)

                    # Sauvegarder le fichier PDF
                    pdf_file_path = os.path.join(qr_code_dir, f"Calendar_for_{child_name.replace(' ', '_')}.pdf")
                    pdf.output(pdf_file_path)
                    pdf_files.append(pdf_file_path)

                # Créer un fichier ZIP contenant les fichiers PDF
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for pdf_file in pdf_files:
                        zip_file.write(pdf_file, os.path.basename(pdf_file))

                # Réinitialiser le pointeur du buffer
                zip_buffer.seek(0)

                # Télécharger le fichier ZIP
                st.download_button(
                    label="Download calendars with QR codes generated (ZIP)",
                    data=zip_buffer,
                    file_name="calendars_with_qr_code.zip",
                    mime="application/zip"
                )

                # Nettoyage : Supprimer les fichiers temporaires et le dossier
                shutil.rmtree(qr_code_dir)
                os.remove(calendar_image_path)
