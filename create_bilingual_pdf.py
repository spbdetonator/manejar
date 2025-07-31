#!/usr/bin/env python3
"""
Bilingual PDF Generator for Spanish-Russian Traffic Questions

This script extracts questions from a Spanish PDF questionnaire about traffic
and driving, translates them to Russian using a comprehensive dictionary, and
creates a bilingual PDF with both Spanish and Russian versions of each question.

Requirements:
- PyPDF2: for PDF text extraction
- reportlab: for PDF generation

Usage:
    python3 create_bilingual_pdf.py

The script will:
1. Extract questions from CUESTIONARIO-DE-PREGUNTAS-Y-RESPUESTAS-.OLAVARRIA-NUEVO-3-1.pdf
2. Translate each question and answer to Russian
3. Generate CUESTIONARIO-BILINGUE-ES-RU.pdf with bilingual content
"""

import PyPDF2
import re
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import os

# Comprehensive Spanish to Russian translation dictionary for traffic/driving context
COMPREHENSIVE_TRANSLATIONS = {
    # Questions words and basic terms
    "¿Qué": "Что",
    "¿Cuál": "Какой", 
    "¿Cuáles": "Какие",
    "¿Cómo": "Как",
    "¿Dónde": "Где",
    "¿Cuándo": "Когда",
    "¿Por qué": "Почему",
    "¿A qué": "К чему",
    "¿En qué": "В чём",
    "¿De qué": "О чём",
    "¿Según": "Согласно",
    "¿Puede": "Может ли",
    "¿Debe": "Должен ли",
    "¿Es": "Является ли",
    "¿Está": "Находится ли",
    
    # Answers and options
    "Verdadero": "Верно",
    "Falso": "Неверно",
    "A.": "А.",
    "B.": "Б.", 
    "C.": "В.",
    "Sí": "Да",
    "No": "Нет",
    
    # Traffic and vehicle terms
    "factor se deben la mayoría de los siniestros viales": "фактор является причиной большинства дорожно-транспортных происшествий",
    "Organización Mundial de la Salud": "Всемирная организация здравоохранения",
    "resultado de diversos factores": "результат различных факторов",
    "aumentar la propia seguridad": "повысить собственную безопасность",
    "condiciones en que se encuentran": "условия, в которых находятся",
    "infraestructura vial": "дорожная инфраструктура",
    "condiciones climáticas": "климатические условия",
    "factor ambiental": "экологический фактор",
    "principal factor de riesgo": "основной фактор риска",
    "condiciones meteorológicas": "метеорологические условия",
    "fallas mecánicas": "механические неисправности",
    "conductas negligentes": "небрежное поведение",
    "propietarios de los vehículos": "владельцы транспортных средств",
    "verificación del estado": "проверка состояния",
    "incidente de tránsito": "дорожный инцидент",
    "incidente vial": "дорожное происшествие",
    "circulación en la vía pública": "движение по общественным дорогам",
    "usuarios de la vía pública": "пользователи общественных дорог",
    "responsable de una parte del tránsito": "ответственен за часть дорожного движения",
    "no causar peligro": "не создавать опасность",
    "entorpecer la circulación": "препятствовать движению",
    "estamos obligados": "мы обязаны",
    "perjuicios o molestias innecesarias": "ненужный вред или неудобства",
    "víctimas fatales": "смертельные жертвы",
    "lesionados graves": "серьёзно пострадавшие",
    "siniestro de tránsito": "дорожно-транспортное происшествие",
    "daños materiales": "материальный ущерб",
    "costos sanitarios": "медицинские расходы",
    "costos administrativos": "административные расходы",
    "premisa básica": "основная предпосылка",
    "obligación de no entorpecer": "обязательство не препятствовать",
    "experiencia de manejo": "опыт вождения",
    "cursos de actualización": "курсы повышения квалификации",
    "temática vial": "дорожная тематика",
    "frecuencia no mayor": "частота не более",
    "principios básicos": "основные принципы",
    "sistema de tránsito": "система дорожного движения",
    "velocidad y confort": "скорость и комфорт",
    "fluidez y seguridad": "плавность и безопасность",
    "comodidad y agilidad": "удобство и ловкость",
    "mayor probabilidad de siniestralidad": "большая вероятность аварий",
    "menor cantidad de vehículos": "меньшее количество транспортных средств",
    "mayor cantidad de vehículos": "большее количество транспортных средств",
    "menor probabilidad": "меньшая вероятность",
    "usuarios de la vía": "пользователи дороги",
    "ordenados de más a menos vulnerable": "упорядочены от наиболее к наименее уязвимым",
    "demarcación horizontal verde": "зелёная горизонтальная разметка",
    "intersección hay una ciclovía": "перекрёстке есть велосипедная дорожка",
    "se aproxima a un cruce ferroviario": "приближается к железнодорожному переезду",
    "cruce exclusivo de peatones": "пешеходный переход",
    "demarcación de la senda peatonal": "разметка пешеходной дорожки",
    "por dónde deben cruzar": "где должны переходить",
    "es indistinto": "всё равно",
    "miren a ambos lados": "посмотрят в обе стороны",
    "coincidencia con las paradas": "совпадение с остановками",
    "prolongación longitudinal": "продольное продолжение",
    "carriles exclusivos": "выделенные полосы",
    "único sentido de circulación": "одностороннее движение",
    "bandas longitudinales demarcadas": "размеченные продольные полосы",
    "calzada destinadas": "проезжая часть предназначена",
    "determinados vehículos": "определённые транспортные средства",
    "ambulancias, bomberos": "скорая помощь, пожарные",
    "vehículos policiales": "полицейские машины",
    
    # Basic vehicle and driving terms
    "vehículo": "транспортное средство",
    "vehículos": "транспортные средства",
    "automóvil": "автомобиль",
    "conductor": "водитель",
    "conductores": "водители",
    "conducir": "водить",
    "conducción": "вождение",
    "tránsito": "дорожное движение",
    "circulación": "движение",
    "vía pública": "общественная дорога",
    "calzada": "проезжая часть",
    "peatón": "пешеход",
    "peatones": "пешеходы",
    "licencia": "лицензия",
    "licencia de conducir": "водительские права",
    "seguridad": "безопасность",
    "velocidad": "скорость",
    "límite": "ограничение",
    "siniestro": "авария",
    "accidente": "авария",
    "colisión": "столкновение",
    "semáforo": "светофор",
    "señal": "знак",
    "señalización": "знаки",
    "carril": "полоса",
    "carriles": "полосы",
    "autopista": "автомагистраль",
    "avenida": "проспект",
    "calle": "улица",
    "esquina": "угол",
    "cruce": "перекресток",
    "intersección": "пересечение",
    "estacionamiento": "парковка",
    "estacionar": "парковаться",
    "parar": "останавливаться",
    "detener": "останавливать",
    "frenar": "тормозить",
    "girar": "поворачивать",
    "derecha": "направо",
    "izquierda": "налево",
    "adelantar": "обгонять",
    "adelantamiento": "обгон",
    "distancia": "расстояние",
    "metro": "метр",
    "metros": "метров",
    "kilómetro": "километр",
    "kilómetros": "километров",
    "hora": "час",
    "horas": "часов",
    "km/h": "км/ч",
    "alcohol": "алкоголь",
    "alcoholemia": "содержание алкоголя в крови",
    "sangre": "кровь",
    "fatiga": "усталость",
    "cansancio": "усталость",
    "luces": "фары",
    "cinturón": "ремень",
    "cinturón de seguridad": "ремень безопасности",
    "casco": "шлем",
    "documento": "документ",
    "documentación": "документы",
    "infracción": "нарушение",
    "multa": "штраф",
    "prohibido": "запрещено",
    "obligatorio": "обязательно",
    "permitido": "разрешено",
    "responsabilidad": "ответственность",
    "responsable": "ответственный",
    "norma": "норма",
    "normas": "нормы",
    "ley": "закон",
    "reglamento": "правила",
    "edad": "возраст",
    "menor": "несовершеннолетний",
    "menores": "несовершеннолетние",
    "adulto": "взрослый",
    "persona": "человек",
    "personas": "люди",
    "pasajero": "пассажир",
    "pasajeros": "пассажиры",
    "transporte": "транспорт",
    "público": "общественный",
    "privado": "частный",
    "emergencia": "чрезвычайная ситуация",
    "ambulancia": "скорая помощь",
    "bomberos": "пожарная",
    "policía": "полиция",
    "hospital": "больница",
    "zona": "зона",
    "urbana": "городская",
    "rural": "сельская",
    "escuela": "школа",
    "túnel": "туннель",
    "puente": "мост",
    "curva": "поворот",
    "recta": "прямая",
    "subida": "подъем",
    "bajada": "спуск",
    "lluvia": "дождь",
    "nieve": "снег",
    "niebla": "туман",
    "viento": "ветер",
    "día": "день",
    "noche": "ночь",
    "clima": "погода",
    "visibilidad": "видимость",
    "espejo": "зеркало",
    "retrovisor": "зеркало заднего вида",
    "motor": "двигатель",
    "frenos": "тормоза",
    "neumático": "шина",
    "neumáticos": "шины",
    "combustible": "топливо",
    "aceite": "масло",
    "batería": "аккумулятор",
    "mantenimiento": "техническое обслуживание",
    "reparación": "ремонт",
    "verificación": "проверка",
    "inspección": "осмотр",
    
    # Additional common words
    "el": "",
    "la": "",
    "los": "",
    "las": "",
    "un": "",
    "una": "",
    "de": "",
    "del": "",
    "que": "что",
    "en": "в",
    "con": "с",
    "por": "по",
    "para": "для",
    "al": "",
    "se": "",
    "como": "как",
    "más": "более",
    "menos": "менее",
    "todo": "весь",
    "toda": "вся",
    "todos": "все",
    "todas": "все",
    "otro": "другой",
    "otra": "другая",
    "otros": "другие",
    "otras": "другие",
    "mismo": "тот же",
    "misma": "та же",
    "mismos": "те же",
    "mismas": "те же",
    "este": "этот",
    "esta": "эта",
    "estos": "эти",
    "estas": "эти",
    "ese": "тот",
    "esa": "та",
    "esos": "те",
    "esas": "те",
    "cuando": "когда",
    "donde": "где",
    "como": "как",
    "porque": "потому что",
    "pero": "но",
    "sin": "без",
    "desde": "с",
    "hasta": "до",
    "entre": "между",
    "sobre": "на",
    "bajo": "под",
    "ante": "перед",
    "tras": "за",
    "durante": "во время",
    "mediante": "посредством",
    "según": "согласно",
    "excepto": "кроме",
    "salvo": "кроме",
    "menos": "кроме",
    "incluso": "даже",
    "también": "также",
    "tampoco": "тоже не",
    "siempre": "всегда",
    "nunca": "никогда",
    "jamás": "никогда",
    "ya": "уже",
    "aún": "ещё",
    "todavía": "ещё",
    "apenas": "едва",
    "solo": "только",
    "sólo": "только",
    "solamente": "только",
    "únicamente": "исключительно"
}

def comprehensive_translate(text):
    """Comprehensive Spanish to Russian translation"""
    result = text
    
    # Sort translations by length (longer first) to avoid partial replacements
    sorted_translations = sorted(COMPREHENSIVE_TRANSLATIONS.items(), 
                                 key=lambda x: len(x[0]), reverse=True)
    
    for spanish, russian in sorted_translations:
        if spanish in result:
            result = result.replace(spanish, russian)
    
    return result

def extract_questions_from_pdf(pdf_path):
    """Extract questions and answers from the PDF file"""
    questions = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        # Extract all text
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
    
    # Split into lines and clean
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    
    # Filter out headers, page numbers, etc.
    filtered_lines = []
    for line in lines:
        # Skip headers and title pages
        if any(skip in line.lower() for skip in ['batería de preguntas', 'preguntas examen', 'licencia de conducir', 
                                                 'anexo i:', 'preguntas generales', 'algunas de las preguntas']):
            continue
        filtered_lines.append(line)
    
    # Process questions - look for question patterns followed by options
    i = 0
    question_num = 1
    
    while i < len(filtered_lines):
        line = filtered_lines[i]
        
        # Check if this line looks like a question (ends with ?)
        if line.endswith('?') and len(line) > 20:
            question_text = line
            options = []
            
            # Look ahead for options
            j = i + 1
            option_count = 0
            while j < len(filtered_lines) and j < i + 10 and option_count < 5:
                next_line = filtered_lines[j]
                
                # Check for multiple choice options
                if re.match(r'^[ABC]\.\s+', next_line):
                    options.append(next_line)
                    option_count += 1
                # Check for True/False options
                elif re.match(r'^•\s*(Verdadero|Falso)', next_line):
                    options.append(next_line)
                    option_count += 1
                # If we find another question, stop
                elif next_line.endswith('?') and len(next_line) > 20:
                    break
                # If we find something that looks like a section header, stop
                elif next_line.isupper() and len(next_line) > 10:
                    break
                
                j += 1
            
            # Special handling for True/False questions
            if len(options) == 0:
                # Look for "Verdadero" and "Falso" pattern
                j = i + 1
                verdadero_found = False
                falso_found = False
                while j < len(filtered_lines) and j < i + 5:
                    if 'Verdadero' in filtered_lines[j]:
                        verdadero_found = True
                    if 'Falso' in filtered_lines[j]:
                        falso_found = True
                    j += 1
                
                if verdadero_found and falso_found:
                    options = ['• Verdadero', '• Falso']
            
            # Add question if we found options
            if options:
                questions.append({
                    'number': question_num,
                    'question': question_text,
                    'options': options
                })
                question_num += 1
                
                # Skip past the options we just processed
                i = j
            else:
                i += 1
        else:
            i += 1
    
    return questions

def create_bilingual_pdf(questions, output_path):
    """Create a bilingual PDF with Spanish and Russian translations"""
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=15,
        alignment=1,
        textColor='grey'
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    
    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=15,
        spaceBefore=2,
        spaceAfter=2
    )
    
    russian_question_style = ParagraphStyle(
        'RussianQuestionStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=6,
        spaceAfter=4,
        fontName='Helvetica-Bold',
        textColor='darkblue'
    )
    
    russian_answer_style = ParagraphStyle(
        'RussianAnswerStyle',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=15,
        spaceBefore=2,
        spaceAfter=2,
        textColor='darkblue'
    )
    
    # Add title
    title = Paragraph("CUESTIONARIO BILINGÜE ESPAÑOL-RUSO<br/>ESPAÑOL-РУССКИЙ ВОПРОСНИК", title_style)
    story.append(title)
    
    subtitle = Paragraph("Preguntas de Examen Teórico - Licencia de Conducir<br/>Вопросы теоретического экзамена - Водительские права", subtitle_style)
    story.append(subtitle)
    
    story.append(Spacer(1, 15))
    
    # Process each question
    for i, q in enumerate(questions):
        print(f"Processing question {i + 1}/{len(questions)}")
        
        # Add Spanish question
        question_text = f"{q['number']}. {q['question']}"
        story.append(Paragraph(f"<b>{question_text}</b>", question_style))
        
        # Add Spanish options
        for option in q['options']:
            story.append(Paragraph(option, answer_style))
        
        # Add Russian translation
        russian_question = comprehensive_translate(q['question'])
        story.append(Paragraph(f"<b>{q['number']}. {russian_question}</b>", russian_question_style))
        
        # Add Russian options
        for option in q['options']:
            russian_option = comprehensive_translate(option)
            story.append(Paragraph(russian_option, russian_answer_style))
        
        # Add spacing between questions
        story.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(story)
    print(f"PDF created: {output_path}")

def main():
    # Input and output paths
    input_pdf = "/home/runner/work/manejar/manejar/CUESTIONARIO-DE-PREGUNTAS-Y-RESPUESTAS-.OLAVARRIA-NUEVO-3-1.pdf"
    output_pdf = "/home/runner/work/manejar/manejar/CUESTIONARIO-BILINGUE-ES-RU.pdf"
    
    print("Extracting questions from PDF...")
    questions = extract_questions_from_pdf(input_pdf)
    print(f"Extracted {len(questions)} questions")
    
    print("Creating bilingual PDF...")
    create_bilingual_pdf(questions, output_pdf)
    
    print(f"Bilingual PDF created successfully: {output_pdf}")

if __name__ == "__main__":
    main()