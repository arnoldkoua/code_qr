import streamlit as st
import qrcode
from fpdf import FPDF
from PIL import Image
import pandas as pd
import os
import zipfile
from io import BytesIO
import shutil

# Titre de l'application
st.title("Generate Calendars with QR codes")

# Charger le fichier Excel
uploaded_file = st.file_uploader("Download Excel file", type=["xlsx"], key="excel_uploader_unique")

if uploaded_file is not None:
    # Lire les données depuis le fichier Excel
    df = pd.read_excel(uploaded_file)

    # Vérifier les colonnes nécessaires
    required_columns = ["community", "school_id", "school_name", "child_id", "child_name", "child_gender", "class", "teacher_name", "teacher_gender"]
    if not all(column in df.columns for column in required_columns):
        st.error(f"The Excel file must contain the following columns : {required_columns}")
    else:
        # Télécharger l'image du calendrier (recto)
        calendar_image = st.file_uploader("Download calendar image (front side)", type=["png", "jpg", "jpeg"], key="calendar_image_uploader_unique")
        # Télécharger l'image du verso
        back_image = st.file_uploader("Download back image (back side)", type=["png", "jpg", "jpeg"], key="back_image_uploader_unique")
        
        if calendar_image is not None and back_image is not None:
            # Bouton pour générer les QR codes
            if st.button("Generate calendars with QR Code"):
                # Convertir les images téléchargées en chemins temporaires
                calendar_image_path = f"temp_calendar_image.{calendar_image.name.split('.')[-1]}"
                back_image_path = f"temp_back_image.{back_image.name.split('.')[-1]}"
                with open(calendar_image_path, "wb") as f:
                    f.write(calendar_image.getbuffer())
                with open(back_image_path, "wb") as f:
                    f.write(back_image.getbuffer())
                
                # Générer les QR codes et créer les fichiers PDF
                pdf_files = []
                qr_code_dir = "qr_code_outputs"
                if not os.path.exists(qr_code_dir):
                    os.makedirs(qr_code_dir)

                for i, row in df.iterrows():
                    # Extraire les données de l'enfant
                    community = row["community"]
                    schoolid = row["school_id"]
                    school = row["school_name"]
                    child_id = row["child_id"]
                    child_name = row["child_name"]
                    child_gender = row["child_gender"]
                    child_class = row["class"]
                    teacher_name = row["teacher_name"]
                    teacher_gender = row["teacher_gender"]

                    # Convertir les données en une chaîne de caractères séparée par des virgules
                    data_str = f"{community},{schoolid},{school},{child_id},{child_name},{child_gender},{child_class},{teacher_name},{teacher_gender}"

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
                    pdf = FPDF(unit='mm', format='A4')

                    # Ajouter le recto avec l'école, le nom de l'enfant, et le QR code
                    # Ajouter le recto (page en paysage)
                    pdf.add_page(orientation='L')
                    pdf.set_font("Helvetica", 'B', size=12)
                    # pdf.cell(25, 0, f"        School : {school}", ln=True, align='L')
                    pdf.cell(190, 20, f"                                          School : {school}          Class : {child_class}         Name of the child: {child_name}", ln=True, align='L')
                    pdf.image(qr_image_path, x=19, y=2, w=35, h=35)
                    pdf.image(calendar_image_path, x=20, y=27, w=250)

                    # Ajouter le verso (page en portrait)
                    pdf.add_page(orientation='P')
                    pdf.image(back_image_path, x=10, y=10, w=190)  # Ajustez les dimensions et la position selon vos besoins

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
                os.remove(back_image_path)
