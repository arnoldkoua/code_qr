import streamlit as st
import qrcode
from fpdf import FPDF
from PIL import Image
import pandas as pd
import os

# Titre de l'application
st.title("Génération de calendriers avec QR codes")

# Charger le fichier Excel
uploaded_file = st.file_uploader("Téléchargez le fichier Excel", type=["xlsx"], key="excel_uploader_unique")

if uploaded_file is not None:
    # Lire les données depuis le fichier Excel
    df = pd.read_excel(uploaded_file)

    # Vérifier les colonnes nécessaires
    required_columns = ["School", "Class", "Child's Name", "Code"]
    if not all(column in df.columns for column in required_columns):
        st.error(f"Le fichier Excel doit contenir les colonnes suivantes : {required_columns}")
    else:
        # Téléchargement de l'image du calendrier
        calendar_image = st.file_uploader("Téléchargez l'image du calendrier", type=["png", "jpg", "jpeg"], key="calendar_image_uploader_unique")
        
        if calendar_image is not None:
            # Convertir l'image téléchargée en un chemin temporaire
            calendar_image_path = f"temp_calendar_image.{calendar_image.name.split('.')[-1]}"
            with open(calendar_image_path, "wb") as f:
                f.write(calendar_image.getbuffer())
            
            # Générer les QR codes et créer les fichiers PDF
            pdf_files = []

            for i, row in df.iterrows():
                # Extraire les données de l'enfant
                school = row["School"]
                child_class = row["Class"]
                child_name = row["Child's Name"]
                code = row["Code"]

                # Convertir les données en une chaîne de caractères séparée par des virgules
                data_str = f"{school},{child_class},{child_name},{code}"

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
                qr_image_path = f'temp_qr_code_{i + 1}.png'
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
                pdf_file_path = f"Calendar_for_{child_name.replace(' ', '_')}.pdf"
                pdf.output(pdf_file_path)
                pdf_files.append(pdf_file_path)

                # Supprimer les images temporaires
                os.remove(qr_image_path)

            # Afficher les fichiers PDF générés et permettre le téléchargement
            st.success("Les fichiers PDF ont été générés avec succès.")
            for pdf_file in pdf_files:
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label=f"Télécharger {pdf_file}",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

            # Supprimer les fichiers PDF générés
            for pdf_file in pdf_files:
                os.remove(pdf_file)

            # Supprimer l'image temporaire du calendrier
            os.remove(calendar_image_path)
