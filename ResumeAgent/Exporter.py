# docx_builder.py
from docx import Document

def build_docx(resume_data: dict, output_path: str):
    doc = Document()

    doc.add_heading(resume_data["name"], level=1)
    doc.add_paragraph(resume_data["summary"])

    doc.add_heading("Skills", level=2)
    doc.add_paragraph(", ".join(resume_data["skills"]))

    doc.add_heading("Experience", level=2)

    for role in resume_data["experience"]:
        doc.add_heading(
            f'{role["title"]} – {role["company"]}', level=3
        )
        for bullet in role["bullets"]:
            doc.add_paragraph(bullet, style="List Bullet")

    doc.save(output_path)
